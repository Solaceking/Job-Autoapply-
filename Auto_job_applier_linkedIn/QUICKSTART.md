# Auto Job Applier - Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```powershell
cd Auto_job_applier_linkedIn
pip install -r requirements.txt
```

### 2. Configure LinkedIn Credentials
Open `config/secrets.py` and enter:
```python
username = "your_linkedin_email@example.com"
password = "your_linkedin_password"
```

### 3. Configure Search Preferences
Open `config/search.py` and customize:
```python
search_terms = ["Python Developer", "Senior Developer"]
search_location = "United States"
easy_apply_only = True
date_posted = "Past week"
```

### 4. Run the GUI
```powershell
python gui.py
```

---

## 🎯 GUI Features

### Configuration Tabs
- **Job Search**: Specify job title, location, and application limits
- **Credentials**: LinkedIn email/password and resume path
- **Settings**: Headless mode, stealth mode, AI integration, etc.

### Controls
- **▶ START**: Begin automated job application
- **⏹ STOP**: Stop the running process
- **🗑 CLEAR LOG**: Clear the log output

### Live Logging
Color-coded logs show:
- 🔵 **Info** (blue) - Status updates
- 🟢 **Success** (green) - Completed actions
- 🟠 **Warning** (orange) - Potential issues
- 🔴 **Error** (red) - Problems requiring attention
- ⚫ **Debug** (gray) - Technical details

---

## 📦 Build Windows Executable

### Automatic Build
```powershell
cd Auto_job_applier_linkedIn
.\build.bat
```

Executable will be created at: `dist\AutoJobApplier\AutoJobApplier.exe`

### Manual Build
```powershell
pip install pyinstaller
pyinstaller --name "AutoJobApplier" --windowed --onefile gui.py
```

---

## ⚙️ Essential Configuration Files

### config/secrets.py
```python
username = "your_email@gmail.com"      # LinkedIn email
password = "your_password"             # LinkedIn password
use_AI = True                          # Enable AI features
ai_provider = "openai"                 # "openai", "gemini", "deepseek"
llm_api_key = "sk-..."                 # API key for chosen provider
llm_model = "gpt-4o"                   # Model name
```

### config/search.py
```python
search_terms = ["Python Developer", "Software Engineer"]
search_location = "United States"
easy_apply_only = True
date_posted = "Past week"
experience_level = []  # Leave empty for all levels
job_type = ["Full-time"]
salary = "$100,000+"
```

### config/questions.py
```python
default_resume_path = "path/to/resume.pdf"
years_of_experience = "5"
require_visa = "No"
linked_in = "https://www.linkedin.com/in/yourprofile"
desired_salary = 150000
```

### config/settings.py
```python
run_in_background = False      # Headless mode
stealth_mode = False           # Anti-detection
safe_mode = True               # Guest profile
keep_screen_awake = True       # Prevent sleep
pause_before_submit = True     # Review before apply
```

---

## 🚀 Running on Startup (Optional)

### Windows Startup Shortcut
1. Create shortcut to: `dist\AutoJobApplier\AutoJobApplier.exe`
2. Right-click → Properties
3. Advanced → Check "Run as administrator"
4. Move to: `C:\Users\[YourUsername]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

### Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger and action to run the .exe
4. Choose "Run with highest privileges"

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Chrome not found | Install Google Chrome or use `stealth_mode = True` |
| Login fails | Disable 2FA, verify credentials in `config/secrets.py` |
| GUI won't start | Run: `pip install -r requirements.txt --upgrade` |
| Build fails | Ensure Python 3.11+ is installed |
| No applications found | Check job search filters in `config/search.py` |

---

## 📊 Application History

Applications are tracked in: `all_excels/all_applied_applications_history.csv`

Columns:
- Timestamp
- Job Title
- Company
- Location
- Status (Applied/Failed)
- Error Details

---

## 💡 Pro Tips

1. **Test First**: Run on a secondary account before production
2. **Monitor Logs**: Check the log window for errors
3. **Gradual Scaling**: Start with 10-20 applications, increase gradually
4. **Use AI**: Customize resumes per job = higher acceptance rates
5. **Pause Reviews**: Enable `pause_before_submit` initially
6. **Schedule Runs**: Run during off-hours to appear natural
7. **Rotate Credentials**: Use different sessions occasionally

---

## 📞 Support

- **GitHub**: https://github.com/GodsScion/Auto_job_applier_linkedIn
- **Discord**: https://discord.gg/fFp7uUzWCY
- **Issues**: Check existing issues or create a new one

---

## ⚠️ Important Disclaimer

This tool automates LinkedIn job applications. While educational, it may:
- Violate LinkedIn's Terms of Service
- Result in account restrictions/bans
- Trigger LinkedIn's anti-bot systems

**Use responsibly and at your own risk.**
