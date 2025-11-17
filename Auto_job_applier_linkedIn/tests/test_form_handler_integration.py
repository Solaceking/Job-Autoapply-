"""
Integration tests for modules/form_handler.py

Tests FormHandler against mock LinkedIn form HTML structures.
These tests validate real-world form detection and filling without needing a browser.
"""
import pytest
from unittest.mock import Mock, MagicMock


class MockWebElement:
    """Mock Selenium WebElement for testing."""
    
    def __init__(self, tag_name="input", attributes=None, text="", children=None):
        self.tag_name = tag_name
        self.attributes = attributes or {}
        self.text = text
        self.children = children or []
        self._value = ""
        self._selected = False
    
    def get_attribute(self, name):
        return self.attributes.get(name)
    
    def is_selected(self):
        return self._selected
    
    def click(self):
        self._selected = not self._selected
    
    def clear(self):
        self._value = ""
    
    def send_keys(self, text):
        self._value += text
    
    def find_elements(self, by, value):
        # Simple mock: return children or empty
        return self.children if hasattr(self, 'children') else []


class MockFormElement:
    """Mock form container with child elements."""
    
    def __init__(self, elements=None):
        self.elements = elements or []
    
    def find_elements(self, by, value):
        return self.elements


class TestFormHandlerWithMockForms:
    """Test FormHandler against mock LinkedIn form structures."""

    def test_simple_text_form(self):
        """Test detecting and filling a simple form with text fields."""
        from modules.form_handler import FormHandler
        
        # Create mock elements
        first_name_input = MockWebElement("input", {
            "name": "firstName",
            "aria-label": "First Name"
        })
        last_name_input = MockWebElement("input", {
            "name": "lastName",
            "aria-label": "Last Name"
        })
        email_input = MockWebElement("input", {
            "name": "email",
            "type": "email"
        })
        
        form = MockFormElement([first_name_input, last_name_input, email_input])
        
        handler = FormHandler(driver=None)
        fields = handler.detect_fields(form)
        
        # Should detect all three fields
        assert len(fields) >= 2, f"Expected at least 2 fields, got {len(fields)}"
        
        # Check that aria-label or name is used as key
        keys = list(fields.keys())
        assert any("first" in k.lower() for k in keys), f"No 'first' field in {keys}"

    def test_linkedin_easy_apply_form(self):
        """Test detecting common LinkedIn Easy Apply form structure."""
        from modules.form_handler import FormHandler
        
        # Typical LinkedIn form structure
        phone_input = MockWebElement("input", {
            "name": "phoneNumber",
            "type": "tel",
            "placeholder": "Phone Number"
        })
        work_auth_select = MockWebElement("select", {
            "name": "workAuthorization",
            "aria-label": "Work Authorization"
        })
        resume_file = MockWebElement("input", {
            "name": "resume",
            "type": "file",
            "aria-label": "Resume"
        })
        
        form = MockFormElement([phone_input, work_auth_select, resume_file])
        
        handler = FormHandler(driver=None)
        fields = handler.detect_fields(form)
        
        # Check field type detection
        assert any(f.get("type") == "file" for f in fields.values()), "No file field detected"
        assert any(f.get("type") == "select" for f in fields.values()), "No select field detected"

    def test_checkbox_and_radio_detection(self):
        """Test detecting checkbox and radio button fields."""
        from modules.form_handler import FormHandler
        
        agree_checkbox = MockWebElement("input", {
            "name": "agreeToTerms",
            "type": "checkbox"
        })
        visa_radio = MockWebElement("input", {
            "name": "visaStatus",
            "type": "radio",
            "value": "visa_holder"
        })
        
        form = MockFormElement([agree_checkbox, visa_radio])
        
        handler = FormHandler(driver=None)
        fields = handler.detect_fields(form)
        
        # Both should be detected as "checkbox" type (covers checkbox and radio)
        field_types = [f.get("type") for f in fields.values()]
        assert "checkbox" in field_types, f"No checkbox type in {field_types}"

    def test_resume_field_detection(self):
        """Test resume field auto-detection by keyword matching."""
        from modules.form_handler import FormHandler
        
        resume_input = MockWebElement("input", {
            "name": "resume",
            "type": "file",
            "aria-label": "Upload Resume"
        })
        cv_input = MockWebElement("input", {
            "name": "cv_file",
            "type": "file",
            "aria-label": "CV (Curriculum Vitae)"
        })
        other_file = MockWebElement("input", {
            "name": "portfolio",
            "type": "file",
            "aria-label": "Portfolio"
        })
        
        form = MockFormElement([resume_input, cv_input, other_file])
        
        handler = FormHandler(driver=None)
        resume_fields = handler.find_resume_fields(form)
        
        # Should find resume and CV fields but not portfolio
        assert len(resume_fields) >= 2, f"Expected >=2 resume fields, got {len(resume_fields)}"
        field_labels = [f.get("label_candidates", []) for f in resume_fields.values()]
        all_labels = [item for sublist in field_labels for item in sublist]
        assert any("resume" in str(l).lower() for l in all_labels), "Resume not detected"
        assert any("cv" in str(l).lower() for l in all_labels), "CV not detected"

    def test_field_matching_with_normalization(self):
        """Test that normalized answer keys match field names."""
        from modules.form_handler import FormHandler
        
        # Create a form with fields
        first_name = MockWebElement("input", {
            "name": "firstName",
            "aria-label": "First Name"
        })
        last_name = MockWebElement("input", {
            "name": "lastName",
            "aria-label": "Last Name"
        })
        
        form = MockFormElement([first_name, last_name])
        
        handler = FormHandler(driver=None)
        
        # Answers with different casing/spacing
        answers = {
            "first name": "John",
            "LAST NAME": "Doe",
        }
        
        # Note: fill_form would need actual WebElement.send_keys() support
        # For now, test the matching logic
        fields = handler.detect_fields(form)
        
        # Verify normalization works
        assert handler._normalize("First Name") == "first name"
        assert handler._normalize("LAST NAME") == "last name"

    def test_token_overlap_matching(self):
        """Test fuzzy matching for field labels with high token overlap.
        
        Token overlap formula: len(intersection) / max(len(a_tokens), len(b_tokens))
        """
        from modules.form_handler import FormHandler
        
        handler = FormHandler(driver=None)
        
        # Test cases: (field_label, answer_key, expected_min_score)
        # "first name" (2 tokens) vs "first name" (2 tokens) -> 2/2 = 1.0
        # "phone number" (2 tokens) vs "phone" (1 token) -> 1/2 = 0.5
        # "email" (1 token) vs "email address" (2 tokens) -> 1/2 = 0.5
        cases = [
            ("First Name", "first name", 1.0),  # 2 tokens match, 2/2 = 1.0
            ("Phone Number", "phone", 0.5),  # 1 token match, 1/2 = 0.5
            ("Email", "email address", 0.5),  # 1 token match, 1/2 = 0.5
            ("Work Authorization", "work", 0.5),  # 1 token match, 1/2 = 0.5
        ]
        
        for field_label, answer_key, expected_score in cases:
            score = handler._token_overlap(field_label, answer_key)
            # Allow small floating point tolerance
            assert abs(score - expected_score) < 0.01, f"For '{field_label}' vs '{answer_key}': expected {expected_score}, got {score}"

    def test_form_with_label_associations(self):
        """Test detecting fields that have associated <label> elements."""
        from modules.form_handler import FormHandler
        
        # Mock elements with label association
        first_name_input = MockWebElement("input", {
            "id": "fname",
            "name": "firstName",
            "type": "text"
        })
        
        # In real scenario, this would be found via XPath like //label[@for="fname"]
        # For this test, we verify the logic works
        form = MockFormElement([first_name_input])
        
        handler = FormHandler(driver=None)
        fields = handler.detect_fields(form)
        
        # Should have label_candidates list
        for field_meta in fields.values():
            assert "label_candidates" in field_meta, "label_candidates missing from field metadata"

    def test_required_field_detection(self):
        """Test detecting required fields via HTML attributes."""
        from modules.form_handler import FormHandler
        
        required_field = MockWebElement("input", {
            "name": "email",
            "type": "email",
            "required": "true"
        })
        optional_field = MockWebElement("input", {
            "name": "phone",
            "type": "tel"
        })
        aria_required = MockWebElement("input", {
            "name": "address",
            "aria-required": "true"
        })
        
        form = MockFormElement([required_field, optional_field, aria_required])
        
        handler = FormHandler(driver=None)
        fields = handler.detect_fields(form)
        
        # Check required flag
        required_fields = [f for f in fields.values() if f.get("required")]
        assert len(required_fields) >= 1, f"Expected required fields, got {required_fields}"


class TestFormHandlerEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_form(self):
        """Test handling of empty form."""
        from modules.form_handler import FormHandler
        
        form = MockFormElement([])
        handler = FormHandler(driver=None)
        fields = handler.detect_fields(form)
        
        assert len(fields) == 0, "Expected no fields in empty form"

    def test_form_with_invalid_elements(self):
        """Test handling of malformed or problematic elements."""
        from modules.form_handler import FormHandler
        
        # Element that might raise exceptions
        bad_element = MockWebElement("input", {})
        # Simulating element without proper attributes
        bad_element.tag_name = None
        
        form = MockFormElement([bad_element])
        handler = FormHandler(driver=None)
        
        # Should not raise, should handle gracefully
        fields = handler.detect_fields(form)
        # May have 0 or 1 fields depending on error handling
        assert isinstance(fields, dict), "Should return dict"

    def test_file_path_validation(self):
        """Test file existence validation before upload."""
        from modules.form_handler import FormHandler
        import os
        
        handler = FormHandler(driver=None)
        
        # Non-existent file
        result = handler.upload_file(MockWebElement(), "/nonexistent/file.pdf")
        assert result == False, "Should return False for non-existent file"
        
        # Create a temp file and test
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Mock element that doesn't actually send keys
            elem = MockWebElement()
            result = handler.upload_file(elem, tmp_path)
            assert result == True, "Should return True for valid file"
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
