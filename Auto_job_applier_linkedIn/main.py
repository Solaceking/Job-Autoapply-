'''
Auto Job Applier - Windows Native Application Entry Point
Production-Ready Desktop App for LinkedIn Job Automation

This script serves as the entry point for the Windows standalone executable.
Qt-based GUI for modern, cross-platform experience.
'''

# Python 3.12+ compatibility: distutils/LooseVersion were removed
# This MUST run before any other imports to ensure undetected_chromedriver works
try:
    from distutils.version import LooseVersion, StrictVersion
except Exception:
    import re
    import sys as _sys
    from functools import total_ordering
    from types import ModuleType

    distutils_module = _sys.modules.get("distutils")
    if distutils_module is None:
        distutils_module = ModuleType("distutils")
        _sys.modules["distutils"] = distutils_module

    version_module = _sys.modules.get("distutils.version")
    if version_module is None:
        version_module = ModuleType("distutils.version")
        _sys.modules["distutils.version"] = version_module

    if not hasattr(distutils_module, "version"):
        distutils_module.version = version_module

    @total_ordering
    class _LooseVersion:
        """Lightweight LooseVersion fallback for undetected_chromedriver."""
        component_re = re.compile(r"(\d+|[a-zA-Z]+|[^a-zA-Z\d]+)")

        def __init__(self, vstring):
            self.vstring = str(vstring)
            self.version = self._parse(self.vstring)

        def _parse(self, vstring):
            parts = []
            for part in self.component_re.findall(vstring):
                if part.isdigit():
                    parts.append(int(part))
                else:
                    parts.append(part.lower())
            return parts

        def _coerce(self, other):
            if isinstance(other, _LooseVersion):
                return other.version
            return self._parse(str(getattr(other, "vstring", other)))

        def __eq__(self, other):
            return self.version == self._coerce(other)

        def __lt__(self, other):
            return self.version < self._coerce(other)

        def __repr__(self):
            return f"LooseVersion('{self.vstring}')"

        def __str__(self):
            return self.vstring

    class _StrictVersion(_LooseVersion):
        pass

    version_module.LooseVersion = _LooseVersion
    version_module.StrictVersion = _StrictVersion
    version_module.__all__ = ["LooseVersion", "StrictVersion"]

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Launch the Qt GUI application"""
    try:
        from gui import MaterialDesignGUI
        from PySide6 import QtWidgets
        
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # Set application metadata
        app.setApplicationName("LinkedIn Auto Job Applier")
        app.setApplicationVersion("3.0.2 - Material Design (Fixed)")
        app.setOrganizationName("LinkedIn Automation")
        
        # Create and show main window
        window = MaterialDesignGUI()
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
