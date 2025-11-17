'''
Auto Job Applier - Windows Native Application Entry Point
Production-Ready Desktop App for LinkedIn Job Automation

This script serves as the entry point for the Windows standalone executable.
Qt-based GUI for modern, cross-platform experience.
'''

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Launch the Qt GUI application"""
    try:
        from gui import MainWindow
        from PySide6 import QtWidgets
        
        app = QtWidgets.QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName("Auto Job Applier")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("LinkedIn Automation")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())
    
    except ImportError as e:
        # Show error dialog using Qt if PySide6 is missing
        try:
            from PySide6 import QtWidgets
            app = QtWidgets.QApplication(sys.argv)
            QtWidgets.QMessageBox.critical(
                None,
                "Import Error",
                f"Failed to import required modules:\n\n{str(e)}\n\n"
                "Please ensure all dependencies are installed:\n"
                "pip install -r requirements.txt"
            )
        except:
            # Fallback to console error
            print(f"\nERROR: {str(e)}\n")
            print("Please install dependencies: pip install -r requirements.txt\n")
        sys.exit(1)
    
    except Exception as e:
        # Show unexpected error dialog
        try:
            from PySide6 import QtWidgets
            app = QtWidgets.QApplication(sys.argv)
            QtWidgets.QMessageBox.critical(
                None,
                "Fatal Error",
                f"An unexpected error occurred:\n\n{str(e)}"
            )
        except:
            print(f"\nFATAL ERROR: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
