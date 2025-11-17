# 📦 Deployment Guide - LinkedIn Auto Job Applier

Complete guide for building, testing, and deploying the production-ready Windows application.

---

## 🎯 Pre-Deployment Checklist

### **Prerequisites**
- [ ] Python 3.11 or higher installed
- [ ] Google Chrome browser installed
- [ ] Git installed and configured
- [ ] Windows 10+ operating system
- [ ] Administrator privileges (for installation)

### **Configuration**
- [ ] `config/secrets.py` configured with credentials
- [ ] `config/search.py` customized for job search
- [ ] `config/settings.py` reviewed and adjusted
- [ ] AI API keys added (if using AI features)
- [ ] Resume files prepared in supported formats

---

## 🛠️ Development Build

### **Step 1: Clone Repository**
```bash
git clone https://github.com/Solaceking/Job-Autoapply-.git
cd Job-Autoapply-/Auto_job_applier_linkedIn
```

### **Step 2: Create Virtual Environment**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Windows Command Prompt:
.venv\Scripts\activate.bat
```

### **Step 3: Install Dependencies**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

### **Step 4: Test Run**
```bash
# Run the Qt GUI application
python main.py

# Or run directly:
python gui.py
```

---

## 🏗️ Production Build

### **Automated Build (Recommended)**

```bash
# Run the build script
.\build.bat
```

This will:
1. ✅ Install/upgrade pip and setuptools
2. ✅ Install PyInstaller
3. ✅ Install all dependencies
4. ✅ Create standalone `.exe` file
5. ✅ Place executable in `dist/` folder

**Output**: `dist/AutoJobApplier.exe` (~200-250 MB)

### **Manual Build**

```bash
# Install PyInstaller
pip install pyinstaller>=6.3.0

# Build with all options
pyinstaller --name "AutoJobApplier" ^
    --windowed ^
    --onefile ^
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
```

### **Build with Icon** (Optional)

```bash
# If you have an icon file
pyinstaller --icon=assets/icon.ico [other options] main.py
```

---

## 🧪 Testing

### **Unit Tests**

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=modules --cov-report=html tests/

# View coverage report
# Open htmlcov/index.html in browser
```

### **Integration Tests**

```bash
# Run integration tests only
pytest tests/test_form_handler_integration.py -v

# Run specific test
pytest tests/test_error_recovery.py::test_captcha_detection -v
```

### **Manual Testing Checklist**

- [ ] Application launches without errors
- [ ] GUI renders correctly
- [ ] Navigation buttons work
- [ ] Job search form accepts input
- [ ] Settings save and load correctly
- [ ] Browser opens successfully
- [ ] LinkedIn login works
- [ ] Job application workflow completes
- [ ] Error handling works (test with invalid credentials)
- [ ] CAPTCHA banner appears when needed
- [ ] Stop button terminates process
- [ ] Progress bars update correctly
- [ ] Logs display properly with color coding

---

## 📦 Distribution

### **Single Executable Distribution**

1. **Test the `.exe`**:
   ```bash
   # Run from dist folder
   cd dist
   .\AutoJobApplier.exe
   ```

2. **Create Distribution Package**:
   ```
   AutoJobApplier-v2.0/
   ├── AutoJobApplier.exe          # Main executable
   ├── README.txt                  # Quick start instructions
   ├── QUICKSTART.md              # Detailed guide
   ├── LICENSE.txt                # License file
   └── config/                    # Configuration templates
       ├── secrets.py.template
       ├── search.py.template
       └── settings.py.template
   ```

3. **Compress for Distribution**:
   ```bash
   # Create ZIP archive
   # Use 7-Zip, WinRAR, or built-in Windows compression
   ```

### **Installer Creation** (Advanced)

#### Using NSIS (Nullsoft Scriptable Install System)

1. **Download NSIS**: https://nsis.sourceforge.io/Download

2. **Create `installer.nsi`**:
   ```nsis
   ; Auto Job Applier Installer Script
   !define APP_NAME "Auto Job Applier"
   !define APP_VERSION "2.0.0"
   !define APP_PUBLISHER "LinkedIn Automation"
   !define APP_EXE "AutoJobApplier.exe"
   
   Name "${APP_NAME} ${APP_VERSION}"
   OutFile "AutoJobApplier-Setup-v${APP_VERSION}.exe"
   InstallDir "$PROGRAMFILES\${APP_NAME}"
   
   Section "Install"
       SetOutPath "$INSTDIR"
       File "dist\${APP_EXE}"
       File /r "config"
       File "README.md"
       File "LICENSE"
       
       CreateDirectory "$SMPROGRAMS\${APP_NAME}"
       CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
       CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
       
       WriteUninstaller "$INSTDIR\Uninstall.exe"
   SectionEnd
   
   Section "Uninstall"
       Delete "$INSTDIR\${APP_EXE}"
       Delete "$INSTDIR\Uninstall.exe"
       RMDir /r "$INSTDIR"
       Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
       Delete "$DESKTOP\${APP_NAME}.lnk"
       RMDir "$SMPROGRAMS\${APP_NAME}"
   SectionEnd
   ```

3. **Build Installer**:
   ```bash
   "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
   ```

---

## 🚀 Deployment Scenarios

### **Scenario 1: Personal Use**

```bash
# Simple distribution
1. Build: .\build.bat
2. Test: dist\AutoJobApplier.exe
3. Move to desired location
4. Create desktop shortcut
5. Configure and run
```

### **Scenario 2: Team Distribution**

```bash
# Package with documentation
1. Build executable
2. Create distribution folder with:
   - AutoJobApplier.exe
   - Configuration templates
   - README and guides
   - Example resume files
3. Compress to ZIP
4. Share via email/cloud storage
5. Provide setup instructions
```

### **Scenario 3: Public Release**

```bash
# Full release package
1. Build and test executable
2. Create installer with NSIS
3. Generate release notes
4. Create GitHub release
5. Upload installer and ZIP
6. Update documentation
7. Announce on social media
```

---

## 📋 Configuration for Deployment

### **Template Files**

Create sanitized template versions of config files:

#### `config/secrets.py.template`
```python
# LinkedIn Credentials
username = "your.email@example.com"  # Replace with your LinkedIn email
password = "your_password_here"       # Replace with your password

# AI Configuration (Optional)
use_AI = False                        # Set to True to enable AI features
ai_provider = "openai"                # Options: openai, gemini, deepseek
llm_api_key = "your-api-key-here"    # Get from provider's website
llm_model = "gpt-4o"                  # Model to use
```

#### `config/search.py.template`
```python
# Job Search Configuration
search_terms = ["Python Developer", "Software Engineer"]
search_location = "United States"
easy_apply_only = True
date_posted = "Past week"  # Options: 24hr, week, month, any
max_applications = 30      # Daily application limit
```

#### `config/settings.py.template`
```python
# Application Settings
stealth_mode = True          # Use undetected ChromeDriver
headless = False             # Run browser in background
safe_mode = True             # Use guest browser profile
keep_screen_awake = False    # Prevent screen from sleeping
run_in_background = False    # Minimize browser interactions
```

### **User Instructions**

Include `FIRST_TIME_SETUP.txt`:
```
=================================================================
Auto Job Applier - First Time Setup
=================================================================

STEP 1: Configure Your Credentials
-----------------------------------
1. Navigate to: config/
2. Open secrets.py in a text editor
3. Replace placeholder values with your real credentials:
   - LinkedIn email
   - LinkedIn password
   - (Optional) AI API keys

STEP 2: Customize Job Search
----------------------------
1. Open config/search.py
2. Update search_terms with desired job titles
3. Set your preferred location
4. Adjust max_applications limit

STEP 3: Review Settings
-----------------------
1. Open config/settings.py
2. Review and adjust automation settings
3. Enable/disable features as needed

STEP 4: Run the Application
---------------------------
1. Double-click AutoJobApplier.exe
2. Review settings in GUI
3. Click "Search & Apply" to start
4. Monitor progress in real-time

TROUBLESHOOTING
---------------
- If Chrome doesn't open: Install Google Chrome
- If login fails: Check credentials, disable 2FA
- If CAPTCHA appears: Solve manually, click Resume
- For errors: Check logs/ folder for details

SUPPORT
-------
- Documentation: See docs/ folder
- Issues: GitHub Issues page
- Community: Discord server (link in README)

=================================================================
```

---

## 🔒 Security Considerations

### **Before Distribution**

- [ ] Remove all real credentials from config files
- [ ] Clear all logs and temporary files
- [ ] Remove `.venv` and `__pycache__` folders
- [ ] Ensure `.gitignore` is properly configured
- [ ] Don't include personal data in build
- [ ] Test with fresh configuration

### **User Security Warnings**

Include in README/documentation:
```
⚠️ SECURITY WARNINGS:
- NEVER share your credentials
- Use strong, unique passwords
- Consider using test accounts
- Enable 2FA after testing
- Don't store credentials in plain text (future: use keyring)
- Be aware of LinkedIn's Terms of Service
- Use at your own risk
```

---

## 📊 Release Checklist

### **Pre-Release**
- [ ] All tests passing
- [ ] Code reviewed and cleaned
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] Changelog created
- [ ] Build tested on clean Windows machine
- [ ] Configuration templates created
- [ ] User guides written

### **Release**
- [ ] Create Git tag (e.g., v2.0.0)
- [ ] Build final executable
- [ ] Create installer (if applicable)
- [ ] Create distribution packages
- [ ] Upload to GitHub Releases
- [ ] Update README with release notes
- [ ] Announce release

### **Post-Release**
- [ ] Monitor for issues
- [ ] Respond to user feedback
- [ ] Update documentation as needed
- [ ] Plan next iteration

---

## 📈 Version Control

### **Versioning Scheme**

Use Semantic Versioning (SemVer): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features, backward-compatible (e.g., 2.0.0 → 2.1.0)
- **PATCH**: Bug fixes (e.g., 2.1.0 → 2.1.1)

### **Tagging Releases**

```bash
# Create annotated tag
git tag -a v2.0.0 -m "Release v2.0.0 - Qt GUI Production Release"

# Push tag to remote
git push origin v2.0.0

# Create GitHub release from tag
# (Use GitHub web interface)
```

---

## 🎓 Best Practices

1. **Always test on clean system** before distribution
2. **Provide clear documentation** for end users
3. **Include error reporting** mechanism
4. **Keep dependencies up to date** (security patches)
5. **Maintain changelog** for transparency
6. **Respond to user feedback** promptly
7. **Plan for updates** and bug fixes
8. **Consider auto-update** mechanism (future feature)

---

## 📞 Support

For deployment issues:
- **Documentation**: See `/docs` folder
- **GitHub Issues**: Report bugs and request features
- **Community**: Join Discord for help
- **Email**: [Your contact email]

---

## ✅ Final Deployment Command Summary

```bash
# Quick deployment workflow
git pull origin master                # Get latest changes
.\build.bat                           # Build executable
dist\AutoJobApplier.exe              # Test
# Package and distribute
```

---

**Ready to deploy!** 🚀

Your LinkedIn Auto Job Applier is now production-ready for distribution.
