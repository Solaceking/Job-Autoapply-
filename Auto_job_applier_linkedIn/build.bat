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

REM Build the executable
pyinstaller --name "AutoJobApplier" ^
    --windowed ^
    --onefile ^
    --icon=assets\icon.ico ^
    --add-data "config;config" ^
    --add-data "modules;modules" ^
    --add-data "templates;templates" ^
    --collect-all selenium ^
    --collect-all undetected_chromedriver ^
    --hidden-import=selenium ^
    --hidden-import=undetected_chromedriver ^
    --hidden-import=flask ^
    --hidden-import=google.generativeai ^
    --distpath "dist\AutoJobApplier" ^
    gui.py

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
echo Executable created: dist\AutoJobApplier\AutoJobApplier.exe
echo ============================================================================
echo.
echo To run the application, execute:
echo   dist\AutoJobApplier\AutoJobApplier.exe
echo.
echo To create an installer (optional):
echo   1. Download NSIS: https://nsis.sourceforge.io/Main_Page
echo   2. Run: "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
echo.

pause
