"""
Form handler helpers for detecting and filling application forms.
This module provides a thin, testable API used by the automation manager.

Contract (small):
- Inputs: Selenium WebElement (form container) or webdriver instance
- Outputs: dict of detected fields and fill outcome
- Errors: Raise informative exceptions on unexpected states; otherwise return best-effort results

This file intentionally provides conservative, best-effort implementations and
leaves project-specific heuristics to Phase 3 tuning.
"""
from typing import Dict, Any, Callable, List, Optional, Tuple
import os
import re

# Type alias for the GUI logging callback: log(level: str, message: str)
LogCallback = Optional[Callable[[str, str], None]]


class FormHandler:
    """Helper class to detect and fill common form field types.

    Methods are intentionally small and side-effect-free where possible so they
    are easy to test. They accept a logging callback to keep GUI decoupled.
    """

    def __init__(self, driver, log_cb: LogCallback = None, progress_cb: Optional[Callable[[int], None]] = None):
        self.driver = driver
        self.log = log_cb or (lambda level, msg: None)
        # progress_cb receives an integer percent (0-100) after each field is processed
        self.progress_cb = progress_cb or (lambda percent: None)

    def detect_fields(self, form_element) -> Dict[str, Dict[str, Any]]:
        """Return a mapping of field_name -> metadata for inputs inside form_element.

        Metadata keys include: 'type' (text/select/checkbox/file), 'element' (WebElement),
        'required' (bool), 'label' (str)
        """
        fields: Dict[str, Dict[str, Any]] = {}
        # find inputs/selects/textarea using modern Selenium API; tolerate older/later versions
        try:
            inputs = form_element.find_elements("xpath", ".//input|.//select|.//textarea")
        except Exception:
            # fall back to a safer search by tag name
            inputs = []
            for tag in ("input", "select", "textarea"):
                try:
                    inputs.extend(form_element.find_elements("tag name", tag))
                except Exception:
                    continue

        for idx, inp in enumerate(inputs):
            try:
                tag = (inp.tag_name or "").lower()
                t = (inp.get_attribute("type") or "").lower()

                # Derive a friendly key for matching: prefer aria-label/name/id/placeholder/label text
                name_attr = (inp.get_attribute("name") or "").strip()
                id_attr = (inp.get_attribute("id") or "").strip()
                placeholder = (inp.get_attribute("placeholder") or "").strip()
                aria = (inp.get_attribute("aria-label") or "").strip()

                label_text = None
                # try to find a <label for="id"> if id present
                if id_attr:
                    try:
                        lbl = form_element.find_elements("xpath", f".//label[@for=\"{id_attr}\"]")
                        if lbl:
                            label_text = lbl[0].text.strip()
                    except Exception:
                        label_text = None

                # Compose keys (prioritized)
                candidates: List[str] = []
                if aria:
                    candidates.append(aria)
                if name_attr:
                    candidates.append(name_attr)
                if id_attr:
                    candidates.append(id_attr)
                if placeholder:
                    candidates.append(placeholder)
                if label_text:
                    candidates.append(label_text)
                if not candidates:
                    candidates.append(f"field_{idx}")

                # choose canonical key
                key = candidates[0]
                required = (inp.get_attribute("required") is not None) or (inp.get_attribute("aria-required") == "true")

                if tag == "select":
                    ftype = "select"
                elif t in ("checkbox", "radio"):
                    ftype = "checkbox"
                elif t in ("file",):
                    ftype = "file"
                else:
                    ftype = "text"

                fields[key] = {"type": ftype, "element": inp, "required": required, "label_candidates": candidates}
            except Exception:
                # best-effort: skip problematic element
                continue

        self.log("debug", f"Detected {len(fields)} form fields: {list(fields.keys())}")
        return fields

    def fill_text(self, element, value: str) -> bool:
        """Fill a single text-like input element with value."""
        try:
            element.clear()
            element.send_keys(value)
            return True
        except Exception as e:
            self.log("error", f"Failed to fill text field: {e}")
            return False

    def select_option(self, select_element, visible_text: str) -> bool:
        """Select an option by visible text from a <select> element."""
        try:
            from selenium.webdriver.support.ui import Select

            sel = Select(select_element)
            sel.select_by_visible_text(visible_text)
            return True
        except Exception as e:
            self.log("error", f"Failed to select option '{visible_text}': {e}")
            return False

    def click_checkbox(self, element, value: bool = True) -> bool:
        """Set checkbox/radio to value (True=checked)."""
        try:
            is_selected = element.is_selected()
            if is_selected != value:
                element.click()
            return True
        except Exception as e:
            self.log("error", f"Failed to toggle checkbox: {e}")
            return False

    def upload_file(self, element, file_path: str) -> bool:
        """Upload file by sending path to file input element."""
        try:
            if not os.path.exists(file_path):
                self.log("error", f"File not found: {file_path}")
                return False
            element.send_keys(file_path)
            return True
        except Exception as e:
            self.log("error", f"Failed to upload file '{file_path}': {e}")
            return False

    def fill_form(self, form_element, answers: Dict[str, Any]) -> Dict[str, Any]:
        """High-level helper that detects fields and fills them using answers mapping.

        answers: mapping from label or name -> value
        Returns a dict with per-field success status.
        """
        result: Dict[str, Any] = {}
        fields = self.detect_fields(form_element)

        # Helper to find best answer for a field based on candidates
        def find_answer_for_field(candidates: List[str]) -> Tuple[Optional[Any], Optional[str]]:
            # exact key match first
            for key in candidates:
                if key in answers:
                    return answers[key], key
            # try normalized matching (case-insensitive, whitespace)
            norm_map = {self._normalize(k): v for k, v in answers.items()}
            for key in candidates:
                nk = self._normalize(key)
                if nk in norm_map:
                    return norm_map[nk], key
            # try substring/token overlap
            for key in candidates:
                for akey in answers:
                    if self._token_overlap(key, akey) >= 0.6:
                        return answers[akey], akey
            return None, None

        total = len(fields) or 1
        for idx, (key, meta) in enumerate(fields.items()):
            ftype = meta.get("type")
            elem = meta.get("element")
            candidates = meta.get("label_candidates", [key])

            answer, matched_key = find_answer_for_field(candidates)
            if answer is None:
                result[key] = {"status": "skipped", "reason": "no_answer"}
                continue

            ok = False
            if ftype == "text":
                ok = self.fill_text(elem, str(answer))
            elif ftype == "select":
                ok = self.select_option(elem, str(answer))
            elif ftype == "checkbox":
                ok = self.click_checkbox(elem, bool(answer))
            elif ftype == "file":
                ok = self.upload_file(elem, str(answer))

            status = "ok" if ok else "failed"
            result[key] = {"status": status, "matched_key": matched_key, "type": ftype}

            # Emit per-field progress (rounded integer percent)
            try:
                percent = int(((idx + 1) / total) * 100)
                self.progress_cb(percent)
            except Exception:
                pass

        return result

    def _normalize(self, s: str) -> str:
        return re.sub(r"\s+", " ", (s or "").strip().lower())

    def _token_overlap(self, a: str, b: str) -> float:
        """Return simple token overlap ratio between two strings (0..1)."""
        ta = set(self._normalize(a).split())
        tb = set(self._normalize(b).split())
        if not ta or not tb:
            return 0.0
        inter = ta.intersection(tb)
        return len(inter) / max(len(ta), len(tb))

    def find_resume_fields(self, form_element) -> Dict[str, Any]:
        """Detect file input fields that likely expect resume uploads.
        
        Looks for common patterns in field names/labels like:
        - resume, cv, curriculum vitae, document
        
        Returns: dict mapping field_key -> field_metadata
        """
        resume_keywords = ["resume", "cv", "curriculum", "vitae", "document", "file"]
        fields = self.detect_fields(form_element)
        resume_fields = {}

        for key, meta in fields.items():
            if meta.get("type") != "file":
                continue
            # check if key contains resume-like keywords
            normalized_key = self._normalize(key)
            for keyword in resume_keywords:
                if keyword in normalized_key:
                    resume_fields[key] = meta
                    break

        return resume_fields

