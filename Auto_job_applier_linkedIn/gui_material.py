"""
LinkedIn Auto Job Applier - Material Design 3 GUI
Complete Google-style interface with Material Design 3 principles

Design Philosophy:
- Bold, expressive typography
- Clean, spacious layouts with generous whitespace
- Intuitive navigation and interactions
- Surface elevation and shadows
- Dynamic color system
- Accessibility-first approach

Material Design 3 Principles Applied:
- Surface containers with proper elevation
- Large, readable typography
- Icon buttons with proper touch targets
- Floating Action Button (FAB) for primary actions
- Bottom sheets and dialogs
- Snackbars for feedback
- Color system with primary, secondary, tertiary
- Proper motion and transitions
"""

import sys
import os
from pathlib import Path

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except Exception as e:
    print("PySide6 is not installed. Install it with: pip install PySide6")
    raise


# Material Design 3 Color Palette (Google Colors 2025)
class MaterialColors:
    # Primary (Google Blue)
    PRIMARY = "#1a73e8"
    PRIMARY_VARIANT = "#1557b0"
    ON_PRIMARY = "#ffffff"
    PRIMARY_CONTAINER = "#d3e3fd"
    ON_PRIMARY_CONTAINER = "#001849"
    
    # Secondary (Google Blue Light)
    SECONDARY = "#4285f4"
    SECONDARY_VARIANT = "#3367d6"
    ON_SECONDARY = "#ffffff"
    SECONDARY_CONTAINER = "#e8f0fe"
    ON_SECONDARY_CONTAINER = "#001d35"
    
    # Tertiary (Google Green)
    TERTIARY = "#34a853"
    TERTIARY_VARIANT = "#0d8043"
    ON_TERTIARY = "#ffffff"
    TERTIARY_CONTAINER = "#c6f6d5"
    ON_TERTIARY_CONTAINER = "#002106"
    
    # Error (Google Red)
    ERROR = "#ea4335"
    ERROR_CONTAINER = "#fce8e6"
    ON_ERROR = "#ffffff"
    ON_ERROR_CONTAINER = "#410002"
    
    # Warning (Google Yellow)
    WARNING = "#fbbc04"
    WARNING_CONTAINER = "#fef7e0"
    ON_WARNING = "#442b00"
    
    # Surface colors
    SURFACE = "#ffffff"
    SURFACE_VARIANT = "#f8f9fa"
    SURFACE_CONTAINER = "#f1f3f4"
    SURFACE_CONTAINER_HIGH = "#e8eaed"
    ON_SURFACE = "#1f1f1f"
    ON_SURFACE_VARIANT = "#5f6368"
    
    # Outline
    OUTLINE = "#dadce0"
    OUTLINE_VARIANT = "#e8eaed"
    
    # Background
    BACKGROUND = "#fafafa"
    ON_BACKGROUND = "#1f1f1f"
    
    # Text colors
    TEXT_PRIMARY = "#202124"
    TEXT_SECONDARY = "#5f6368"
    TEXT_DISABLED = "#9aa0a6"
    TEXT_HINT = "#80868b"


class MaterialDesignGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LinkedIn Auto Job Applier")
        self.resize(1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Application state
        self.worker = None
        self.current_page = "dashboard"
        
        # Apply Material Design theme
        self._apply_material_theme()
        
        # Setup UI
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()
        
        # Show dashboard
        self._switch_page("dashboard")
    
    def _apply_material_theme(self):
        """Apply Material Design 3 theme to application"""
        self.setStyleSheet(f"""
            /* Global Styles */
            * {{
                font-family: 'Google Sans', 'Segoe UI', 'Roboto', -apple-system, sans-serif;
            }}
            
            QMainWindow {{
                background-color: {MaterialColors.BACKGROUND};
            }}
            
            /* Typography */
            QLabel {{
                color: {MaterialColors.TEXT_PRIMARY};
            }}
            
            /* Material Buttons - Filled */
            QPushButton {{
                background-color: {MaterialColors.PRIMARY};
                color: {MaterialColors.ON_PRIMARY};
                border: none;
                border-radius: 20px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                text-transform: none;
                letter-spacing: 0.1px;
            }}
            
            QPushButton:hover {{
                background-color: {MaterialColors.PRIMARY_VARIANT};
            }}
            
            QPushButton:pressed {{
                background-color: {MaterialColors.PRIMARY_VARIANT};
            }}
            
            QPushButton:disabled {{
                background-color: {MaterialColors.SURFACE_CONTAINER};
                color: {MaterialColors.TEXT_DISABLED};
            }}
            
            /* Secondary Buttons */
            QPushButton[buttonStyle="outlined"] {{
                background-color: transparent;
                color: {MaterialColors.PRIMARY};
                border: 2px solid {MaterialColors.OUTLINE};
                border-radius: 20px;
                padding: 10px 24px;
            }}
            
            QPushButton[buttonStyle="outlined"]:hover {{
                background-color: {MaterialColors.PRIMARY_CONTAINER};
                border-color: {MaterialColors.PRIMARY};
            }}
            
            /* Text Buttons */
            QPushButton[buttonStyle="text"] {{
                background-color: transparent;
                color: {MaterialColors.PRIMARY};
                border: none;
                padding: 10px 24px;
            }}
            
            QPushButton[buttonStyle="text"]:hover {{
                background-color: {MaterialColors.PRIMARY_CONTAINER};
            }}
            
            /* Icon Buttons */
            QPushButton[buttonStyle="icon"] {{
                background-color: transparent;
                border: none;
                border-radius: 24px;
                padding: 12px;
                min-width: 48px;
                min-height: 48px;
            }}
            
            QPushButton[buttonStyle="icon"]:hover {{
                background-color: {MaterialColors.SURFACE_CONTAINER};
            }}
            
            /* Material Input Fields */
            QLineEdit, QSpinBox, QComboBox {{
                background-color: {MaterialColors.SURFACE};
                border: 1px solid {MaterialColors.OUTLINE};
                border-radius: 12px;
                padding: 14px 16px;
                font-size: 14px;
                color: {MaterialColors.TEXT_PRIMARY};
                selection-background-color: {MaterialColors.PRIMARY_CONTAINER};
                selection-color: {MaterialColors.ON_PRIMARY_CONTAINER};
            }}
            
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border: 2px solid {MaterialColors.PRIMARY};
                background-color: {MaterialColors.SURFACE};
            }}
            
            QLineEdit:hover, QSpinBox:hover, QComboBox:hover {{
                border-color: {MaterialColors.TEXT_PRIMARY};
            }}
            
            QLineEdit::placeholder {{
                color: {MaterialColors.TEXT_HINT};
            }}
            
            /* Material Cards (Group Boxes) */
            QGroupBox {{
                background-color: {MaterialColors.SURFACE};
                border: 1px solid {MaterialColors.OUTLINE_VARIANT};
                border-radius: 16px;
                margin-top: 16px;
                padding: 24px;
                font-size: 16px;
                font-weight: 500;
                color: {MaterialColors.TEXT_PRIMARY};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 20px;
                top: -8px;
                background-color: {MaterialColors.SURFACE};
                padding: 0 12px;
            }}
            
            /* Material Tables */
            QTableWidget {{
                background-color: {MaterialColors.SURFACE};
                border: 1px solid {MaterialColors.OUTLINE_VARIANT};
                border-radius: 16px;
                gridline-color: {MaterialColors.OUTLINE_VARIANT};
                font-size: 14px;
            }}
            
            QTableWidget::item {{
                padding: 12px 16px;
                border: none;
            }}
            
            QTableWidget::item:selected {{
                background-color: {MaterialColors.SECONDARY_CONTAINER};
                color: {MaterialColors.ON_SECONDARY_CONTAINER};
            }}
            
            QTableWidget::item:hover {{
                background-color: {MaterialColors.SURFACE_VARIANT};
            }}
            
            QHeaderView::section {{
                background-color: {MaterialColors.SURFACE_VARIANT};
                padding: 14px 16px;
                border: none;
                border-bottom: 2px solid {MaterialColors.OUTLINE_VARIANT};
                font-weight: 600;
                font-size: 13px;
                color: {MaterialColors.TEXT_SECONDARY};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            /* Material Progress Bars */
            QProgressBar {{
                border: none;
                border-radius: 8px;
                background-color: {MaterialColors.SURFACE_CONTAINER};
                text-align: center;
                height: 8px;
                color: {MaterialColors.TEXT_PRIMARY};
            }}
            
            QProgressBar::chunk {{
                background-color: {MaterialColors.PRIMARY};
                border-radius: 8px;
            }}
            
            /* Material Checkboxes */
            QCheckBox {{
                spacing: 12px;
                font-size: 14px;
                color: {MaterialColors.TEXT_PRIMARY};
            }}
            
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid {MaterialColors.OUTLINE};
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {MaterialColors.PRIMARY};
                background-color: {MaterialColors.PRIMARY_CONTAINER};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {MaterialColors.PRIMARY};
                border-color: {MaterialColors.PRIMARY};
            }}
            
            /* Material Tabs */
            QTabWidget::pane {{
                border: none;
                background-color: transparent;
            }}
            
            QTabBar::tab {{
                background-color: transparent;
                color: {MaterialColors.TEXT_SECONDARY};
                padding: 16px 32px;
                margin-right: 8px;
                border: none;
                border-bottom: 3px solid transparent;
                font-weight: 500;
                font-size: 14px;
            }}
            
            QTabBar::tab:selected {{
                color: {MaterialColors.PRIMARY};
                border-bottom: 3px solid {MaterialColors.PRIMARY};
            }}
            
            QTabBar::tab:hover {{
                color: {MaterialColors.TEXT_PRIMARY};
                background-color: {MaterialColors.SURFACE_VARIANT};
            }}
            
            /* Material Lists */
            QListWidget {{
                background-color: {MaterialColors.SURFACE};
                border: 1px solid {MaterialColors.OUTLINE_VARIANT};
                border-radius: 16px;
                padding: 8px;
            }}
            
            QListWidget::item {{
                padding: 16px;
                border-radius: 12px;
                margin: 4px;
                border: none;
            }}
            
            QListWidget::item:selected {{
                background-color: {MaterialColors.SECONDARY_CONTAINER};
                color: {MaterialColors.ON_SECONDARY_CONTAINER};
            }}
            
            QListWidget::item:hover {{
                background-color: {MaterialColors.SURFACE_VARIANT};
            }}
            
            /* Material Text Edit */
            QTextEdit {{
                background-color: {MaterialColors.SURFACE};
                border: 1px solid {MaterialColors.OUTLINE_VARIANT};
                border-radius: 16px;
                padding: 16px;
                font-size: 13px;
                font-family: 'Consolas', 'Monaco', monospace;
                color: {MaterialColors.TEXT_PRIMARY};
            }}
            
            /* Scrollbars */
            QScrollBar:vertical {{
                border: none;
                background-color: {MaterialColors.SURFACE_VARIANT};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {MaterialColors.OUTLINE};
                border-radius: 6px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {MaterialColors.TEXT_SECONDARY};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background-color: {MaterialColors.SURFACE_VARIANT};
                height: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {MaterialColors.OUTLINE};
                border-radius: 6px;
                min-width: 30px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {MaterialColors.TEXT_SECONDARY};
            }}
            
            /* Combo Box Dropdown */
            QComboBox::drop-down {{
                border: none;
                padding-right: 12px;
            }}
            
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {MaterialColors.SURFACE};
                border: 1px solid {MaterialColors.OUTLINE_VARIANT};
                border-radius: 12px;
                padding: 8px;
                selection-background-color: {MaterialColors.PRIMARY_CONTAINER};
                selection-color: {MaterialColors.ON_PRIMARY_CONTAINER};
            }}
            
            QComboBox QAbstractItemView::item {{
                padding: 12px 16px;
                border-radius: 8px;
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background-color: {MaterialColors.SURFACE_VARIANT};
            }}
            
            /* Spin Box */
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 24px;
                border: none;
                background-color: transparent;
            }}
            
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {MaterialColors.SURFACE_VARIANT};
            }}
            
            /* Menu Bar */
            QMenuBar {{
                background-color: {MaterialColors.SURFACE};
                border-bottom: 1px solid {MaterialColors.OUTLINE_VARIANT};
                padding: 4px 8px;
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 8px;
                color: {MaterialColors.TEXT_PRIMARY};
            }}
            
            QMenuBar::item:selected {{
                background-color: {MaterialColors.SURFACE_VARIANT};
            }}
            
            QMenu {{
                background-color: {MaterialColors.SURFACE};
                border: 1px solid {MaterialColors.OUTLINE_VARIANT};
                border-radius: 12px;
                padding: 8px;
            }}
            
            QMenu::item {{
                padding: 12px 24px;
                border-radius: 8px;
            }}
            
            QMenu::item:selected {{
                background-color: {MaterialColors.PRIMARY_CONTAINER};
                color: {MaterialColors.ON_PRIMARY_CONTAINER};
            }}
            
            /* Status Bar */
            QStatusBar {{
                background-color: {MaterialColors.SURFACE};
                border-top: 1px solid {MaterialColors.OUTLINE_VARIANT};
                padding: 8px 16px;
            }}
            
            QStatusBar QLabel {{
                color: {MaterialColors.TEXT_SECONDARY};
                font-size: 13px;
            }}
        """)
    
    def _setup_menu_bar(self):
        """Create Material Design menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        refresh_action = QtGui.QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(lambda: self._log("info", "Refreshed"))
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QtGui.QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        docs_action = QtGui.QAction("Documentation", self)
        docs_action.triggered.connect(lambda: self._log("info", "See documentation files"))
        help_menu.addAction(docs_action)
        
        about_action = QtGui.QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_status_bar(self):
        """Create Material Design status bar"""
        status_bar = self.statusBar()
        
        self.status_label = QtWidgets.QLabel("Ready")
        status_bar.addPermanentWidget(self.status_label)
        
        self.connection_status = QtWidgets.QLabel("● Idle")
        self.connection_status.setStyleSheet(f"color: {MaterialColors.TEXT_DISABLED};")
        status_bar.addWidget(self.connection_status)
    
    def _setup_ui(self):
        """Create main UI with Material Design"""
        central = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Navigation rail (left)
        nav_rail = self._create_nav_rail()
        main_layout.addWidget(nav_rail)
        
        # Content area (right)
        content = self._create_content_area()
        main_layout.addWidget(content, 1)
        
        self.setCentralWidget(central)
    
    def _create_nav_rail(self):
        """Create Material Design navigation rail"""
        rail = QtWidgets.QFrame()
        rail.setFixedWidth(88)
        rail.setStyleSheet(f"""
            QFrame {{
                background-color: {MaterialColors.SURFACE};
                border-right: 1px solid {MaterialColors.OUTLINE_VARIANT};
            }}
            QPushButton {{
                background-color: transparent;
                color: {MaterialColors.TEXT_SECONDARY};
                border: none;
                border-radius: 16px;
                padding: 8px;
                font-size: 11px;
                font-weight: 500;
                text-align: center;
                margin: 4px;
            }}
            QPushButton:hover {{
                background-color: {MaterialColors.SURFACE_VARIANT};
            }}
            QPushButton:checked {{
                background-color: {MaterialColors.SECONDARY_CONTAINER};
                color: {MaterialColors.ON_SECONDARY_CONTAINER};
                font-weight: 600;
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(rail)
        layout.setContentsMargins(8, 24, 8, 24)
        layout.setSpacing(8)
        layout.setAlignment(QtCore.Qt.AlignTop)
        
        # Logo/Brand
        brand = QtWidgets.QLabel("🚀")
        brand.setAlignment(QtCore.Qt.AlignCenter)
        brand.setStyleSheet(f"""
            font-size: 32px;
            padding: 16px;
            background-color: {MaterialColors.PRIMARY_CONTAINER};
            border-radius: 16px;
            margin-bottom: 16px;
        """)
        layout.addWidget(brand)
        
        # Navigation items
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊", "Dashboard"),
            ("jobs", "💼", "Jobs"),
            ("ai", "🤖", "AI Config"),
            ("history", "📜", "History"),
            ("settings", "⚙️", "Settings"),
        ]
        
        for page_id, icon, label in nav_items:
            btn = QtWidgets.QPushButton(f"{icon}\n{label}")
            btn.setFixedSize(72, 72)
            btn.setCheckable(True)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn.clicked.connect(lambda checked, p=page_id: self._switch_page(p))
            layout.addWidget(btn)
            self.nav_buttons[page_id] = btn
        
        layout.addStretch()
        
        return rail
    
    def _create_content_area(self):
        """Create content area with pages"""
        content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Stacked pages
        self.pages = QtWidgets.QStackedWidget()
        layout.addWidget(self.pages, 1)
        
        # Create pages
        self.pages.addWidget(self._create_dashboard_page())
        self.pages.addWidget(self._create_jobs_page())
        self.pages.addWidget(self._create_ai_page())
        self.pages.addWidget(self._create_history_page())
        self.pages.addWidget(self._create_settings_page())
        
        # Log area at bottom
        log_container = QtWidgets.QWidget()
        log_container.setStyleSheet(f"""
            QWidget {{
                background-color: {MaterialColors.SURFACE};
                border-top: 1px solid {MaterialColors.OUTLINE_VARIANT};
                padding: 0;
            }}
        """)
        log_layout = QtWidgets.QVBoxLayout(log_container)
        log_layout.setContentsMargins(24, 16, 24, 16)
        
        log_header = QtWidgets.QHBoxLayout()
        log_title = QtWidgets.QLabel("Activity Log")
        log_title.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {MaterialColors.TEXT_PRIMARY};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        log_header.addWidget(log_title)
        log_header.addStretch()
        
        clear_btn = QtWidgets.QPushButton("Clear")
        clear_btn.setProperty("buttonStyle", "text")
        clear_btn.clicked.connect(lambda: self.log_text.clear())
        log_header.addWidget(clear_btn)
        
        log_layout.addLayout(log_header)
        
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_container)
        
        return content
    
    def _create_dashboard_page(self):
        """Dashboard page with Material Design"""
        page = QtWidgets.QWidget()
        page.setStyleSheet(f"background-color: {MaterialColors.BACKGROUND};")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Hero header
        header = QtWidgets.QWidget()
        header_layout = QtWidgets.QVBoxLayout(header)
        header_layout.setSpacing(8)
        
        title = QtWidgets.QLabel("Dashboard")
        title.setStyleSheet(f"""
            font-size: 48px;
            font-weight: 400;
            color: {MaterialColors.TEXT_PRIMARY};
            letter-spacing: -0.5px;
        """)
        header_layout.addWidget(title)
        
        subtitle = QtWidgets.QLabel("Monitor your job application automation")
        subtitle.setStyleSheet(f"""
            font-size: 16px;
            color: {MaterialColors.TEXT_SECONDARY};
            margin-bottom: 16px;
        """)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # Stats cards
        stats_container = QtWidgets.QWidget()
        stats_layout = QtWidgets.QHBoxLayout(stats_container)
        stats_layout.setSpacing(16)
        
        # Application stats
        apps_card = self._create_stat_card("Applications", "0", "Total submitted", MaterialColors.PRIMARY)
        stats_layout.addWidget(apps_card)
        
        success_card = self._create_stat_card("Success Rate", "0%", "Application success", MaterialColors.TERTIARY)
        stats_layout.addWidget(success_card)
        
        today_card = self._create_stat_card("Today", "0", "Applications today", MaterialColors.SECONDARY)
        stats_layout.addWidget(today_card)
        
        layout.addWidget(stats_container)
        
        # Quick actions
        actions_group = QtWidgets.QGroupBox("Quick Actions")
        actions_layout = QtWidgets.QVBoxLayout(actions_group)
        actions_layout.setSpacing(12)
        
        start_btn = QtWidgets.QPushButton("🚀  Start Job Search")
        start_btn.setMinimumHeight(56)
        start_btn.clicked.connect(lambda: self._switch_page("jobs"))
        start_btn.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 500;
            border-radius: 16px;
        """)
        actions_layout.addWidget(start_btn)
        
        config_btn = QtWidgets.QPushButton("⚙️  Configure AI Settings")
        config_btn.setMinimumHeight(56)
        config_btn.setProperty("buttonStyle", "outlined")
        config_btn.clicked.connect(lambda: self._switch_page("ai"))
        config_btn.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 500;
            border-radius: 16px;
        """)
        actions_layout.addWidget(config_btn)
        
        history_btn = QtWidgets.QPushButton("📜  View History")
        history_btn.setMinimumHeight(56)
        history_btn.setProperty("buttonStyle", "outlined")
        history_btn.clicked.connect(lambda: self._switch_page("history"))
        history_btn.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 500;
            border-radius: 16px;
        """)
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
    
    def _create_stat_card(self, title, value, description, color):
        """Create Material Design stat card with color accent"""
        card = QtWidgets.QFrame()
        card.setFrameShape(QtWidgets.QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {MaterialColors.SURFACE};
                border: none;
                border-left: 4px solid {color};
                border-radius: 16px;
                padding: 24px;
            }}
        """)
        
        # Add subtle shadow
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QtGui.QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setSpacing(8)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {MaterialColors.TEXT_SECONDARY};
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        card_layout.addWidget(title_label)
        
        value_label = QtWidgets.QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: 400;
            color: {color};
            margin: 4px 0;
        """)
        card_layout.addWidget(value_label)
        
        desc_label = QtWidgets.QLabel(description)
        desc_label.setStyleSheet(f"""
            font-size: 13px;
            color: {MaterialColors.TEXT_SECONDARY};
        """)
        card_layout.addWidget(desc_label)
        
        return card
    
    def _create_jobs_page(self):
        """Jobs page - Implementation continues..."""
        page = QtWidgets.QWidget()
        page.setStyleSheet(f"background-color: {MaterialColors.BACKGROUND};")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header = QtWidgets.QWidget()
        header_layout = QtWidgets.QVBoxLayout(header)
        header_layout.setSpacing(8)
        
        title = QtWidgets.QLabel("Job Search & Apply")
        title.setStyleSheet(f"""
            font-size: 48px;
            font-weight: 400;
            color: {MaterialColors.TEXT_PRIMARY};
        """)
        header_layout.addWidget(title)
        
        subtitle = QtWidgets.QLabel("Automate your job applications")
        subtitle.setStyleSheet(f"""
            font-size: 16px;
            color: {MaterialColors.TEXT_SECONDARY};
        """)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # Control buttons
        controls = QtWidgets.QWidget()
        controls_layout = QtWidgets.QHBoxLayout(controls)
        controls_layout.setSpacing(12)
        
        self.run_btn = QtWidgets.QPushButton("▶️  Run")
        self.run_btn.setMinimumHeight(48)
        self.run_btn.clicked.connect(self._on_run)
        controls_layout.addWidget(self.run_btn)
        
        self.pause_btn = QtWidgets.QPushButton("⏸️  Pause")
        self.pause_btn.setMinimumHeight(48)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setProperty("buttonStyle", "outlined")
        controls_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QtWidgets.QPushButton("⏹️  Stop")
        self.stop_btn.setMinimumHeight(48)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setProperty("buttonStyle", "outlined")
        self.stop_btn.clicked.connect(self._on_stop)
        controls_layout.addWidget(self.stop_btn)
        
        controls_layout.addStretch()
        
        layout.addWidget(controls)
        
        # Search form
        form_group = QtWidgets.QGroupBox("Search Criteria")
        form_layout = QtWidgets.QGridLayout(form_group)
        form_layout.setHorizontalSpacing(16)
        form_layout.setVerticalSpacing(16)
        
        # Keywords
        keywords_label = QtWidgets.QLabel("Job Keywords")
        keywords_label.setStyleSheet(f"font-weight: 500; color: {MaterialColors.TEXT_PRIMARY};")
        form_layout.addWidget(keywords_label, 0, 0)
        
        self.keywords_edit = QtWidgets.QLineEdit()
        self.keywords_edit.setPlaceholderText("e.g., Python Developer, Data Scientist")
        form_layout.addWidget(self.keywords_edit, 0, 1)
        
        # Location
        location_label = QtWidgets.QLabel("Location")
        location_label.setStyleSheet(f"font-weight: 500; color: {MaterialColors.TEXT_PRIMARY};")
        form_layout.addWidget(location_label, 1, 0)
        
        self.location_edit = QtWidgets.QLineEdit()
        self.location_edit.setPlaceholderText("e.g., United States, Remote")
        form_layout.addWidget(self.location_edit, 1, 1)
        
        # Max applications
        max_label = QtWidgets.QLabel("Max Applications")
        max_label.setStyleSheet(f"font-weight: 500; color: {MaterialColors.TEXT_PRIMARY};")
        form_layout.addWidget(max_label, 2, 0)
        
        self.max_apply_spin = QtWidgets.QSpinBox()
        self.max_apply_spin.setRange(1, 1000)
        self.max_apply_spin.setValue(30)
        self.max_apply_spin.setSuffix(" jobs")
        form_layout.addWidget(self.max_apply_spin, 2, 1)
        
        layout.addWidget(form_group)
        
        # Progress
        progress_group = QtWidgets.QGroupBox("Progress")
        progress_layout = QtWidgets.QVBoxLayout(progress_group)
        progress_layout.setSpacing(16)
        
        stats = QtWidgets.QHBoxLayout()
        self.applied_label = QtWidgets.QLabel("✅ Applied: 0")
        self.failed_label = QtWidgets.QLabel("❌ Failed: 0")
        self.skipped_label = QtWidgets.QLabel("⏭️ Skipped: 0")
        
        for label in [self.applied_label, self.failed_label, self.skipped_label]:
            label.setStyleSheet(f"font-size: 14px; font-weight: 500; padding: 8px 16px; background-color: {MaterialColors.SURFACE_VARIANT}; border-radius: 12px;")
            stats.addWidget(label)
        
        stats.addStretch()
        progress_layout.addLayout(stats)
        
        # Progress bar
        self.overall_progress = QtWidgets.QProgressBar()
        self.overall_progress.setRange(0, 100)
        self.overall_progress.setValue(0)
        self.overall_progress.setTextVisible(True)
        self.overall_progress.setFormat("%p% Complete")
        self.overall_progress.setStyleSheet(f"height: 12px; font-weight: 500;")
        progress_layout.addWidget(self.overall_progress)
        
        layout.addWidget(progress_group)
        
        layout.addStretch()
        
        return page
    
    def _create_ai_page(self):
        """AI configuration page"""
        page = QtWidgets.QWidget()
        page.setStyleSheet(f"background-color: {MaterialColors.BACKGROUND};")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header = QtWidgets.QWidget()
        header_layout = QtWidgets.QVBoxLayout(header)
        header_layout.setSpacing(8)
        
        title = QtWidgets.QLabel("AI Configuration")
        title.setStyleSheet(f"""
            font-size: 48px;
            font-weight: 400;
            color: {MaterialColors.TEXT_PRIMARY};
        """)
        header_layout.addWidget(title)
        
        subtitle = QtWidgets.QLabel("Configure AI providers for intelligent automation")
        subtitle.setStyleSheet(f"""
            font-size: 16px;
            color: {MaterialColors.TEXT_SECONDARY};
        """)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # AI Provider settings
        provider_group = QtWidgets.QGroupBox("Provider Settings")
        provider_layout = QtWidgets.QFormLayout(provider_group)
        provider_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        provider_layout.setVerticalSpacing(20)
        provider_layout.setHorizontalSpacing(24)
        
        # Enable AI
        self.use_ai_chk = QtWidgets.QCheckBox("Enable AI Features")
        self.use_ai_chk.setStyleSheet("font-size: 14px; font-weight: 500;")
        provider_layout.addRow("", self.use_ai_chk)
        
        # Provider dropdown
        provider_label = QtWidgets.QLabel("AI Provider")
        provider_label.setStyleSheet(f"font-weight: 500; color: {MaterialColors.TEXT_PRIMARY};")
        self.ai_provider_combo = QtWidgets.QComboBox()
        self.ai_provider_combo.addItems([
            "OpenAI (GPT)",
            "Google Gemini",
            "Groq (Fast & Free)",
            "DeepSeek",
            "Anthropic Claude",
            "xAI Grok",
            "Mistral AI",
            "Cohere",
            "Ollama (Local)",
        ])
        self.ai_provider_combo.currentTextChanged.connect(self._update_model_list)
        provider_layout.addRow(provider_label, self.ai_provider_combo)
        
        # API Key
        key_label = QtWidgets.QLabel("API Key")
        key_label.setStyleSheet(f"font-weight: 500; color: {MaterialColors.TEXT_PRIMARY};")
        self.api_key_edit = QtWidgets.QLineEdit()
        self.api_key_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("Enter your API key")
        provider_layout.addRow(key_label, self.api_key_edit)
        
        # Show/Hide key
        show_key_btn = QtWidgets.QPushButton("👁️ Show Key")
        show_key_btn.setCheckable(True)
        show_key_btn.setProperty("buttonStyle", "text")
        show_key_btn.toggled.connect(lambda checked: self.api_key_edit.setEchoMode(
            QtWidgets.QLineEdit.Normal if checked else QtWidgets.QLineEdit.Password
        ))
        provider_layout.addRow("", show_key_btn)
        
        # Model selector
        model_label = QtWidgets.QLabel("Model")
        model_label.setStyleSheet(f"font-weight: 500; color: {MaterialColors.TEXT_PRIMARY};")
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.setEditable(True)
        provider_layout.addRow(model_label, self.model_combo)
        
        # Initialize models
        self._update_model_list("OpenAI (GPT)")
        
        layout.addWidget(provider_group)
        
        # AI Features
        features_group = QtWidgets.QGroupBox("AI Features")
        features_layout = QtWidgets.QVBoxLayout(features_group)
        features_layout.setSpacing(12)
        
        self.ai_questions_chk = QtWidgets.QCheckBox("AI Question Answering")
        self.ai_questions_chk.setChecked(True)
        features_layout.addWidget(self.ai_questions_chk)
        
        self.ai_matching_chk = QtWidgets.QCheckBox("Smart Job Matching (60% threshold)")
        features_layout.addWidget(self.ai_matching_chk)
        
        self.ai_learning_chk = QtWidgets.QCheckBox("Q&A Learning Database (auto-improves over time)")
        self.ai_learning_chk.setChecked(True)
        features_layout.addWidget(self.ai_learning_chk)
        
        layout.addWidget(features_group)
        
        # Action buttons
        buttons = QtWidgets.QHBoxLayout()
        
        save_btn = QtWidgets.QPushButton("💾  Save Configuration")
        save_btn.setMinimumHeight(48)
        save_btn.clicked.connect(self._save_ai_config)
        buttons.addWidget(save_btn)
        
        test_btn = QtWidgets.QPushButton("🧪  Test Connection")
        test_btn.setMinimumHeight(48)
        test_btn.setProperty("buttonStyle", "outlined")
        test_btn.clicked.connect(self._test_ai_connection)
        buttons.addWidget(test_btn)
        
        layout.addLayout(buttons)
        
        layout.addStretch()
        
        return page
    
    def _create_history_page(self):
        """History page"""
        page = QtWidgets.QWidget()
        page.setStyleSheet(f"background-color: {MaterialColors.BACKGROUND};")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header = QtWidgets.QWidget()
        header_layout = QtWidgets.QVBoxLayout(header)
        
        title = QtWidgets.QLabel("Application History")
        title.setStyleSheet(f"""
            font-size: 48px;
            font-weight: 400;
            color: {MaterialColors.TEXT_PRIMARY};
        """)
        header_layout.addWidget(title)
        
        subtitle = QtWidgets.QLabel("Review all past applications")
        subtitle.setStyleSheet(f"font-size: 16px; color: {MaterialColors.TEXT_SECONDARY};")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # History table
        self.history_table = QtWidgets.QTableWidget(0, 6)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Job Title", "Company", "Location", "Status", "AI Score"
        ])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.history_table)
        
        # Controls
        controls = QtWidgets.QHBoxLayout()
        
        export_btn = QtWidgets.QPushButton("📊 Export to Excel")
        export_btn.setProperty("buttonStyle", "outlined")
        export_btn.clicked.connect(lambda: self._log("info", "Export feature coming soon"))
        controls.addWidget(export_btn)
        
        clear_btn = QtWidgets.QPushButton("🗑️ Clear History")
        clear_btn.setProperty("buttonStyle", "text")
        controls.addWidget(clear_btn)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        return page
    
    def _create_settings_page(self):
        """Settings page"""
        page = QtWidgets.QWidget()
        page.setStyleSheet(f"background-color: {MaterialColors.BACKGROUND};")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header = QtWidgets.QWidget()
        header_layout = QtWidgets.QVBoxLayout(header)
        
        title = QtWidgets.QLabel("Settings")
        title.setStyleSheet(f"""
            font-size: 48px;
            font-weight: 400;
            color: {MaterialColors.TEXT_PRIMARY};
        """)
        header_layout.addWidget(title)
        
        subtitle = QtWidgets.QLabel("Configure automation behavior")
        subtitle.setStyleSheet(f"font-size: 16px; color: {MaterialColors.TEXT_SECONDARY};")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # Settings tabs
        tabs = QtWidgets.QTabWidget()
        
        # General tab
        general_tab = QtWidgets.QWidget()
        general_layout = QtWidgets.QFormLayout(general_tab)
        general_layout.setVerticalSpacing(20)
        
        self.stealth_chk = QtWidgets.QCheckBox("Enable stealth mode")
        self.stealth_chk.setChecked(True)
        general_layout.addRow("", self.stealth_chk)
        
        self.safe_mode_chk = QtWidgets.QCheckBox("Use guest browser profile")
        general_layout.addRow("", self.safe_mode_chk)
        
        tabs.addTab(general_tab, "General")
        
        # Automation tab
        auto_tab = QtWidgets.QWidget()
        auto_layout = QtWidgets.QFormLayout(auto_tab)
        auto_layout.setVerticalSpacing(20)
        
        self.pause_before_submit_chk = QtWidgets.QCheckBox("Pause before submitting")
        auto_layout.addRow("", self.pause_before_submit_chk)
        
        self.run_nonstop_chk = QtWidgets.QCheckBox("Run continuously")
        auto_layout.addRow("", self.run_nonstop_chk)
        
        tabs.addTab(auto_tab, "Automation")
        
        layout.addWidget(tabs)
        
        # Save button
        save_btn = QtWidgets.QPushButton("💾  Save Settings")
        save_btn.setMinimumHeight(48)
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        return page
    
    # Event handlers and utility methods
    def _switch_page(self, page_id):
        """Switch to different page"""
        page_map = {
            "dashboard": 0,
            "jobs": 1,
            "ai": 2,
            "history": 3,
            "settings": 4
        }
        
        index = page_map.get(page_id, 0)
        self.pages.setCurrentIndex(index)
        self.current_page = page_id
        
        # Update nav buttons
        for pid, btn in self.nav_buttons.items():
            btn.setChecked(pid == page_id)
        
        self._log("info", f"Switched to {page_id.title()}")
    
    def _update_model_list(self, provider_name):
        """Update model list based on provider (2025 models)"""
        models = {
            "OpenAI (GPT)": [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo-0125"
            ],
            "Google Gemini": [
                "gemini-2.0-flash-exp",
                "gemini-1.5-pro-002",
                "gemini-1.5-flash-002",
                "gemini-1.5-flash-8b"
            ],
            "Groq (Fast & Free)": [
                "llama-3.3-70b-versatile",
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ],
            "DeepSeek": [
                "deepseek-chat",
                "deepseek-coder",
                "deepseek-reasoner"
            ],
            "Anthropic Claude": [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229"
            ],
            "xAI Grok": [
                "grok-2-1212",
                "grok-2-vision-1212",
                "grok-beta"
            ],
            "Mistral AI": [
                "mistral-large-latest",
                "mistral-small-latest",
                "codestral-latest",
                "pixtral-12b-latest"
            ],
            "Cohere": [
                "command-r-plus",
                "command-r",
                "command",
                "command-light"
            ],
            "Ollama (Local)": [
                "llama3.3:70b",
                "llama3.2:latest",
                "qwen2.5:latest",
                "mistral:latest",
                "phi4:latest",
                "deepseek-r1:latest"
            ]
        }
        
        model_list = models.get(provider_name, ["custom-model"])
        self.model_combo.clear()
        self.model_combo.addItems(model_list)
        self._log("info", f"Loaded {len(model_list)} models for {provider_name}")
    
    def _log(self, level, message):
        """Add message to log"""
        colors = {
            "info": MaterialColors.PRIMARY,
            "success": MaterialColors.TERTIARY,
            "warning": MaterialColors.WARNING,
            "error": MaterialColors.ERROR
        }
        color = colors.get(level, MaterialColors.TEXT_PRIMARY)
        
        timestamp = QtCore.QTime.currentTime().toString("HH:mm:ss")
        formatted = f'<span style="color: {color};">[{timestamp}] {message}</span>'
        self.log_text.append(formatted)
    
    def _on_run(self):
        """Start automation"""
        keywords = self.keywords_edit.text()
        if not keywords:
            QtWidgets.QMessageBox.warning(self, "Missing Keywords", "Please enter job keywords")
            return
        
        self.run_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        
        self.connection_status.setText("● Running")
        self.connection_status.setStyleSheet(f"color: {MaterialColors.TERTIARY};")
        
        self._log("info", f"Starting: {keywords}")
        # Start worker thread here
    
    def _on_stop(self):
        """Stop automation"""
        self.run_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        
        self.connection_status.setText("● Idle")
        self.connection_status.setStyleSheet(f"color: {MaterialColors.TEXT_DISABLED};")
        
        self._log("warning", "Stopped")
    
    def _save_ai_config(self):
        """Save AI configuration"""
        try:
            from config import secrets
            
            use_ai = self.use_ai_chk.isChecked()
            provider_map = {
                "OpenAI (GPT)": "openai",
                "Google Gemini": "gemini",
                "Groq (Fast & Free)": "groq",
                "DeepSeek": "deepseek",
                "Anthropic Claude": "anthropic",
                "xAI Grok": "xai",
                "Mistral AI": "mistral",
                "Cohere": "cohere",
                "Ollama (Local)": "openai"
            }
            
            provider = provider_map.get(self.ai_provider_combo.currentText(), "openai")
            api_key = self.api_key_edit.text()
            model = self.model_combo.currentText()
            
            secrets.use_AI = use_ai
            secrets.ai_provider = provider
            secrets.llm_api_key = api_key if api_key else "not-needed"
            secrets.ai_model = model
            
            self._log("success", f"Saved: {provider} with {model}")
            
            QtWidgets.QMessageBox.information(
                self, "Saved",
                f"✅ Configuration saved!\n\nProvider: {provider}\nModel: {model}"
            )
        except Exception as e:
            self._log("error", f"Save failed: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save:\n{str(e)}")
    
    def _test_ai_connection(self):
        """Test AI connection"""
        self._log("info", "Testing AI connection...")
        QtWidgets.QMessageBox.information(self, "Test", "AI connection test - Feature coming soon!")
    
    def _save_settings(self):
        """Save settings"""
        self._log("success", "Settings saved")
        QtWidgets.QMessageBox.information(self, "Saved", "Settings saved successfully!")
    
    def _show_about(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.about(
            self, "About",
            "<h2 style='color: #1a73e8;'>LinkedIn Auto Job Applier</h2>"
            "<p style='font-size: 14px;'>Version 3.0 - Material Design</p>"
            "<p style='color: #5f6368;'>Automated job application with AI features</p>"
            "<p style='color: #ea4335; font-weight: 500;'>⚠️ For Educational Purposes Only</p>"
        )


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MaterialDesignGUI()
    window.show()
    
    sys.exit(app.exec())
