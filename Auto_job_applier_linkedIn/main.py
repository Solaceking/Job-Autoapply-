'''
Auto Job Applier - Windows Native Application Entry Point
Production-Ready Desktop App for LinkedIn Job Automation

This script serves as the entry point for the Windows standalone executable
'''

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Launch the GUI application"""
    try:
        # Prefer Qt GUI if available
        try:
            from qt_gui import MainWindow
            from PySide6 import QtWidgets

            app = QtWidgets.QApplication([])
            w = MainWindow()
            w.show()
            sys.exit(app.exec())
        except Exception:
            # Fallback to legacy Tkinter GUI
            from gui import main as run_gui
            run_gui()
    
    except ImportError as e:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Import Error",
            f"Failed to import required modules:\n\n{str(e)}\n\n"
            "Please ensure all dependencies are installed:\n"
            "pip install -r requirements.txt"
        )
        root.destroy()
        sys.exit(1)
    
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Fatal Error",
            f"An unexpected error occurred:\n\n{str(e)}"
        )
        root.destroy()
        sys.exit(1)


if __name__ == "__main__":
    main()
