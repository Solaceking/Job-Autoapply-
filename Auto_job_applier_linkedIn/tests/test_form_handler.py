"""
Unit smoke tests for modules/form_handler.py

Tests focus on pure functions (normalization, matching) that don't require a browser.
"""
import pytest


class TestFormHandlerHelpers:
    """Test FormHandler helper functions without Selenium."""

    def test_normalize_simple(self):
        """Test basic normalization: lowercase, strip, collapse whitespace."""
        from modules.form_handler import FormHandler

        handler = FormHandler(driver=None)
        assert handler._normalize("First Name") == "first name"
        assert handler._normalize("  MULTIPLE   SPACES  ") == "multiple spaces"
        assert handler._normalize("") == ""
        assert handler._normalize("   ") == ""

    def test_normalize_special_chars(self):
        """Test normalization preserves special chars."""
        from modules.form_handler import FormHandler

        handler = FormHandler(driver=None)
        assert handler._normalize("Email (Required)") == "email (required)"
        assert handler._normalize("Phone-Number") == "phone-number"

    def test_token_overlap_exact(self):
        """Test token overlap with exact matches."""
        from modules.form_handler import FormHandler

        handler = FormHandler(driver=None)
        assert handler._token_overlap("first name", "first name") == 1.0
        assert handler._token_overlap("hello", "hello") == 1.0

    def test_token_overlap_partial(self):
        """Test token overlap with partial matches."""
        from modules.form_handler import FormHandler

        handler = FormHandler(driver=None)
        # "first name" and "first" -> 1 token match out of max(2,1)=2 -> 0.5
        result = handler._token_overlap("first name", "first")
        assert result == 0.5, f"Expected 0.5, got {result}"

        # "first name" and "name" -> 1 token match out of max(2,1)=2 -> 0.5
        result = handler._token_overlap("first name", "name")
        assert result == 0.5, f"Expected 0.5, got {result}"

    def test_token_overlap_none(self):
        """Test token overlap with no matches."""
        from modules.form_handler import FormHandler

        handler = FormHandler(driver=None)
        assert handler._token_overlap("hello", "world") == 0.0
        assert handler._token_overlap("", "world") == 0.0
        assert handler._token_overlap("hello", "") == 0.0

    def test_token_overlap_case_insensitive(self):
        """Test token overlap is case-insensitive."""
        from modules.form_handler import FormHandler

        handler = FormHandler(driver=None)
        assert handler._token_overlap("FIRST NAME", "first name") == 1.0
        assert handler._token_overlap("First Name", "FIRST") == 0.5

    def test_token_overlap_whitespace_collapsed(self):
        """Test token overlap handles extra whitespace."""
        from modules.form_handler import FormHandler

        handler = FormHandler(driver=None)
        assert handler._token_overlap("first   name", "first name") == 1.0


class TestQuestionHandlerHelpers:
    """Test QuestionHandler helper functions without Selenium."""

    def test_normalize_simple(self):
        """Test question normalization."""
        from modules.question_handler import QuestionHandler

        handler = QuestionHandler(driver=None)
        assert handler.normalize_question_text("Are you available?") == "are you available?"
        assert handler.normalize_question_text("  MULTIPLE   SPACES  ") == "multiple spaces"
        assert handler.normalize_question_text("") == ""

    def test_score_match_exact(self):
        """Test score match with exact matches."""
        from modules.question_handler import QuestionHandler

        handler = QuestionHandler(driver=None)
        assert handler._score_match("are you available", "are you available") == 1.0
        assert handler._score_match("hello", "hello") == 1.0

    def test_score_match_partial(self):
        """Test score match with partial overlaps."""
        from modules.question_handler import QuestionHandler

        handler = QuestionHandler(driver=None)
        # "are you available" vs "are you" -> 2/3 = 0.667
        result = handler._score_match("are you available", "are you")
        assert 0.6 < result < 0.7, f"Expected ~0.667, got {result}"

    def test_score_match_none(self):
        """Test score match with no overlap."""
        from modules.question_handler import QuestionHandler

        handler = QuestionHandler(driver=None)
        assert handler._score_match("hello world", "goodbye moon") == 0.0
        assert handler._score_match("", "something") == 0.0

    def test_match_answer_exact(self):
        """Test answer matching with exact normalized key."""
        from modules.question_handler import QuestionHandler

        handler = QuestionHandler(driver=None)
        answers = {
            "are you available": "Yes",
            "experience level": "Senior",
        }
        result = handler.match_answer("Are You Available?", answers)
        assert result is not None
        assert result[0] == "Yes"
        # Score is high due to 2 out of 3 tokens matching ("are", "you", "available")
        assert result[1] > 0.6

    def test_match_answer_partial(self):
        """Test answer matching with partial overlap."""
        from modules.question_handler import QuestionHandler

        handler = QuestionHandler(driver=None)
        answers = {
            "are you available": "Yes",
        }
        result = handler.match_answer("are you available to start immediately", answers)
        assert result is not None
        assert result[0] == "Yes"
        assert result[1] >= 0.5  # high confidence partial (3 out of 5 tokens)

    def test_match_answer_no_match(self):
        """Test answer matching with no close match."""
        from modules.question_handler import QuestionHandler

        handler = QuestionHandler(driver=None)
        answers = {
            "are you available": "Yes",
        }
        result = handler.match_answer("completely unrelated question", answers)
        assert result is None

    def test_match_answer_multiple_keys(self):
        """Test answer matching selects best key."""
        from modules.question_handler import QuestionHandler

        handler = QuestionHandler(driver=None)
        answers = {
            "experience": "10 years",
            "years of experience": "10 years",
        }
        # should match "years of experience" better
        result = handler.match_answer("how many years of experience", answers)
        assert result is not None
        assert result[0] == "10 years"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
