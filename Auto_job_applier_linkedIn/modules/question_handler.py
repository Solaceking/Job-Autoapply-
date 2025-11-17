"""
Question handler for mapping application questions to answers and providing
helpers to interact with question widgets.

The module exposes `QuestionHandler` with a simple method `answer_questions` that
accepts a list of question web elements and a mapping of known answers.
"""
from typing import Callable, Dict, Any, List, Optional, Tuple
import re

LogCallback = Optional[Callable[[str, str], None]]


class QuestionHandler:
    def __init__(self, driver, log_cb: LogCallback = None):
        self.driver = driver
        self.log = log_cb or (lambda level, msg: None)

    def normalize_question_text(self, text: str) -> str:
        """Normalize question text to a compact fingerprint used for matching answers."""
        if not text:
            return ""
        return re.sub(r"\s+", " ", text.strip().lower())

    def _score_match(self, q: str, key: str) -> float:
        """Return a simple score (0..1) for how well key matches q (higher = better)."""
        if not q or not key:
            return 0.0
        qn = set(q.split())
        kn = set(self.normalize_question_text(key).split())
        if not qn or not kn:
            return 0.0
        inter = qn.intersection(kn)
        return len(inter) / max(len(qn), len(kn))

    def match_answer(self, question_text: str, answers_map: Dict[str, Any]) -> Optional[Tuple[Any, float]]:
        """Return the best matching answer and score for the given question_text.

        Scores allow caller to decide a threshold for automatic answering.
        """
        q = self.normalize_question_text(question_text)
        # direct exact normalized key
        for key, val in answers_map.items():
            if self.normalize_question_text(key) == q:
                return val, 1.0

        # score all keys
        best_key = None
        best_score = 0.0
        for key, val in answers_map.items():
            score = self._score_match(q, key)
            if score > best_score:
                best_score = score
                best_key = key

        if best_key is None:
            return None
        return answers_map[best_key], best_score

    def answer_question_element(self, question_element, answers_map: Dict[str, Any], min_score: float = 0.45) -> Dict[str, Any]:
        """Inspect a question element and attempt to answer it.

        Returns metadata: {'status': 'answered'|'skipped'|'failed', 'value': ..., 'score': float}
        """
        try:
            # heuristics: extract visible text
            text = (question_element.text or question_element.get_attribute('innerText') or '').strip()
            qtext = self.normalize_question_text(text)
            matched = self.match_answer(qtext, answers_map)

            # If no match or low score, optionally consult LLM fallback (if enabled)
            answer = None
            score = 0.0
            if matched is None:
                self.log('warning', f'No match for question: {qtext}')
            else:
                answer, score = matched

            # If match missing or below confidence, try LLM fallback if available
            if (matched is None) or (score < min_score):
                try:
                    from modules.llm_fallback import get_llm
                    llm = get_llm()
                    if llm and llm.is_enabled():
                        # pass the visible text as context
                        ctx = (question_element.text or '') if question_element is not None else None
                        llm_answer = llm.call_llm(qtext, context=ctx)
                        if llm_answer:
                            self.log('info', f'LLM provided fallback answer for question: {qtext}')
                            answer = llm_answer
                            # mark score as 0 to indicate machine-sourced
                            score = 0.0
                            # proceed to fill using LLM answer
                        else:
                            # no LLM answer available; if original match was low confidence, skip
                            if matched is None:
                                return {'status': 'skipped', 'reason': 'no_answer', 'score': 0.0}
                            if score < min_score:
                                self.log('warning', f'Low confidence match for question (score={score:.2f}): {qtext}')
                                return {'status': 'skipped', 'reason': 'low_confidence', 'score': score}
                except Exception:
                    # If anything fails when calling LLM, fallback to prior behavior
                    if matched is None:
                        return {'status': 'skipped', 'reason': 'no_answer', 'score': 0.0}
                    if score < min_score:
                        self.log('warning', f'Low confidence match for question (score={score:.2f}): {qtext}')
                        return {'status': 'skipped', 'reason': 'low_confidence', 'score': score}

            # find input inside question_element
            input_el = None
            try:
                input_el = question_element.find_element('xpath', ".//input|.//select|.//textarea")
            except Exception:
                pass

            if input_el is None:
                self.log('error', f'Could not find input for question: {qtext}')
                return {'status': 'failed', 'reason': 'no_input', 'score': score}

            tag = (input_el.tag_name or '').lower()
            t = (input_el.get_attribute('type') or '').lower()

            # Fill according to type
            if tag == 'select':
                from selenium.webdriver.support.ui import Select

                try:
                    Select(input_el).select_by_visible_text(str(answer))
                except Exception:
                    # try selecting by value
                    try:
                        Select(input_el).select_by_value(str(answer))
                    except Exception as e:
                        self.log('error', f'Failed to select for question: {e}')
                        return {'status': 'failed', 'reason': 'select_failed', 'score': score}
            elif t in ('checkbox', 'radio'):
                try:
                    desired = bool(answer)
                    if input_el.is_selected() != desired:
                        input_el.click()
                except Exception as e:
                    self.log('error', f'Checkbox/radio click failed: {e}')
                    return {'status': 'failed', 'reason': 'click_failed', 'score': score}
            else:
                try:
                    input_el.clear()
                    input_el.send_keys(str(answer))
                except Exception as e:
                    self.log('error', f'Failed to type answer: {e}')
                    return {'status': 'failed', 'reason': 'typing_failed', 'score': score}

            return {'status': 'answered', 'value': answer, 'score': score}
        except Exception as e:
            self.log('error', f'Exception while answering question: {e}')
            return {'status': 'failed', 'reason': str(e), 'score': 0.0}

    def answer_questions(self, questions: List[Any], answers_map: Dict[str, Any], min_score: float = 0.45) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for q in questions:
            results.append(self.answer_question_element(q, answers_map, min_score=min_score))
        return results
