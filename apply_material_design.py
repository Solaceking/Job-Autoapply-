#!/usr/bin/env python3
"""
Script to apply Material Design styling to gui.py
This script adds Google Material Design 3 styles to make the GUI look professional
"""

import re

def apply_material_design():
    """Apply Material Design styles to gui.py"""
    
    # Read the current GUI file
    with open('Auto_job_applier_linkedIn/gui.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Material Design CSS stylesheet
    material_stylesheet = '''
        # Set Material Design color palette
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1765cc;
            }
            QPushButton:pressed {
                background-color: #1557b0;
            }
            QPushButton:disabled {
                background-color: #dadce0;
                color: #80868b;
            }
            QLineEdit, QSpinBox, QComboBox {
                border: 1px solid #dadce0;
                border-radius: 8px;
                padding: 10px 12px;
                background-color: white;
                selection-background-color: #1a73e8;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 2px solid #1a73e8;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #e8eaed;
                border-radius: 12px;
                margin-top: 12px;
                padding: 20px;
                font-weight: 500;
                font-size: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #202124;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #e8eaed;
                border-radius: 12px;
                gridline-color: #f1f3f4;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e8eaed;
                font-weight: 500;
                color: #5f6368;
            }
            QProgressBar {
                border: none;
                border-radius: 8px;
                background-color: #e8eaed;
                text-align: center;
                height: 16px;
            }
            QProgressBar::chunk {
                background-color: #1a73e8;
                border-radius: 8px;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #e8eaed;
                border-radius: 12px;
                padding: 12px;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #5f6368;
            }
            QCheckBox::indicator:checked {
                background-color: #1a73e8;
                border-color: #1a73e8;
            }
            QTabWidget::pane {
                border: 1px solid #e8eaed;
                border-radius: 12px;
                background-color: white;
                padding: 16px;
            }
            QTabBar::tab {
                background-color: transparent;
                color: #5f6368;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #1a73e8;
                border-bottom: 3px solid #1a73e8;
            }
            QTabBar::tab:hover {
                background-color: #f1f3f4;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #e8eaed;
                border-radius: 12px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            QListWidget::item:hover {
                background-color: #f1f3f4;
            }
        """)
        '''
    
    # Replace _setup_ui method to add stylesheet
    setup_ui_pattern = r'(    def _setup_ui\(self\):\s*""".*?"""\s*)(central = QtWidgets\.QWidget\(\))'
    
    replacement = r'\1' + material_stylesheet + r'\n        \2'
    
    content = re.sub(setup_ui_pattern, replacement, content, flags=re.DOTALL)
    
    # Update navigation rail styling
    nav_old = '''nav.setStyleSheet("""
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
        """)'''
    
    nav_new = '''nav.setStyleSheet("""
            QFrame {
                background-color: white;
                border-right: 1px solid #e8eaed;
            }
            QPushButton {
                background-color: transparent;
                color: #5f6368;
                border: none;
                padding: 8px;
                text-align: center;
                font-size: 12px;
                font-weight: 500;
                border-radius: 16px;
                margin: 4px;
            }
            QPushButton:hover {
                background-color: #f1f3f4;
            }
            QPushButton:checked {
                background-color: #e8f0fe;
                color: #1a73e8;
                font-weight: 600;
            }
        """)'''
    
    content = content.replace(nav_old, nav_new)
    
    # Update nav width
    content = content.replace('nav.setFixedWidth(100)', 'nav.setFixedWidth(88)')
    content = content.replace('btn.setFixedSize(90, 70)', 'btn.setFixedSize(80, 80)')
    
    # Add shadow effect method before _show_about
    shadow_method = '''
    def _create_shadow(self):
        """Create Material Design shadow effect"""
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QtGui.QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        return shadow
    
    '''
    
    content = content.replace('    def _show_about(self):', shadow_method + '    def _show_about(self):')
    
    # Update version number and about dialog
    content = content.replace(
        '"<h2>LinkedIn Auto Job Applier</h2>"',
        '"<div style=\'font-family: Segoe UI, Roboto, Arial; line-height: 1.6;\'>"'
        + '"<h2 style=\'color: #1a73e8; font-weight: 400;\'>LinkedIn Auto Job Applier</h2>"'
    )
    content = content.replace(
        '"<p>Version 2.0.0</p>"',
        '"<p style=\'color: #5f6368; font-size: 14px;\'>Version 3.0.0 - Material Design</p>"'
    )
    content = content.replace(
        '"<p>Automated job application system for LinkedIn</p>"',
        '"<p style=\'color: #202124; font-size: 14px;\'>Automated job application system for LinkedIn with AI-powered features</p>"'
    )
    content = content.replace(
        '"<p><b>⚠️ For Educational Purposes Only</b></p>"',
        '"<p style=\'color: #ea4335; font-weight: 500; font-size: 14px;\'>⚠️ For Educational Purposes Only</p>"'
    )
    content = content.replace(
        '"<p>Use at your own risk. May violate LinkedIn Terms of Service.</p>"',
        '"<p style=\'color: #80868b; font-size: 13px;\'>Use at your own risk. May violate LinkedIn Terms of Service.</p>"'
        + '"</div>"'
    )
    
    # Write the updated content
    with open('Auto_job_applier_linkedIn/gui.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Material Design styling applied successfully!")
    print("📁 Backup saved as: Auto_job_applier_linkedIn/gui_backup.py")

if __name__ == '__main__':
    apply_material_design()
