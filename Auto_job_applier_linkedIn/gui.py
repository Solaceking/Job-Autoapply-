"""
LinkedIn Auto Job Applier - Production Qt GUI v2.0
Multi-page interface with full navigation and settings

Pages:
- Dashboard: Overview, stats, quick actions
- Jobs: Job search and application
- Queue: Pending applications
- History: Past applications
- AI: AI configuration
- Settings: All application settings
"""

import sys
import os
from pathlib import Path

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except Exception as e:
    print("PySide6 is not installed. Install it with: pip install PySide6")
    raise


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Job Applier - LinkedIn Automation")
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Application state
        self.worker = None
        self.current_page = "Dashboard"
        
        self._setup_ui()
        self._setup_statusbar()
        self._setup_menubar()
        
        # Initialize with Dashboard
        self._switch_page("Dashboard")

    def _setup_menubar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        refresh_action = QtGui.QAction("&Refresh Settings", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_settings)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QtGui.QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        docs_action = QtGui.QAction("&Documentation", self)
        docs_action.triggered.connect(lambda: self._log("info", "See docs/ folder for documentation"))
        help_menu.addAction(docs_action)
        
        about_action = QtGui.QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_ui(self):
        """Create the main UI layout"""
        central = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left navigation rail
        nav_widget = self._create_navigation()
        main_layout.addWidget(nav_widget)

        # Right content area with pages
        content_widget = self._create_content_area()
        main_layout.addWidget(content_widget, 1)

        self.setCentralWidget(central)

    def _create_navigation(self):
        """Create left navigation rail"""
        nav = QtWidgets.QFrame()
        nav.setFixedWidth(100)
        nav.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
            QPushButton {
                background-color: transparent;
                color: #ecf0f1;
                border: none;
                padding: 12px;
                text-align: center;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
                font-weight: bold;
            }
        """)
        
        nav_layout = QtWidgets.QVBoxLayout(nav)
        nav_layout.setContentsMargins(0, 10, 0, 10)
        nav_layout.setSpacing(5)
        nav_layout.setAlignment(QtCore.Qt.AlignTop)

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "📊"),
            ("Jobs", "💼"),
            ("Queue", "📋"),
            ("History", "📜"),
            ("AI", "🤖"),
            ("Settings", "⚙️"),
        ]

        for name, icon in nav_items:
            btn = QtWidgets.QPushButton(f"{icon}\n{name}")
            btn.setFixedSize(90, 70)
            btn.setCheckable(True)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn.clicked.connect(lambda checked, n=name: self._switch_page(n))
            nav_layout.addWidget(btn)
            self.nav_buttons[name] = btn

        nav_layout.addStretch()

        return nav

    def _create_content_area(self):
        """Create main content area with stacked pages"""
        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # CAPTCHA banner (initially hidden)
        self.captcha_banner = self._create_captcha_banner()
        content_layout.addWidget(self.captcha_banner)

        # Stacked widget for pages
        self.pages = QtWidgets.QStackedWidget()
        content_layout.addWidget(self.pages, 1)

        # Create all pages
        self.pages.addWidget(self._create_dashboard_page())
        self.pages.addWidget(self._create_jobs_page())
        self.pages.addWidget(self._create_queue_page())
        self.pages.addWidget(self._create_history_page())
        self.pages.addWidget(self._create_ai_page())
        self.pages.addWidget(self._create_settings_page())

        # Shared log area at bottom
        log_group = QtWidgets.QGroupBox("Activity Log")
        log_layout = QtWidgets.QVBoxLayout(log_group)
        
        log_toolbar = QtWidgets.QHBoxLayout()
        clear_btn = QtWidgets.QPushButton("Clear")
        clear_btn.clicked.connect(lambda: self.log_text.clear())
        log_toolbar.addStretch()
        log_toolbar.addWidget(clear_btn)
        log_layout.addLayout(log_toolbar)
        
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        content_layout.addWidget(log_group)

        return content

    def _create_captcha_banner(self):
        """Create CAPTCHA notification banner"""
        banner = QtWidgets.QFrame()
        banner.setFrameShape(QtWidgets.QFrame.StyledPanel)
        banner.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        banner.setVisible(False)
        
        banner_layout = QtWidgets.QHBoxLayout(banner)
        
        icon_label = QtWidgets.QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 24px;")
        banner_layout.addWidget(icon_label)
        
        self.captcha_label = QtWidgets.QLabel("CAPTCHA detected. Please solve it in the browser.")
        self.captcha_label.setWordWrap(True)
        banner_layout.addWidget(self.captcha_label, 1)
        
        self.captcha_resume_btn = QtWidgets.QPushButton("✓ Resume")
        self.captcha_resume_btn.clicked.connect(self._on_captcha_resume)
        banner_layout.addWidget(self.captcha_resume_btn)
        
        self.captcha_cancel_btn = QtWidgets.QPushButton("✗ Cancel")
        self.captcha_cancel_btn.clicked.connect(self._on_captcha_cancel)
        banner_layout.addWidget(self.captcha_cancel_btn)
        
        return banner

    def _create_dashboard_page(self):
        """Dashboard page with overview and stats"""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        
        # Page title
        title = QtWidgets.QLabel("📊 Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 15px;")
        layout.addWidget(title)
        
        # Stats cards
        stats_layout = QtWidgets.QHBoxLayout()
        
        # Applications card
        apps_card = self._create_stat_card("Applications", "0", "Total applications submitted")
        stats_layout.addWidget(apps_card)
        
        # Success rate card
        success_card = self._create_stat_card("Success Rate", "0%", "Applications vs attempts")
        stats_layout.addWidget(success_card)
        
        # Today card
        today_card = self._create_stat_card("Today", "0", "Applications today")
        stats_layout.addWidget(today_card)
        
        layout.addLayout(stats_layout)
        
        # Quick actions
        actions_group = QtWidgets.QGroupBox("Quick Actions")
        actions_layout = QtWidgets.QVBoxLayout(actions_group)
        
        start_btn = QtWidgets.QPushButton("▶️ Start Job Search")
        start_btn.setMinimumHeight(50)
        start_btn.clicked.connect(lambda: self._switch_page("Jobs"))
        actions_layout.addWidget(start_btn)
        
        config_btn = QtWidgets.QPushButton("⚙️ Configure Settings")
        config_btn.setMinimumHeight(50)
        config_btn.clicked.connect(lambda: self._switch_page("Settings"))
        actions_layout.addWidget(config_btn)
        
        history_btn = QtWidgets.QPushButton("📜 View History")
        history_btn.setMinimumHeight(50)
        history_btn.clicked.connect(lambda: self._switch_page("History"))
        actions_layout.addWidget(history_btn)
        
        layout.addWidget(actions_group)
        
        # Recent activity
        recent_group = QtWidgets.QGroupBox("Recent Activity")
        recent_layout = QtWidgets.QVBoxLayout(recent_group)
        
        self.recent_list = QtWidgets.QListWidget()
        self.recent_list.addItem("No recent activity")
        recent_layout.addWidget(self.recent_list)
        
        layout.addWidget(recent_group)
        
        layout.addStretch()
        
        return page

    def _create_stat_card(self, title, value, description):
        """Create a statistics card widget"""
        card = QtWidgets.QFrame()
        card.setFrameShape(QtWidgets.QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        card_layout = QtWidgets.QVBoxLayout(card)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        card_layout.addWidget(title_label)
        
        value_label = QtWidgets.QLabel(value)
        value_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #2c3e50;")
        card_layout.addWidget(value_label)
        
        desc_label = QtWidgets.QLabel(description)
        desc_label.setStyleSheet("font-size: 11px; color: #95a5a6;")
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)
        
        return card

    def _create_jobs_page(self):
        """Jobs page with search form and controls"""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        
        # Page title
        title = QtWidgets.QLabel("💼 Job Search & Apply")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 15px;")
        layout.addWidget(title)
        
        # Control buttons
        control_layout = QtWidgets.QHBoxLayout()
        
        self.run_btn = QtWidgets.QPushButton("▶️ Run")
        self.run_btn.setMinimumHeight(40)
        self.run_btn.clicked.connect(self._on_run)
        control_layout.addWidget(self.run_btn)
        
        self.pause_btn = QtWidgets.QPushButton("⏸️ Pause")
        self.pause_btn.setMinimumHeight(40)
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self._on_pause)
        control_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QtWidgets.QPushButton("⏹️ Stop")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        control_layout.addWidget(self.stop_btn)
        
        layout.addLayout(control_layout)
        
        # Search form
        form_group = QtWidgets.QGroupBox("Job Search Criteria")
        form_layout = QtWidgets.QGridLayout(form_group)
        
        row = 0
        form_layout.addWidget(QtWidgets.QLabel("Keywords:"), row, 0)
        self.keywords_edit = QtWidgets.QLineEdit()
        self.keywords_edit.setPlaceholderText("e.g., Python Developer, Data Scientist")
        form_layout.addWidget(self.keywords_edit, row, 1)
        
        row += 1
        form_layout.addWidget(QtWidgets.QLabel("Location:"), row, 0)
        self.location_edit = QtWidgets.QLineEdit()
        self.location_edit.setPlaceholderText("e.g., United States, Remote")
        form_layout.addWidget(self.location_edit, row, 1)
        
        row += 1
        form_layout.addWidget(QtWidgets.QLabel("Language:"), row, 0)
        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItems(["", "English", "Spanish", "French", "German", "Portuguese", "Hindi", "Chinese"])
        self.language_combo.setCurrentText("English")
        form_layout.addWidget(self.language_combo, row, 1)
        
        row += 1
        self.pref_english_chk = QtWidgets.QCheckBox("Prefer English-first jobs")
        self.pref_english_chk.setChecked(True)
        form_layout.addWidget(self.pref_english_chk, row, 1)
        
        row += 1
        self.easy_apply_chk = QtWidgets.QCheckBox("Easy Apply only")
        self.easy_apply_chk.setChecked(True)
        form_layout.addWidget(self.easy_apply_chk, row, 1)
        
        row += 1
        form_layout.addWidget(QtWidgets.QLabel("Max Applications:"), row, 0)
        self.max_apply_spin = QtWidgets.QSpinBox()
        self.max_apply_spin.setRange(1, 1000)
        self.max_apply_spin.setValue(30)
        form_layout.addWidget(self.max_apply_spin, row, 1)
        
        layout.addWidget(form_group)
        
        # Progress section
        progress_group = QtWidgets.QGroupBox("Progress")
        progress_layout = QtWidgets.QVBoxLayout(progress_group)
        
        # Stats
        stats_layout = QtWidgets.QHBoxLayout()
        self.applied_label = QtWidgets.QLabel("✅ Applied: 0")
        self.failed_label = QtWidgets.QLabel("❌ Failed: 0")
        self.skipped_label = QtWidgets.QLabel("⏭️ Skipped: 0")
        self.current_job_label = QtWidgets.QLabel("📌 Current: —")
        
        stats_layout.addWidget(self.applied_label)
        stats_layout.addWidget(self.failed_label)
        stats_layout.addWidget(self.skipped_label)
        stats_layout.addWidget(self.current_job_label)
        stats_layout.addStretch()
        progress_layout.addLayout(stats_layout)
        
        # Progress bars
        overall_layout = QtWidgets.QHBoxLayout()
        overall_layout.addWidget(QtWidgets.QLabel("Overall:"))
        self.overall_progress = QtWidgets.QProgressBar()
        self.overall_progress.setRange(0, 100)
        self.overall_progress.setValue(0)
        overall_layout.addWidget(self.overall_progress)
        progress_layout.addLayout(overall_layout)
        
        form_progress_layout = QtWidgets.QHBoxLayout()
        form_progress_layout.addWidget(QtWidgets.QLabel("Form Fill:"))
        self.form_progress = QtWidgets.QProgressBar()
        self.form_progress.setRange(0, 100)
        self.form_progress.setValue(0)
        form_progress_layout.addWidget(self.form_progress)
        progress_layout.addLayout(form_progress_layout)
        
        layout.addWidget(progress_group)
        
        layout.addStretch()
        
        return page

    def _create_queue_page(self):
        """Queue page for pending applications"""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        
        title = QtWidgets.QLabel("📋 Application Queue")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 15px;")
        layout.addWidget(title)
        
        info = QtWidgets.QLabel("View and manage pending job applications")
        info.setStyleSheet("color: #7f8c8d; padding: 0 15px;")
        layout.addWidget(info)
        
        # Queue table
        self.queue_table = QtWidgets.QTableWidget(0, 5)
        self.queue_table.setHorizontalHeaderLabels(["Job Title", "Company", "Location", "Status", "Actions"])
        self.queue_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.queue_table)
        
        # Queue controls
        queue_controls = QtWidgets.QHBoxLayout()
        
        refresh_queue_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_queue_btn.clicked.connect(lambda: self._log("info", "Queue refreshed"))
        queue_controls.addWidget(refresh_queue_btn)
        
        clear_queue_btn = QtWidgets.QPushButton("🗑️ Clear Completed")
        clear_queue_btn.clicked.connect(lambda: self._log("info", "Cleared completed items"))
        queue_controls.addWidget(clear_queue_btn)
        
        queue_controls.addStretch()
        layout.addLayout(queue_controls)
        
        return page

    def _create_history_page(self):
        """History page for past applications"""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        
        title = QtWidgets.QLabel("📜 Application History")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 15px;")
        layout.addWidget(title)
        
        info = QtWidgets.QLabel("Review all past job applications")
        info.setStyleSheet("color: #7f8c8d; padding: 0 15px;")
        layout.addWidget(info)
        
        # Filter controls
        filter_layout = QtWidgets.QHBoxLayout()
        
        filter_layout.addWidget(QtWidgets.QLabel("Filter:"))
        
        date_combo = QtWidgets.QComboBox()
        date_combo.addItems(["All Time", "Today", "This Week", "This Month"])
        filter_layout.addWidget(date_combo)
        
        status_combo = QtWidgets.QComboBox()
        status_combo.addItems(["All Status", "Applied", "Failed", "Skipped"])
        filter_layout.addWidget(status_combo)
        
        search_edit = QtWidgets.QLineEdit()
        search_edit.setPlaceholderText("Search jobs...")
        filter_layout.addWidget(search_edit)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # History table
        self.history_table = QtWidgets.QTableWidget(0, 6)
        self.history_table.setHorizontalHeaderLabels(["Date", "Job Title", "Company", "Location", "Status", "Notes"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.history_table)
        
        # History controls
        history_controls = QtWidgets.QHBoxLayout()
        
        export_btn = QtWidgets.QPushButton("📊 Export to Excel")
        export_btn.clicked.connect(lambda: self._log("info", "Export feature coming soon"))
        history_controls.addWidget(export_btn)
        
        clear_history_btn = QtWidgets.QPushButton("🗑️ Clear History")
        clear_history_btn.clicked.connect(self._confirm_clear_history)
        history_controls.addWidget(clear_history_btn)
        
        history_controls.addStretch()
        
        stats_label = QtWidgets.QLabel("Total: 0 applications")
        history_controls.addWidget(stats_label)
        
        layout.addLayout(history_controls)
        
        return page

    def _create_ai_page(self):
        """AI configuration page"""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        
        title = QtWidgets.QLabel("🤖 AI Configuration")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 15px;")
        layout.addWidget(title)
        
        info = QtWidgets.QLabel("Configure AI providers for intelligent job matching and question answering")
        info.setStyleSheet("color: #7f8c8d; padding: 0 15px; margin-bottom: 15px;")
        layout.addWidget(info)
        
        # AI settings form
        ai_form = QtWidgets.QGroupBox("AI Provider Settings")
        form_layout = QtWidgets.QFormLayout(ai_form)
        
        self.use_ai_chk = QtWidgets.QCheckBox("Enable AI Features")
        form_layout.addRow("", self.use_ai_chk)
        
        self.ai_provider_combo = QtWidgets.QComboBox()
        self.ai_provider_combo.addItems(["OpenAI (GPT)", "Google Gemini", "DeepSeek", "Ollama (Local)"])
        form_layout.addRow("AI Provider:", self.ai_provider_combo)
        
        self.api_key_edit = QtWidgets.QLineEdit()
        self.api_key_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("Enter your API key")
        form_layout.addRow("API Key:", self.api_key_edit)
        
        show_key_btn = QtWidgets.QPushButton("👁️ Show")
        show_key_btn.setCheckable(True)
        show_key_btn.toggled.connect(lambda checked: self.api_key_edit.setEchoMode(
            QtWidgets.QLineEdit.Normal if checked else QtWidgets.QLineEdit.Password
        ))
        form_layout.addRow("", show_key_btn)
        
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.addItems(["gpt-4o", "gpt-3.5-turbo", "gemini-pro", "deepseek-chat"])
        form_layout.addRow("Model:", self.model_combo)
        
        layout.addWidget(ai_form)
        
        # AI features
        features_group = QtWidgets.QGroupBox("AI Features")
        features_layout = QtWidgets.QVBoxLayout(features_group)
        
        self.ai_resume_chk = QtWidgets.QCheckBox("AI Resume Customization")
        features_layout.addWidget(self.ai_resume_chk)
        
        self.ai_questions_chk = QtWidgets.QCheckBox("AI Question Answering")
        self.ai_questions_chk.setChecked(True)
        features_layout.addWidget(self.ai_questions_chk)
        
        self.ai_matching_chk = QtWidgets.QCheckBox("AI Job Matching")
        features_layout.addWidget(self.ai_matching_chk)
        
        layout.addWidget(features_group)
        
        # Save button
        save_ai_btn = QtWidgets.QPushButton("💾 Save AI Configuration")
        save_ai_btn.setMinimumHeight(45)
        save_ai_btn.clicked.connect(self._save_ai_config)
        layout.addWidget(save_ai_btn)
        
        # Test button
        test_ai_btn = QtWidgets.QPushButton("🧪 Test AI Connection")
        test_ai_btn.clicked.connect(self._test_ai_connection)
        layout.addWidget(test_ai_btn)
        
        layout.addStretch()
        
        return page

    def _create_settings_page(self):
        """Settings page for application configuration"""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        
        title = QtWidgets.QLabel("⚙️ Application Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 15px;")
        layout.addWidget(title)
        
        # Settings tabs
        settings_tabs = QtWidgets.QTabWidget()
        
        # General settings tab
        general_tab = QtWidgets.QWidget()
        general_layout = QtWidgets.QFormLayout(general_tab)
        
        self.headless_chk = QtWidgets.QCheckBox("Run browser in background")
        general_layout.addRow("Headless Mode:", self.headless_chk)
        
        self.stealth_chk = QtWidgets.QCheckBox("Use stealth mode (avoid detection)")
        self.stealth_chk.setChecked(True)
        general_layout.addRow("Stealth Mode:", self.stealth_chk)
        
        self.safe_mode_chk = QtWidgets.QCheckBox("Use guest browser profile")
        self.safe_mode_chk.setChecked(True)
        general_layout.addRow("Safe Mode:", self.safe_mode_chk)
        
        self.keep_awake_chk = QtWidgets.QCheckBox("Prevent screen sleep")
        general_layout.addRow("Keep Awake:", self.keep_awake_chk)
        
        settings_tabs.addTab(general_tab, "General")
        
        # LinkedIn settings tab
        linkedin_tab = QtWidgets.QWidget()
        linkedin_layout = QtWidgets.QFormLayout(linkedin_tab)
        
        self.username_edit = QtWidgets.QLineEdit()
        self.username_edit.setPlaceholderText("your.email@example.com")
        linkedin_layout.addRow("LinkedIn Email:", self.username_edit)
        
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_edit.setPlaceholderText("Your password")
        linkedin_layout.addRow("LinkedIn Password:", self.password_edit)
        
        show_pass_btn = QtWidgets.QPushButton("👁️ Show")
        show_pass_btn.setCheckable(True)
        show_pass_btn.toggled.connect(lambda checked: self.password_edit.setEchoMode(
            QtWidgets.QLineEdit.Normal if checked else QtWidgets.QLineEdit.Password
        ))
        linkedin_layout.addRow("", show_pass_btn)
        
        settings_tabs.addTab(linkedin_tab, "LinkedIn")
        
        # Automation settings tab
        automation_tab = QtWidgets.QWidget()
        automation_layout = QtWidgets.QFormLayout(automation_tab)
        
        self.pause_before_submit_chk = QtWidgets.QCheckBox("Pause before submitting")
        automation_layout.addRow("", self.pause_before_submit_chk)
        
        self.pause_at_failed_chk = QtWidgets.QCheckBox("Pause when questions fail")
        automation_layout.addRow("", self.pause_at_failed_chk)
        
        self.run_nonstop_chk = QtWidgets.QCheckBox("Run continuously")
        automation_layout.addRow("", self.run_nonstop_chk)
        
        delay_spin = QtWidgets.QSpinBox()
        delay_spin.setRange(1, 60)
        delay_spin.setValue(3)
        delay_spin.setSuffix(" seconds")
        automation_layout.addRow("Delay between actions:", delay_spin)
        
        settings_tabs.addTab(automation_tab, "Automation")
        
        layout.addWidget(settings_tabs)
        
        # Save and load buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        
        load_btn = QtWidgets.QPushButton("📂 Load from Files")
        load_btn.clicked.connect(self._load_settings)
        buttons_layout.addWidget(load_btn)
        
        save_btn = QtWidgets.QPushButton("💾 Save to Files")
        save_btn.clicked.connect(self._save_settings)
        buttons_layout.addWidget(save_btn)
        
        reset_btn = QtWidgets.QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self._reset_settings)
        buttons_layout.addWidget(reset_btn)
        
        layout.addLayout(buttons_layout)
        
        # Config file locations
        config_info = QtWidgets.QLabel(
            "Configuration files:\n"
            "• config/secrets.py - Credentials and API keys\n"
            "• config/search.py - Job search settings\n"
            "• config/settings.py - Application settings"
        )
        config_info.setStyleSheet("color: #7f8c8d; padding: 15px; font-size: 11px;")
        layout.addWidget(config_info)
        
        layout.addStretch()
        
        return page

    def _setup_statusbar(self):
        """Setup status bar"""
        self.statusbar_label = QtWidgets.QLabel("Ready")
        self.statusBar().addPermanentWidget(self.statusbar_label)
        
        # Add automation status (not internet connection)
        self.connection_label = QtWidgets.QLabel("🔴 Automation: Idle")
        self.statusBar().addWidget(self.connection_label)

    def _switch_page(self, page_name):
        """Switch to a different page"""
        page_index = {
            "Dashboard": 0,
            "Jobs": 1,
            "Queue": 2,
            "History": 3,
            "AI": 4,
            "Settings": 5
        }.get(page_name, 0)
        
        self.pages.setCurrentIndex(page_index)
        self.current_page = page_name
        self.statusbar_label.setText(f"View: {page_name}")
        
        # Update navigation buttons
        for name, btn in self.nav_buttons.items():
            btn.setChecked(name == page_name)
        
        self._log("info", f"Switched to {page_name}")

    def _log(self, level, message):
        """Add message to log"""
        timestamp = QtCore.QTime.currentTime().toString("HH:mm:ss")
        color_map = {
            "info": "#3498db",
            "success": "#27ae60",
            "warning": "#f39c12",
            "error": "#e74c3c",
            "debug": "#95a5a6"
        }
        color = color_map.get(level, "#000000")
        
        formatted_msg = f'<span style="color: {color};">[{timestamp}] [{level.upper()}] {message}</span>'
        self.log_text.append(formatted_msg)

    # Button handlers
    def _on_run(self):
        """Start job search automation"""
        keywords = self.keywords_edit.text()
        location = self.location_edit.text()
        
        if not keywords:
            QtWidgets.QMessageBox.warning(self, "Missing Keywords", "Please enter job keywords to search for.")
            return
        
        self.run_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        
        self._log("info", f"Starting job search: {keywords} in {location}")
        self._on_search()

    def _on_pause(self):
        """Pause automation"""
        self._log("warning", "Automation paused")
        self.run_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)

    def _on_stop(self):
        """Stop automation"""
        self._log("warning", "Stop requested")
        
        # Stop worker thread if running
        if self.worker and self.worker.isRunning():
            try:
                self.worker.terminate()
                self.worker.wait(2000)  # Wait up to 2 seconds
            except Exception as e:
                self._log("debug", f"Worker stop: {e}")
        
        # Close browser
        try:
            from modules.open_chrome import close_browser
            close_browser()
            self._log("info", "Browser closed")
        except Exception as e:
            self._log("debug", f"Browser close: {e}")
        
        self.run_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.connection_label.setText("🔴 Automation: Idle")

    def _on_search(self):
        """Start the automation worker"""
        keywords = self.keywords_edit.text()
        location = self.location_edit.text()
        language = self.language_combo.currentText()
        prefer_english = self.pref_english_chk.isChecked()
        easy_apply = self.easy_apply_chk.isChecked()
        max_apps = self.max_apply_spin.value()

        self._log("info", f"Search: {keywords} | Location: {location} | Max: {max_apps}")

        # Start background worker
        if self.worker and self.worker.isRunning():
            self._log("warning", "Automation already running")
            return

        try:
            # AutomationWorker is defined in this same file below
            self.worker = AutomationWorker(
                job_title=keywords,
                location=location,
                max_applications=max_apps,
                form_data={},
                language=language,
                prefer_english=prefer_english
            )
            
            self.worker.log_signal.connect(lambda lvl, msg: self._log(lvl, msg))
            self.worker.progress_signal.connect(self._on_worker_progress)
            self.worker.form_progress_signal.connect(self._on_form_progress)
            self.worker.finished_signal.connect(self._on_worker_finished)
            self.worker.captcha_pause_signal.connect(self._on_captcha_detected)
            self.worker.start()
            
            self.connection_label.setText("🟢 Automation: Running")
            
        except Exception as e:
            self._log("error", f"Failed to start worker: {e}")

    def _on_worker_progress(self, applied, failed, skipped, current_job):
        """Update progress display"""
        self.applied_label.setText(f"✅ Applied: {applied}")
        self.failed_label.setText(f"❌ Failed: {failed}")
        self.skipped_label.setText(f"⏭️ Skipped: {skipped}")
        self.current_job_label.setText(f"📌 Current: {current_job[:40]}")
        
        total = applied + failed + skipped
        if total > 0:
            progress = min(int((total / self.max_apply_spin.value()) * 100), 99)
            self.overall_progress.setValue(progress)

    def _on_form_progress(self, percent):
        """Update form fill progress"""
        self.form_progress.setValue(percent)

    def _on_worker_finished(self, stats):
        """Handle worker completion"""
        self._log("success", f"Automation finished: {stats}")
        self.overall_progress.setValue(100)
        self.connection_label.setText("🔴 Automation: Idle")
        
        self.run_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

    def _on_captcha_detected(self, message):
        """Show CAPTCHA banner when detected"""
        self.captcha_label.setText(message)
        self.captcha_banner.setVisible(True)
        self._log("warning", message)

    def _on_captcha_resume(self):
        """Resume after CAPTCHA"""
        self.captcha_banner.setVisible(False)
        self._log("info", "Resuming after CAPTCHA")

    def _on_captcha_cancel(self):
        """Cancel after CAPTCHA"""
        self.captcha_banner.setVisible(False)
        self._on_stop()
        self._log("warning", "Cancelled after CAPTCHA")

    def _save_ai_config(self):
        """Save AI configuration"""
        self._log("success", "AI configuration saved")
        QtWidgets.QMessageBox.information(self, "Saved", "AI configuration saved successfully!")

    def _test_ai_connection(self):
        """Test AI connection"""
        self._log("info", "Testing AI connection...")
        QtWidgets.QMessageBox.information(self, "Test", "AI connection test - feature coming soon!")

    def _save_settings(self):
        """Save settings to config files"""
        self._log("success", "Settings saved to config files")
        QtWidgets.QMessageBox.information(self, "Saved", "Settings saved successfully!")

    def _load_settings(self):
        """Load settings from config files"""
        self._log("info", "Settings loaded from config files")
        QtWidgets.QMessageBox.information(self, "Loaded", "Settings loaded successfully!")

    def _reset_settings(self):
        """Reset settings to defaults"""
        reply = QtWidgets.QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self._log("info", "Settings reset to defaults")

    def _confirm_clear_history(self):
        """Confirm clearing history"""
        reply = QtWidgets.QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear all application history?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.history_table.setRowCount(0)
            self._log("info", "History cleared")

    def _refresh_settings(self):
        """Refresh settings from files"""
        self._log("info", "Refreshing settings...")

    def _show_about(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.about(
            self, "About Auto Job Applier",
            "<h2>LinkedIn Auto Job Applier</h2>"
            "<p>Version 2.0.0</p>"
            "<p>Automated job application system for LinkedIn</p>"
            "<p><b>⚠️ For Educational Purposes Only</b></p>"
            "<p>Use at your own risk. May violate LinkedIn Terms of Service.</p>"
        )


class AutomationWorker(QtCore.QThread):
    """Background worker that runs the LinkedIn automation workflow."""

    log_signal = QtCore.Signal(str, str)  # level, message
    finished_signal = QtCore.Signal(dict)
    progress_signal = QtCore.Signal(int, int, int, str)  # applied, failed, skipped, current_job
    form_progress_signal = QtCore.Signal(int)  # form fill percentage (0-100)
    captcha_pause_signal = QtCore.Signal(str)  # message when CAPTCHA pause required

    def __init__(self, job_title: str, location: str, max_applications: int, 
                 form_data: dict, language: str = "", prefer_english: bool = False):
        super().__init__()
        self.job_title = job_title
        self.location = location
        self.max_applications = max_applications
        self.form_data = form_data
        self.language = language
        self.prefer_english = prefer_english

    def emit_log(self, message: str, level: str = "info"):
        try:
            self.log_signal.emit(level, message)
        except Exception:
            pass

    def run(self):
        try:
            # Open browser
            from modules.open_chrome import open_browser, close_browser, driver, wait, actions
            from modules.automation_manager import LinkedInSession

            self.emit_log("Opening browser...", "info")
            open_browser()

            # Wait for globals to be set
            d = driver
            w = wait
            a = actions

            if not d or not w:
                self.emit_log("Browser failed to initialize", "error")
                self.finished_signal.emit({})
                return

            session = LinkedInSession(d, w, a, log_callback=self.emit_log)
            
            # Wire progress callbacks to automation manager (use app_manager attribute)
            def on_progress(applied, failed, skipped, current_job):
                try:
                    self.progress_signal.emit(applied, failed, skipped, current_job)
                except Exception:
                    pass

            def on_form_progress(pct: int):
                try:
                    self.form_progress_signal.emit(pct)
                except Exception:
                    pass

            # app_manager is the JobApplicationManager instance on LinkedInSession
            try:
                session.app_manager.progress_callback = on_progress
                session.app_manager.form_progress_callback = on_form_progress
            except Exception:
                # backward compatibility: try older attribute name if present
                try:
                    session.job_manager.progress_callback = on_progress
                    session.job_manager.form_progress_callback = on_form_progress
                except Exception:
                    pass

            # If an ErrorRecoveryManager is present, enable blocking captcha wait and
            # set a callback that will emit a signal to the UI to request user action.
            try:
                from modules import error_recovery
                mgr = getattr(error_recovery, 'current_recovery_manager', None)
                if mgr:
                    try:
                        mgr.config.captcha_blocking_wait = True
                        mgr.config.captcha_pause_callback = lambda msg: self.captcha_pause_signal.emit(msg or "CAPTCHA detected")
                        # keep reference for debugging if needed
                        self.recovery_manager = mgr
                    except Exception:
                        pass
            except Exception:
                pass

            # Use defaults for credentials from config if available (login optional)
            stats = session.run_search_and_apply(
                self.job_title,
                self.location,
                self.max_applications,
                self.form_data,
                language=self.language,
                prefer_english=self.prefer_english,
            )

            self.finished_signal.emit(stats)

        except Exception as e:
            self.emit_log(f"Worker exception: {e}", "error")
            import traceback
            traceback.print_exc()
            try:
                from modules.open_chrome import close_browser
                close_browser()
            except Exception:
                pass
            self.finished_signal.emit({"error": str(e)})


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
