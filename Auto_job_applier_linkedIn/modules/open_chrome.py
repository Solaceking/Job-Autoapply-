'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''

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
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Additional stealth options
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        
        if run_in_background:
            options.add_argument("--headless")
        
        if disable_extensions:
            options.add_argument("--disable-extensions")

        print_lg("IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM! Or it's highly likely that application will just open browser and not do anything!")
        
        if safe_mode:
            print_lg("SAFE MODE: Guest profile - browsing history will not be saved!")
        else:
            profile_dir = find_default_profile_directory()
            if profile_dir:
                options.add_argument(f"--user-data-dir={profile_dir}")
                print_lg(f"Using Chrome profile: {profile_dir}")
            else:
                print_lg("Warning: Could not find default Chrome profile, using temporary profile")

        if stealth_mode:
            print_lg("Downloading Chrome Driver... This may take some time!")
            driver = uc.Chrome(options=options)
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
        
        driver.maximize_window()
        wait = WebDriverWait(driver, 5)
        actions = ActionChains(driver)
        
        print_lg("Chrome browser opened successfully!")
        
    except TimeoutError as e:
        msg = 'Seems like either... \n\n1. Chrome is already running. \nA. Close all Chrome windows and try again. \n\n2. Google Chrome or Chromedriver is out dated. \nA. Update browser and Chromedriver (You can run "windows-setup.bat" in /setup folder for Windows PC to update Chromedriver)! \n\n3. If error occurred when using "stealth_mode", try reinstalling undetected-chromedriver. \nA. Open a terminal and use commands "pip uninstall undetected-chromedriver" and "pip install undetected-chromedriver". \n\n\nIf issue persists, try Safe Mode. Set, safe_mode = True in config.py \n\nPlease check GitHub discussions/support for solutions https://github.com/GodsScion/Auto_job_applier_linkedIn \n                                   OR \nReach out in discord ( https://discord.gg/fFp7uUzWCY )'
        print_lg(msg)
        critical_error_log("In Opening Chrome", e)
        try:
            from pyautogui import alert
            alert(msg, "Error in opening chrome")
        except ImportError:
            pass
        if driver:
            driver.quit()
            
    except Exception as e:
        msg = 'Seems like either... \n\n1. Chrome is already running. \nA. Close all Chrome windows and try again. \n\n2. Google Chrome or Chromedriver is out dated. \nA. Update browser and Chromedriver (You can run "windows-setup.bat" in /setup folder for Windows PC to update Chromedriver)! \n\n3. If error occurred when using "stealth_mode", try reinstalling undetected-chromedriver. \nA. Open a terminal and use commands "pip uninstall undetected-chromedriver" and "pip install undetected-chromedriver". \n\n\nIf issue persists, try Safe Mode. Set, safe_mode = True in config.py \n\nPlease check GitHub discussions/support for solutions https://github.com/GodsScion/Auto_job_applier_linkedIn \n                                   OR \nReach out in discord ( https://discord.gg/fFp7uUzWCY )'
        print_lg(msg)
        critical_error_log("In Opening Chrome", e)
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
