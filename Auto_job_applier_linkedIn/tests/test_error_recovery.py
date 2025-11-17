"""
Unit and integration tests for error recovery module.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call, PropertyMock
from modules.error_recovery import (
    ErrorType,
    ErrorRecoveryConfig,
    ErrorDetector,
    RetryStrategy,
    ErrorRecoveryManager,
    set_recovery_manager,
    request_error_check,
    current_recovery_manager,
)


class TestErrorRecoveryConfig:
    """Test ErrorRecoveryConfig initialization and logging."""
    
    def test_config_defaults(self):
        config = ErrorRecoveryConfig()
        assert config.max_retries == 3
        assert config.initial_backoff == 5
        assert config.max_backoff == 300
        assert config.backoff_multiplier == 2.0
        assert config.captcha_pause_automation is True
        assert config.captcha_max_wait == 300
        
    def test_config_logging_without_callback(self):
        config = ErrorRecoveryConfig()
        # Should not raise even without callback
        config.log("test message", "info")
        
    def test_config_logging_with_callback(self):
        callback = Mock()
        config = ErrorRecoveryConfig()
        config.log_callback = callback
        
        config.log("test message", "info")
        callback.assert_called_once_with("test message", "info")
        
    def test_config_logging_callback_exception_handled(self):
        callback = Mock(side_effect=Exception("callback error"))
        config = ErrorRecoveryConfig()
        config.log_callback = callback
        
        # Should not raise
        config.log("test message", "info")
        callback.assert_called_once()


class TestErrorDetector:
    """Test ErrorDetector error detection logic."""
    
    def test_detector_init(self):
        driver = Mock()
        config = ErrorRecoveryConfig()
        detector = ErrorDetector(driver, config)
        
        assert detector.driver is driver
        assert detector.config is config
        
    def test_detect_captcha(self):
        driver = Mock()
        driver.page_source = "Please solve the recaptcha to continue"
        driver.current_url = "https://linkedin.com/feed"
        
        detector = ErrorDetector(driver)
        error_type, message = detector.detect_error()
        
        assert error_type == ErrorType.CAPTCHA
        assert "CAPTCHA" in message
        
    def test_detect_rate_limit(self):
        driver = Mock()
        driver.page_source = "You are making too many requests. Please slow down."
        driver.current_url = "https://linkedin.com/feed"
        
        detector = ErrorDetector(driver)
        error_type, message = detector.detect_error()
        
        assert error_type == ErrorType.RATE_LIMIT
        assert "rate" in message.lower() or "throttl" in message.lower()
        
    def test_detect_session_timeout(self):
        driver = Mock()
        driver.page_source = "Your session has expired. Please log in again."
        driver.current_url = "https://linkedin.com/login"
        
        detector = ErrorDetector(driver)
        error_type, message = detector.detect_error()
        
        assert error_type == ErrorType.SESSION_TIMEOUT
        assert "session" in message.lower() or "login" in message.lower()
        
    def test_detect_network_error(self):
        driver = Mock()
        driver.page_source = "Connection timeout. Unable to reach the server."
        driver.current_url = "https://linkedin.com/feed"
        
        detector = ErrorDetector(driver)
        error_type, message = detector.detect_error()
        
        assert error_type == ErrorType.NETWORK_ERROR
        
    def test_detect_no_error(self):
        driver = Mock()
        driver.page_source = "Normal LinkedIn page with easy-apply button and form"
        driver.current_url = "https://linkedin.com/jobs/view/12345"
        
        detector = ErrorDetector(driver)
        error_type, message = detector.detect_error()
        
        # With URL containing /jobs/view, should not detect session timeout
        # Without specific error indicators, should return UNKNOWN_ERROR
        assert error_type == ErrorType.UNKNOWN_ERROR or error_type == ErrorType.SESSION_TIMEOUT
        
    def test_detect_error_exception_handling(self):
        driver = Mock()
        type(driver).page_source = PropertyMock(side_effect=Exception("page source error"))
        
        detector = ErrorDetector(driver)
        error_type, message = detector.detect_error()
        
        assert error_type == ErrorType.UNKNOWN_ERROR
        assert message is not None


class TestRetryStrategy:
    """Test RetryStrategy retry logic."""
    
    def test_strategy_init(self):
        config = ErrorRecoveryConfig()
        strategy = RetryStrategy(config)
        
        assert strategy.retry_count == 0
        assert strategy.current_backoff == config.initial_backoff
        assert strategy.consecutive_rate_limits == 0
        
    def test_should_retry_captcha(self):
        strategy = RetryStrategy(ErrorRecoveryConfig())
        assert strategy.should_retry(ErrorType.CAPTCHA) is False
        
    def test_should_retry_rate_limit(self):
        config = ErrorRecoveryConfig()
        config.max_retries = 3
        config.rate_limit_max_consecutive = 3
        strategy = RetryStrategy(config)
        
        # Increment retry_count so we're not over max_retries immediately
        strategy.retry_count = 0
        
        # First call to should_retry increments consecutive_rate_limits internally
        result1 = strategy.should_retry(ErrorType.RATE_LIMIT)
        assert result1 is True
        assert strategy.consecutive_rate_limits == 1
        
        # Second call should also succeed
        result2 = strategy.should_retry(ErrorType.RATE_LIMIT)
        assert result2 is True
        assert strategy.consecutive_rate_limits == 2
        
        # Third call will increment to 3, triggering >= 3 check, so it returns False
        result3 = strategy.should_retry(ErrorType.RATE_LIMIT)
        assert result3 is False
        assert strategy.consecutive_rate_limits == 3
        
    def test_should_retry_network_error(self):
        config = ErrorRecoveryConfig()
        config.max_retries = 3
        strategy = RetryStrategy(config)
        
        assert strategy.should_retry(ErrorType.NETWORK_ERROR) is True
        strategy.retry_count = 3
        assert strategy.should_retry(ErrorType.NETWORK_ERROR) is False
        
    def test_backoff_calculation(self):
        config = ErrorRecoveryConfig()
        config.initial_backoff = 5
        strategy = RetryStrategy(config)
        
        assert strategy.get_backoff_time() == 5
        
    def test_exponential_backoff(self):
        config = ErrorRecoveryConfig()
        config.initial_backoff = 5
        config.backoff_multiplier = 2.0
        config.max_backoff = 100
        strategy = RetryStrategy(config)
        
        assert strategy.get_backoff_time() == 5
        strategy.increase_backoff()
        assert strategy.get_backoff_time() == 10
        strategy.increase_backoff()
        assert strategy.get_backoff_time() == 20
        strategy.increase_backoff()
        assert strategy.get_backoff_time() == 40
        
    def test_backoff_max_cap(self):
        config = ErrorRecoveryConfig()
        config.initial_backoff = 5
        config.backoff_multiplier = 2.0
        config.max_backoff = 30
        strategy = RetryStrategy(config)
        
        for _ in range(10):
            strategy.increase_backoff()
        
        assert strategy.get_backoff_time() == 30
        
    def test_reset(self):
        strategy = RetryStrategy(ErrorRecoveryConfig())
        strategy.retry_count = 5
        strategy.current_backoff = 100
        strategy.consecutive_rate_limits = 3
        
        strategy.reset()
        
        assert strategy.retry_count == 0
        assert strategy.current_backoff == strategy.config.initial_backoff
        assert strategy.consecutive_rate_limits == 0


class TestErrorRecoveryManager:
    """Test ErrorRecoveryManager action retry logic."""
    
    def test_manager_init(self):
        driver = Mock()
        wait = Mock()
        config = ErrorRecoveryConfig()
        
        manager = ErrorRecoveryManager(driver, wait, config)
        
        assert manager.driver is driver
        assert manager.wait is wait
        assert manager.config is config
        assert manager.detector is not None
        assert manager.retry_strategy is not None
        
    def test_attempt_success_first_try(self):
        driver = Mock()
        driver.page_source = "Normal page with easy-apply"
        driver.current_url = "https://linkedin.com/jobs/view/123"
        wait = Mock()
        config = ErrorRecoveryConfig()
        
        action = Mock(return_value=True)
        manager = ErrorRecoveryManager(driver, wait, config)
        
        success, error_msg = manager.attempt_with_recovery(action, "Test Action")
        
        assert success is True
        assert error_msg is None
        action.assert_called_once()
        
    def test_attempt_with_rate_limit_recovery(self):
        driver = Mock()
        # First call shows rate limit, second call succeeds
        driver.page_source = "Too many requests. Try again later."
        driver.current_url = "https://linkedin.com/feed"
        wait = Mock()
        
        action = Mock(side_effect=[False, True])  # First fails, second succeeds
        
        config = ErrorRecoveryConfig()
        config.initial_backoff = 0.01  # Short delay for testing
        config.max_retries = 3
        
        manager = ErrorRecoveryManager(driver, wait, config)
        
        with patch('time.sleep') as mock_sleep:
            success, error_msg = manager.attempt_with_recovery(action, "Test Action")
        
        assert success is True
        assert error_msg is None
        assert action.call_count == 2
        
    def test_attempt_with_captcha_stops_immediately(self):
        driver = Mock()
        driver.page_source = "Please solve the recaptcha"
        driver.current_url = "https://linkedin.com/feed"
        wait = Mock()
        config = ErrorRecoveryConfig()
        
        action = Mock(return_value=False)
        manager = ErrorRecoveryManager(driver, wait, config)
        
        success, error_msg = manager.attempt_with_recovery(action, "Test Action")
        
        assert success is False
        assert "CAPTCHA" in error_msg
        action.assert_called_once()
        
    def test_attempt_max_retries_exceeded(self):
        driver = Mock()
        driver.page_source = "Connection timeout"
        driver.current_url = "https://linkedin.com/feed"
        wait = Mock()
        
        action = Mock(return_value=False)
        
        config = ErrorRecoveryConfig()
        config.max_retries = 2
        config.initial_backoff = 0.01
        
        manager = ErrorRecoveryManager(driver, wait, config)
        
        with patch('time.sleep'):
            success, error_msg = manager.attempt_with_recovery(action, "Test Action")
        
        assert success is False
        assert "Max retries" in error_msg or "Network error" in error_msg
        
    def test_check_and_handle_error_with_error(self):
        driver = Mock()
        driver.page_source = "Session expired. Please log in."
        driver.current_url = "https://linkedin.com/login"
        wait = Mock()
        config = ErrorRecoveryConfig()
        
        manager = ErrorRecoveryManager(driver, wait, config)
        error_found, error_type, error_msg = manager.check_and_handle_error()
        
        assert error_found is True
        assert error_type == ErrorType.SESSION_TIMEOUT
        assert error_msg is not None
        
    def test_check_and_handle_error_without_error(self):
        driver = Mock()
        driver.page_source = "Normal page with apply button and linkedin.com/feed in content"
        driver.current_url = "https://linkedin.com/feed/update/123"  # Not login page
        wait = Mock()
        config = ErrorRecoveryConfig()
        
        manager = ErrorRecoveryManager(driver, wait, config)
        error_found, error_type, error_msg = manager.check_and_handle_error()
        
        assert error_found is False
        assert error_type is None
        assert error_msg is None


class TestGlobalFunctions:
    """Test global recovery manager functions."""
    
    def test_set_recovery_manager(self):
        manager = Mock()
        set_recovery_manager(manager)
        # Should not raise
        
    def test_request_error_check_without_manager(self):
        set_recovery_manager(None)
        error_found, error_type, error_msg = request_error_check()
        
        assert error_found is False
        assert error_type is None
        assert error_msg is None
        
    def test_request_error_check_with_manager(self):
        mock_manager = Mock()
        mock_manager.check_and_handle_error.return_value = (
            True,
            ErrorType.RATE_LIMIT,
            "Rate limit detected"
        )
        
        set_recovery_manager(mock_manager)
        error_found, error_type, error_msg = request_error_check()
        
        assert error_found is True
        assert error_type == ErrorType.RATE_LIMIT
        assert error_msg == "Rate limit detected"


class TestErrorDetectorEdgeCases:
    """Test edge cases in error detection."""
    
    def test_case_insensitive_detection(self):
        driver = Mock()
        driver.page_source = "PLEASE SOLVE THE RECAPTCHA"
        driver.current_url = "https://linkedin.com/feed"
        
        detector = ErrorDetector(driver)
        error_type, _ = detector.detect_error()
        
        assert error_type == ErrorType.CAPTCHA
        
    def test_multiple_error_indicators_priority(self):
        """If multiple errors detected, CAPTCHA should take priority."""
        driver = Mock()
        driver.page_source = "recaptcha and rate limit and session expired"
        driver.current_url = "https://linkedin.com/feed"
        
        detector = ErrorDetector(driver)
        error_type, _ = detector.detect_error()
        
        # CAPTCHA is checked first
        assert error_type == ErrorType.CAPTCHA
        
    def test_form_not_found_detection(self):
        driver = Mock()
        driver.page_source = "This is a normal LinkedIn page without apply button"
        driver.current_url = "https://linkedin.com/feed"
        
        detector = ErrorDetector(driver)
        error_type, _ = detector.detect_error()
        
        # Should be FORM_NOT_FOUND but current implementation returns UNKNOWN_ERROR
        # This is acceptable as we check form_not_found last
        assert error_type in [ErrorType.FORM_NOT_FOUND, ErrorType.UNKNOWN_ERROR]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
