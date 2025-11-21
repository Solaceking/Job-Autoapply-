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
import subprocess
import platform
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


class QADatabaseDialog(QtWidgets.QDialog):
    """Dialog for viewing and editing Q&A database entries"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Q&A Database Manager")
        self.resize(1200, 700)
        self.setMinimumSize(900, 600)
        
        # Initialize database
        from modules.qa_database import QADatabase
        self.qa_db = QADatabase()
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QtWidgets.QLabel("Question & Answer Database")
        header.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 400;
            color: {MaterialColors.TEXT_PRIMARY};
            margin-bottom: 8px;
        """)
        layout.addWidget(header)
        
        subtitle = QtWidgets.QLabel("View, edit, and manage stored questions and answers")
        subtitle.setStyleSheet(f"font-size: 14px; color: {MaterialColors.TEXT_SECONDARY};")
        layout.addWidget(subtitle)
        
        # Search bar
        search_container = QtWidgets.QHBoxLayout()
        search_label = QtWidgets.QLabel("Search:")
        search_label.setStyleSheet(f"font-size: 14px; color: {MaterialColors.TEXT_SECONDARY};")
        search_container.addWidget(search_label)
        
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("Search questions or answers...")
        self.search_box.textChanged.connect(self._filter_table)
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e5e7eb;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1a73e8;
            }
        """)
        search_container.addWidget(self.search_box)
        layout.addLayout(search_container)
        
        # Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Question", "Answer", "Job Title", "Company", "Times Used", "Last Used", "Actions"
        ])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                gridline-color: #f3f4f6;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QHeaderView::section {
                background-color: #f9fafb;
                color: #374151;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
            }
            QTableWidget::item:alternate {
                background-color: #f9fafb;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
        """)
        layout.addWidget(self.table)
        
        # Stats label
        self.stats_label = QtWidgets.QLabel()
        self.stats_label.setStyleSheet(f"font-size: 13px; color: {MaterialColors.TEXT_SECONDARY};")
        layout.addWidget(self.stats_label)
        
        # Bottom buttons
        buttons = QtWidgets.QHBoxLayout()
        
        refresh_btn = QtWidgets.QPushButton("REFRESH")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.clicked.connect(self._load_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 20px;
                font-size: 13px;
                font-weight: 600;
                text-transform: uppercase;
            }
            QPushButton:hover { background-color: #4f46e5; }
            QPushButton:pressed { background-color: #4338ca; }
        """)
        buttons.addWidget(refresh_btn)
        
        export_btn = QtWidgets.QPushButton("EXPORT TO CSV")
        export_btn.setMinimumHeight(40)
        export_btn.clicked.connect(self._export_to_csv)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 20px;
                font-size: 13px;
                font-weight: 600;
                text-transform: uppercase;
            }
            QPushButton:hover { background-color: #059669; }
            QPushButton:pressed { background-color: #047857; }
        """)
        buttons.addWidget(export_btn)
        
        buttons.addStretch()
        
        close_btn = QtWidgets.QPushButton("CLOSE")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 20px;
                font-size: 13px;
                font-weight: 600;
                text-transform: uppercase;
            }
            QPushButton:hover { background-color: #4b5563; }
            QPushButton:pressed { background-color: #374151; }
        """)
        buttons.addWidget(close_btn)
        
        layout.addLayout(buttons)
    
    def _load_data(self):
        """Load data from Q&A database"""
        try:
            questions = self.qa_db.get_all_questions(limit=1000)
            self.all_data = questions  # Store for filtering
            self._populate_table(questions)
            self.stats_label.setText(f"📊 Total entries: {len(questions)}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to load Q&A database:\n{str(e)}")
    
    def _populate_table(self, questions):
        """Populate table with question data"""
        self.table.setRowCount(len(questions))
        
        for row, q in enumerate(questions):
            # Question
            question_item = QtWidgets.QTableWidgetItem(q.get('question', '')[:100])
            question_item.setToolTip(q.get('question', ''))
            self.table.setItem(row, 0, question_item)
            
            # Answer
            answer_item = QtWidgets.QTableWidgetItem(q.get('answer', '')[:100])
            answer_item.setToolTip(q.get('answer', ''))
            self.table.setItem(row, 1, answer_item)
            
            # Job Title
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(q.get('job_title', '')))
            
            # Company
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(q.get('company', '')))
            
            # Times Used
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(q.get('times_used', 0))))
            
            # Last Used
            last_used = q.get('last_used', '')
            if last_used:
                # Format timestamp
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(last_used)
                    last_used = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            self.table.setItem(row, 5, QtWidgets.QTableWidgetItem(last_used))
            
            # Actions - Edit button
            edit_btn = QtWidgets.QPushButton("EDIT")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #2563eb; }
            """)
            edit_btn.clicked.connect(lambda checked, r=row, data=q: self._edit_entry(data))
            self.table.setCellWidget(row, 6, edit_btn)
    
    def _filter_table(self, text):
        """Filter table based on search text"""
        if not hasattr(self, 'all_data'):
            return
        
        if not text:
            self._populate_table(self.all_data)
            return
        
        text_lower = text.lower()
        filtered = [
            q for q in self.all_data
            if text_lower in q.get('question', '').lower() or 
               text_lower in q.get('answer', '').lower() or
               text_lower in q.get('job_title', '').lower() or
               text_lower in q.get('company', '').lower()
        ]
        self._populate_table(filtered)
        self.stats_label.setText(f"📊 Showing {len(filtered)} of {len(self.all_data)} entries")
    
    def _edit_entry(self, data):
        """Edit a Q&A entry"""
        dialog = EditQADialog(data, self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # Get updated values
            updated = dialog.get_values()
            # Update database
            self.qa_db.store_question(
                updated['question'],
                updated['answer'],
                updated.get('job_title', ''),
                updated.get('company', ''),
                updated.get('job_context', '')
            )
            # Reload data
            self._load_data()
            QtWidgets.QMessageBox.information(self, "Success", "Entry updated successfully!")
    
    def _export_to_csv(self):
        """Export Q&A database to CSV"""
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Q&A Database",
            "qa_database_export.csv",
            "CSV Files (*.csv);;All Files (*.*)"
        )
        if file_path:
            if self.qa_db.export_to_csv(file_path):
                QtWidgets.QMessageBox.information(
                    self,
                    "Success",
                    f"Q&A Database exported successfully to:\n{file_path}"
                )
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to export Q&A database"
                )


class EditQADialog(QtWidgets.QDialog):
    """Dialog for editing a single Q&A entry"""
    
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Edit Q&A Entry")
        self.resize(600, 500)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the edit dialog UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Question
        layout.addWidget(QtWidgets.QLabel("Question:"))
        self.question_edit = QtWidgets.QTextEdit()
        self.question_edit.setPlainText(self.data.get('question', ''))
        self.question_edit.setMaximumHeight(100)
        self.question_edit.setStyleSheet("padding: 8px; border: 2px solid #e5e7eb; border-radius: 4px;")
        layout.addWidget(self.question_edit)
        
        # Answer
        layout.addWidget(QtWidgets.QLabel("Answer:"))
        self.answer_edit = QtWidgets.QTextEdit()
        self.answer_edit.setPlainText(self.data.get('answer', ''))
        self.answer_edit.setMaximumHeight(100)
        self.answer_edit.setStyleSheet("padding: 8px; border: 2px solid #e5e7eb; border-radius: 4px;")
        layout.addWidget(self.answer_edit)
        
        # Job Title
        layout.addWidget(QtWidgets.QLabel("Job Title (optional):"))
        self.job_title_edit = QtWidgets.QLineEdit(self.data.get('job_title', ''))
        self.job_title_edit.setStyleSheet("padding: 8px; border: 2px solid #e5e7eb; border-radius: 4px;")
        layout.addWidget(self.job_title_edit)
        
        # Company
        layout.addWidget(QtWidgets.QLabel("Company (optional):"))
        self.company_edit = QtWidgets.QLineEdit(self.data.get('company', ''))
        self.company_edit.setStyleSheet("padding: 8px; border: 2px solid #e5e7eb; border-radius: 4px;")
        layout.addWidget(self.company_edit)
        
        # Buttons
        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("CANCEL")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #4b5563; }
        """)
        buttons.addWidget(cancel_btn)
        
        save_btn = QtWidgets.QPushButton("SAVE")
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        buttons.addWidget(save_btn)
        
        layout.addLayout(buttons)
    
    def get_values(self):
        """Get updated values from form"""
        return {
            'question': self.question_edit.toPlainText(),
            'answer': self.answer_edit.toPlainText(),
            'job_title': self.job_title_edit.text(),
            'company': self.company_edit.text(),
            'job_context': self.data.get('job_context', '')
        }


class MaterialDesignGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ApplyFlow - AI-Powered Job Application Automation")
        self.resize(1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Application state
        self.worker = None
        self.current_page = "dashboard"
        
        # Statistics tracking
        self.stats = {
            "total_applied": 0,
            "total_failed": 0,
            "total_skipped": 0,
            "today_applied": 0
        }
        
        # Apply Material Design theme
        self._apply_material_theme()
        
        # Setup UI
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()
        
        # Load saved personal information
        self._load_personal_settings()
        
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
                min-height: 24px;
                selection-background-color: {MaterialColors.PRIMARY_CONTAINER};
                selection-color: {MaterialColors.ON_PRIMARY_CONTAINER};
            }}
            
            QComboBox {{
                min-height: 28px;
                padding: 16px 16px;
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
            
            /* ComboBox Text Color */
            QComboBox {{
                color: {MaterialColors.TEXT_PRIMARY};
            }}
            
            /* Material Cards (Group Boxes) */
            QGroupBox {{
                background-color: {MaterialColors.SURFACE};
                border: 1px solid {MaterialColors.OUTLINE_VARIANT};
                border-radius: 16px;
                margin-top: 20px;
                padding: 24px;
                font-size: 16px;
                font-weight: 500;
                color: {MaterialColors.TEXT_PRIMARY};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 20px;
                top: 8px;
                background-color: {MaterialColors.SURFACE};
                padding: 4px 12px;
                color: {MaterialColors.TEXT_PRIMARY};
            }}
            
            /* Fix for labels inside GroupBox */
            QGroupBox QLabel {{
                background-color: transparent;
                color: {MaterialColors.TEXT_PRIMARY};
            }}
            
            /* Fix for widgets inside GroupBox */
            QGroupBox QCheckBox {{
                background-color: transparent;
                color: {MaterialColors.TEXT_PRIMARY};
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
        """
        Create clean, simple sidebar navigation
        Minimalist design with clear icons and text
        """
        self.sidebar = QtWidgets.QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar_expanded = False
        
        # Clean, simple design with solid colors
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: #f8f9fa;
                border-right: 1px solid #e0e0e0;
            }}
            QPushButton {{
                background-color: transparent;
                color: #202124;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 15px;
                font-weight: 500;
                text-align: left;
                margin: 2px 8px;
            }}
            QPushButton:hover {{
                background-color: #e8eaed;
            }}
            QPushButton:checked {{
                background-color: #1a73e8;
                color: #ffffff;
                font-weight: 600;
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(self.sidebar)
        layout.setContentsMargins(0, 24, 0, 24)
        layout.setSpacing(4)
        layout.setAlignment(QtCore.Qt.AlignTop)
        
        # Simple logo/brand
        brand_container = QtWidgets.QWidget()
        brand_layout = QtWidgets.QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(16, 0, 16, 16)
        brand_layout.setSpacing(4)
        
        brand_label = QtWidgets.QLabel("ApplyFlow")
        brand_label.setStyleSheet("""
            font-size: 22px;
            font-weight: 700;
            color: #1a73e8;
            padding: 8px 0;
        """)
        brand_layout.addWidget(brand_label)
        
        tagline = QtWidgets.QLabel("Job Automation")
        tagline.setStyleSheet("""
            font-size: 12px;
            color: #5f6368;
            font-weight: 500;
        """)
        brand_layout.addWidget(tagline)
        
        layout.addWidget(brand_container)
        
        # Simple separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #e0e0e0; margin: 0 12px 12px 12px;")
        layout.addWidget(separator)
        
        # Navigation items - simple and clear
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "Dashboard"),
            ("jobs", "Job Search"),
            ("ai", "AI Settings"),
            ("history", "History"),
            ("logs", "Activity Log"),
            None,  # Spacer
            ("settings", "Settings"),
            ("help", "Help"),
        ]
        
        for item in nav_items:
            if item is None:
                layout.addStretch()
                continue
                
            page_id, label = item
            
            btn = QtWidgets.QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn.setMinimumHeight(44)
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            
            # Click handler
            if page_id in ["dashboard", "jobs", "ai", "history"]:
                btn.clicked.connect(lambda checked, p=page_id: self._switch_page(p))
            elif page_id == "logs":
                btn.clicked.connect(lambda: self._show_logs())
            elif page_id == "settings":
                btn.clicked.connect(lambda: self._switch_page("settings"))
            elif page_id == "help":
                btn.clicked.connect(lambda: self._show_help())
            
            layout.addWidget(btn)
            self.nav_buttons[page_id] = btn
        
        return self.sidebar
    

    def _show_logs(self):
        """Scroll to logs section"""
        self._log("info", "Activity log is at the bottom of the window")
    
    def _show_help(self):
        """Show help dialog"""
        QtWidgets.QMessageBox.information(
            self, "ApplyFlow Help",
            "⚡ ApplyFlow - AI-Powered Job Applications\n\n"
            "Quick Start Guide:\n\n"
            "1. 📄 Upload your resume in Job Search page\n"
            "2. 🤖 Configure AI provider and API key\n"
            "3. 🔍 Set your job search criteria\n"
            "4. ▶️  Click Run to start automation\n"
            "5. 🔐 Log into LinkedIn when Chrome opens\n"
            "6. ✨ Watch ApplyFlow apply to jobs automatically!\n\n"
            "For support, check the documentation or activity logs."
        )
    
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
        stats_layout.setSpacing(20)
        
        # Application stats (store references to update later)
        total_apps = self.stats["total_applied"]
        total_failed = self.stats["total_failed"]
        total_skipped = self.stats["total_skipped"]
        success_rate = 0
        if total_apps + total_failed > 0:
            success_rate = round((total_apps / (total_apps + total_failed)) * 100)
        
        self.apps_value = QtWidgets.QLabel(str(total_apps))
        apps_card = self._create_stat_card("APPLICATIONS", self.apps_value, "Total submitted", MaterialColors.PRIMARY)
        stats_layout.addWidget(apps_card)
        
        self.success_value = QtWidgets.QLabel(f"{success_rate}%")
        success_card = self._create_stat_card("SUCCESS RATE", self.success_value, "Application success", MaterialColors.TERTIARY)
        stats_layout.addWidget(success_card)
        
        self.today_value = QtWidgets.QLabel(str(self.stats["today_applied"]))
        today_card = self._create_stat_card("TODAY", self.today_value, "Applications today", MaterialColors.SECONDARY)
        stats_layout.addWidget(today_card)
        
        layout.addWidget(stats_container)
        
        # Quick actions section title
        actions_title = QtWidgets.QLabel("Quick Actions")
        actions_title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 500;
            color: {MaterialColors.TEXT_PRIMARY};
            margin-top: 8px;
            margin-bottom: 4px;
        """)
        layout.addWidget(actions_title)
        
        # Quick action buttons in horizontal layout
        actions_container = QtWidgets.QWidget()
        actions_layout = QtWidgets.QHBoxLayout(actions_container)
        actions_layout.setSpacing(16)
        
        start_btn = QtWidgets.QPushButton("START JOB SEARCH")
        start_btn.setMinimumHeight(56)
        start_btn.setMinimumWidth(180)
        start_btn.clicked.connect(lambda: self._switch_page("jobs"))
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        actions_layout.addWidget(start_btn)
        
        config_btn = QtWidgets.QPushButton("CONFIGURE AI")
        config_btn.setMinimumHeight(56)
        config_btn.setMinimumWidth(180)
        config_btn.clicked.connect(lambda: self._switch_page("ai"))
        config_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        actions_layout.addWidget(config_btn)
        
        history_btn = QtWidgets.QPushButton("VIEW HISTORY")
        history_btn.setMinimumHeight(56)
        history_btn.setMinimumWidth(180)
        history_btn.clicked.connect(lambda: self._switch_page("history"))
        history_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
            QPushButton:pressed {
                background-color: #6d28d9;
            }
        """)
        actions_layout.addWidget(history_btn)
        
        layout.addWidget(actions_container)
        
        # Recent activity
        recent_group = QtWidgets.QGroupBox("Recent Activity")
        recent_layout = QtWidgets.QVBoxLayout(recent_group)
        
        self.recent_list = QtWidgets.QListWidget()
        self.recent_list.addItem("No recent activity")
        recent_layout.addWidget(self.recent_list)
        
        layout.addWidget(recent_group)
        
        layout.addStretch()
        
        return page
    
    def _create_stat_card(self, title, value_widget, description, color):
        """Create Material Design stat card with color accent"""
        card = QtWidgets.QFrame()
        card.setFrameShape(QtWidgets.QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {MaterialColors.SURFACE};
                border: 1px solid {MaterialColors.OUTLINE_VARIANT};
                border-left: 5px solid {color};
                border-radius: 16px;
                padding: 24px;
                min-width: 200px;
            }}
            QFrame:hover {{
                border: 1px solid {MaterialColors.OUTLINE};
                border-left: 5px solid {color};
            }}
        """)
        
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setSpacing(12)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {MaterialColors.TEXT_SECONDARY};
            letter-spacing: 0.5px;
        """)
        card_layout.addWidget(title_label)
        
        # Use the passed widget instead of creating new label
        value_widget.setStyleSheet(f"""
            font-size: 42px;
            font-weight: 300;
            color: {color};
            margin: 8px 0;
        """)
        card_layout.addWidget(value_widget)
        
        desc_label = QtWidgets.QLabel(description)
        desc_label.setStyleSheet(f"""
            font-size: 13px;
            color: {MaterialColors.TEXT_SECONDARY};
        """)
        card_layout.addWidget(desc_label)
        
        card_layout.addStretch()
        
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
        
        # Control buttons - Clean, bold, professional
        controls = QtWidgets.QWidget()
        controls_layout = QtWidgets.QHBoxLayout(controls)
        controls_layout.setSpacing(16)
        
        # Run button - Primary action, green
        self.run_btn = QtWidgets.QPushButton("RUN")
        self.run_btn.setMinimumHeight(56)
        self.run_btn.setMinimumWidth(140)
        self.run_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
            QPushButton:disabled {{
                background-color: #d1d5db;
                color: #9ca3af;
            }}
        """)
        self.run_btn.clicked.connect(self._on_run)
        controls_layout.addWidget(self.run_btn)
        
        # Pause button - Secondary action, amber
        self.pause_btn = QtWidgets.QPushButton("PAUSE")
        self.pause_btn.setMinimumHeight(56)
        self.pause_btn.setMinimumWidth(140)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setCheckable(True)
        self.pause_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: #f59e0b;
                border: 2px solid #f59e0b;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background-color: #fef3c7;
            }}
            QPushButton:pressed {{
                background-color: #fde68a;
            }}
            QPushButton:checked {{
                background-color: #f59e0b;
                color: white;
            }}
            QPushButton:disabled {{
                background-color: #f9fafb;
                color: #d1d5db;
                border-color: #e5e7eb;
            }}
        """)
        self.pause_btn.clicked.connect(self._on_pause_resume)
        controls_layout.addWidget(self.pause_btn)
        
        # Stop button - Destructive action, red
        self.stop_btn = QtWidgets.QPushButton("STOP")
        self.stop_btn.setMinimumHeight(56)
        self.stop_btn.setMinimumWidth(140)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: #ef4444;
                border: 2px solid #ef4444;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background-color: #fee2e2;
            }}
            QPushButton:pressed {{
                background-color: #fecaca;
            }}
            QPushButton:disabled {{
                background-color: #f9fafb;
                color: #d1d5db;
                border-color: #e5e7eb;
            }}
        """)
        self.stop_btn.clicked.connect(self._on_stop)
        controls_layout.addWidget(self.stop_btn)
        
        # Status indicator
        self.connection_status = QtWidgets.QLabel("READY")
        self.connection_status.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: #6b7280;
            background-color: #f3f4f6;
            padding: 16px 24px;
            border-radius: 8px;
            letter-spacing: 0.5px;
        """)
        controls_layout.addWidget(self.connection_status)
        
        controls_layout.addStretch()
        
        layout.addWidget(controls)
        
        # Resume upload section - Clean design
        resume_group = QtWidgets.QGroupBox("Resume / CV")
        resume_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: 600;
                color: {MaterialColors.TEXT_PRIMARY};
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background-color: white;
            }}
        """)
        resume_layout = QtWidgets.QHBoxLayout(resume_group)
        resume_layout.setSpacing(12)
        
        self.resume_path_edit = QtWidgets.QLineEdit()
        self.resume_path_edit.setPlaceholderText("No resume selected - click Browse to upload")
        self.resume_path_edit.setReadOnly(True)
        self.resume_path_edit.setMinimumHeight(44)
        self.resume_path_edit.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: #f9fafb;
            }
        """)
        self.resume_path_edit.setToolTip(
            "📄 Your resume file path will appear here after selection.\n"
            "The resume is used by AI to:\n"
            "• Answer job application questions intelligently\n"
            "• Match your skills with job requirements\n"
            "• Generate personalized cover letters (if needed)"
        )
        resume_layout.addWidget(self.resume_path_edit, 1)
        
        browse_resume_btn = QtWidgets.QPushButton("Browse Files")
        browse_resume_btn.clicked.connect(self._browse_resume)
        browse_resume_btn.setMinimumWidth(140)
        browse_resume_btn.setMinimumHeight(44)
        browse_resume_btn.setToolTip(
            "📁 Click to select your resume file from your computer.\n\n"
            "Supported formats:\n"
            "• PDF (.pdf) - Recommended for best compatibility\n"
            "• Word (.docx, .doc)\n"
            "• Text (.txt)\n\n"
            "Tips:\n"
            "• Keep your resume updated with latest experience\n"
            "• Use a clean, professional format\n"
            "• File size under 5MB works best"
        )
        browse_resume_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #374151;
                border: 2px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #e5e7eb;
            }
        """)
        resume_layout.addWidget(browse_resume_btn)
        
        layout.addWidget(resume_group)
        
        # Search form - Clean, professional design
        form_group = QtWidgets.QGroupBox("Job Search Criteria")
        form_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: 600;
                color: {MaterialColors.TEXT_PRIMARY};
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 20px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background-color: white;
            }}
        """)
        # 2-Column Grid Layout for Professional Side-by-Side Design
        form_layout = QtWidgets.QGridLayout(form_group)
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setHorizontalSpacing(20)  # Space between columns
        form_layout.setVerticalSpacing(12)    # Space between rows
        
        # Keywords (Left Column)
        keywords_label = QtWidgets.QLabel("Job Title / Keywords")
        keywords_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: #374151;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        form_layout.addWidget(keywords_label, 0, 0)  # Row 0, Column 0
        
        self.keywords_edit = QtWidgets.QLineEdit()
        self.keywords_edit.setPlaceholderText("Software Engineer, Data Analyst, Product Manager...")
        self.keywords_edit.setMinimumHeight(52)
        self.keywords_edit.setStyleSheet("""
            QLineEdit {
                font-size: 15px;
                padding: 12px 16px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        self.keywords_edit.setToolTip(
            "🔍 Enter job titles or keywords to search for on LinkedIn.\n\n"
            "Examples:\n"
            "• 'Software Engineer' - Searches for software engineering roles\n"
            "• 'Marketing Manager' - Searches for marketing management jobs\n"
            "• 'Data Analyst' - Searches for data analysis positions\n\n"
            "Tips:\n"
            "• Be specific for better results (e.g., 'Senior Full Stack Developer')\n"
            "• Use job titles that match your experience level\n"
            "• Try different variations if results are limited"
        )
        form_layout.addWidget(self.keywords_edit, 1, 0)  # Row 1, Column 0
        
        # Location (Right Column)
        location_label = QtWidgets.QLabel("Location")
        location_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: #374151;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        form_layout.addWidget(location_label, 0, 1)  # Row 0, Column 1
        
        self.location_edit = QtWidgets.QLineEdit()
        self.location_edit.setPlaceholderText("New York, Remote, United States...")
        self.location_edit.setMinimumHeight(52)
        self.location_edit.setStyleSheet("""
            QLineEdit {
                font-size: 15px;
                padding: 12px 16px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        self.location_edit.setToolTip(
            "📍 Enter the location where you want to find jobs.\n\n"
            "Examples:\n"
            "• 'New York, NY' - Jobs in New York City area\n"
            "• 'Remote' - Work-from-home positions anywhere\n"
            "• 'San Francisco, CA' - Jobs in San Francisco\n"
            "• 'United States' - Jobs anywhere in the US\n"
            "• 'London, UK' - Jobs in London, United Kingdom\n\n"
            "Tips:\n"
            "• Use 'Remote' for work-from-home opportunities\n"
            "• Be as specific or broad as you need\n"
            "• LinkedIn will search within a reasonable radius"
        )
        form_layout.addWidget(self.location_edit, 1, 1)  # Row 1, Column 1
        
        # Set equal column stretch for balanced layout
        form_layout.setColumnStretch(0, 1)
        form_layout.setColumnStretch(1, 1)
        
        # Hidden fields with defaults (for compatibility)
        self.job_level_combo = QtWidgets.QComboBox()
        self.job_level_combo.addItems(["All Levels", "Entry level", "Mid-Senior level"])
        self.job_level_combo.setCurrentIndex(0)
        self.job_level_combo.setVisible(False)
        
        self.max_apply_spin = QtWidgets.QSpinBox()
        self.max_apply_spin.setRange(1, 1000)
        self.max_apply_spin.setValue(30)
        self.max_apply_spin.setVisible(False)
        
        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItems(["English"])
        self.language_combo.setVisible(False)
        
        self.easy_apply_chk = QtWidgets.QCheckBox("Easy Apply")
        self.easy_apply_chk.setChecked(True)
        self.easy_apply_chk.setVisible(False)
        
        layout.addWidget(form_group)
        
        # Progress
        progress_group = QtWidgets.QGroupBox("Progress")
        progress_layout = QtWidgets.QVBoxLayout(progress_group)
        progress_layout.setSpacing(16)
        
        stats = QtWidgets.QHBoxLayout()
        stats.setSpacing(12)
        
        self.applied_label = QtWidgets.QLabel("Applied: 0")
        self.applied_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            padding: 12px 20px;
            background-color: #d1fae5;
            color: #065f46;
            border-radius: 8px;
            border: 2px solid #10b981;
        """)
        stats.addWidget(self.applied_label)
        
        self.failed_label = QtWidgets.QLabel("Failed: 0")
        self.failed_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            padding: 12px 20px;
            background-color: #fee2e2;
            color: #991b1b;
            border-radius: 8px;
            border: 2px solid #ef4444;
        """)
        stats.addWidget(self.failed_label)
        
        self.skipped_label = QtWidgets.QLabel("Skipped: 0")
        self.skipped_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            padding: 12px 20px;
            background-color: #fef3c7;
            color: #92400e;
            border-radius: 8px;
            border: 2px solid #f59e0b;
        """)
        stats.addWidget(self.skipped_label)
        
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
        # Create scroll area for entire page
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"background-color: {MaterialColors.BACKGROUND};")
        
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
        provider_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: 600;
                color: #1f2937;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background-color: white;
            }
            QCheckBox {
                font-size: 14px;
                font-weight: 500;
                color: #374151;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border: 2px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border-color: #3b82f6;
            }
            QCheckBox::indicator:checked {
                background-color: #3b82f6;
                border-color: #3b82f6;
            }
            QLineEdit, QComboBox {
                font-size: 14px;
                padding: 10px 14px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                background-color: white;
                min-height: 40px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        provider_layout = QtWidgets.QFormLayout(provider_group)
        provider_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        provider_layout.setVerticalSpacing(20)
        provider_layout.setHorizontalSpacing(24)
        provider_layout.setContentsMargins(20, 20, 20, 20)
        
        # Enable AI
        self.use_ai_chk = QtWidgets.QCheckBox("Enable AI Features")
        self.use_ai_chk.setToolTip(
            "🤖 Turn on AI-powered automation features.\n"
            "When enabled: AI answers custom questions, matches jobs to resume.\n"
            "When disabled: Only fills standard fields with personal info.\n"
            "Recommended: ON for intelligent job applications."
        )
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
        self.ai_provider_combo.setToolTip(
            "🎯 Choose your AI service provider.\n\n"
            "✅ Groq (Fast & Free): Recommended for beginners - FREE and FAST!\n"
            "💡 OpenAI (GPT): Most powerful, costs money but high quality\n"
            "🌐 Google Gemini: Free tier available, good quality\n"
            "💻 Ollama (Local): Run AI on your computer, no API key needed\n\n"
            "Get API keys from provider websites (groq.com, openai.com, etc.)"
        )
        self.ai_provider_combo.currentTextChanged.connect(self._update_model_list)
        provider_layout.addRow(provider_label, self.ai_provider_combo)
        
        # API Key
        key_label = QtWidgets.QLabel("API Key")
        key_label.setStyleSheet(f"font-weight: 500; color: {MaterialColors.TEXT_PRIMARY};")
        self.api_key_edit = QtWidgets.QLineEdit()
        self.api_key_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("Enter your API key")
        self.api_key_edit.setToolTip(
            "🔑 Your API key for authenticating with the AI provider.\n\n"
            "How to get your API key:\n"
            "1. Sign up at provider website (groq.com, openai.com, etc.)\n"
            "2. Navigate to API Keys or Developer section\n"
            "3. Create a new API key and copy it here\n\n"
            "⚠️ Keep your API key secret! Don't share it with anyone.\n"
            "Groq offers FREE API keys with generous limits!"
        )
        provider_layout.addRow(key_label, self.api_key_edit)
        
        # Show/Hide key
        show_key_btn = QtWidgets.QPushButton("SHOW KEY")
        show_key_btn.setCheckable(True)
        show_key_btn.setMinimumHeight(36)
        show_key_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6b7280;
                border: 2px solid #e5e7eb;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.5px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                border-color: #3b82f6;
                color: #3b82f6;
            }
            QPushButton:checked {
                background-color: #3b82f6;
                color: white;
                border-color: #3b82f6;
            }
        """)
        show_key_btn.toggled.connect(lambda checked: (
            self.api_key_edit.setEchoMode(QtWidgets.QLineEdit.Normal if checked else QtWidgets.QLineEdit.Password),
            show_key_btn.setText("HIDE KEY" if checked else "SHOW KEY")
        ))
        provider_layout.addRow("", show_key_btn)
        
        # Model selector
        model_label = QtWidgets.QLabel("Model")
        model_label.setStyleSheet(f"font-weight: 500; color: {MaterialColors.TEXT_PRIMARY};")
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.setToolTip(
            "🧠 The specific AI model to use for generating responses.\n\n"
            "Different models have different capabilities:\n"
            "⚡ Fast models: Quick responses, good for simple questions\n"
            "💪 Powerful models: Better reasoning, more accurate answers\n\n"
            "Groq recommended: llama-3.3-70b-versatile (great balance!)\n"
            "The list updates based on your selected provider."
        )
        # Remove setEditable - we want dropdown selection, not text entry
        provider_layout.addRow(model_label, self.model_combo)
        
        # Initialize models
        self._update_model_list("OpenAI (GPT)")
        
        layout.addWidget(provider_group)
        
        # AI Features
        features_group = QtWidgets.QGroupBox("AI Features")
        features_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: 600;
                color: #1f2937;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background-color: white;
            }
            QCheckBox {
                font-size: 14px;
                font-weight: 500;
                color: #374151;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border: 2px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border-color: #3b82f6;
            }
            QCheckBox::indicator:checked {
                background-color: #3b82f6;
                border-color: #3b82f6;
            }
        """)
        features_layout = QtWidgets.QVBoxLayout(features_group)
        features_layout.setSpacing(16)
        features_layout.setContentsMargins(20, 20, 20, 20)
        
        self.ai_questions_chk = QtWidgets.QCheckBox("AI Question Answering")
        self.ai_questions_chk.setChecked(True)
        self.ai_questions_chk.setToolTip(
            "💬 AI automatically answers custom application questions.\n\n"
            "Examples: 'Why do you want this job?', 'What are your strengths?'\n"
            "AI analyzes your resume and generates relevant, personalized answers.\n\n"
            "Recommended: ON - This is a core feature that saves massive time!"
        )
        features_layout.addWidget(self.ai_questions_chk)
        
        self.ai_matching_chk = QtWidgets.QCheckBox("Smart Job Matching (40% threshold)")
        self.ai_matching_chk.setToolTip(
            "🎯 AI evaluates how well each job matches your resume.\n\n"
            "40% threshold means: Only apply if job is 40%+ match with your skills.\n"
            "Lower threshold = More applications (less selective)\n"
            "Higher threshold = Fewer applications (more selective)\n\n"
            "Recommended: Leave OFF to apply to all Easy Apply jobs.\n"
            "Turn ON to focus on jobs that truly match your profile."
        )
        features_layout.addWidget(self.ai_matching_chk)
        
        self.ai_learning_chk = QtWidgets.QCheckBox("Q&A Learning Database (auto-improves over time)")
        self.ai_learning_chk.setChecked(True)
        self.ai_learning_chk.setToolTip(
            "📚 Saves Q&A pairs to local database for faster future responses.\n\n"
            "When you answer a question once, AI remembers it.\n"
            "Next time the same question appears, uses saved answer (instant!).\n"
            "Over time, builds a personalized Q&A library for your applications.\n\n"
            "Recommended: ON - Makes automation faster and more consistent!"
        )
        features_layout.addWidget(self.ai_learning_chk)
        
        layout.addWidget(features_group)
        
        # Action buttons
        buttons = QtWidgets.QHBoxLayout()
        buttons.setSpacing(16)
        
        save_btn = QtWidgets.QPushButton("SAVE CONFIGURATION")
        save_btn.setMinimumHeight(56)
        save_btn.setMinimumWidth(200)
        save_btn.clicked.connect(self._save_ai_config)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        buttons.addWidget(save_btn)
        
        test_btn = QtWidgets.QPushButton("TEST CONNECTION")
        test_btn.setMinimumHeight(56)
        test_btn.setMinimumWidth(200)
        test_btn.clicked.connect(self._test_ai_connection)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        buttons.addWidget(test_btn)
        
        layout.addLayout(buttons)
        
        layout.addStretch()
        
        # Set the page as scroll area's widget
        scroll.setWidget(page)
        return scroll
    
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
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                gridline-color: #f3f4f6;
            }
            QTableWidget::item {
                padding: 10px;
                border: none;
            }
            QHeaderView::section {
                background-color: #f9fafb;
                color: #374151;
                font-size: 13px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
            }
            QTableWidget::item:alternate {
                background-color: #f9fafb;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
        """)
        layout.addWidget(self.history_table)
        
        # Controls
        controls = QtWidgets.QHBoxLayout()
        
        export_btn = QtWidgets.QPushButton("EXPORT TO EXCEL")
        export_btn.setMinimumHeight(44)
        export_btn.setMinimumWidth(160)
        export_btn.clicked.connect(lambda: self._log("info", "Export feature coming soon"))
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        controls.addWidget(export_btn)
        
        clear_btn = QtWidgets.QPushButton("CLEAR HISTORY")
        clear_btn.setMinimumHeight(44)
        clear_btn.setMinimumWidth(160)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            }
        """)
        controls.addWidget(clear_btn)
        
        # Open Reports Folder button
        open_folder_btn = QtWidgets.QPushButton("OPEN REPORTS FOLDER")
        open_folder_btn.setMinimumHeight(44)
        open_folder_btn.setMinimumWidth(180)
        open_folder_btn.clicked.connect(self._open_reports_folder)
        open_folder_btn.setToolTip(
            "📂 Open the folder containing CSV reports.\n\n"
            "CSV Files:\n"
            "• all_applied_applications_history.csv - Successfully applied jobs\n"
            "• all_failed_applications_history.csv - Failed application attempts\n\n"
            "You can open these files in Excel, Google Sheets, or any CSV editor."
        )
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
            QPushButton:pressed {
                background-color: #4338ca;
            }
        """)
        controls.addWidget(open_folder_btn)
        
        # View/Edit Q&A Database button
        qa_view_btn = QtWidgets.QPushButton("VIEW Q&A DATABASE")
        qa_view_btn.setMinimumHeight(44)
        qa_view_btn.setMinimumWidth(180)
        qa_view_btn.clicked.connect(self._open_qa_database_viewer)
        qa_view_btn.setToolTip(
            "🗄️ View and edit the Question & Answer database.\n\n"
            "Features:\n"
            "• View all questions and answers encountered\n"
            "• Edit answers to improve future applications\n"
            "• See usage statistics and timestamps\n"
            "• Search and filter entries\n"
            "• Export to CSV for external editing"
        )
        qa_view_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
            QPushButton:pressed {
                background-color: #6d28d9;
            }
        """)
        controls.addWidget(qa_view_btn)
        
        # Open Logs Folder button
        logs_btn = QtWidgets.QPushButton("OPEN LOGS FOLDER")
        logs_btn.setMinimumHeight(44)
        logs_btn.setMinimumWidth(160)
        logs_btn.clicked.connect(self._open_logs_folder)
        logs_btn.setToolTip(
            "📋 Open the logs folder for debugging.\n\n"
            "Contains:\n"
            "• captcha_events.csv - CAPTCHA detection log\n"
            "• llm_cache.json - AI response cache\n"
            "• Other runtime logs and debug files"
        )
        logs_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
            QPushButton:pressed {
                background-color: #b45309;
            }
        """)
        controls.addWidget(logs_btn)
        
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
        general_tab.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: 500;
                color: #374151;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border: 2px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border-color: #3b82f6;
            }
            QCheckBox::indicator:checked {
                background-color: #3b82f6;
                border-color: #3b82f6;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTMuMzMzMyA0TDYgMTEuMzMzM0wyLjY2NjY3IDgiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+);
            }
        """)
        general_layout = QtWidgets.QVBoxLayout(general_tab)
        general_layout.setSpacing(20)
        general_layout.setContentsMargins(24, 24, 24, 24)
        
        self.stealth_chk = QtWidgets.QCheckBox("Enable stealth mode")
        self.stealth_chk.setChecked(True)
        self.stealth_chk.setToolTip(
            "🕵️ Uses undetected-chromedriver to bypass LinkedIn's bot detection.\n"
            "Helps avoid account restrictions and CAPTCHA challenges.\n"
            "Recommended: Keep this ON for safer automation."
        )
        general_layout.addWidget(self.stealth_chk)
        
        self.safe_mode_chk = QtWidgets.QCheckBox("Use guest browser profile")
        self.safe_mode_chk.setToolTip(
            "🔒 Uses a temporary browser profile instead of your main Chrome profile.\n"
            "Keeps your personal browsing data separate from automation.\n"
            "Note: You'll need to log in to LinkedIn each time.\n"
            "Recommended: OFF if you want to stay logged in."
        )
        general_layout.addWidget(self.safe_mode_chk)
        
        general_layout.addStretch()
        
        tabs.addTab(general_tab, "General")
        
        # Automation tab
        auto_tab = QtWidgets.QWidget()
        auto_tab.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: 500;
                color: #374151;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border: 2px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border-color: #3b82f6;
            }
            QCheckBox::indicator:checked {
                background-color: #3b82f6;
                border-color: #3b82f6;
            }
        """)
        auto_layout = QtWidgets.QVBoxLayout(auto_tab)
        auto_layout.setSpacing(20)
        auto_layout.setContentsMargins(24, 24, 24, 24)
        
        self.pause_before_submit_chk = QtWidgets.QCheckBox("Pause before submitting")
        self.pause_before_submit_chk.setToolTip(
            "⏸️ Pauses automation before submitting each application.\n"
            "Gives you a chance to review the filled form before submission.\n"
            "Useful for: Checking answers, ensuring accuracy, manual edits.\n"
            "Recommended: ON if you want manual control over submissions."
        )
        auto_layout.addWidget(self.pause_before_submit_chk)
        
        self.run_nonstop_chk = QtWidgets.QCheckBox("Run continuously")
        self.run_nonstop_chk.setToolTip(
            "🔄 Keeps applying to jobs until manually stopped.\n"
            "Will continue searching and applying beyond the initial results.\n"
            "Useful for: Mass applications, overnight runs, maximizing reach.\n"
            "Recommended: OFF for controlled application sessions."
        )
        auto_layout.addWidget(self.run_nonstop_chk)
        
        auto_layout.addStretch()
        
        tabs.addTab(auto_tab, "Automation")
        
        # Personal Info tab
        personal_tab = QtWidgets.QWidget()
        personal_scroll = QtWidgets.QScrollArea()
        personal_scroll.setWidgetResizable(True)
        personal_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        personal_content = QtWidgets.QWidget()
        personal_content.setStyleSheet("""
            QLineEdit, QSpinBox {
                font-size: 14px;
                padding: 10px 14px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                background-color: white;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QLabel {
                font-size: 13px;
                font-weight: 600;
                color: #374151;
            }
        """)
        personal_layout = QtWidgets.QFormLayout(personal_content)
        personal_layout.setVerticalSpacing(20)
        personal_layout.setContentsMargins(20, 20, 20, 20)
        personal_layout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        # Info message
        info_label = QtWidgets.QLabel(
            "Personal information is required for job applications.\n"
            "This data will be used to fill out application forms automatically."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"""
            background-color: #dbeafe;
            color: #1e40af;
            padding: 16px;
            border-radius: 8px;
            border: 2px solid #3b82f6;
            margin-bottom: 12px;
            font-size: 13px;
            font-weight: 500;
        """)
        personal_layout.addRow(info_label)
        
        # Full Name
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("David Imongirien")
        self.name_edit.setMinimumHeight(40)
        self.name_edit.setToolTip(
            "📝 Your full legal name as it appears on official documents.\n"
            "This will be used to fill the 'Name' field in job applications.\n"
            "Example: John Michael Smith"
        )
        personal_layout.addRow("Full Name *:", self.name_edit)
        
        # Email
        self.email_edit = QtWidgets.QLineEdit()
        self.email_edit.setPlaceholderText("your.email@example.com")
        self.email_edit.setMinimumHeight(40)
        self.email_edit.setToolTip(
            "📧 Your professional email address for job communications.\n"
            "Employers will use this to contact you about applications.\n"
            "Tip: Use a professional email, not 'cooldude123@example.com'"
        )
        personal_layout.addRow("Email *:", self.email_edit)
        
        # Phone
        self.phone_edit = QtWidgets.QLineEdit()
        self.phone_edit.setPlaceholderText("+1 (555) 123-4567")
        self.phone_edit.setMinimumHeight(40)
        self.phone_edit.setToolTip(
            "📱 Your contact phone number including country/area code.\n"
            "Format: +1 (555) 123-4567 or +44 20 1234 5678\n"
            "Recruiters may call/text you for interviews."
        )
        personal_layout.addRow("Phone Number *:", self.phone_edit)
        
        # LinkedIn URL
        self.linkedin_edit = QtWidgets.QLineEdit()
        self.linkedin_edit.setPlaceholderText("https://linkedin.com/in/yourprofile")
        self.linkedin_edit.setMinimumHeight(40)
        self.linkedin_edit.setToolTip(
            "💼 Your LinkedIn profile URL (optional but recommended).\n"
            "Format: https://linkedin.com/in/yourname\n"
            "Tip: Customize your LinkedIn URL for a professional look!"
        )
        personal_layout.addRow("LinkedIn URL:", self.linkedin_edit)
        
        # Current Company
        self.company_edit = QtWidgets.QLineEdit()
        self.company_edit.setPlaceholderText("Acme Corporation")
        self.company_edit.setMinimumHeight(40)
        self.company_edit.setToolTip(
            "🏢 Your current or most recent employer's name.\n"
            "Leave blank if unemployed or student.\n"
            "Example: Google, Microsoft, Self-Employed"
        )
        personal_layout.addRow("Current Company:", self.company_edit)
        
        # Current Title
        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("Senior Software Engineer")
        self.title_edit.setMinimumHeight(40)
        self.title_edit.setToolTip(
            "👔 Your current job title or most recent position.\n"
            "Be specific: 'Senior Full Stack Developer' not just 'Developer'\n"
            "Students can use: 'Computer Science Student' or 'Recent Graduate'"
        )
        personal_layout.addRow("Current Title:", self.title_edit)
        
        # Years of Experience
        self.experience_spin = QtWidgets.QSpinBox()
        self.experience_spin.setRange(0, 50)
        self.experience_spin.setValue(5)
        self.experience_spin.setMinimumHeight(40)
        self.experience_spin.setToolTip(
            "📊 Total years of professional work experience in your field.\n"
            "Count internships, part-time, and freelance work.\n"
            "Entry-level: 0-2 years | Mid-level: 3-7 years | Senior: 8+ years"
        )
        personal_layout.addRow("Years of Experience:", self.experience_spin)
        
        # City
        self.city_edit = QtWidgets.QLineEdit()
        self.city_edit.setPlaceholderText("New York")
        self.city_edit.setMinimumHeight(40)
        self.city_edit.setToolTip(
            "🌆 The city where you currently live or want to work.\n"
            "Important for location-based job matching.\n"
            "Example: San Francisco, London, Toronto"
        )
        personal_layout.addRow("City:", self.city_edit)
        
        # State
        self.state_edit = QtWidgets.QLineEdit()
        self.state_edit.setPlaceholderText("NY")
        self.state_edit.setMinimumHeight(40)
        self.state_edit.setToolTip(
            "📍 Your state, province, or region.\n"
            "Use standard abbreviations for US states (NY, CA, TX).\n"
            "International: Full name (Ontario, Queensland, Bavaria)"
        )
        personal_layout.addRow("State/Province:", self.state_edit)
        
        # Country
        self.country_edit = QtWidgets.QLineEdit()
        self.country_edit.setPlaceholderText("United States")
        self.country_edit.setMinimumHeight(40)
        self.country_edit.setToolTip(
            "🌍 Your country of residence.\n"
            "Use full country name: United States, United Kingdom, Canada\n"
            "This affects job eligibility and visa sponsorship requirements."
        )
        personal_layout.addRow("Country:", self.country_edit)
        
        # Zip Code
        self.zip_edit = QtWidgets.QLineEdit()
        self.zip_edit.setPlaceholderText("10001")
        self.zip_edit.setMinimumHeight(40)
        self.zip_edit.setToolTip(
            "📮 Your postal/zip code for accurate location matching.\n"
            "US: 5-digit (10001) or 9-digit (10001-1234)\n"
            "UK: Format like SW1A 1AA | Canada: A1A 1A1"
        )
        personal_layout.addRow("Zip/Postal Code:", self.zip_edit)
        
        # Website/Portfolio
        self.website_edit = QtWidgets.QLineEdit()
        self.website_edit.setPlaceholderText("https://yourportfolio.com")
        self.website_edit.setMinimumHeight(40)
        self.website_edit.setToolTip(
            "🌐 Your personal website or online portfolio (optional).\n"
            "Great for: Designers, developers, writers, photographers\n"
            "Include https:// - Example: https://johndoe.com"
        )
        personal_layout.addRow("Website/Portfolio:", self.website_edit)
        
        # GitHub (for tech roles)
        self.github_edit = QtWidgets.QLineEdit()
        self.github_edit.setPlaceholderText("https://github.com/yourusername")
        self.github_edit.setMinimumHeight(40)
        self.github_edit.setToolTip(
            "💻 Your GitHub profile URL (especially for tech roles).\n"
            "Employers use this to review your code and projects.\n"
            "Format: https://github.com/yourusername\n"
            "Tip: Make sure you have public repos showcasing your skills!"
        )
        personal_layout.addRow("GitHub URL:", self.github_edit)
        
        personal_scroll.setWidget(personal_content)
        
        personal_tab_layout = QtWidgets.QVBoxLayout(personal_tab)
        personal_tab_layout.setContentsMargins(0, 0, 0, 0)
        personal_tab_layout.addWidget(personal_scroll)
        
        tabs.addTab(personal_tab, "Personal Info")
        
        layout.addWidget(tabs)
        
        # Save button
        save_btn = QtWidgets.QPushButton("SAVE SETTINGS")
        save_btn.setMinimumHeight(56)
        save_btn.setMinimumWidth(200)
        save_btn.clicked.connect(self._save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
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
        # Check if log_text exists (it's created in _setup_ui)
        if not hasattr(self, 'log_text'):
            return
        
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
    

    def _browse_resume(self):
        """Browse for resume file"""
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Resume/CV",
            "",
            "PDF Files (*.pdf);;Word Documents (*.docx *.doc);;All Files (*.*)"
        )
        if file_path:
            self.resume_path_edit.setText(file_path)
            # Save to config
            from config import questions
            questions.default_resume_path = file_path
            self._log("success", f"Resume selected: {file_path}")
    
    def _open_reports_folder(self):
        """Open the folder containing CSV reports (cross-platform)"""
        try:
            # Get the reports folder path from settings
            from config.settings import file_name
            reports_folder = os.path.dirname(file_name)
            
            # Create folder if it doesn't exist
            if not os.path.exists(reports_folder):
                os.makedirs(reports_folder, exist_ok=True)
                self._log("info", f"Created reports folder: {reports_folder}")
            
            # Get absolute path
            abs_path = os.path.abspath(reports_folder)
            
            # Open folder in file explorer (cross-platform)
            system = platform.system()
            
            if system == "Windows":
                # Windows: Use explorer
                os.startfile(abs_path)
            elif system == "Darwin":
                # macOS: Use open
                subprocess.run(["open", abs_path], check=True)
            else:
                # Linux: Use xdg-open
                subprocess.run(["xdg-open", abs_path], check=True)
            
            self._log("success", f"Opened reports folder: {abs_path}")
            
        except Exception as e:
            self._log("error", f"Failed to open reports folder: {str(e)}")
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                f"Could not open reports folder:\n{str(e)}\n\nFolder path: {os.path.abspath(reports_folder)}"
            )
    
    def _open_qa_database_viewer(self):
        """Open the Q&A Database viewer/editor dialog"""
        try:
            dialog = QADatabaseDialog(self)
            dialog.exec()
            self._log("success", "Q&A Database viewer opened")
        except Exception as e:
            self._log("error", f"Failed to open Q&A Database viewer: {str(e)}")
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                f"Could not open Q&A Database viewer:\n{str(e)}"
            )
    
    def _open_logs_folder(self):
        """Open the logs folder (cross-platform)"""
        try:
            # Get the logs folder path from settings
            from config.settings import logs_folder_path
            logs_folder = logs_folder_path or "logs/"
            
            # Create folder if it doesn't exist
            if not os.path.exists(logs_folder):
                os.makedirs(logs_folder, exist_ok=True)
                self._log("info", f"Created logs folder: {logs_folder}")
            
            # Get absolute path
            abs_path = os.path.abspath(logs_folder)
            
            # Open folder in file explorer (cross-platform)
            system = platform.system()
            
            if system == "Windows":
                # Windows: Use explorer
                os.startfile(abs_path)
            elif system == "Darwin":
                # macOS: Use open
                subprocess.run(["open", abs_path], check=True)
            else:
                # Linux: Use xdg-open
                subprocess.run(["xdg-open", abs_path], check=True)
            
            self._log("success", f"Opened logs folder: {abs_path}")
            
        except Exception as e:
            self._log("error", f"Failed to open logs folder: {str(e)}")
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                f"Could not open logs folder:\n{str(e)}\n\nFolder path: {os.path.abspath(logs_folder)}"
            )
    
    def _on_run(self):
        """Start automation"""
        keywords = self.keywords_edit.text()
        location = self.location_edit.text()
        
        if not keywords:
            QtWidgets.QMessageBox.warning(self, "Missing Keywords", "Please enter job keywords")
            return
        
        self.run_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.pause_btn.setText("PAUSE")
        self.stop_btn.setEnabled(True)
        
        self.connection_status.setText("RUNNING")
        self.connection_status.setStyleSheet("""
            font-size: 13px;
            font-weight: 600;
            color: white;
            background-color: #10b981;
            padding: 16px 24px;
            border-radius: 8px;
            letter-spacing: 0.5px;
        """)
        
        self._log("info", f"Starting: {keywords} in {location}")
        
        # Start worker thread
        if self.worker and self.worker.isRunning():
            self._log("warning", "Automation already running")
            return
        
        try:
            max_apps = self.max_apply_spin.value()
            
            self.worker = AutomationWorker(
                job_title=keywords,
                location=location,
                max_applications=max_apps,
                form_data={},
                language="",
                prefer_english=True
            )
            
            # Connect signals
            self.worker.log_signal.connect(lambda lvl, msg: self._log(lvl, msg))
            self.worker.progress_signal.connect(self._on_worker_progress)
            self.worker.finished_signal.connect(self._on_worker_finished)
            
            self.worker.start()
            
        except Exception as e:
            self._log("error", f"Failed to start: {e}")
            self._on_stop()
    
    def _on_worker_progress(self, applied, failed, skipped, current_job):
        """Update progress from worker"""
        self.applied_label.setText(f"Applied: {applied}")
        self.failed_label.setText(f"Failed: {failed}")
        self.skipped_label.setText(f"Skipped: {skipped}")
        
        # Update dashboard stats
        self.stats["total_applied"] = applied
        self.stats["total_failed"] = failed
        self.stats["total_skipped"] = skipped
        self.stats["today_applied"] = applied  # In real app, filter by today
        
        # Update dashboard stat cards
        if hasattr(self, 'apps_value'):
            self.apps_value.setText(str(applied))
        if hasattr(self, 'today_value'):
            self.today_value.setText(str(applied))
        if hasattr(self, 'success_value'):
            if applied + failed > 0:
                success_rate = round((applied / (applied + failed)) * 100)
                self.success_value.setText(f"{success_rate}%")
        
        total = applied + failed + skipped
        max_apps = self.max_apply_spin.value()
        if total > 0 and max_apps > 0:
            progress = min(int((total / max_apps) * 100), 99)
            self.overall_progress.setValue(progress)
        
        self._log("info", f"Progress: {applied} applied, {failed} failed, {skipped} skipped")
    
    def _on_worker_finished(self, stats):
        """Handle worker completion"""
        self._log("success", f"Automation finished!")
        self.overall_progress.setValue(100)
        self._on_stop()
    
    def _on_stop(self):
        """Stop automation and clean up browser properly"""
        # Actually stop the worker thread
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait(2000)  # Wait up to 2 seconds
            self.worker = None
        
        # Clean up browser to prevent "window not found" errors
        try:
            from modules.open_chrome import close_browser
            close_browser()
            self._log("info", "Browser closed properly")
        except Exception as e:
            self._log("debug", f"Browser cleanup: {e}")
        
        self.run_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setChecked(False)
        self.pause_btn.setText("PAUSE")
        self.stop_btn.setEnabled(False)
        
        self.connection_status.setText("READY")
        self.connection_status.setStyleSheet("""
            font-size: 13px;
            font-weight: 600;
            color: #6b7280;
            background-color: #f3f4f6;
            padding: 16px 24px;
            border-radius: 8px;
            letter-spacing: 0.5px;
        """)
        
        self._log("warning", "Stopped")
    
    def _on_pause_resume(self):
        """Toggle pause/resume automation"""
        if not self.worker or not self.worker.isRunning():
            return
        
        if self.pause_btn.isChecked():
            # Pausing
            self.pause_btn.setText("RESUME")
            self.connection_status.setText("PAUSED")
            self.connection_status.setStyleSheet("""
                font-size: 13px;
                font-weight: 600;
                color: white;
                background-color: #f59e0b;
                padding: 16px 24px;
                border-radius: 8px;
                letter-spacing: 0.5px;
            """)
            self._log("warning", "Paused - Click Resume to continue")
            # Note: Actual pause logic would need to be implemented in worker thread
        else:
            # Resuming
            self.pause_btn.setText("PAUSE")
            self.connection_status.setText("RUNNING")
            self.connection_status.setStyleSheet("""
                font-size: 13px;
                font-weight: 600;
                color: white;
                background-color: #10b981;
                padding: 16px 24px;
                border-radius: 8px;
                letter-spacing: 0.5px;
            """)
            self._log("success", "Resumed")
            # Note: Actual resume logic would need to be implemented in worker thread
    
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
        try:
            provider = self.ai_provider_combo.currentText()
            model = self.model_combo.currentText()
            api_key = self.api_key_edit.text()
            
            if not api_key or api_key == "not-needed":
                if "Ollama" not in provider:
                    QtWidgets.QMessageBox.warning(
                        self, "Missing API Key",
                        "Please enter your API key to test the connection."
                    )
                    return
            
            self._log("info", f"Testing connection to {provider}...")
            
            # Show processing dialog
            progress = QtWidgets.QProgressDialog(
                "Testing AI connection...", "Cancel", 0, 0, self
            )
            progress.setWindowTitle("Testing")
            progress.setWindowModality(QtCore.Qt.WindowModal)
            progress.show()
            QtWidgets.QApplication.processEvents()
            
            # Actually test the AI connection
            test_success = False
            error_msg = ""
            
            try:
                provider_name = self.ai_provider_combo.currentText().split()[0].lower()
                
                # Test based on provider type
                if "groq" in provider_name:
                    from groq import Groq
                    client = Groq(api_key=api_key)
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=5
                    )
                    test_success = True
                    
                elif "openai" in provider_name or "ollama" in provider_name:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key if api_key != "not-needed" else "dummy")
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=5
                    )
                    test_success = True
                    
                elif "gemini" in provider_name or "google" in provider_name:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    model_obj = genai.GenerativeModel(model)
                    response = model_obj.generate_content("test")
                    test_success = True
                    
                elif "deepseek" in provider_name:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=5
                    )
                    test_success = True
                    
                else:
                    # Generic OpenAI-compatible test
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=5
                    )
                    test_success = True
                    
            except Exception as api_error:
                test_success = False
                error_msg = str(api_error)
            
            progress.close()
            
            if test_success:
                QtWidgets.QMessageBox.information(
                    self, "Connection Successful",
                    f"✅ Successfully connected to {provider}\n\nModel: {model}\n\nAPI is working correctly!"
                )
                self._log("success", f"Connection test successful: {provider}")
            else:
                raise Exception(error_msg)
            
        except Exception as e:
            self._log("error", f"Connection test failed: {e}")
            QtWidgets.QMessageBox.critical(
                self, "Connection Failed",
                f"❌ Failed to connect to AI provider\n\nError: {str(e)}"
            )
    
    def _load_personal_settings(self):
        """Load saved personal information from config/personals.py"""
        try:
            from modules.settings_manager import load_personals_settings
            
            personals = load_personals_settings()
            
            if personals:
                # Load data into form fields
                self.name_edit.setText(personals.get("full_name", ""))
                self.email_edit.setText(personals.get("email", ""))
                self.phone_edit.setText(personals.get("phone", ""))
                self.linkedin_edit.setText(personals.get("linkedin_url", ""))
                self.company_edit.setText(personals.get("current_company", ""))
                self.title_edit.setText(personals.get("current_title", ""))
                self.experience_spin.setValue(personals.get("years_of_experience", 0))
                self.city_edit.setText(personals.get("city", ""))
                self.state_edit.setText(personals.get("state", ""))
                self.country_edit.setText(personals.get("country", ""))
                self.zip_edit.setText(personals.get("zip_code", ""))
                self.website_edit.setText(personals.get("website", ""))
                self.github_edit.setText(personals.get("github", ""))
                
                self._log("info", f"Loaded personal information for {personals.get('full_name', 'user')}")
            else:
                self._log("warning", "No personal information configured yet")
        except Exception as e:
            self._log("debug", f"Could not load personal settings: {e}")
    
    def _save_settings(self):
        """Save settings including personal information"""
        try:
            import os
            
            # Save personal information to config/personals.py
            personals_path = os.path.join(os.path.dirname(__file__), "config", "personals.py")
            
            personal_data = {
                "full_name": self.name_edit.text().strip(),
                "email": self.email_edit.text().strip(),
                "phone": self.phone_edit.text().strip(),
                "linkedin_url": self.linkedin_edit.text().strip(),
                "current_company": self.company_edit.text().strip(),
                "current_title": self.title_edit.text().strip(),
                "years_of_experience": self.experience_spin.value(),
                "city": self.city_edit.text().strip(),
                "state": self.state_edit.text().strip(),
                "country": self.country_edit.text().strip(),
                "zip_code": self.zip_edit.text().strip(),
                "website": self.website_edit.text().strip(),
                "github": self.github_edit.text().strip(),
            }
            
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(personals_path), exist_ok=True)
            
            # Write to personals.py
            with open(personals_path, "w", encoding="utf-8") as f:
                f.write("'''\n")
                f.write("Personal Information Configuration\n")
                f.write("Auto-generated by ApplyFlow GUI\n")
                f.write("'''\n\n")
                
                for key, value in personal_data.items():
                    if isinstance(value, str):
                        f.write(f'{key} = "{value}"\n')
                    else:
                        f.write(f'{key} = {value}\n')
            
            self._log("success", "Settings saved")
            QtWidgets.QMessageBox.information(
                self, "Saved", 
                "Settings saved successfully!\n\n"
                "✅ Personal information configured\n"
                "✅ Ready for job applications"
            )
        except Exception as e:
            self._log("error", f"Failed to save settings: {e}")
            QtWidgets.QMessageBox.critical(
                self, "Error", 
                f"Failed to save settings:\n{str(e)}"
            )
    
    def _show_about(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.about(
            self, "About ApplyFlow",
            "<h2 style='color: #2962ff;'>⚡ ApplyFlow</h2>"
            "<p style='font-size: 14px; font-weight: 500;'>Version 1.0 - Professional Edition</p>"
            "<p style='color: #5f6368; margin-top: 12px;'>AI-powered job application automation platform</p>"
            "<p style='color: #5f6368;'>Streamline your job search with intelligent automation</p>"
            "<p style='color: #ea4335; font-weight: 600; margin-top: 16px;'>⚠️ For Educational & Personal Use Only</p>"
            "<p style='color: #888; font-size: 12px; margin-top: 12px;'>Use responsibly and comply with LinkedIn's Terms of Service</p>"
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
            # Import modules
            import modules.open_chrome as chrome_module
            from modules.automation_manager import LinkedInSession

            self.emit_log("Opening browser...", "info")
            chrome_module.open_browser()

            # Access the global variables AFTER opening browser
            d = chrome_module.driver
            w = chrome_module.wait
            a = chrome_module.actions

            if not d or not w:
                self.emit_log("Browser failed to initialize", "error")
                self.finished_signal.emit({})
                return

            session = LinkedInSession(d, w, a, log_callback=self.emit_log)
            
            # Wire progress callbacks
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

            try:
                session.app_manager.progress_callback = on_progress
                session.app_manager.form_progress_callback = on_form_progress
            except Exception:
                try:
                    session.job_manager.progress_callback = on_progress
                    session.job_manager.form_progress_callback = on_form_progress
                except Exception:
                    pass

            # CAPTCHA handling
            try:
                from modules import error_recovery
                mgr = getattr(error_recovery, 'current_recovery_manager', None)
                if mgr:
                    try:
                        mgr.config.captcha_blocking_wait = True
                        mgr.config.captcha_pause_callback = lambda msg: self.captcha_pause_signal.emit(msg or "CAPTCHA detected")
                        self.recovery_manager = mgr
                    except Exception:
                        pass
            except Exception:
                pass

            # Run automation
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
    app.setStyle("Fusion")
    
    window = MaterialDesignGUI()
    window.show()
    
    sys.exit(app.exec())
