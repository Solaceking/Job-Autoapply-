# 🚀 LinkedIn Auto Job Applier

<div align="center">

**Automate your LinkedIn job applications with AI-powered intelligence**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Qt](https://img.shields.io/badge/Qt-PySide6-green.svg)](https://www.qt.io/qt-for-python)
[![License](https://img.shields.io/badge/License-AGPL--3.0-red.svg)](https://www.gnu.org/licenses/agpl-3.0.en.html)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

*A production-ready Windows desktop application for automated LinkedIn job applications*

</div>

---

## ⚠️ **IMPORTANT DISCLAIMER**

**This project is for EDUCATIONAL PURPOSES ONLY**

Using automation on LinkedIn may violate their [Terms of Service](https://www.linkedin.com/legal/user-agreement) and could result in:
- Account restrictions or permanent bans
- Loss of access to your LinkedIn account
- Potential legal consequences

**Use at your own risk.** Only use with test accounts you don't mind losing.

---

## ✨ Features

### 🎨 **Modern Qt GUI**
- **Professional Interface**: Clean, modern Qt-based desktop application
- **Left Navigation Rail**: Easy access to Dashboard, Jobs, Queue, History, AI, and Settings
- **Real-time Progress Tracking**: Live statistics and progress bars
- **Color-coded Logging**: Info, Success, Warning, Error levels
- **CAPTCHA Handling**: Non-modal banner system for manual CAPTCHA solving

### 🤖 **AI-Powered Automation**
- **Multi-Provider Support**: OpenAI (GPT-4), Google Gemini, DeepSeek
- **Smart Question Answering**: AI analyzes and answers application questions
- **Skills Extraction**: Automatic resume parsing and skills matching
- **Custom Responses**: Tailored answers based on job requirements

### 🔧 **Robust Automation**
- **Selenium-based**: Reliable web automation with undetected ChromeDriver
- **Error Recovery**: Comprehensive error handling and auto-recovery
- **Form Handler**: Intelligent form filling with validation
- **Multi-language Support**: Filter jobs by language preference
- **Easy Apply Focus**: Target LinkedIn's Easy Apply jobs

### 📊 **Advanced Features**
- **Progress Tracking**: Real-time application statistics
- **History Management**: Track all applications with detailed logs
- **Queue System**: Manage and prioritize job applications
- **Settings Persistence**: Save and restore configurations
- **Thread-safe Operations**: Non-blocking UI with background processing

---

## 🎯 Quick Start

### **Option 1: Run from Source** (Development)

```bash
# Clone the repository
git clone https://github.com/Solaceking/Job-Autoapply-.git
cd Job-Autoapply-/Auto_job_applier_linkedIn

# Install dependencies
pip install -r requirements.txt

# Configure credentials (see Configuration section)
# Edit config/secrets.py

# Run the application
python main.py
```

### **Option 2: Windows Executable** (Production)

```bash
# Build standalone .exe
.\build.bat

# Run the executable
dist\AutoJobApplier\AutoJobApplier.exe
```

---

## ⚙️ Configuration

### **1. LinkedIn Credentials** 
Edit `config/secrets.py`:
```python
username = "your.email@example.com"
password = "your_secure_password"
```

### **2. Job Search Parameters**
Edit `config/search.py`:
```python
search_terms = ["Python Developer", "Software Engineer"]
search_location = "United States"
easy_apply_only = True
date_posted = "Past week"  # Options: 24hr, week, month, any
```

### **3. AI Configuration** (Optional)
Edit `config/secrets.py`:
```python
use_AI = True
ai_provider = "openai"  # Options: openai, gemini, deepseek
llm_api_key = "your-api-key-here"
llm_model = "gpt-4o"  # or gpt-3.5-turbo, gemini-pro, etc.
```

### **4. Application Settings**
Edit `config/settings.py`:
```python
stealth_mode = True           # Use undetected ChromeDriver
headless = False              # Run browser in background
safe_mode = True              # Use guest profile
max_applications = 30         # Daily application limit
```

---

## 📦 Project Structure

```
Auto_job_applier_linkedIn/
├── gui.py                      # Main Qt GUI application
├── main.py                     # Entry point
├── runAiBot.py                 # Core automation engine
├── build.bat                   # Windows build script
├── requirements.txt            # Python dependencies
│
├── config/
│   ├── search.py              # Job search configuration
│   ├── secrets.py             # Credentials & API keys
│   └── settings.py            # Application settings
│
├── modules/
│   ├── automation_manager.py  # LinkedIn session management
│   ├── error_recovery.py      # Error handling & recovery
│   ├── form_handler.py        # Form filling automation
│   ├── open_chrome.py         # Browser initialization
│   ├── question_handler.py    # Application question logic
│   └── settings_manager.py    # Settings persistence
│
├── tests/
│   ├── test_error_recovery.py
│   ├── test_form_handler.py
│   └── test_form_handler_integration.py
│
└── docs/
    ├── START_HERE.md           # Project overview
    ├── QUICKSTART.md           # 5-minute setup guide
    ├── SETUP_GUIDE.md          # Detailed configuration
    └── IMPLEMENTATION_SUMMARY.md  # Technical documentation
```

---

## 🛠️ Development

### **Prerequisites**
- Python 3.11 or higher
- Google Chrome browser
- Windows 10+ (for .exe builds)

### **Install Development Dependencies**
```bash
pip install -r requirements.txt
pip install pytest pytest-cov  # For testing
```

### **Run Tests**
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=modules tests/

# Run specific test
pytest tests/test_form_handler.py
```

### **Build Windows Executable**
```bash
# Automated build
.\build.bat

# Manual build
pyinstaller --name "AutoJobApplier" --windowed --onefile main.py
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [START_HERE.md](Auto_job_applier_linkedIn/START_HERE.md) | Project overview and quick links |
| [QUICKSTART.md](Auto_job_applier_linkedIn/QUICKSTART.md) | 5-minute setup guide |
| [SETUP_GUIDE.md](Auto_job_applier_linkedIn/SETUP_GUIDE.md) | Detailed configuration guide |
| [IMPLEMENTATION_SUMMARY.md](Auto_job_applier_linkedIn/IMPLEMENTATION_SUMMARY.md) | Technical architecture |
| [DEVELOPMENT_ROADMAP.md](Auto_job_applier_linkedIn/DEVELOPMENT_ROADMAP.md) | Future enhancements |

---

## 🐛 Troubleshooting

### **Common Issues**

| Issue | Solution |
|-------|----------|
| Chrome not found | Install Google Chrome or set `stealth_mode = True` |
| Login fails | Check credentials, disable 2FA temporarily |
| GUI won't start | Run `pip install -r requirements.txt --upgrade` |
| CAPTCHA blocks | Solve manually in browser, click "Resume" |
| Build fails | Ensure Python 3.11+ and PyInstaller installed |

### **Debug Mode**
Enable detailed logging in `config/settings.py`:
```python
verbose = True
debug_mode = True
```

---

## 🎓 What You Can Learn

This project demonstrates:
- ✅ **Web Automation**: Selenium, ChromeDriver, form handling
- ✅ **GUI Development**: Qt/PySide6, threading, signals/slots
- ✅ **AI Integration**: OpenAI, Gemini, DeepSeek APIs
- ✅ **Error Handling**: Recovery strategies, CAPTCHA management
- ✅ **Python Packaging**: PyInstaller, Windows executables
- ✅ **Testing**: Unit tests, integration tests, pytest
- ✅ **Configuration Management**: Multi-file config system
- ✅ **Threading**: Non-blocking UI, background workers

---

## 🚦 Roadmap

### **Version 2.1** (Planned)
- [ ] Multi-platform support (macOS, Linux)
- [ ] Resume customization per application
- [ ] Advanced filtering and job scoring
- [ ] Application tracking dashboard
- [ ] Email notifications

### **Version 3.0** (Future)
- [ ] Web-based UI (Flask/React)
- [ ] Cloud deployment options
- [ ] Team collaboration features
- [ ] Advanced analytics and reporting
- [ ] Browser extension

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| **Total Lines of Code** | 5,200+ |
| **Python Files** | 13 |
| **Test Files** | 3 |
| **Documentation** | 3,000+ lines |
| **Supported AI Providers** | 3 |
| **Languages** | English (extensible) |

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0).

See the [LICENSE](LICENSE) file for details.

**Key points:**
- ✅ Free to use and modify
- ✅ Open source
- ⚠️ Must disclose source if distributed
- ⚠️ Network use counts as distribution

---

## 🙏 Acknowledgments

- **Original Author**: [Sai Vignesh Golla](https://github.com/GodsScion)
- **Original Project**: [Auto_job_applier_linkedIn](https://github.com/GodsScion/Auto_job_applier_linkedIn)
- **Community**: Discord support community
- **Contributors**: All contributors to this fork

---

## 📞 Support

- **Documentation**: See `/docs` folder
- **Issues**: [GitHub Issues](https://github.com/Solaceking/Job-Autoapply-/issues)
- **Original Discord**: [Join Community](https://discord.gg/fFp7uUzWCY)

---

## ⭐ Show Your Support

If this project helped you, please give it a ⭐️ on GitHub!

---

<div align="center">

**Made with ❤️ for job seekers worldwide**

*Remember: Use responsibly and ethically*

</div>
