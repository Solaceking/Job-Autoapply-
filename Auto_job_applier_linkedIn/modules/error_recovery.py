"""
Error detection and recovery module for LinkedIn automation.

Detects common application errors (CAPTCHA, rate limits, session timeout, etc.)
and provides recovery strategies with exponential backoff retry logic.
"""

import time
import re
import threading
import csv
import os
from datetime import datetime
from typing import Optional, Tuple, Callable
from enum import Enum
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from config.settings import logs_folder_path
from modules.helpers import make_directories


class ErrorType(Enum):
    """Enumeration of detectable error types."""
    CAPTCHA = "captcha"
    RATE_LIMIT = "rate_limit"
    SESSION_TIMEOUT = "session_timeout"
    NETWORK_ERROR = "network_error"
    FORM_NOT_FOUND = "form_not_found"
    LOGIN_REQUIRED = "login_required"
    UNKNOWN_ERROR = "unknown_error"


class ErrorRecoveryConfig:
    """Configuration for error recovery behavior."""
    
    def __init__(self):
        # Retry configuration
        self.max_retries = 3
        self.initial_backoff = 5  # seconds
        self.max_backoff = 300  # 5 minutes
        self.backoff_multiplier = 2.0
        
        # Captcha handling
        self.captcha_pause_automation = True  # Pause all automation on CAPTCHA
        self.captcha_max_wait = 300  # 5 minutes for user to solve
        # If True, the recovery manager will block and wait for a user-driven resume
        # This is False by default to preserve non-blocking behavior in tests.
        self.captcha_blocking_wait = False
        # Optional callback invoked when a CAPTCHA is detected and pause is requested.
        # Signature: callback(message: str) -> None
        self.captcha_pause_callback = None
        
        # Rate limit handling
        self.rate_limit_wait = 60  # Initial wait
        self.rate_limit_max_consecutive = 3  # Fail after 3 consecutive
        
        # Session timeout
        self.session_timeout_auto_login = False  # Requires credentials
        
        # Logging callback
        self.log_callback: Optional[Callable[[str, str], None]] = None

    def log(self, message: str, level: str = "info"):
        """Log a message."""
        if self.log_callback:
            try:
                self.log_callback(message, level)
            except Exception:
                pass


class ErrorDetector:
    """Detects common LinkedIn automation errors from page state."""
    
    def __init__(self, driver: WebDriver, config: Optional[ErrorRecoveryConfig] = None):
        self.driver = driver
        self.config = config or ErrorRecoveryConfig()

    def detect_error(self) -> Tuple[ErrorType, Optional[str]]:
        """
        Detect if there's an error on the current page.
        
        Returns:
            (ErrorType, error_message) tuple
        """
        try:
            page_source = self.driver.page_source.lower()
            current_url = self.driver.current_url.lower()
            
            # Check for CAPTCHA (most common on LinkedIn)
            if self._check_captcha(page_source, current_url):
                return ErrorType.CAPTCHA, "CAPTCHA detected on page"
            
            # Check for rate limit
            if self._check_rate_limit(page_source):
                return ErrorType.RATE_LIMIT, "Rate limit or throttling detected"
            
            # Check for session timeout
            if self._check_session_timeout(page_source, current_url):
                return ErrorType.SESSION_TIMEOUT, "Session expired or login required"
            
            # Check for network/connection errors
            if self._check_network_error(page_source):
                return ErrorType.NETWORK_ERROR, "Network error detected"
            
            # Check if form is missing (application may have closed)
            if self._check_form_not_found(page_source):
                return ErrorType.FORM_NOT_FOUND, "Application form not found"
            
            return ErrorType.UNKNOWN_ERROR, None
            
        except Exception as e:
            self.config.log(f"Error during detection: {e}", "error")
            return ErrorType.UNKNOWN_ERROR, str(e)

    def _check_captcha(self, page_source: str, url: str) -> bool:
        """Check for CAPTCHA indicators with visual verification to avoid false positives."""
        # STRICT: Check URL first (most reliable)
        if "checkpoint" in url or "challenge" in url or "/security/" in url:
            return True
        
        # STRICT: Only check for visible CAPTCHA elements in DOM
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Check if actual reCAPTCHA iframe is present and visible
            captcha_selectors = [
                "//iframe[contains(@src, 'recaptcha')]",
                "//div[@class='g-recaptcha']",
                "//div[contains(@class, 'captcha')][@style and not(contains(@style, 'display: none'))]",
            ]
            
            for selector in captcha_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element and element.is_displayed():
                        self.config.log("Visual CAPTCHA element found on page", "warning")
                        return True
                except:
                    continue
        except:
            pass
        
        # STRICT: Very specific text patterns that indicate real CAPTCHA
        critical_indicators = [
            "let's do a quick security check",  # LinkedIn's exact phrase
            "verify you're not a robot",  # Common phrase
            "solve this puzzle",  # CAPTCHA instructions
        ]
        
        return any(indicator in page_source for indicator in critical_indicators)

    def _check_rate_limit(self, page_source: str) -> bool:
        """Check for rate limit or throttling messages."""
        rate_limit_indicators = [
            "too many requests",
            "slow down",
            "try again later",
            "temporarily unavailable",
            "too many attempts",
            "rate limit",
            "please wait",
        ]
        return any(indicator in page_source for indicator in rate_limit_indicators)

    def _check_session_timeout(self, page_source: str, url: str) -> bool:
        """Check for session timeout with visual verification to avoid false positives."""
        # STRICT: Check URL first - only login page indicates actual timeout
        if "linkedin.com/login" in url or "linkedin.com/uas/login" in url:
            return True
        
        # STRICT: Check for actual login form elements
        try:
            from selenium.webdriver.common.by import By
            
            # Check if login form is actually present and visible
            login_selectors = [
                "//input[@id='username']",  # LinkedIn login username field
                "//input[@type='email' and @name='session_key']",  # Login email
                "//form[contains(@class, 'login__form')]",  # Login form
            ]
            
            for selector in login_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element and element.is_displayed():
                        self.config.log("Login form detected - session expired", "warning")
                        return True
                except:
                    continue
        except:
            pass
        
        # STRICT: Very specific text that indicates real login requirement
        critical_session_indicators = [
            "session has expired",  # Exact phrase
            "you must be logged in",  # Exact phrase
            "sign in to continue",  # LinkedIn's phrase
        ]
        
        return any(indicator in page_source for indicator in critical_session_indicators)

    def _check_network_error(self, page_source: str) -> bool:
        """Check for network or connection errors."""
        network_indicators = [
            "connection refused",
            "connection timeout",
            "unable to connect",
            "no internet",
            "network error",
            "502 bad gateway",
            "503 service unavailable",
        ]
        return any(indicator in page_source for indicator in network_indicators)

    def _check_form_not_found(self, page_source: str) -> bool:
        """Check if the application form is missing."""
        # Look for "easy apply" button or form
        if "easy-apply" not in page_source and "apply" not in page_source:
            return True
        return False


class RetryStrategy:
    """Exponential backoff retry strategy."""
    
    def __init__(self, config: ErrorRecoveryConfig):
        self.config = config
        self.retry_count = 0
        self.current_backoff = config.initial_backoff
        self.consecutive_rate_limits = 0

    def should_retry(self, error_type: ErrorType) -> bool:
        """Determine if we should retry based on error type."""
        if error_type == ErrorType.CAPTCHA:
            # Don't auto-retry CAPTCHA; require user intervention
            return False
        
        if error_type == ErrorType.RATE_LIMIT:
            self.consecutive_rate_limits += 1
            if self.consecutive_rate_limits >= self.config.rate_limit_max_consecutive:
                self.config.log(
                    f"Max consecutive rate limits ({self.config.rate_limit_max_consecutive}) reached",
                    "warning"
                )
                return False
            return self.retry_count < self.config.max_retries
        
        if error_type == ErrorType.SESSION_TIMEOUT:
            # Could retry if we have auto-login enabled
            return self.config.session_timeout_auto_login and self.retry_count < self.config.max_retries
        
        if error_type == ErrorType.NETWORK_ERROR:
            return self.retry_count < self.config.max_retries
        
        return False

    def get_backoff_time(self) -> float:
        """Get the current backoff time in seconds."""
        return min(self.current_backoff, self.config.max_backoff)

    def increase_backoff(self):
        """Increase backoff time exponentially."""
        self.retry_count += 1
        self.current_backoff = min(
            self.current_backoff * self.config.backoff_multiplier,
            self.config.max_backoff
        )

    def reset(self):
        """Reset retry counter and backoff for successful operation."""
        self.retry_count = 0
        self.current_backoff = self.config.initial_backoff
        self.consecutive_rate_limits = 0


class ErrorRecoveryManager:
    """Manages error detection and recovery for job applications."""
    
    def __init__(self, driver: WebDriver, wait: WebDriverWait, config: Optional[ErrorRecoveryConfig] = None):
        self.driver = driver
        self.wait = wait
        self.config = config or ErrorRecoveryConfig()
        self.detector = ErrorDetector(driver, config)
        self.retry_strategy = RetryStrategy(config)
        # Event used to coordinate CAPTCHA resume when blocking wait is enabled
        self.captcha_resume_event = threading.Event()
        # Ensure logs directory exists
        try:
            make_directories([logs_folder_path])
        except Exception:
            pass

    def attempt_with_recovery(
        self,
        action: Callable[[], bool],
        action_name: str = "Job Application",
        max_retries: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Attempt an action with error detection and recovery.
        
        Args:
            action: Callable that performs the action and returns success bool
            action_name: Description of the action for logging
            max_retries: Override max retries for this action
        
        Returns:
            (success: bool, error_message: Optional[str])
        """
        self.retry_strategy.reset()
        if max_retries:
            self.retry_strategy.config.max_retries = max_retries
        
        attempt = 0
        while attempt <= self.retry_strategy.config.max_retries:
            try:
                # Attempt the action
                self.config.log(f"Attempting {action_name} (attempt {attempt + 1})...", "info")
                result = action()
                
                if result:
                    self.config.log(f"{action_name} successful", "success")
                    self.retry_strategy.reset()
                    return True, None
                
                # Action failed; check for errors
                error_type, error_msg = self.detector.detect_error()
                
                if error_type == ErrorType.UNKNOWN_ERROR:
                    self.config.log(f"{action_name} failed (unknown error)", "warning")
                    return False, "Unknown error"
                
                self.config.log(f"{action_name} failed: {error_type.value} - {error_msg}", "warning")
                
                # Handle specific error types
                if error_type == ErrorType.CAPTCHA:
                    # Take screenshot for debugging
                    try:
                        import os
                        import time
                        from config.settings import logs_folder_path
                        screenshot_dir = os.path.join(logs_folder_path, "screenshots")
                        os.makedirs(screenshot_dir, exist_ok=True)
                        screenshot_path = os.path.join(screenshot_dir, f"captcha_{int(time.time())}.png")
                        self.driver.save_screenshot(screenshot_path)
                        self.config.log(f"CAPTCHA screenshot saved: {screenshot_path}", "info")
                    except Exception as e:
                        self.config.log(f"Could not save screenshot: {e}", "debug")
                    
                    self.config.log(
                        f"CAPTCHA detected. Pausing automation. Please solve and press resume.",
                        "warning"
                    )
                    # Record pause event
                    try:
                        self._record_captcha_event("paused", error_msg)
                    except Exception:
                        pass
                    # If configured to block, notify via callback and wait for resume event
                    if self.config.captcha_blocking_wait:
                        # Clear previous event state
                        try:
                            self.captcha_resume_event.clear()
                        except Exception:
                            pass

                        # Notify UI or other listeners that captcha requires user action
                        if getattr(self.config, 'captcha_pause_callback', None):
                            try:
                                self.config.captcha_pause_callback(error_msg or "CAPTCHA detected")
                            except Exception:
                                pass

                        # Wait for resume event or timeout
                        waited = self.captcha_resume_event.wait(timeout=self.config.captcha_max_wait)
                        if not waited:
                            self.config.log("CAPTCHA wait timed out", "error")
                            try:
                                self._record_captcha_event("timeout", error_msg)
                            except Exception:
                                pass
                            return False, f"CAPTCHA timeout: {error_msg}"

                        # Resumed by user: retry the action without incrementing attempt count
                        self.config.log("Resuming after CAPTCHA by user action", "info")
                        try:
                            self._record_captcha_event("resumed", error_msg)
                        except Exception:
                            pass
                        continue

                    # Default behavior: do not block, return control to caller
                    return False, f"CAPTCHA detected: {error_msg}"
                
                if error_type == ErrorType.RATE_LIMIT:
                    backoff = self.retry_strategy.get_backoff_time()
                    self.config.log(
                        f"Rate limited. Waiting {backoff:.0f} seconds before retry...",
                        "warning"
                    )
                    time.sleep(backoff)
                    self.retry_strategy.increase_backoff()
                    attempt += 1
                    continue
                
                if error_type == ErrorType.SESSION_TIMEOUT:
                    self.config.log(
                        "Session timeout. Stopping automation.",
                        "error"
                    )
                    return False, "Session timeout"
                
                if error_type == ErrorType.NETWORK_ERROR:
                    backoff = self.retry_strategy.get_backoff_time()
                    self.config.log(
                        f"Network error. Waiting {backoff:.0f} seconds before retry...",
                        "warning"
                    )
                    time.sleep(backoff)
                    self.retry_strategy.increase_backoff()
                    attempt += 1
                    continue
                
                # Other errors: don't retry
                return False, f"{error_type.value}: {error_msg}"
            
            except Exception as e:
                self.config.log(f"Exception during {action_name}: {e}", "error")
                return False, str(e)
        
        return False, f"Max retries ({self.retry_strategy.config.max_retries}) exceeded"

    def check_and_handle_error(self) -> Tuple[bool, Optional[ErrorType], Optional[str]]:
        """
        Check current page for errors and handle if found.
        
        Returns:
            (error_found: bool, error_type: ErrorType, error_message: str)
        """
        error_type, error_msg = self.detector.detect_error()
        
        if error_type == ErrorType.UNKNOWN_ERROR:
            return False, None, None
        
        self.config.log(f"Error detected: {error_type.value} - {error_msg}", "warning")
        
        return True, error_type, error_msg

    def request_resume(self):
        """
        Request the recovery manager to resume from a CAPTCHA wait.
        This sets the internal resume event which will allow a blocked attempt
        to continue.
        """
        try:
            self.captcha_resume_event.set()
            self.config.log("Resume requested (captcha)", "info")
            # record resume request
            try:
                self._record_captcha_event("resume_requested", None)
            except Exception:
                pass
        except Exception:
            pass

    def _record_captcha_event(self, event_type: str, note: Optional[str]):
        """Append a timestamped CAPTCHA event to logs/captcha_events.csv.

        Columns: timestamp, event_type, note, current_url
        """
        try:
            logs_dir = logs_folder_path or "logs/"
            logs_dir = os.path.expanduser(logs_dir)
            # ensure directory exists
            make_directories([logs_dir])
            csv_path = os.path.join(logs_dir, "captcha_events.csv")
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur_url = None
            try:
                cur_url = getattr(self.driver, 'current_url', None)
            except Exception:
                cur_url = None
            row = [ts, event_type, note or "", cur_url or ""]
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # If file was just created, write header
                if f.tell() == 0:
                    writer.writerow(["timestamp", "event", "note", "url"])
                writer.writerow(row)
        except Exception as e:
            # best-effort: log to configured log callback
            try:
                self.config.log(f"Failed to record captcha event: {e}", "error")
            except Exception:
                pass


# Global error recovery manager (set by automation_manager)
current_recovery_manager: Optional[ErrorRecoveryManager] = None


def set_recovery_manager(manager: Optional[ErrorRecoveryManager]):
    """Set the global error recovery manager."""
    global current_recovery_manager
    current_recovery_manager = manager


def request_error_check() -> Tuple[bool, Optional[ErrorType], Optional[str]]:
    """
    Request a check for errors on the current page.
    
    Returns:
        (error_found, error_type, error_message)
    """
    if current_recovery_manager:
        return current_recovery_manager.check_and_handle_error()
    return False, None, None


def request_resume() -> bool:
    """Request global recovery manager to resume after a CAPTCHA.

    Returns True if a manager was signalled, False otherwise.
    """
    if current_recovery_manager:
        try:
            current_recovery_manager.request_resume()
            return True
        except Exception:
            return False
    return False
