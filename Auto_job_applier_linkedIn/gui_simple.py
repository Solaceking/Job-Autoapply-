"""
LinkedIn Auto Job Applier - Simple, Stable GUI
Clean, functional interface that just works.
"""

import sys
import os
from pathlib import Path

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except Exception as e:
    print("PySide6 is not installed. Install it with: pip install PySide6")
    raise


class SimpleGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LinkedIn Auto Job Applier")
        self.resize(1000, 700)
        
        # State
        self.worker = None
        self.is_running = False
        
        # Setup UI
        self._setup_ui()
        self._apply_styles()
        
    def _setup_ui(self):
        """Create the UI layout"""
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title = QtWidgets.QLabel("LinkedIn Job Application Bot")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0a66c2;")
        main_layout.addWidget(title)
        
        # Tab widget for different sections
        tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(tabs)
        
        # Job Search Tab
        search_tab = self._create_search_tab()
        tabs.addTab(search_tab, "Job Search")
        
        # AI Config Tab
        ai_tab = self._create_ai_tab()
        tabs.addTab(ai_tab, "AI Configuration")
        
        # Logs Tab
        log_tab = self._create_log_tab()
        tabs.addTab(log_tab, "Activity Log")
        
    def _create_search_tab(self):
        """Create job search tab"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # Job Search Parameters
        params_group = QtWidgets.QGroupBox("Search Parameters")
        params_layout = QtWidgets.QFormLayout()
        
        self.job_keywords = QtWidgets.QLineEdit()
        self.job_keywords.setPlaceholderText("e.g., Python Developer, Software Engineer")
        params_layout.addRow("Job Keywords:", self.job_keywords)
        
        self.location = QtWidgets.QLineEdit()
        self.location.setPlaceholderText("e.g., Remote, New York, United States")
        params_layout.addRow("Location:", self.location)
        
        self.max_applications = QtWidgets.QSpinBox()
        self.max_applications.setRange(1, 100)
        self.max_applications.setValue(30)
        params_layout.addRow("Max Applications:", self.max_applications)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Control Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.start_btn = QtWidgets.QPushButton("▶ Start")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.clicked.connect(self._start_automation)
        
        self.stop_btn = QtWidgets.QPushButton("⏹ Stop")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_automation)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        layout.addLayout(button_layout)
        
        # Progress
        progress_group = QtWidgets.QGroupBox("Progress")
        progress_layout = QtWidgets.QVBoxLayout()
        
        stats_layout = QtWidgets.QHBoxLayout()
        
        self.applied_label = QtWidgets.QLabel("Applied: 0")
        self.failed_label = QtWidgets.QLabel("Failed: 0")
        self.skipped_label = QtWidgets.QLabel("Skipped: 0")
        
        stats_layout.addWidget(self.applied_label)
        stats_layout.addWidget(self.failed_label)
        stats_layout.addWidget(self.skipped_label)
        stats_layout.addStretch()
        
        progress_layout.addLayout(stats_layout)
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        layout.addStretch()
        return widget
    
    def _create_ai_tab(self):
        """Create AI configuration tab"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        
        ai_group = QtWidgets.QGroupBox("AI Settings")
        ai_layout = QtWidgets.QFormLayout()
        
        self.ai_enabled = QtWidgets.QCheckBox("Enable AI Features")
        self.ai_enabled.setChecked(True)
        ai_layout.addRow("", self.ai_enabled)
        
        self.ai_provider = QtWidgets.QComboBox()
        self.ai_provider.addItems([
            "Groq (Fast & Free)",
            "OpenAI (GPT)",
            "Google Gemini",
            "DeepSeek",
            "Anthropic Claude"
        ])
        self.ai_provider.currentTextChanged.connect(self._update_models)
        ai_layout.addRow("Provider:", self.ai_provider)
        
        self.ai_model = QtWidgets.QComboBox()
        ai_layout.addRow("Model:", self.ai_model)
        
        self.api_key = QtWidgets.QLineEdit()
        self.api_key.setEchoMode(QtWidgets.QLineEdit.Password)
        self.api_key.setPlaceholderText("Enter your API key")
        ai_layout.addRow("API Key:", self.api_key)
        
        save_btn = QtWidgets.QPushButton("Save AI Settings")
        save_btn.clicked.connect(self._save_ai_config)
        ai_layout.addRow("", save_btn)
        
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)
        
        # Load initial models
        self._update_models("Groq (Fast & Free)")
        
        layout.addStretch()
        return widget
    
    def _create_log_tab(self):
        """Create activity log tab"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        
        self.log_text = QtWidgets.QPlainTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        clear_btn = QtWidgets.QPushButton("Clear Log")
        clear_btn.clicked.connect(self.log_text.clear)
        layout.addWidget(clear_btn)
        
        return widget
    
    def _update_models(self, provider):
        """Update model dropdown based on provider"""
        models = {
            "Groq (Fast & Free)": ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"],
            "OpenAI (GPT)": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "Google Gemini": ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
            "DeepSeek": ["deepseek-chat", "deepseek-reasoner"],
            "Anthropic Claude": ["claude-3-7-sonnet", "claude-3-5-sonnet", "claude-3-haiku"]
        }
        
        self.ai_model.clear()
        self.ai_model.addItems(models.get(provider, ["custom-model"]))
        self._log(f"Loaded {self.ai_model.count()} models for {provider}")
    
    def _save_ai_config(self):
        """Save AI configuration"""
        try:
            from config import secrets
            
            secrets.use_AI = self.ai_enabled.isChecked()
            secrets.ai_provider = self.ai_provider.currentText().split()[0].lower()
            secrets.ai_model = self.ai_model.currentText()
            secrets.llm_api_key = self.api_key.text()
            
            # Save to file
            config_path = Path(__file__).parent / "config" / "secrets.py"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    content = f.read()
                
                # Update values (simple replacement)
                import re
                content = re.sub(r'use_AI\s*=\s*.*', f'use_AI = {secrets.use_AI}', content)
                content = re.sub(r'ai_provider\s*=\s*["\'].*["\']', f'ai_provider = "{secrets.ai_provider}"', content)
                content = re.sub(r'ai_model\s*=\s*["\'].*["\']', f'ai_model = "{secrets.ai_model}"', content)
                
                with open(config_path, 'w') as f:
                    f.write(content)
                
                self._log("✓ AI settings saved successfully", "success")
            else:
                self._log("⚠ Config file not found", "warning")
                
        except Exception as e:
            self._log(f"✗ Failed to save AI settings: {e}", "error")
    
    def _start_automation(self):
        """Start job automation"""
        if not self.job_keywords.text().strip():
            QtWidgets.QMessageBox.warning(self, "Missing Information", "Please enter job keywords")
            return
        
        if not self.location.text().strip():
            QtWidgets.QMessageBox.warning(self, "Missing Information", "Please enter location")
            return
        
        self.is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Reset stats
        self.applied_label.setText("Applied: 0")
        self.failed_label.setText("Failed: 0")
        self.skipped_label.setText("Skipped: 0")
        self.progress_bar.setValue(0)
        
        # Start worker thread
        self.worker = AutomationWorker(
            self.job_keywords.text(),
            self.location.text(),
            self.max_applications.value()
        )
        self.worker.log_signal.connect(self._on_log)
        self.worker.progress_signal.connect(self._on_progress)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.start()
        
        self._log(f"Starting: {self.job_keywords.text()} in {self.location.text()}")
    
    def _stop_automation(self):
        """Stop automation"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._log("Stopped by user")
    
    def _on_log(self, level, message):
        """Handle log messages"""
        self._log(message, level)
    
    def _on_progress(self, applied, failed, skipped, current_job):
        """Update progress"""
        self.applied_label.setText(f"Applied: {applied}")
        self.failed_label.setText(f"Failed: {failed}")
        self.skipped_label.setText(f"Skipped: {skipped}")
        
        total = applied + failed + skipped
        max_apps = self.max_applications.value()
        percent = int((total / max_apps) * 100) if max_apps > 0 else 0
        self.progress_bar.setValue(min(percent, 100))
        
        if current_job:
            self._log(f"Current: {current_job}")
    
    def _on_finished(self, stats):
        """Handle automation completion"""
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        self._log("Automation finished!", "success")
    
    def _log(self, message, level="info"):
        """Add log message"""
        # Safety check - log_text might not exist during initialization
        if not hasattr(self, 'log_text'):
            return
        
        timestamp = QtCore.QTime.currentTime().toString("HH:mm:ss")
        
        # Color coding
        if level == "error":
            color = "#d32f2f"
        elif level == "warning":
            color = "#f57c00"
        elif level == "success":
            color = "#388e3c"
        else:
            color = "#202124"
        
        formatted = f'<span style="color: #666;">[{timestamp}]</span> <span style="color: {color};">{message}</span>'
        self.log_text.appendHtml(formatted)
    
    def _apply_styles(self):
        """Apply stylesheet"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: #0a66c2;
            }
            QLineEdit, QSpinBox, QComboBox {
                padding: 8px;
                border: 1px solid #dadce0;
                border-radius: 4px;
                background-color: white;
                min-height: 25px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 2px solid #0a66c2;
            }
            QPushButton {
                background-color: #0a66c2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #004182;
            }
            QPushButton:disabled {
                background-color: #9e9e9e;
            }
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #0a66c2;
                border-radius: 3px;
            }
            QPlainTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
        """)


class AutomationWorker(QtCore.QThread):
    """Background worker for automation"""
    log_signal = QtCore.Signal(str, str)  # level, message
    progress_signal = QtCore.Signal(int, int, int, str)  # applied, failed, skipped, current_job
    finished_signal = QtCore.Signal(dict)
    
    def __init__(self, job_title, location, max_apps):
        super().__init__()
        self.job_title = job_title
        self.location = location
        self.max_apps = max_apps
    
    def run(self):
        """Run automation"""
        try:
            # Import here to ensure distutils shim runs first
            import modules.open_chrome as chrome_module
            from modules.automation_manager import LinkedInSession
            
            self.log_signal.emit("info", "Opening browser...")
            chrome_module.open_browser()
            
            driver = chrome_module.driver
            wait = chrome_module.wait
            actions = chrome_module.actions
            
            if not driver or not wait:
                self.log_signal.emit("error", "Browser failed to initialize")
                self.finished_signal.emit({})
                return
            
            session = LinkedInSession(driver, wait, actions, 
                                     log_callback=lambda msg: self.log_signal.emit("info", msg))
            
            # Progress callback
            def on_progress(applied, failed, skipped, current_job):
                self.progress_signal.emit(applied, failed, skipped, current_job)
            
            # Run automation
            stats = session.run_search_and_apply(
                self.job_title,
                self.location,
                self.max_apps,
                {}
            )
            
            self.finished_signal.emit(stats or {})
            
        except Exception as e:
            self.log_signal.emit("error", f"Worker exception: {e}")
            import traceback
            traceback.print_exc()
            self.finished_signal.emit({})


def main():
    """Launch the application"""
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = SimpleGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
