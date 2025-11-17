# Auto Job Applier - Setup & Deployment Guide

## Overview
This is a production-ready Windows native application for automating LinkedIn job applications with AI-powered resume customization.

## System Requirements
- **OS**: Windows 10 or later
- **Python**: 3.11 or higher (for development)
- **Chrome/Chromium**: Latest version
- **RAM**: Minimum 4GB
- **Storage**: 500MB free space

## Quick Start (Development)

### 1. Clone Repository
```bash
git clone https://github.com/GodsScion/Auto_job_applier_linkedIn.git
cd Auto_job_applier_linkedIn
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Settings
Edit these files in the `config/` folder:

- **`config/secrets.py`** - LinkedIn credentials & AI API keys
- **`config/personals.py`** - Your personal information
- **`config/questions.py`** - Answers to common application questions
- **`config/search.py`** - Job search preferences
- **`config/settings.py`** - Bot behavior settings

### 4. Run the Application
```bash
python gui.py
```
or
```bash
python main.py
```

## Building Windows Standalone Executable

### Prerequisites
- Python 3.11+ installed and in PATH
- All dependencies installed: `pip install -r requirements.txt`

### Build Steps

#### Option 1: Automatic Build (Recommended)
```bash
# Double-click this file:
build.bat

# Or run from command line:
cd Auto_job_applier_linkedIn
build.bat
```

The script will:
1. ✅ Install/upgrade pip and dependencies
2. ✅ Install PyInstaller
3. ✅ Create standalone executable
4. ✅ Output: `dist/AutoJobApplier/AutoJobApplier.exe`

#### Option 2: Manual Build
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --name "AutoJobApplier" ^
    --windowed ^
    --onefile ^
    --add-data "config;config" ^
    --add-data "modules;modules" ^
    --collect-all selenium ^
    --collect-all undetected_chromedriver ^
    gui.py
```

## Running the Application

### Development Mode
```bash
python gui.py
```

### Standalone Executable (After Build)
```bash
# Navigate to dist folder
cd dist/AutoJobApplier

# Run the executable
AutoJobApplier.exe
```

## Configuration Guide

### LinkedIn Credentials
Edit `config/secrets.py`:
```python
username = "your.email@gmail.com"
password = "your_linkedin_password"
```

### AI Integration (Optional)
For resume customization using AI:

#### OpenAI
```python
use_AI = True
ai_provider = "openai"
llm_api_url = "https://api.openai.com/v1/"
llm_api_key = "sk-..."  # Your OpenAI API key
llm_model = "gpt-4o"
```

#### Google Gemini
```python
use_AI = True
ai_provider = "gemini"
llm_api_key = "your-gemini-api-key"
llm_model = "gemini-1.5-flash"
```

#### Local LLM (Ollama/LM Studio)
```python
use_AI = True
ai_provider = "openai"
llm_api_url = "http://localhost:1234/v1/"
llm_api_key = "not-needed"
llm_model = "llama-2-7b-chat"
llm_spec = "openai-like"
```

### Job Search Preferences
Edit `config/search.py`:
```python
search_terms = ["Python Developer", "Senior Developer", "Full Stack Developer"]
search_location = "United States"
easy_apply_only = True
date_posted = "Past week"
salary = "$100,000+"
```

## Features

✅ **Automated Job Search**: Search LinkedIn jobs by title and location
✅ **Easy Apply**: Automatically applies to jobs with EasyApply
✅ **Form Filling**: Auto-fills application forms with your information
✅ **AI Resume Customization**: Uses AI to tailor resume to job requirements
✅ **Application History**: Tracks all applications with success/failure status
✅ **Multi-Tab Management**: Handles multiple browser tabs efficiently
✅ **Anti-Detection**: Stealth mode to avoid LinkedIn bot detection
✅ **Logging**: Detailed logs for debugging and monitoring
✅ **GUI Interface**: User-friendly Windows native GUI

## Advanced Settings

### GUI Settings (`config/settings.py`)
```python
# Run browser in background (headless)
run_in_background = False

# Enable stealth mode for anti-detection
stealth_mode = False

# Use guest profile (safer)
safe_mode = True

# Keep screen awake during execution
keep_screen_awake = True

# Pause before submitting each application
pause_before_submit = True

# Click speed (randomized 0-N seconds)
click_gap = 2
```

## Troubleshooting

### "Chrome not found" Error
- Ensure Google Chrome is installed in the default location
- On Windows: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- Or download from: https://www.google.com/chrome

### "Chromedriver not found" Error
```bash
# Option 1: Use stealth_mode (auto-downloads chromedriver)
# Edit config/settings.py
stealth_mode = True

# Option 2: Manual chromedriver
# 1. Download from: https://googlechromelabs.github.io/chrome-for-testing/
# 2. Extract to Chrome installation folder
```

### LinkedIn Login Fails
- Verify username and password in `config/secrets.py`
- Check if 2FA is enabled (disable for automation)
- Try `safe_mode = True` in `config/settings.py`

### Application Won't Start
```bash
# Verify all dependencies are installed
pip install -r requirements.txt --upgrade

# Check Python version
python --version  # Should be 3.11+

# Test imports
python -c "from gui import main; print('OK')"
```

## Project Structure
```
Auto_job_applier_linkedIn/
├── gui.py                    # Main GUI application
├── main.py                   # Windows app entry point
├── runAiBot.py              # Original automation script
├── app.py                    # Flask web dashboard (optional)
├── build.bat                # Windows build script
├── requirements.txt         # Python dependencies
├── config/                  # Configuration files
│   ├── personals.py        # Personal information
│   ├── questions.py        # Application answers
│   ├── search.py           # Search preferences
│   ├── secrets.py          # Credentials & API keys
│   └── settings.py         # Bot settings
├── modules/                 # Core automation modules
│   ├── open_chrome.py      # Browser initialization
│   ├── helpers.py          # Utility functions
│   ├── clickers_and_finders.py  # Element interaction
│   ├── validator.py        # Configuration validation
│   └── ai/                 # AI integrations
├── templates/              # HTML templates (Flask)
└── all_excels/             # Application history (CSV)
```

## Performance Tips

1. **Use Stealth Mode** for longer sessions (anti-detection)
2. **Enable Headless Mode** to reduce resource usage
3. **Limit Applications**: Set reasonable limits in search config
4. **Use Pause Settings** to review each application before submit
5. **Monitor Logs** for errors and adjust configuration

## API Costs (If Using AI)

### OpenAI
- GPT-4: $0.03-0.06 per 1K tokens
- GPT-4o: $0.015 per 1K tokens (recommended)
- ~$0.50-2.00 per 100 applications

### Google Gemini
- Gemini 1.5: $0.075-0.30 per 1M tokens
- ~$0.10-0.50 per 100 applications (very cheap)

### DeepSeek
- Most affordable option (~$0.01-0.05 per 100 apps)

## Support & Community

- **GitHub Issues**: https://github.com/GodsScion/Auto_job_applier_linkedIn/issues
- **Discord Community**: https://discord.gg/fFp7uUzWCY
- **Original Repository**: https://github.com/GodsScion/Auto_job_applier_linkedIn

## License

GNU Affero General Public License v3.0
See LICENSE file for details

## Disclaimer

⚠️ **Important**: 
- This tool automates LinkedIn, which may violate LinkedIn's Terms of Service
- Use at your own risk on accounts you don't mind getting restricted
- Not recommended for production/professional accounts
- For educational purposes only
- Use responsibly and ethically

## Changelog

### v2024.12.29
- ✨ New production-ready Tkinter GUI
- 🎨 Tabbed configuration interface
- 📊 Advanced logging with color-coded levels
- ⚙️ Windows native application support
- 🔧 Improved error handling and recovery
- 📦 PyInstaller build script for .exe packaging
- 📝 Comprehensive documentation

