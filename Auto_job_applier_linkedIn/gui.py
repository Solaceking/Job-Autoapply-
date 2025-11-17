'''
Auto Job Applier - LinkedIn Automation Tool
Windows Native GUI Application

Author:     Sai Vignesh Golla (Original), Modified for Production
License:    GNU Affero General Public License
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn
Version:    2024.12.29.16.00
'''

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import os
import sys
import csv
from datetime import datetime
from pathlib import Path

# Set CSV field size limit
csv.field_size_limit(1000000)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration imports
try:
    from config.personals import first_name, middle_name, last_name, phone_number
    from config.questions import default_resume_path, linkedin_headline, pause_before_submit, pause_at_failed_question
    from config.search import search_terms, search_location
    from config.secrets import username, password, use_AI, ai_provider
    from config.settings import run_in_background, stealth_mode, safe_mode, keep_screen_awake
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import config files: {str(e)}")
    sys.exit(1)

# Module imports
try:
    from modules.open_chrome import open_browser, close_browser, driver, wait, actions
    from modules.helpers import print_lg, critical_error_log, make_directories
    from modules.validator import validate_config
    from modules.automation_manager import LinkedInSession, JobApplicationManager
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import modules: {str(e)}")
    sys.exit(1)


class JobApplicationGUI:
    """Production-grade GUI for LinkedIn Job Application Automation"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Job Applier - LinkedIn")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Set window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass
        
        # Application state
        self.is_running = False
        self.driver = None
        self.wait = None
        self.actions = None
        self.log_queue = queue.Queue()
        
        # Setup styles
        self.setup_styles()
        
        # Build UI
        self.setup_ui()
        
        # Start log queue checker
        self.check_log_queue()
        
        self.log("=== Auto Job Applier Started ===")
        self.log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def setup_styles(self):
        """Configure ttk styles for modern look."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Define colors
        style.configure("TLabel", font=("Segoe UI", 9))
        style.configure("Title.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Heading.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 9))
        style.configure("Accent.TButton", font=("Segoe UI", 9, "bold"))
    
    def setup_ui(self):
        """Create the main GUI layout."""
        
        # Main container with paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ==================== LEFT PANEL - CONFIGURATION ====================
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Notebook (tabs) for different config sections
        config_notebook = ttk.Notebook(left_frame)
        config_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Job Search
        search_frame = ttk.Frame(config_notebook, padding="15")
        config_notebook.add(search_frame, text="Job Search")
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Job Title:", style="Heading.TLabel").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.job_title_var = tk.StringVar(value=search_terms[0] if search_terms else "Python Developer")
        ttk.Entry(search_frame, textvariable=self.job_title_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(search_frame, text="Location:", style="Heading.TLabel").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.location_var = tk.StringVar(value=search_location or "United States")
        ttk.Entry(search_frame, textvariable=self.location_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(search_frame, text="Max Applications:", style="Heading.TLabel").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.max_applications_var = tk.IntVar(value=50)
        ttk.Spinbox(search_frame, from_=1, to=500, textvariable=self.max_applications_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=10)
        
        # Tab 2: Credentials
        creds_frame = ttk.Frame(config_notebook, padding="15")
        config_notebook.add(creds_frame, text="Credentials")
        creds_frame.columnconfigure(1, weight=1)
        
        ttk.Label(creds_frame, text="LinkedIn Email:", style="Heading.TLabel").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.email_var = tk.StringVar(value=username or "")
        ttk.Entry(creds_frame, textvariable=self.email_var, width=30, show="*").grid(row=0, column=1, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(creds_frame, text="LinkedIn Password:", style="Heading.TLabel").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.password_var = tk.StringVar(value=password or "")
        ttk.Entry(creds_frame, textvariable=self.password_var, width=30, show="•").grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(creds_frame, text="Resume Path:", style="Heading.TLabel").grid(row=2, column=0, sticky=tk.W, pady=10)
        resume_frame = ttk.Frame(creds_frame)
        resume_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10)
        resume_frame.columnconfigure(0, weight=1)
        self.resume_var = tk.StringVar(value=default_resume_path or "")
        ttk.Entry(resume_frame, textvariable=self.resume_var, width=25).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(resume_frame, text="Browse...", command=self.browse_resume, width=10).grid(row=0, column=1, padx=(5, 0))
        
        # Tab 3: Settings
        settings_frame = ttk.Frame(config_notebook, padding="15")
        config_notebook.add(settings_frame, text="Settings")
        
        self.headless_var = tk.BooleanVar(value=run_in_background)
        ttk.Checkbutton(settings_frame, text="Run in Background (Headless Mode)", variable=self.headless_var).pack(anchor=tk.W, pady=8)
        
        self.stealth_var = tk.BooleanVar(value=stealth_mode)
        ttk.Checkbutton(settings_frame, text="Stealth Mode (Anti-Detection)", variable=self.stealth_var).pack(anchor=tk.W, pady=8)
        
        self.safe_mode_var = tk.BooleanVar(value=safe_mode)
        ttk.Checkbutton(settings_frame, text="Safe Mode (Guest Profile)", variable=self.safe_mode_var).pack(anchor=tk.W, pady=8)
        
        self.keep_awake_var = tk.BooleanVar(value=keep_screen_awake)
        ttk.Checkbutton(settings_frame, text="Keep Screen Awake", variable=self.keep_awake_var).pack(anchor=tk.W, pady=8)
        
        self.use_ai_var = tk.BooleanVar(value=use_AI)
        ttk.Checkbutton(settings_frame, text="Use AI for Resume Customization", variable=self.use_ai_var).pack(anchor=tk.W, pady=8)
        
        self.pause_submit_var = tk.BooleanVar(value=pause_before_submit)
        ttk.Checkbutton(settings_frame, text="Pause Before Submit", variable=self.pause_submit_var).pack(anchor=tk.W, pady=8)
        
        # Control Buttons Frame
        button_frame = ttk.LabelFrame(left_frame, text="Controls", padding="10")
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="▶ START", command=self.start_application, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=10)
        
        self.stop_button = ttk.Button(button_frame, text="⏹ STOP", command=self.stop_application, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=10)
        
        self.clear_button = ttk.Button(button_frame, text="🗑 CLEAR LOG", command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=10)
        
        # ==================== RIGHT PANEL - OUTPUT LOG ====================
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        log_label = ttk.Label(right_frame, text="Application Log", style="Heading.TLabel")
        log_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Scrolled text widget for logs
        self.output_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            height=30,
            width=70,
            font=("Consolas", 9),
            bg="#f0f0f0",
            fg="#000000"
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different log levels
        self.output_text.tag_configure("info", foreground="#0066cc")
        self.output_text.tag_configure("success", foreground="#00aa00")
        self.output_text.tag_configure("warning", foreground="#ff7700")
        self.output_text.tag_configure("error", foreground="#cc0000")
        self.output_text.tag_configure("debug", foreground="#888888")
        
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress_var = tk.IntVar(value=0)
        self.progress_label = ttk.Label(status_frame, text="0%")
        self.progress_label.pack(side=tk.RIGHT, padx=(10, 0))
    
    def log(self, message, level="info"):
        """Thread-safe logging with different levels."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        self.log_queue.put((formatted_msg, level))
    
    def check_log_queue(self):
        """Periodically check and process log queue."""
        try:
            while True:
                message, level = self.log_queue.get_nowait()
                self.output_text.insert(tk.END, message + "\n", level)
                self.output_text.see(tk.END)
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_log_queue)
    
    def browse_resume(self):
        """Open file dialog to select resume."""
        filename = filedialog.askopenfilename(
            title="Select Resume",
            filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx"), ("All files", "*.*")]
        )
        if filename:
            self.resume_var.set(filename)
            self.log(f"Resume selected: {filename}", "success")
    
    def start_application(self):
        """Start the job application process."""
        
        # Validation
        if not self.email_var.get():
            messagebox.showerror("Validation Error", "Please enter LinkedIn email!")
            return
        
        if not self.password_var.get():
            messagebox.showerror("Validation Error", "Please enter LinkedIn password!")
            return
        
        if not self.resume_var.get():
            messagebox.showerror("Validation Error", "Please select a resume!")
            return
        
        if not os.path.exists(self.resume_var.get()):
            messagebox.showerror("File Error", f"Resume file not found: {self.resume_var.get()}")
            return
        
        # Update UI state
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Running...")
        
        self.log("Starting job application process...", "info")
        self.log(f"Job Title: {self.job_title_var.get()}", "info")
        self.log(f"Location: {self.location_var.get()}", "info")
        
        # Run application in separate thread
        app_thread = threading.Thread(target=self.run_application, daemon=True)
        app_thread.start()
    
    def run_application(self):
        """Main application logic (runs in background thread)."""
        linkedin_session = None
        try:
            self.log("Validating configuration...", "info")
            validate_config()
            
            self.log("Opening Chrome browser...", "info")
            self.driver, self.wait, self.actions = open_browser()
            
            if self.driver is None:
                self.log("ERROR: Failed to open browser!", "error")
                self.status_var.set("Error - Browser initialization failed")
                return
            
            self.log("Browser opened successfully", "success")
            
            # Create LinkedIn session with logging callback
            linkedin_session = LinkedInSession(
                self.driver, 
                self.wait, 
                self.actions, 
                log_callback=self.log
            )
            
            # Login to LinkedIn
            self.log("Logging in to LinkedIn...", "info")
            if not linkedin_session.login(self.email_var.get(), self.password_var.get()):
                self.log("ERROR: Failed to login to LinkedIn!", "error")
                self.status_var.set("Error - Login failed")
                return
            
            self.log("Successfully logged in to LinkedIn!", "success")
            
            # Prepare form data
            form_data = {
                'job_title': self.job_title_var.get(),
                'location': self.location_var.get(),
                'resume_path': self.resume_var.get(),
            }
            
            # Run job search and application workflow
            self.log(f"Starting job search for: {self.job_title_var.get()} in {self.location_var.get()}", "info")
            
            stats = linkedin_session.run_search_and_apply(
                job_title=self.job_title_var.get(),
                location=self.location_var.get(),
                max_applications=self.max_applications_var.get(),
                form_data=form_data
            )
            
            # Show final statistics
            self.log(f"\n{'='*60}", "info")
            self.log("APPLICATION SESSION COMPLETED", "success")
            self.log(f"  Total Applied: {stats['applied']}", "success")
            self.log(f"  Failed: {stats['failed']}", "warning" if stats['failed'] > 0 else "success")
            self.log(f"  Skipped: {stats['skipped']}", "info")
            self.log(f"  Total Processed: {stats['total']}", "info")
            self.log(f"{'='*60}\n", "info")
            
            self.status_var.set(f"Completed - Applied: {stats['applied']}, Failed: {stats['failed']}, Skipped: {stats['skipped']}")
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}", "error")
            self.status_var.set("Error - See log for details")
            critical_error_log("In GUI Application", e)
        
        finally:
            self.log("Closing browser...", "info")
            if self.driver:
                try:
                    close_browser()
                    self.log("Browser closed successfully", "success")
                except Exception as e:
                    self.log(f"Error closing browser: {str(e)}", "warning")
            
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def stop_application(self):
        """Stop the running application."""
        self.is_running = False
        
        if self.driver:
            try:
                close_browser()
                self.log("Browser closed", "info")
            except Exception as e:
                self.log(f"Error closing browser: {str(e)}", "warning")
        
        self.status_var.set("Stopped by user")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("Application stopped!", "warning")
    
    def clear_log(self):
        """Clear the log output."""
        self.output_text.delete(1.0, tk.END)
        self.log("Log cleared", "debug")


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = JobApplicationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
