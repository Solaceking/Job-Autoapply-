@echo off
REM ============================================================================
REM Auto Job Applier - Windows Build Script
REM ============================================================================
REM This script packages the application into a standalone Windows executable
REM ============================================================================

echo.
echo ============================================================================
echo Auto Job Applier - Windows Build Script
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Installing/Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo.
echo [2/5] Installing PyInstaller...
pip install pyinstaller>=6.0.0

echo.
echo [3/5] Installing project dependencies...
pip install -r requirements.txt

echo.
echo [4/5] Creating standalone executable...
echo.

REM Build the executable with Qt GUI
pyinstaller --name "AutoJobApplier" ^
    --windowed ^
    --onefile ^
    --icon=assets\icon.ico ^
    --add-data "config;config" ^
    --add-data "modules;modules" ^
    --collect-all selenium ^
    --collect-all undetected_chromedriver ^
    --collect-all PySide6 ^
    --hidden-import=selenium ^
    --hidden-import=undetected_chromedriver ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=google.generativeai ^
    --hidden-import=openai ^
    --distpath "dist" ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [5/5] Build Complete!
echo.
echo ============================================================================
echo Executable created: dist\AutoJobApplier.exe
echo ============================================================================
echo.
echo To run the application, execute:
echo   dist\AutoJobApplier.exe
echo.
echo Next Steps:
echo   1. Configure credentials in config/secrets.py
echo   2. Customize job search in config/search.py
echo   3. Run the executable: dist\AutoJobApplier.exe
echo.
echo To create an installer (optional):
echo   1. Download NSIS: https://nsis.sourceforge.io/Main_Page
echo   2. Create installer.nsi script
echo   3. Run: "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
echo.

pause
