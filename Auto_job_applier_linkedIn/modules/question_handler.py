"""
Question handler for mapping application questions to answers and providing
helpers to interact with question widgets.

The module exposes `QuestionHandler` with a simple method `answer_questions` that
accepts a list of question web elements and a mapping of known answers.

Enhanced with AI integration for intelligent question answering.
"""
from typing import Callable, Dict, Any, List, Optional, Tuple
import re

LogCallback = Optional[Callable[[str, str], None]]


class QuestionHandler:
    def __init__(self, driver, log_cb: LogCallback = None, job_context: Optional[Dict[str, str]] = None):
        self.driver = driver
        self.log = log_cb or (lambda level, msg: None)
        self.job_context = job_context or {}  # Store job context for AI
        self.ai_handler = None
        self.use_ai = False
        self.qa_database = None
        
        # Initialize AI if enabled
        try:
            from config.secrets import use_AI
            self.use_ai = use_AI
            if self.use_ai:
                from modules.ai_handler import ai_handler
                self.ai_handler = ai_handler
                self.log('info', '✅ AI Question Answering enabled')
        except Exception as e:
            self.log('warning', f'AI not available: {e}')
            self.use_ai = False
        
        # Initialize Q&A Database
        try:
            from modules.qa_database import QADatabase
            self.qa_database = QADatabase(log_cb=log_cb)
        except Exception as e:
            self.log('warning', f'Q&A Database not available: {e}')

    def _build_ai_context(self) -> str:
        """Build context string for AI from job information."""
        context_parts = []
        
        if self.job_context.get('title'):
            context_parts.append(f"Job Title: {self.job_context['title']}")
        if self.job_context.get('company'):
            context_parts.append(f"Company: {self.job_context['company']}")
        if self.job_context.get('location'):
            context_parts.append(f"Location: {self.job_context['location']}")
        if self.job_context.get('description'):
            # Limit description to 500 chars
            desc = self.job_context['description'][:500]
            context_parts.append(f"Job Description: {desc}")
        
        return "\n".join(context_parts) if context_parts else None
    
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

            # If no match or low score, try AI/Database
            answer = None
            score = 0.0
            answer_source = 'static'  # Track where answer came from
            
            if matched is None:
                self.log('warning', f'No match for question: {qtext}')
            else:
                answer, score = matched

            # If match missing or below confidence, try AI/Database
            if (matched is None) or (score < min_score):
                ai_answer = None
                
                # Step 1: Check Q&A Database first (fastest)
                if self.qa_database:
                    try:
                        db_result = self.qa_database.find_similar_question(text, threshold=0.8)
                        if db_result:
                            ai_answer = db_result['answer']
                            answer_source = 'database'
                            self.log('info', f'📚 Using answer from Q&A database (ID: {db_result["id"]})')
                            # Update usage stats
                            self.qa_database.update_usage(db_result['id'])
                    except Exception as e:
                        self.log('warning', f'Q&A Database lookup failed: {e}')
                
                # Step 2: If not in database, try AI
                if not ai_answer and self.use_ai and self.ai_handler:
                    try:
                        # Build context for AI
                        context = self._build_ai_context()
                        ai_answer = self.ai_handler.answer_question(text, context)
                        
                        if ai_answer:
                            answer_source = 'ai'
                            self.log('info', f'🤖 AI generated answer for: {text[:50]}...')
                            
                            # Store in database for future use
                            if self.qa_database:
                                try:
                                    self.qa_database.store_question(
                                        question=text,
                                        answer=ai_answer,
                                        job_title=self.job_context.get('title', ''),
                                        company=self.job_context.get('company', ''),
                                        job_context=context
                                    )
                                except Exception as e:
                                    self.log('warning', f'Failed to store Q&A: {e}')
                    except Exception as e:
                        self.log('error', f'AI answer generation failed: {e}')
                
                # Use AI answer if we got one
                if ai_answer:
                    answer = ai_answer
                    score = 0.9  # High score for AI answers
                else:
                    # No AI answer available
                    if matched is None:
                        return {'status': 'skipped', 'reason': 'no_answer', 'score': 0.0, 'source': 'none'}
                    if score < min_score:
                        self.log('warning', f'Low confidence match for question (score={score:.2f}): {qtext}')
                        return {'status': 'skipped', 'reason': 'low_confidence', 'score': score, 'source': 'static'}

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

            return {'status': 'answered', 'value': answer, 'score': score, 'source': answer_source}
        except Exception as e:
            self.log('error', f'Exception while answering question: {e}')
            return {'status': 'failed', 'reason': str(e), 'score': 0.0}

    def answer_questions(self, questions: List[Any], answers_map: Dict[str, Any], min_score: float = 0.45) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for q in questions:
            results.append(self.answer_question_element(q, answers_map, min_score=min_score))
        return results
