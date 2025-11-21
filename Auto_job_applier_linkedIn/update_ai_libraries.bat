@echo off
echo ========================================
echo Updating AI Libraries for ApplyFlow
echo ========================================
echo.
echo This will update the AI libraries to fix the 'proxies' error
echo.

pip install --upgrade openai>=1.54.0
pip install --upgrade google-generativeai>=0.8.0
pip install --upgrade groq>=0.12.0

echo.
echo ========================================
echo Update Complete!
echo ========================================
echo.
echo You can now run ApplyFlow with:
echo python gui.py
echo.
pause
