'''
Auto Job Applier - Integration Layer
Bridges GUI with LinkedIn Automation Logic

This module connects the GUI to the core automation features from runAiBot.py
Handles job searching, form filling, and application submission.
'''

import csv
import os
import re
from datetime import datetime
from typing import Callable, Optional, Tuple, List
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
                        'Status', 'Job URL', 'Error Details'
                    ])
                self.log(f"Created applications history file: {file_name}", "success")
            
            if not os.path.exists(failed_file_name):
                with open(failed_file_name, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'Timestamp', 'Job Title', 'Company', 'Location',
                        'Error Reason', 'Job URL', 'Full Error'
                    ])
                self.log(f"Created failed applications file: {failed_file_name}", "success")
        
        except Exception as e:
            self.log(f"Error setting up CSV files: {str(e)}", "error")
    
    def log_application(self, job_title: str, company: str, location: str, 
                       status: str, job_url: str = "", error: str = ""):
        """
        Log an application to CSV file.
        
        Args:
            job_title: Title of the job
            company: Company name
            location: Job location
            status: Status (Applied, Failed, Skipped)
            job_url: URL of the job posting
            error: Error message if any
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(file_name, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp,
                    truncate_for_csv(job_title),
                    truncate_for_csv(company),
                    truncate_for_csv(location),
                    status,
                    job_url,
                    truncate_for_csv(error) if error else ""
                ])
            
            self.log(f"Logged application: {company} - {job_title}", "debug")
        
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
            
            # Wait for job listings to load
            self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "job-card-container")))
            
            # If prefer_english is set, we'll later prefer job descriptions that contain predominantly English text.
            self.log(f"Job listings loaded. Found job listings on page. language={language} prefer_english={prefer_english}", "success")
            return True
        
        except TimeoutException:
            self.log("Timeout: Job listings failed to load", "error")
            return False
        except Exception as e:
            self.log(f"Error searching jobs: {str(e)}", "error")
            return False
    
    def get_job_listings(self) -> List[dict]:
        """
        Get job listings from current page.
        
        Returns:
            List of job dictionaries with title, company, location, url
        """
        jobs = []
        try:
            job_cards = self.driver.find_elements(By.CLASS_NAME, "job-card-container")
            
            for job_card in job_cards[:20]:  # Limit to 20 per page
                try:
                    # Extract job details
                    title_elem = job_card.find_element(By.CLASS_NAME, "job-card-title")
                    company_elem = job_card.find_element(By.CLASS_NAME, "job-card-company-name")
                    
                    job_title = title_elem.text if title_elem else "Unknown"
                    company = company_elem.text if company_elem else "Unknown"
                    location = "LinkedIn"  # Would need to extract from page
                    
                    jobs.append({
                        'title': job_title,
                        'company': company,
                        'location': location,
                        'element': job_card,
                        'url': self.driver.current_url
                    })
                
                except Exception as e:
                    self.log(f"Error extracting job details: {str(e)}", "debug")
                    continue
            
            self.log(f"Extracted {len(jobs)} job listings", "info")
            return jobs
        
        except Exception as e:
            self.log(f"Error getting job listings: {str(e)}", "error")
            return []
    
    def click_easy_apply(self) -> bool:
        """
        Click the Easy Apply button if available.
        
        Returns:
            True if button clicked, False otherwise
        """
        try:
            easy_apply_button = try_xp(self.driver, '//button[contains(text(), "Easy Apply")]')
            
            if easy_apply_button:
                easy_apply_button.click()
                self.log("Clicked Easy Apply button", "success")
                return True
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

            # Evaluate fill results: if any field marked ok, consider success
            ok_count = sum(1 for v in fill_results.values() if v.get("status") == "ok") if isinstance(fill_results, dict) else 0
            if ok_count > 0:
                self.log("Application form filled", "success")
                return True

            # Nothing filled; still return False
            self.log("No fields were filled by the automated form handler", "warning")
            return False

        # Use error recovery manager for robust error handling
        success, error_msg = self.recovery_manager.attempt_with_recovery(_fill_form_action, "Fill Application Form")
        if not success and error_msg:
            self.log(f"Error recovery: {error_msg}", "error")
        return success
    
    def submit_application(self) -> bool:
        """
        Submit the application form.
        
        Returns:
            True if submitted successfully, False otherwise
        """
        try:
            # Find and click submit button
            submit_button = try_xp(self.driver, '//button[contains(text(), "Submit") or contains(text(), "Apply")]')
            
            if submit_button:
                submit_button.click()
                self.log("Application submitted", "success")
                self.applied_count += 1
                return True
            else:
                self.log("Submit button not found", "warning")
                return False
        
        except Exception as e:
            self.log(f"Error submitting application: {str(e)}", "error")
            self.failed_count += 1
            return False
    
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
                    job_data['element'].click()

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
