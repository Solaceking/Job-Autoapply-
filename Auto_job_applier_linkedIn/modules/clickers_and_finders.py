'''
Selenium Helper Functions for Finding and Interacting with Elements

This module provides robust, fault-tolerant wrapper functions for common
Selenium operations. All functions handle exceptions gracefully and return
None on failure rather than raising exceptions.

Author:     Auto Job Applier Project
License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
Created:    2025-11-17
Purpose:    Provide reliable element finding and interaction methods
'''

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    InvalidSelectorException
)
import time


def try_xp(driver, xpath: str, timeout: int = 5, return_multiple: bool = False):
    """
    Safely find element(s) by XPath with timeout.
    
    This is a fault-tolerant wrapper around Selenium's find_element_by_xpath.
    Returns None instead of raising exceptions if element not found.
    
    Args:
        driver: Selenium WebDriver instance
        xpath: XPath expression to locate element(s)
        timeout: Maximum seconds to wait for element (default: 5)
        return_multiple: If True, return list of all matching elements (default: False)
    
    Returns:
        WebElement if found (or list if return_multiple=True), None if not found or on error
    
    Usage Examples:
        # Find single element
        button = try_xp(driver, '//button[contains(text(), "Submit")]')
        if button:
            button.click()
        
        # Find multiple elements
        cards = try_xp(driver, '//div[@class="job-card"]', return_multiple=True)
        if cards:
            for card in cards:
                print(card.text)
    
    Edge Cases Handled:
        - Element not found within timeout
        - Invalid XPath syntax
        - Stale element reference
        - Element exists but not visible/interactable
        - Driver is None or closed
        - Multiple elements when expecting one (returns first)
    """
    if not driver:
        return None
    
    try:
        # Validate xpath is not empty
        if not xpath or not isinstance(xpath, str):
            return None
        
        # Wait for element to be present in DOM
        wait = WebDriverWait(driver, timeout)
        
        if return_multiple:
            # Wait for at least one element, then find all
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            elements = driver.find_elements(By.XPATH, xpath)
            return elements if elements else None
        else:
            # Wait for and return single element
            element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return element
    
    except TimeoutException:
        # Element not found within timeout - this is normal, return None
        return None
    
    except InvalidSelectorException:
        # Invalid XPath syntax
        try:
            from modules.helpers import print_lg
            print_lg(f"Invalid XPath syntax: {xpath}", "error")
        except:
            pass
        return None
    
    except StaleElementReferenceException:
        # Element was found but DOM changed, try once more
        try:
            time.sleep(0.5)
            element = driver.find_element(By.XPATH, xpath)
            return element
        except:
            return None
    
    except Exception as e:
        # Catch-all for any other exceptions (driver closed, etc.)
        try:
            from modules.helpers import print_lg
            print_lg(f"Error in try_xp: {str(e)}", "debug")
        except:
            pass
        return None


def try_linkText(driver, text: str, timeout: int = 5, partial: bool = False):
    """
    Safely find element by link text with timeout.
    
    Searches for <a> elements (links) containing the specified text.
    Useful for finding navigation links, buttons styled as links, etc.
    
    Args:
        driver: Selenium WebDriver instance
        text: Link text to search for
        timeout: Maximum seconds to wait for element (default: 5)
        partial: If True, match partial text; if False, match exact text (default: False)
    
    Returns:
        WebElement if found, None if not found or on error
    
    Usage Examples:
        # Find exact link text
        signin = try_linkText(driver, "Sign in")
        if signin:
            signin.click()
        
        # Find partial link text
        profile = try_linkText(driver, "My Profile", partial=True)
    
    Edge Cases Handled:
        - Link not found within timeout
        - Text is None or empty
        - Multiple links with same text (returns first)
        - Link exists but not visible/clickable
        - Driver is None or closed
        - Case sensitivity (searches as-is, consider normalizing if needed)
    """
    if not driver:
        return None
    
    try:
        # Validate text is not empty
        if not text or not isinstance(text, str):
            return None
        
        # Choose search method based on partial flag
        wait = WebDriverWait(driver, timeout)
        
        if partial:
            # Partial link text match
            element = wait.until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, text))
            )
        else:
            # Exact link text match
            element = wait.until(
                EC.presence_of_element_located((By.LINK_TEXT, text))
            )
        
        return element
    
    except TimeoutException:
        # Link not found - this is expected behavior, return None
        return None
    
    except StaleElementReferenceException:
        # Element was found but DOM changed, try once more
        try:
            time.sleep(0.5)
            if partial:
                element = driver.find_element(By.PARTIAL_LINK_TEXT, text)
            else:
                element = driver.find_element(By.LINK_TEXT, text)
            return element
        except:
            return None
    
    except Exception as e:
        # Catch-all for unexpected exceptions
        try:
            from modules.helpers import print_lg
            print_lg(f"Error in try_linkText: {str(e)}", "debug")
        except:
            pass
        return None


def wait_span_click(driver, text: str, timeout: int = 10, partial_match: bool = True):
    """
    Wait for span element containing text and click it.
    
    Specifically searches for <span> elements (often used for buttons, labels, etc.)
    and clicks them when found. More robust than simple click as it waits for
    element to be clickable, not just present.
    
    Args:
        driver: Selenium WebDriver instance
        text: Text content to search for within span elements
        timeout: Maximum seconds to wait for element (default: 10)
        partial_match: If True, match spans containing text; if False, exact match (default: True)
    
    Returns:
        True if element found and clicked successfully, False otherwise
    
    Usage Examples:
        # Click span button
        if wait_span_click(driver, "Continue"):
            print("Clicked Continue button")
        
        # Click exact match
        if wait_span_click(driver, "Submit Application", partial_match=False):
            print("Application submitted")
    
    Edge Cases Handled:
        - Span not found within timeout
        - Span found but not clickable (overlapped by other element)
        - Span found but click intercepted
        - Element becomes stale before click
        - Multiple matching spans (clicks first visible one)
        - Text is None or empty
        - Driver is None or closed
    """
    if not driver:
        return False
    
    try:
        # Validate text is not empty
        if not text or not isinstance(text, str):
            return False
        
        # Build XPath based on match type
        if partial_match:
            xpath = f'//span[contains(text(), "{text}")]'
        else:
            xpath = f'//span[text()="{text}"]'
        
        # Wait for element to be clickable (not just present)
        wait = WebDriverWait(driver, timeout)
        span_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        
        # Try to click the element
        span_element.click()
        return True
    
    except TimeoutException:
        # Span not found or not clickable within timeout
        return False
    
    except ElementClickInterceptedException:
        # Click intercepted by another element, try JavaScript click
        try:
            span_element = driver.find_element(By.XPATH, xpath)
            driver.execute_script("arguments[0].click();", span_element)
            return True
        except:
            return False
    
    except StaleElementReferenceException:
        # Element became stale, try to find and click again
        try:
            time.sleep(0.5)
            span_element = driver.find_element(By.XPATH, xpath)
            span_element.click()
            return True
        except:
            return False
    
    except Exception as e:
        # Catch-all for unexpected exceptions
        try:
            from modules.helpers import print_lg
            print_lg(f"Error in wait_span_click: {str(e)}", "debug")
        except:
            pass
        return False


def text_input_by_ID(driver, element_id: str, text: str, clear_first: bool = True, wait_timeout: int = 5):
    """
    Input text into an element by its ID attribute.
    
    Safely finds input field by ID, optionally clears existing content,
    and enters the provided text. Handles various input types (text, email, 
    password, textarea, etc.)
    
    Args:
        driver: Selenium WebDriver instance
        element_id: ID attribute of the input element
        text: Text to input into the element
        clear_first: If True, clear existing text before input (default: True)
        wait_timeout: Maximum seconds to wait for element (default: 5)
    
    Returns:
        True if text input successfully, False otherwise
    
    Usage Examples:
        # Basic usage
        text_input_by_ID(driver, "username", "john.doe@example.com")
        text_input_by_ID(driver, "password", "secretpass")
        
        # Don't clear existing text (append instead)
        text_input_by_ID(driver, "comment", " Additional note", clear_first=False)
    
    Edge Cases Handled:
        - Element not found within timeout
        - Element found but not interactable
        - Element is disabled or read-only
        - Text is None (converts to empty string)
        - Element ID is None or empty
        - Element becomes stale during operation
        - Element is hidden or behind another element
        - Clear operation fails but input might still work
        - Driver is None or closed
    """
    if not driver:
        return False
    
    try:
        # Validate element_id is not empty
        if not element_id or not isinstance(element_id, str):
            return False
        
        # Convert None text to empty string
        if text is None:
            text = ""
        
        # Convert text to string if not already
        text = str(text)
        
        # Wait for element to be present and visible
        wait = WebDriverWait(driver, wait_timeout)
        element = wait.until(EC.presence_of_element_located((By.ID, element_id)))
        
        # Check if element is actually interactable
        if not element.is_displayed() or not element.is_enabled():
            try:
                from modules.helpers import print_lg
                print_lg(f"Element '{element_id}' not interactable", "warning")
            except:
                pass
            return False
        
        # Clear existing text if requested
        if clear_first:
            try:
                element.clear()
            except Exception:
                # Clear might fail on some element types, but we can still try send_keys
                pass
        
        # Input the text
        element.send_keys(text)
        return True
    
    except TimeoutException:
        # Element not found within timeout
        try:
            from modules.helpers import print_lg
            print_lg(f"Input element with ID '{element_id}' not found", "warning")
        except:
            pass
        return False
    
    except ElementNotInteractableException:
        # Element found but cannot be interacted with
        # Try JavaScript as fallback
        try:
            element = driver.find_element(By.ID, element_id)
            driver.execute_script(f"arguments[0].value = '{text}';", element)
            # Trigger input event so validation runs
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element)
            return True
        except:
            return False
    
    except StaleElementReferenceException:
        # Element became stale, try once more
        try:
            time.sleep(0.5)
            element = driver.find_element(By.ID, element_id)
            if clear_first:
                element.clear()
            element.send_keys(text)
            return True
        except:
            return False
    
    except Exception as e:
        # Catch-all for unexpected exceptions
        try:
            from modules.helpers import print_lg
            print_lg(f"Error in text_input_by_ID for '{element_id}': {str(e)}", "debug")
        except:
            pass
        return False


# Export all functions
__all__ = [
    'try_xp',
    'try_linkText',
    'wait_span_click',
    'text_input_by_ID',
]
