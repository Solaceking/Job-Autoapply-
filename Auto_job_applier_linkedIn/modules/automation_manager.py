'''
Auto Job Applier - Integration Layer
Bridges GUI with LinkedIn Automation Logic

This module connects the GUI to the core automation features from runAiBot.py
Handles job searching, form filling, and application submission.
'''

import csv
import os
import re
import time
from datetime import datetime
from typing import Callable, Optional, Tuple, List, Dict, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from modules.helpers import print_lg, truncate_for_csv, make_directories
from modules.clickers_and_finders import try_xp, try_linkText, wait_span_click, text_input_by_ID
from config.settings import file_name, failed_file_name
from modules.form_handler import FormHandler
from modules.question_handler import QuestionHandler

from modules.settings_manager import load_personals_settings, load_resume_settings
from modules.error_recovery import ErrorRecoveryManager, ErrorRecoveryConfig, set_recovery_manager

# Global reference to currently active JobApplicationManager (for cooperative cancellation)
current_manager = None

def request_cancel_current():
    """Request cancellation of the currently running manager, if any.

    Returns True if a manager was signalled, False otherwise.
    """
    global current_manager
    try:
        if current_manager:
            try:
                current_manager.request_cancel()
            except Exception:
                pass
            # also try to close browser (best-effort)
            try:
                from modules.open_chrome import close_browser
                close_browser()
            except Exception:
                pass
            return True
    except Exception:
        pass
    return False


class JobApplicationManager:
    """
    Manages LinkedIn job applications through Selenium automation.
    Provides high-level interface for GUI integration.
    """
    
    def __init__(self, driver: WebDriver, wait: WebDriverWait, actions: ActionChains, log_callback: Callable = None):
        """
        Initialize the job application manager.
        
        Args:
            driver: Selenium WebDriver instance
            wait: WebDriverWait instance
            actions: ActionChains instance
            log_callback: Optional callback function for logging (receives message and level)
        """
        self.driver = driver
        self.wait = wait
        self.actions = actions
        self.log_callback = log_callback or self._default_log
        self.progress_callback = None  # Optional: (applied, failed, skipped, current_job_title) -> None
        
        # Statistics
        self.applied_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        # Cancellation flag for cooperative shutdown
        self.cancel_requested = False

        # Helpers
        # Callback for per-form progress (percent 0-100). GUI can set this to receive updates.
        self.form_progress_callback: Optional[Callable[[int], None]] = None

        # internal emitter passed to FormHandler which forwards to form_progress_callback
        def _emit_form_progress(p: int):
            try:
                if self.form_progress_callback:
                    self.form_progress_callback(p)
            except Exception:
                pass

        self.form_handler = FormHandler(self.driver, log_cb=self.log_callback, progress_cb=_emit_form_progress)
        self.question_handler = QuestionHandler(self.driver, log_cb=self.log_callback)

        # CSV setup
        make_directories([file_name, failed_file_name])
        self._setup_csv_files()

        # Error recovery manager setup
        self.error_recovery_config = ErrorRecoveryConfig()
        self.error_recovery_config.log_callback = self.log_callback
        self.recovery_manager = ErrorRecoveryManager(self.driver, self.wait, self.error_recovery_config)
        set_recovery_manager(self.recovery_manager)
    
    def _default_log(self, message: str, level: str = "info"):
        """Default logging if no callback provided."""
        print_lg(message)
    
    def log(self, message: str, level: str = "info"):
        """Log a message through callback."""
        self.log_callback(message, level)
    
    def _setup_csv_files(self):
        """Setup CSV files for tracking applications."""
        try:
            if not os.path.exists(file_name):
                with open(file_name, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'Timestamp', 'Job Title', 'Company', 'Location',
                        'Status', 'Job URL', 
                        'AI Match Score', 'Match Strengths', 'Match Gaps',
                        'Questions Count', 'AI Answered', 'Static Answered',
                        'Application Time (s)', 'Error Details'
                    ])
                self.log(f"Created applications history file: {file_name}", "success")
            
            if not os.path.exists(failed_file_name):
                with open(failed_file_name, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'Timestamp', 'Job Title', 'Company', 'Location',
                        'Error Reason', 'Job URL', 
                        'AI Match Score', 'Skip Reason', 'Full Error'
                    ])
                self.log(f"Created failed applications file: {failed_file_name}", "success")
        
        except Exception as e:
            self.log(f"Error setting up CSV files: {str(e)}", "error")
    
    def log_application(self, job_title: str, company: str, location: str, 
                       status: str, job_url: str = "", error: str = "", 
                       match_score: int = 0, match_strengths: str = "", match_gaps: str = "",
                       questions_count: int = 0, ai_answered: int = 0, static_answered: int = 0,
                       application_time: float = 0.0):
        """
        Log an application to CSV file with AI metrics.
        
        Args:
            job_title: Title of the job
            company: Company name
            location: Job location
            status: Status (Applied, Failed, Skipped)
            job_url: URL of the job posting
            error: Error message if any
            match_score: AI match score (0-100)
            match_strengths: Pipe-separated strengths
            match_gaps: Pipe-separated gaps
            questions_count: Total questions asked
            ai_answered: Questions answered by AI
            static_answered: Questions answered statically
            application_time: Time taken in seconds
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Determine which file to write to
            if status == "Failed" or status == "Skipped":
                target_file = failed_file_name
                row = [
                    timestamp,
                    truncate_for_csv(job_title),
                    truncate_for_csv(company),
                    truncate_for_csv(location),
                    error or status,
                    job_url,
                    match_score if match_score > 0 else "",
                    truncate_for_csv(error) if status == "Skipped" else "",
                    truncate_for_csv(error) if status == "Failed" else ""
                ]
            else:
                target_file = file_name
                row = [
                    timestamp,
                    truncate_for_csv(job_title),
                    truncate_for_csv(company),
                    truncate_for_csv(location),
                    status,
                    job_url,
                    match_score if match_score > 0 else "",
                    truncate_for_csv(match_strengths),
                    truncate_for_csv(match_gaps),
                    questions_count,
                    ai_answered,
                    static_answered,
                    f"{application_time:.1f}" if application_time > 0 else "",
                    truncate_for_csv(error) if error else ""
                ]
            
            with open(target_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            self.log(f"Logged application: {company} - {job_title} (Match: {match_score}%)", "debug")
        
        except Exception as e:
            self.log(f"Error logging application: {str(e)}", "error")

    def request_cancel(self):
        """Request cooperative cancellation of the current job application process."""
        self.cancel_requested = True
        self.log("Cancellation requested", "warning")
    
    def check_login_status(self) -> bool:
        """
        Check if user is logged into LinkedIn.
        
        Returns:
            True if logged in, False otherwise
        """
        try:
            # Check for sign in button (indicates not logged in)
            if try_linkText(self.driver, "Sign in"):
                self.log("Not logged into LinkedIn", "warning")
                return False
            
            # Check if we can access the feed
            if "linkedin.com/feed" in self.driver.current_url:
                self.log("User is logged into LinkedIn", "success")
                return True
            
            self.log("Assuming user is logged in (feed URL not found)", "warning")
            return True
        
        except Exception as e:
            self.log(f"Error checking login status: {str(e)}", "error")
            return False
    
    def search_jobs(self, job_title: str, location: str, max_results: int = 50, language: str = "", prefer_english: bool = False) -> bool:
        """
        Search for jobs on LinkedIn.
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            max_results: Maximum number of results to process
        
        Returns:
            True if search successful, False otherwise
        """
        try:
            self.log(f"Searching for jobs: {job_title} in {location}", "info")
            
            # Build search URL
            # Build search URL. LinkedIn does not expose a simple language query param,
            # but we include language in logging and will apply heuristics during listing
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}"
            if language:
                # append language as a harmless search fragment so it can be used server-side when possible
                search_url += f"&f_L={language}"
            self.driver.get(search_url)
            
            self.log(f"Job search page loaded: {search_url}", "success")
            
            # Wait for job listings to load (try multiple selectors with longer timeout)
            # LinkedIn's HTML structure changes, so try multiple possible selectors
            from selenium.webdriver.support.ui import WebDriverWait
            wait_long = WebDriverWait(self.driver, 15)  # 15 second timeout for initial load
            
            job_cards = None
            selectors_to_try = [
                (By.CLASS_NAME, "job-card-container"),
                (By.CLASS_NAME, "jobs-search-results__list-item"),
                (By.CSS_SELECTOR, "[data-job-id]"),
                (By.CSS_SELECTOR, ".scaffold-layout__list-item"),
                (By.XPATH, "//li[contains(@class, 'jobs-search-results')]"),
                (By.CSS_SELECTOR, "ul.jobs-search-results__list > li"),
            ]
            
            for by_method, selector in selectors_to_try:
                try:
                    self.log(f"Trying selector: {selector}", "debug")
                    wait_long.until(EC.presence_of_element_located((by_method, selector)))
                    job_cards = self.driver.find_elements(by_method, selector)
                    if job_cards and len(job_cards) > 0:
                        self.log(f"Found {len(job_cards)} job cards using selector: {selector}", "success")
                        break
                except TimeoutException:
                    continue
            
            if not job_cards or len(job_cards) == 0:
                self.log("Could not find job listings with any known selector", "error")
                self.log("Page might require login or have different structure", "warning")
                return False
            
            # If prefer_english is set, we'll later prefer job descriptions that contain predominantly English text.
            self.log(f"Job listings loaded. Found {len(job_cards)} listings. language={language} prefer_english={prefer_english}", "success")
            return True
        
        except TimeoutException:
            self.log("Timeout: Job listings failed to load within 15 seconds", "error")
            self.log("This may indicate: slow connection, need to login, or page structure changed", "warning")
            return False
        except Exception as e:
            self.log(f"Error searching jobs: {str(e)}", "error")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}", "debug")
            return False
    
    def get_job_listings(self) -> List[dict]:
        """
        Get job listings from current page using modern LinkedIn selectors.
        
        Returns:
            List of job dictionaries with title, company, location, url
        """
        jobs = []
        try:
            # Try multiple selectors to find job cards (LinkedIn changes structure frequently)
            job_cards = []
            selectors_to_try = [
                (By.CSS_SELECTOR, ".scaffold-layout__list-item"),
                (By.CLASS_NAME, "job-card-container"),
                (By.CLASS_NAME, "jobs-search-results__list-item"),
                (By.CSS_SELECTOR, "[data-job-id]"),
                (By.CSS_SELECTOR, "ul.jobs-search-results__list > li"),
            ]
            
            for by_method, selector in selectors_to_try:
                try:
                    job_cards = self.driver.find_elements(by_method, selector)
                    if job_cards and len(job_cards) > 0:
                        self.log(f"Found {len(job_cards)} job cards using selector: {selector}", "debug")
                        break
                except Exception:
                    continue
            
            if not job_cards:
                self.log("Could not find job cards with any selector", "warning")
                return []
            
            # Extract details from each job card
            for job_card in job_cards[:20]:  # Limit to 20 per page
                try:
                    job_data = self._extract_job_details(job_card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    self.log(f"Error extracting job details: {str(e)}", "debug")
                    continue
            
            self.log(f"Extracted {len(jobs)} job listings", "info")
            return jobs
        
        except Exception as e:
            self.log(f"Error getting job listings: {str(e)}", "error")
            return []
    
    def _extract_job_details(self, job_card) -> Optional[Dict[str, Any]]:
        """
        Extract job details from a job card element using multiple selector strategies.
        
        Args:
            job_card: WebElement representing the job card
            
        Returns:
            Dictionary with job details or None if extraction fails
        """
        try:
            job_title = "Unknown"
            company = "Unknown"
            location = "Unknown"
            job_url = self.driver.current_url
            
            # Strategy 1: Try modern LinkedIn selectors (2024+)
            # Job title selectors
            title_selectors = [
                (By.CSS_SELECTOR, ".job-card-list__title"),
                (By.CSS_SELECTOR, ".jobs-unified-top-card__job-title"),
                (By.CSS_SELECTOR, "[class*='job-title']"),
                (By.CSS_SELECTOR, "h3.base-search-card__title"),
                (By.CSS_SELECTOR, "a.job-card-container__link"),
                (By.XPATH, ".//a[contains(@class, 'job-card')]//strong"),
                (By.XPATH, ".//h3"),
                (By.TAG_NAME, "h3"),
                (By.TAG_NAME, "strong"),
            ]
            
            for by_method, selector in title_selectors:
                try:
                    title_elem = job_card.find_element(by_method, selector)
                    if title_elem and title_elem.text.strip():
                        job_title = title_elem.text.strip()
                        self.log(f"Found title using {selector}: {job_title}", "debug")
                        break
                except:
                    continue
            
            # Company selectors
            company_selectors = [
                (By.CSS_SELECTOR, ".job-card-container__primary-description"),
                (By.CSS_SELECTOR, ".job-card-container__company-name"),
                (By.CSS_SELECTOR, "[class*='company-name']"),
                (By.CSS_SELECTOR, "h4.base-search-card__subtitle"),
                (By.CSS_SELECTOR, ".base-search-card__subtitle"),
                (By.XPATH, ".//h4"),
                (By.TAG_NAME, "h4"),
                (By.XPATH, ".//span[contains(@class, 'company')]"),
            ]
            
            for by_method, selector in company_selectors:
                try:
                    company_elem = job_card.find_element(by_method, selector)
                    if company_elem and company_elem.text.strip():
                        company = company_elem.text.strip()
                        self.log(f"Found company using {selector}: {company}", "debug")
                        break
                except:
                    continue
            
            # Location selectors
            location_selectors = [
                (By.CSS_SELECTOR, ".job-card-container__metadata-item"),
                (By.CSS_SELECTOR, "[class*='location']"),
                (By.CSS_SELECTOR, ".job-search-card__location"),
                (By.CSS_SELECTOR, ".base-search-card__metadata"),
                (By.XPATH, ".//span[contains(text(), ',') or contains(@class, 'location')]"),
            ]
            
            for by_method, selector in location_selectors:
                try:
                    location_elem = job_card.find_element(by_method, selector)
                    if location_elem and location_elem.text.strip():
                        location = location_elem.text.strip()
                        self.log(f"Found location using {selector}: {location}", "debug")
                        break
                except:
                    continue
            
            # Try to extract job URL from link
            try:
                link_elem = job_card.find_element(By.TAG_NAME, "a")
                if link_elem:
                    job_url = link_elem.get_attribute("href") or job_url
            except:
                pass
            
            # Only return if we found at least a title
            if job_title != "Unknown":
                return {
                    'title': job_title,
                    'company': company,
                    'location': location,
                    'element': job_card,
                    'url': job_url
                }
            else:
                self.log(f"Could not extract title from job card", "debug")
                return None
        
        except Exception as e:
            self.log(f"Error in _extract_job_details: {str(e)}", "debug")
            return None
    
    def click_easy_apply(self) -> bool:
        """
        Click the Easy Apply button if available.
        Uses multiple selectors and scrolling to ensure button is found and clickable.
        
        Returns:
            True if button clicked, False otherwise
        """
        try:
            import time
            
            # Multiple Easy Apply button selectors (LinkedIn changes their UI frequently)
            easy_apply_selectors = [
                # Text-based selectors
                '//button[contains(@class, "jobs-apply-button") and contains(., "Easy Apply")]',
                '//button[contains(text(), "Easy Apply")]',
                '//button[contains(., "Easy Apply")]',
                # Class-based selectors
                '//button[contains(@class, "jobs-apply-button")]',
                '//button[@aria-label="Easy Apply"]',
                # Broader selectors
                '//button[contains(@class, "apply")]',
            ]
            
            easy_apply_button = None
            
            # Try each selector
            for selector in easy_apply_selectors:
                easy_apply_button = try_xp(self.driver, selector, timeout=3)
                if easy_apply_button:
                    self.log(f"Found Easy Apply button with selector: {selector}", "debug")
                    break
            
            if not easy_apply_button:
                # Scroll down to see if button appears
                self.log("Easy Apply button not immediately visible, scrolling...", "debug")
                try:
                    self.driver.execute_script("window.scrollBy(0, 300);")
                    time.sleep(1)
                    
                    # Try again after scroll
                    for selector in easy_apply_selectors:
                        easy_apply_button = try_xp(self.driver, selector, timeout=3)
                        if easy_apply_button:
                            self.log(f"Found Easy Apply button after scroll: {selector}", "debug")
                            break
                except Exception as e:
                    self.log(f"Error scrolling: {e}", "debug")
            
            if easy_apply_button:
                # Dismiss any overlays/modals that might be blocking the button
                try:
                    self.driver.execute_script("""
                        // Remove LinkedIn modals/overlays
                        document.querySelectorAll('[role="dialog"], .artdeco-modal, .msg-overlay-bubble-header, .msg-overlay-list-bubble').forEach(el => {
                            if (el) el.style.display = 'none';
                        });
                    """)
                    time.sleep(0.3)
                except:
                    pass
                
                # Scroll button into view before clicking
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", easy_apply_button)
                    time.sleep(0.5)
                except:
                    pass
                
                # Try JavaScript click first (more reliable), then fallback
                clicked = False
                try:
                    # JavaScript click - bypasses overlay issues
                    self.driver.execute_script("arguments[0].click();", easy_apply_button)
                    clicked = True
                    self.log("✅ Clicked Easy Apply button (JS)", "success")
                except Exception as e:
                    self.log(f"JS click failed, trying regular click: {e}", "debug")
                    try:
                        # Fallback to regular click
                        easy_apply_button.click()
                        clicked = True
                        self.log("✅ Clicked Easy Apply button", "success")
                    except Exception as e2:
                        self.log(f"Regular click also failed: {e2}", "error")
                        return False
                
                if clicked:
                    time.sleep(1)  # Wait for form to load
                    return True
                return False
            else:
                self.log("Easy Apply button not found", "warning")
                return False
        
        except Exception as e:
            self.log(f"Error clicking Easy Apply: {str(e)}", "error")
            return False
    
    def fill_application_form(self, form_data: dict) -> bool:
        """
        Fill out the application form with provided data.
        
        Loads personals and resume settings from config and merges with provided form_data.
        Uses FormHandler and QuestionHandler for best-effort field detection and filling.
        
        Args:
            form_data: Dictionary with form field names and values
        
        Returns:
            True if form filled successfully, False otherwise
        """
        def _fill_form_action():
            if self.cancel_requested:
                self.log("Form fill cancelled before start", "warning")
                return False

            self.log("Filling application form...", "info")

            # Find the main form container heuristically
            form_element = try_xp(self.driver, '//form')
            if not form_element:
                form_element = try_xp(self.driver, '//div[contains(@class, "jobs-easy-apply-form")]')

            if not form_element:
                self.log("Could not locate application form on page", "warning")
                return False

            # Load personals and resume from config
            personals = load_personals_settings()
            resume_config = load_resume_settings()
            resume_path = resume_config.get("resume_path", "")
            
            # Merge provided form_data with loaded settings
            merged_data = {}
            merged_data.update(personals)  # personals first
            if form_data:
                merged_data.update(form_data)  # explicit form_data overrides

            # Use FormHandler to detect and fill obvious inputs
            fill_results = self.form_handler.fill_form(form_element, merged_data)

            # Attempt resume upload if we have a path
            if resume_path and os.path.exists(resume_path):
                try:
                    resume_fields = self.form_handler.find_resume_fields(form_element)
                    for field_key, field_meta in resume_fields.items():
                        if self.cancel_requested:
                            break
                        elem = field_meta.get("element")
                        if elem:
                            ok = self.form_handler.upload_file(elem, resume_path)
                            fill_results[field_key] = {"status": "ok" if ok else "failed", "type": "file"}
                except Exception as e:
                    self.log(f"Resume upload attempt failed: {e}", "debug")

            # Try to answer questions using QuestionHandler (best-effort)
            questions = []
            try:
                questions = form_element.find_elements(By.XPATH, './/div[contains(@class, "question") or contains(@class, "application-question") or .//label]')
            except Exception:
                # fallback: attempt to find container children with inputs
                try:
                    questions = form_element.find_elements(By.XPATH, './/*[self::div or self::fieldset]')
                except Exception:
                    questions = []

            if questions and self.cancel_requested == False:
                try:
                    q_results = self.question_handler.answer_questions(questions, merged_data)
                    self.log(f"Answered {len(q_results)} questions (best-effort)", "debug")
                except Exception as e:
                    self.log(f"Question answering failed: {e}", "debug")

            # Evaluate fill results
            ok_count = sum(1 for v in fill_results.values() if v.get("status") == "ok") if isinstance(fill_results, dict) else 0
            
            if ok_count > 0:
                self.log(f"Application form filled ({ok_count} fields)", "success")
                return True
            else:
                # Check if we have personal data configured
                if not merged_data or len(merged_data) == 0:
                    self.log("⚠️ No personal information configured in Settings!", "warning")
                    self.log("📝 Go to Settings page to add: Name, Email, Phone, etc.", "info")
                    self.log("🔄 Will attempt to submit form anyway (may fail)", "warning")
                    # Return True to proceed to submit (LinkedIn may have pre-filled data)
                    return True
                else:
                    self.log(f"No fields were filled (tried with {len(merged_data)} data fields)", "warning")
                    self.log("ℹ️ Form may have pre-filled fields or unusual field names", "info")
                    # Still proceed to submit
                    return True
            return False

        # Use error recovery manager for robust error handling
        success, error_msg = self.recovery_manager.attempt_with_recovery(_fill_form_action, "Fill Application Form")
        if not success and error_msg:
            self.log(f"Error recovery: {error_msg}", "error")
        
        # Wait for form to process and buttons to become enabled
        if success:
            time.sleep(2)  # Give LinkedIn time to enable Submit/Next buttons
            
        return success
    
    def submit_application(self) -> bool:
        """
        Submit the application form.
        Handles multi-step forms (Next, Review, Submit).
        
        Returns:
            True if submitted successfully, False otherwise
        """
        try:
            # LinkedIn Easy Apply flow: Fill → Next → Next → Review → Submit
            # The typical flow has multiple "Next" buttons, then "Review", then "Submit"
            # We need to handle this specific sequence properly
            max_steps = 10  # Increased to handle longer forms
            last_url = None  # Track URL changes to detect if we're stuck
            stuck_count = 0  # Count consecutive clicks on same page
            
            for step in range(max_steps):
                # Check if we're on the Review page
                try:
                    review_page_indicators = [
                        '//h3[contains(text(), "Review your application")]',
                        '//*[contains(text(), "Review your application")]',
                        '//div[contains(@class, "jobs-easy-apply-content") and contains(., "Review")]',
                    ]
                    for indicator in review_page_indicators:
                        if try_xp(self.driver, indicator, timeout=1):
                            self.log("📋 On Review page - checking details before submit", "info")
                            time.sleep(1)  # Brief pause on review page
                            break
                except:
                    pass
                
                # IMPORTANT: Order matters! Try in sequence: Next → Review → Submit
                # Priority order based on LinkedIn's actual flow:
                # 1. Next buttons (early steps)
                # 2. Review button (penultimate step)
                # 3. Submit button (final step)
                button_selectors = [
                    # Priority 1: Next/Continue buttons (most common in early steps)
                    '//button[contains(@aria-label, "Continue to next step")]',
                    '//button[contains(@aria-label, "next")]',
                    '//button[contains(., "Next") and contains(@class, "artdeco-button")]',
                    '//button[contains(text(), "Next")]',
                    '//button[contains(text(), "Continue")]',
                    '//button[@data-easy-apply-next-button]',
                    '//button[contains(@class, "artdeco-button") and contains(@aria-label, "Continue")]',
                    
                    # Priority 2: Review button (after all form pages)
                    '//button[contains(@aria-label, "Review your application")]',
                    '//button[contains(@aria-label, "Review")]',
                    '//button[contains(., "Review") and contains(@class, "artdeco-button")]',
                    '//button[contains(text(), "Review")]',
                    '//button[contains(text(), "Review your application")]',
                    
                    # Priority 3: Submit button (final step after review)
                    '//button[contains(@aria-label, "Submit application")]',
                    '//button[contains(., "Submit") and contains(@class, "artdeco-button")]',
                    '//button[contains(text(), "Submit application")]',
                    '//button[contains(text(), "Submit")]',
                    '//button[contains(@aria-label, "submit")]',
                    
                    # Fallback: Generic primary buttons (if specific text not found)
                    '//footer//button[contains(@class, "artdeco-button--primary")]',
                    '//div[contains(@class, "artdeco-modal")]//button[contains(@class, "artdeco-button--primary")]',
                    '//button[contains(@class, "artdeco-button--primary") and not(contains(@aria-label, "Dismiss"))]',
                ]
                
                button_found = False
                for selector in button_selectors:
                    try:
                        button = try_xp(self.driver, selector, timeout=3)
                        if button and button.is_displayed() and button.is_enabled():
                            # Scroll button into view first
                            try:
                                self.driver.execute_script(
                                    "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                                    button
                                )
                                time.sleep(0.5)
                            except:
                                pass
                            
                            # Get button text for logging
                            button_text = button.text or button.get_attribute("aria-label") or "button"
                            
                            # Determine step type for better logging
                            if "review" in button_text.lower():
                                step_type = "📋 Review"
                            elif "submit" in button_text.lower():
                                step_type = "✅ Submit"
                            elif "next" in button_text.lower() or "continue" in button_text.lower():
                                step_type = "➡️ Next"
                            else:
                                step_type = "▶️ Proceed"
                            
                            # Click using JavaScript (more reliable)
                            try:
                                self.driver.execute_script("arguments[0].click();", button)
                                self.log(f"Step {step + 1}: {step_type} - Clicked '{button_text}'", "info")
                            except:
                                button.click()
                                self.log(f"Step {step + 1}: {step_type} - Clicked '{button_text}'", "info")
                            
                            button_found = True
                            
                            # Special handling for Review button - wait longer for page to load
                            if "review" in button_text.lower():
                                self.log("⏳ Loading review page...", "info")
                                time.sleep(3)  # Review page takes longer to load
                            else:
                                time.sleep(2.5)  # Standard wait for next step
                            
                            # Check if we're stuck on the same page
                            # For LinkedIn Easy Apply, URL often stays the same, so check page content hash
                            current_url = self.driver.current_url
                            
                            # Get a hash of the current form content to detect real changes
                            try:
                                form_content = self.driver.find_element(By.CSS_SELECTOR, 'form, .jobs-easy-apply-content').text
                                current_page_hash = hash(form_content[:500])  # Use first 500 chars
                            except:
                                current_page_hash = hash(current_url)  # Fallback to URL
                            
                            # Only check for stuck if clicking Next button
                            if "next" in button_text.lower():
                                # Check if both URL and content are unchanged
                                if current_url == last_url and current_page_hash == getattr(self, '_last_page_hash', None):
                                    stuck_count += 1
                                    self.log(f"⚠️ Same page detected (stuck count: {stuck_count}/3)", "debug")
                                    if stuck_count >= 3:
                                        self.log("⚠️ Stuck on same page after 3 clicks - likely missing required fields", "warning")
                                        self.log("❌ Closing application and moving to next job", "warning")
                                        # Close the modal
                                        try:
                                            close_button = try_xp(self.driver, '//button[@aria-label="Dismiss"]', timeout=1)
                                            if close_button:
                                                close_button.click()
                                                time.sleep(1)
                                        except:
                                            pass
                                        return False
                                else:
                                    stuck_count = 0  # Reset if URL or content changed
                                    self.log("✓ Form content changed, progressing...", "debug")
                            
                            last_url = current_url
                            self._last_page_hash = current_page_hash
                            
                            # Check if we successfully submitted (look for confirmation)
                            try:
                                confirmation_selectors = [
                                    '//h3[contains(text(), "Application sent")]',
                                    '//h3[contains(text(), "Your application was sent")]',
                                    '//div[contains(@class, "artdeco-modal") and contains(., "Application sent")]',
                                    '//*[contains(text(), "successfully submitted")]',
                                    '//h2[contains(text(), "Application sent")]',
                                ]
                                for conf_selector in confirmation_selectors:
                                    if try_xp(self.driver, conf_selector, timeout=2):
                                        self.log("🎉 Application submitted successfully!", "success")
                                        self.applied_count += 1
                                        return True
                            except:
                                pass
                            
                            break  # Found and clicked a button, move to next step
                    except:
                        continue
                
                if not button_found:
                    # No more buttons found, assume we're done
                    if step > 0:
                        # We clicked at least one button, probably succeeded
                        self.log(f"✅ Application completed ({step} steps)", "success")
                        self.applied_count += 1
                        return True
                    else:
                        self.log("❌ No submit/next button found", "warning")
                        return False
            
            # Reached max steps
            self.log(f"⚠️ Completed {max_steps} steps, assuming success", "warning")
            self.applied_count += 1
            return True
        
        except Exception as e:
            self.log(f"Error submitting application: {str(e)}", "error")
            self.failed_count += 1
            return False
    
    def evaluate_job_match(self, job_data: dict) -> Optional[Dict[str, Any]]:
        """
        Use AI to evaluate job match before applying.
        
        Args:
            job_data: Job details dictionary
            
        Returns:
            Match result dict with score, strengths, gaps or None if AI disabled
        """
        try:
            # Check if AI matching is enabled
            from config import settings
            if not getattr(settings, 'enable_smart_filtering', False):
                return None
            
            # Get AI handler
            from modules.ai_handler import ai_handler
            if not ai_handler.enabled:
                return None
            
            # Get resume text (simplified - use resume path directly)
            resume_text = ""
            try:
                import os
                from config.questions import default_resume_path
                resume_path = default_resume_path
                if resume_path and os.path.isfile(resume_path):
                    # Use filename and basic info as placeholder
                    # TODO: Extract text from PDF/DOCX
                    filename = os.path.basename(resume_path)
                    resume_text = f"Resume: {filename}"
                elif resume_path:
                    self.log(f"Resume file not found: {resume_path}", "warning")
            except Exception as e:
                self.log(f"Could not load resume: {e}", "warning")
            
            # Get job description from page
            job_description = ""
            try:
                desc_element = try_xp(self.driver, '//div[contains(@class, "jobs-description")]//div', timeout=3)
                if desc_element:
                    job_description = desc_element.text[:2000]  # Limit to 2000 chars
            except Exception:
                pass
            
            if not job_description:
                job_description = f"{job_data.get('title', '')} at {job_data.get('company', '')}"
            
            # Call AI to match job
            self.log(f"🤖 Analyzing job match...", "info")
            match_result = ai_handler.match_job(resume_text, job_description)
            
            if match_result:
                score = match_result.get('score', 50)
                self.log(f"Match Score: {score}%", "info")
                
                # Log strengths
                strengths = match_result.get('strengths', [])
                if strengths:
                    self.log(f"✅ Strengths: {', '.join(strengths[:3])}", "success")
                
                # Log gaps
                gaps = match_result.get('gaps', [])
                if gaps:
                    self.log(f"❌ Gaps: {', '.join(gaps[:3])}", "warning")
            
            return match_result
            
        except Exception as e:
            self.log(f"Error evaluating job match: {e}", "error")
            return None
    
    def apply_to_job(self, job_data: dict, form_data: dict) -> bool:
        """
        Complete application process for a single job.
        
        Args:
            job_data: Job details dictionary
            form_data: Form data to fill
        
        Returns:
            True if application successful, False otherwise
        """
        def _apply_action():
            try:
                job_title = job_data.get('title', 'Unknown')
                company = job_data.get('company', 'Unknown')
                location = job_data.get('location', 'Unknown')
                self.log(f"Applying to: {company} - {job_title}", "info")

                # Click job listing
                if self.cancel_requested:
                    self.log("Cancellation requested - aborting apply_to_job", "warning")
                    return False

                if job_data.get('element'):
                    import time
                    from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
                    
                    # Try to click the job card with retry logic for stale/intercepted errors
                    max_click_attempts = 3
                    clicked = False
                    
                    for attempt in range(max_click_attempts):
                        try:
                            # Dismiss any overlays that might be in the way
                            try:
                                # Close any LinkedIn modals/overlays
                                self.driver.execute_script("""
                                    // Remove any overlay elements
                                    document.querySelectorAll('[role="dialog"], .artdeco-modal, .msg-overlay-bubble-header').forEach(el => {
                                        if (el) el.style.display = 'none';
                                    });
                                """)
                            except:
                                pass
                            
                            # Scroll job card into view
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", job_data['element'])
                            time.sleep(0.3)
                            
                            # Try JavaScript click first (more reliable)
                            try:
                                self.driver.execute_script("arguments[0].click();", job_data['element'])
                                clicked = True
                                self.log("Clicked job listing (JS)", "debug")
                                break
                            except:
                                # Fallback to regular click
                                job_data['element'].click()
                                clicked = True
                                self.log("Clicked job listing", "debug")
                                break
                                
                        except StaleElementReferenceException:
                            if attempt < max_click_attempts - 1:
                                self.log(f"Element stale, re-finding (attempt {attempt + 1})...", "warning")
                                time.sleep(1.5)  # Longer wait for DOM to stabilize
                                
                                element_found = False
                                job_title = job_data.get('title', '')
                                
                                # Strategy 1: Re-scan page and get fresh job cards
                                # This is the most reliable since it gets current DOM state
                                if not element_found:
                                    try:
                                        self.log("Strategy 1: Re-scanning page for fresh job cards...", "debug")
                                        selectors_to_try = [
                                            (By.CLASS_NAME, "job-card-container"),
                                            (By.CSS_SELECTOR, ".scaffold-layout__list-item"),
                                            (By.CLASS_NAME, "jobs-search-results__list-item"),
                                        ]
                                        
                                        for by_method, selector in selectors_to_try:
                                            if element_found:
                                                break
                                            try:
                                                fresh_job_cards = self.driver.find_elements(by_method, selector)
                                                if fresh_job_cards and len(fresh_job_cards) > 0:
                                                    self.log(f"Found {len(fresh_job_cards)} fresh job cards", "debug")
                                                    # Try to match by title
                                                    for idx, card in enumerate(fresh_job_cards):
                                                        try:
                                                            # Try multiple selectors for title
                                                            card_title = None
                                                            for title_sel in ["h3", ".job-card-list__title", "a.job-card-container__link", "strong"]:
                                                                try:
                                                                    card_title = card.find_element(By.CSS_SELECTOR, title_sel).text.strip()
                                                                    if card_title:
                                                                        break
                                                                except:
                                                                    continue
                                                            
                                                            if card_title:
                                                                # Clean up duplicated text (e.g., "Sales Manager Sales Manager")
                                                                card_title_clean = ' '.join(dict.fromkeys(card_title.split()))
                                                                job_title_clean = ' '.join(dict.fromkeys(job_title.split()))
                                                                
                                                                # Match if titles are similar
                                                                if (card_title_clean.lower() in job_title_clean.lower() or 
                                                                    job_title_clean.lower() in card_title_clean.lower()):
                                                                    job_data['element'] = card
                                                                    self.log(f"✅ Re-found element (Strategy 1): {card_title_clean[:40]}", "success")
                                                                    element_found = True
                                                                    break
                                                        except:
                                                            continue
                                                    
                                                    # If still not found, just use the first available card
                                                    if not element_found and len(fresh_job_cards) > 0:
                                                        job_data['element'] = fresh_job_cards[0]
                                                        self.log(f"⚠️ Using first available job card (couldn't match title)", "warning")
                                                        element_found = True
                                                    
                                                    if element_found:
                                                        break
                                            except:
                                                continue
                                    except Exception as e:
                                        self.log(f"Strategy 1 failed: {str(e)}", "debug")
                                
                                # Strategy 2: Try to re-find by job URL/ID
                                if not element_found:
                                    try:
                                        self.log("Strategy 2: Searching by job ID...", "debug")
                                        job_url = job_data.get('url', '')
                                        if job_url and 'currentJobId=' in job_url:
                                            job_id = job_url.split('currentJobId=')[1].split('&')[0]
                                            new_element = try_xp(self.driver, f'//a[contains(@href, "{job_id}")]', timeout=2)
                                            if new_element:
                                                job_data['element'] = new_element
                                                self.log(f"✅ Re-found element (Strategy 2): Job ID {job_id}", "success")
                                                element_found = True
                                    except Exception as e:
                                        self.log(f"Strategy 2 failed: {str(e)}", "debug")
                                
                                # If element was found, continue retry loop
                                if element_found:
                                    continue
                            break
                            
                        except ElementClickInterceptedException:
                            if attempt < max_click_attempts - 1:
                                self.log(f"Click intercepted, retrying (attempt {attempt + 1})...", "debug")
                                time.sleep(0.5)
                            else:
                                # Force click with JavaScript
                                try:
                                    self.driver.execute_script("arguments[0].click();", job_data['element'])
                                    clicked = True
                                    self.log("Forced click with JavaScript", "debug")
                                except:
                                    pass
                            break
                    
                    if not clicked:
                        self.log("Could not click job card after retries", "warning")
                        return False
                    
                    # Wait for job details panel to load and update
                    time.sleep(1)
                    
                    # Verify the job details actually loaded (wait for URL or panel to change)
                    try:
                        expected_job_url = job_data.get('url', '')
                        if expected_job_url and 'currentJobId=' in expected_job_url:
                            expected_job_id = expected_job_url.split('currentJobId=')[1].split('&')[0]
                            
                            # Wait up to 5 seconds for the URL to update with the correct job ID
                            for wait_attempt in range(10):  # 10 attempts x 0.5s = 5 seconds max
                                current_url = self.driver.current_url
                                if expected_job_id in current_url:
                                    self.log(f"Job details loaded: {current_url[:80]}...", "debug")
                                    break
                                time.sleep(0.5)
                            else:
                                self.log(f"Warning: Job details may not have loaded (expected ID: {expected_job_id})", "warning")
                    except Exception as e:
                        self.log(f"Could not verify job details loaded: {e}", "debug")
                        # Log current URL anyway
                        try:
                            current_url = self.driver.current_url
                            self.log(f"Current page: {current_url[:80]}...", "debug")
                        except:
                            pass
                    
                    time.sleep(1)  # Additional wait for UI to stabilize

                # Emit progress update
                if self.progress_callback:
                    try:
                        self.progress_callback(self.applied_count, self.failed_count, self.skipped_count, job_title)
                    except Exception:
                        pass

                # Click Easy Apply
                if self.cancel_requested:
                    self.log("Cancellation requested - aborting before Easy Apply", "warning")
                    return False

                if not self.click_easy_apply():
                    self.log(f"Skipping: Easy Apply not available", "warning")
                    self.skipped_count += 1
                    self.log_application(job_title, company, location, "Skipped", error="Easy Apply not available")
                    return False

                # Fill and submit form
                if self.cancel_requested:
                    self.log("Cancellation requested - aborting during form fill", "warning")
                    return False

                if self.fill_application_form(form_data):
                    if self.submit_application():
                        self.log_application(job_title, company, location, "Applied")
                        self.applied_count += 1
                        return True
                    else:
                        self.log_application(job_title, company, location, "Failed", error="Submission error")
                        self.failed_count += 1
                        return False
                else:
                    self.log_application(job_title, company, location, "Failed", error="Form fill error")
                    self.failed_count += 1
                    return False
            except Exception as e:
                self.log(f"Error applying to job: {str(e)}", "error")
                self.failed_count += 1
                self.log_application(
                    job_data.get('title', 'Unknown'),
                    job_data.get('company', 'Unknown'),
                    job_data.get('location', 'Unknown'),
                    "Failed",
                    error=str(e)
                )
                return False

        # Use error recovery manager for robust error handling
        success, error_msg = self.recovery_manager.attempt_with_recovery(_apply_action, "Apply to Job")
        if not success and error_msg:
            self.log(f"Error recovery: {error_msg}", "error")
        return success
    
    def get_statistics(self) -> dict:
        """
        Get application statistics.
        
        Returns:
            Dictionary with applied, failed, and skipped counts
        """
        return {
            'applied': self.applied_count,
            'failed': self.failed_count,
            'skipped': self.skipped_count,
            'total': self.applied_count + self.failed_count + self.skipped_count
        }
    
    def print_statistics(self):
        """Print application statistics."""
        stats = self.get_statistics()
        
        summary = (
            f"\n{'='*50}\n"
            f"Application Statistics:\n"
            f"  Applied: {stats['applied']}\n"
            f"  Failed: {stats['failed']}\n"
            f"  Skipped: {stats['skipped']}\n"
            f"  Total: {stats['total']}\n"
            f"{'='*50}\n"
        )
        
        self.log(summary, "info")


class LinkedInSession:
    """
    Manages a complete LinkedIn automation session.
    Handles login, job search, and bulk applications.
    """
    
    def __init__(self, driver: WebDriver, wait: WebDriverWait, actions: ActionChains, log_callback: Callable = None):
        """Initialize LinkedIn session."""
        self.driver = driver
        self.wait = wait
        self.actions = actions
        self.log_callback = log_callback or print_lg
        self.app_manager = JobApplicationManager(driver, wait, actions, log_callback)
    
    def log(self, message: str, level: str = "info"):
        """Log a message."""
        self.log_callback(message, level)
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to LinkedIn with credentials.
        
        Args:
            email: LinkedIn email
            password: LinkedIn password
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            self.log("Navigating to LinkedIn login page...", "info")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for login form
            self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            
            # Enter credentials
            text_input_by_ID(self.driver, "username", email)
            text_input_by_ID(self.driver, "password", password)
            
            # Click sign in
            sign_in_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            sign_in_button.click()
            
            # Wait for feed to load
            self.wait.until(EC.url_contains("feed"))
            
            self.log("Successfully logged into LinkedIn!", "success")
            return True
        
        except Exception as e:
            self.log(f"Login failed: {str(e)}", "error")
            return False
    
    def run_search_and_apply(self, job_title: str, location: str, max_applications: int, form_data: dict, language: str = "", prefer_english: bool = False) -> dict:
        """
        Run complete job search and application workflow.
        
        Args:
            job_title: Job title to search
            location: Location to search
            max_applications: Max number of applications
            form_data: Form data to use for applications
        
        Returns:
            Statistics dictionary
        """
        try:
            global current_manager
            current_manager = self.app_manager

            self.log(f"Starting job search workflow...", "info")
            
            # Search for jobs (pass language/prefer flags where applicable)
            if not self.app_manager.search_jobs(job_title, location, language=language, prefer_english=prefer_english):
                self.log("Job search failed", "error")
                return self.app_manager.get_statistics()
            
            # Get job listings
            jobs = self.app_manager.get_job_listings()
            
            if not jobs:
                self.log("No jobs found", "warning")
                return self.app_manager.get_statistics()
            
            # Apply to jobs (up to max_applications)
            for i, job in enumerate(jobs[:max_applications]):
                if i >= max_applications:
                    break
                
                # Evaluate job match before applying (if AI enabled)
                match_result = self.app_manager.evaluate_job_match(job)
                job['match_result'] = match_result  # Store for logging
                
                if match_result:
                    score = match_result.get('score', 50)
                    min_threshold = getattr(__import__('config.settings', fromlist=['min_match_score']), 'min_match_score', 60)
                    
                    if score < min_threshold:
                        self.log(f"⏭️  SKIPPED: {job.get('company', 'Unknown')} - {job.get('title', 'Unknown')} (Match: {score}% < {min_threshold}%)", "warning")
                        self.app_manager.skipped_count += 1
                        self.app_manager.log_application(
                            job.get('title', 'Unknown'),
                            job.get('company', 'Unknown'),
                            job.get('location', 'Unknown'),
                            "Skipped",
                            error=f"Low match score: {score}%"
                        )
                        continue
                    else:
                        self.log(f"✅ Good match ({score}%) - Proceeding with application", "success")
                
                self.app_manager.apply_to_job(job, form_data)
                
                # Brief pause between applications
                import time
                time.sleep(2)
            
            # Print final statistics
            self.app_manager.print_statistics()

            return self.app_manager.get_statistics()
        
        except Exception as e:
            self.log(f"Error in search and apply workflow: {str(e)}", "error")
            return self.app_manager.get_statistics()
        finally:
            try:
                current_manager = None
            except Exception:
                pass
