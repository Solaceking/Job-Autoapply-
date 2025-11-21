'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''

# Python 3.12+ compatibility: distutils/LooseVersion were removed
try:  # pragma: no cover - prefers native implementation when available
    from distutils.version import LooseVersion, StrictVersion  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - executed only on Python 3.12+ without distutils
    import re
    import sys
    from functools import total_ordering
    from types import ModuleType

    distutils_module = sys.modules.get("distutils")
    if distutils_module is None:
        distutils_module = ModuleType("distutils")
        sys.modules["distutils"] = distutils_module

    version_module = sys.modules.get("distutils.version")
    if version_module is None:
        version_module = ModuleType("distutils.version")
        sys.modules["distutils.version"] = version_module

    if not hasattr(distutils_module, "version"):
        distutils_module.version = version_module  # type: ignore[attr-defined]

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

    LooseVersion = _LooseVersion
    StrictVersion = _StrictVersion

from modules.helpers import make_directories, find_default_profile_directory, critical_error_log, print_lg
from config.settings import run_in_background, stealth_mode, disable_extensions, safe_mode, file_name, failed_file_name, logs_folder_path, generated_resume_path
from config.questions import default_resume_path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

if stealth_mode:
    import undetected_chromedriver as uc

# Global variables
driver = None
wait = None
actions = None


def open_browser():
    """Initialize and open Chrome browser with configured settings."""
    global driver, wait, actions
    
    try:
        # Close existing driver if any
        if driver:
            try:
                driver.quit()
            except:
                pass
            driver = None
            wait = None
            actions = None
        
        # AGGRESSIVE: Kill any lingering Chrome processes to avoid "window not found" errors
        try:
            import psutil
            import time
            killed_count = 0
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    # Kill Chrome and chromedriver processes
                    if 'chrome' in proc_name or 'chromedriver' in proc_name:
                        proc.kill()
                        killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if killed_count > 0:
                print_lg(f"Cleaned up {killed_count} lingering Chrome processes")
                time.sleep(1)  # Wait for processes to fully terminate
        except ImportError:
            print_lg("psutil not available - skipping process cleanup")
        except Exception as e:
            print_lg(f"Process cleanup warning: {e}")
        
        make_directories([
            file_name,
            failed_file_name,
            logs_folder_path + "/screenshots",
            default_resume_path,
            generated_resume_path + "/temp"
        ])

        # Set up WebDriver with Chrome Profile
        options = uc.ChromeOptions() if stealth_mode else Options()
        
        # Hide automation indicators
        options.add_argument("--disable-blink-features=AutomationControlled")
        # Note: Both excludeSwitches and useAutomationExtension removed
        # These experimental options cause errors in newer Chrome versions
        
        # Additional stealth options
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        
        # CRITICAL: Force new session to avoid "Chrome is already running" error
        options.add_argument("--remote-debugging-port=9222")
        
        if run_in_background:
            options.add_argument("--headless")
        
        if disable_extensions:
            options.add_argument("--disable-extensions")

        print_lg("Preparing to open Chrome browser...")
        
        if safe_mode:
            print_lg("SAFE MODE: Using guest profile")
            # Use incognito/guest mode to avoid profile conflicts
            options.add_argument("--guest")
        else:
            # Use a dedicated automation profile instead of default profile
            import tempfile
            import os
            profile_dir = os.path.join(tempfile.gettempdir(), "chrome_automation_profile")
            options.add_argument(f"--user-data-dir={profile_dir}")
            print_lg(f"Using automation profile: {profile_dir}")

        if stealth_mode:
            print_lg("Opening browser in stealth mode...")
            driver = uc.Chrome(options=options, version_main=None)
        else:
            driver = webdriver.Chrome(options=options)
        
        # Remove automation detection at JavaScript level
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    window.chrome = {
                        runtime: {}
                    };
                """
            })
            print_lg("Automation detection disabled at JavaScript level")
        except Exception as e:
            print_lg(f"Note: Could not disable JS automation detection: {e}")
        
        # Position and maximize window for visibility
        try:
            driver.set_window_position(0, 0)  # Top-left corner
            print_lg("Browser window positioned at top-left")
        except Exception as e:
            print_lg(f"Note: Could not position window: {e}")
        
        driver.maximize_window()
        
        # Bring window to foreground (important for visibility)
        try:
            driver.switch_to.window(driver.current_window_handle)
            
            # Add visual indicator that automation is running
            driver.execute_script("""
                // Add red border to indicate automation is active
                document.body.style.border = '5px solid #ff4444';
                document.body.style.boxSizing = 'border-box';
                
                // Add floating indicator
                var indicator = document.createElement('div');
                indicator.id = 'automation-indicator';
                indicator.innerHTML = '🤖 ApplyFlow Automation Active';
                indicator.style.cssText = `
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 20px;
                    border-radius: 25px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    font-size: 14px;
                    font-weight: 600;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    z-index: 999999;
                    animation: pulse 2s infinite;
                `;
                
                // Add pulsing animation
                var style = document.createElement('style');
                style.innerHTML = `
                    @keyframes pulse {
                        0%, 100% { opacity: 1; transform: scale(1); }
                        50% { opacity: 0.8; transform: scale(1.05); }
                    }
                `;
                document.head.appendChild(style);
                document.body.appendChild(indicator);
            """)
            print_lg("Browser window brought to foreground with visual indicator")
        except Exception as e:
            print_lg(f"Note: Could not bring window to foreground: {e}")
        
        wait = WebDriverWait(driver, 5)
        actions = ActionChains(driver)
        
        print_lg("Chrome browser opened successfully!")
        
    except TimeoutError as e:
        error_details = str(e)
        print_lg(f"ERROR: Browser initialization timeout - {error_details}")
        critical_error_log("Browser Timeout", e)
        if driver:
            try:
                driver.quit()
            except:
                pass
            driver = None
        raise RuntimeError(f"Chrome failed to open (timeout): {error_details}")
            
    except Exception as e:
        error_details = str(e)
        print_lg(f"ERROR: Failed to initialize browser - {error_details}")
        critical_error_log("Browser Init Error", e)
        
        # Provide specific guidance based on error message
        if "chrome not reachable" in error_details.lower():
            print_lg("⚠ Chrome crashed or was closed unexpectedly")
        elif "session not created" in error_details.lower():
            print_lg("⚠ Chrome version mismatch - try updating Chrome or chromedriver")
        elif "invalid argument" in error_details.lower():
            print_lg("⚠ Chrome profile in use - close all Chrome windows and try again")
        
        if driver:
            try:
                driver.quit()
            except:
                pass
            driver = None
        
        raise RuntimeError(f"Chrome failed to open: {error_details}")
        try:
            from pyautogui import alert
            alert(msg, "Error in opening chrome")
        except ImportError:
            pass
        if driver:
            driver.quit()


def close_browser():
    """Close the global browser driver and clear related globals safely."""
    global driver, wait, actions
    try:
        if driver:
            try:
                driver.quit()
            except Exception as inner_e:
                # Log but don't raise - closing should be best-effort
                try:
                    critical_error_log("Error while quitting driver", inner_e)
                except Exception:
                    pass
    except Exception as e:
        try:
            critical_error_log("In close_browser", e)
        except Exception:
            pass
    finally:
        driver = None
        wait = None
        actions = None
