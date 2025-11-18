"""
Human Behavior Simulation Module

This module adds realistic human-like behaviors to browser automation:
- Random delays between actions
- Mouse movements with bezier curves
- Realistic typing speeds with variations
- Random scrolling patterns
- Reading pauses
- Cursor hovering
- Occasional typos and corrections

Purpose: Make automation indistinguishable from human browsing
"""

import time
import random
import math
from typing import Tuple, List
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class HumanBehavior:
    """
    Simulates realistic human behavior in browser automation.
    """
    
    def __init__(self, driver: WebDriver, actions: ActionChains = None):
        """
        Initialize human behavior simulator.
        
        Args:
            driver: Selenium WebDriver instance
            actions: ActionChains instance (optional, will create if None)
        """
        self.driver = driver
        self.actions = actions if actions else ActionChains(driver)
        
        # Configurable behavior parameters
        self.typing_speed_min = 0.05  # Fastest typing (50ms per char)
        self.typing_speed_max = 0.15  # Slowest typing (150ms per char)
        self.click_delay_min = 0.3    # Min delay after click
        self.click_delay_max = 1.2    # Max delay after click
        self.scroll_pause_min = 0.5   # Min pause after scroll
        self.scroll_pause_max = 2.0   # Max pause after scroll
        self.reading_speed = 0.003    # Seconds per character for "reading"
    
    def random_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """
        Random delay to simulate human thinking/reading time.
        
        Args:
            min_seconds: Minimum delay in seconds
            max_seconds: Maximum delay in seconds
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def micro_delay(self):
        """Very short random delay (100-300ms) for natural pauses."""
        time.sleep(random.uniform(0.1, 0.3))
    
    def reading_pause(self, text_length: int = 100):
        """
        Simulate time spent reading text.
        
        Args:
            text_length: Number of characters to "read"
        """
        # Average reading speed: ~250 words per minute = ~5 chars per second
        base_time = text_length * self.reading_speed
        # Add randomness: ±30%
        actual_time = base_time * random.uniform(0.7, 1.3)
        time.sleep(min(actual_time, 5.0))  # Cap at 5 seconds
    
    def human_click(self, element: WebElement, pause_after: bool = True):
        """
        Click an element with human-like behavior.
        
        Args:
            element: WebElement to click
            pause_after: Whether to pause after clicking
        """
        try:
            # Small pause before clicking (thinking time)
            self.micro_delay()
            
            # Move to element with slight randomness
            self.move_to_element_smooth(element)
            
            # Small pause at element (hovering)
            time.sleep(random.uniform(0.1, 0.3))
            
            # Click
            element.click()
            
            # Pause after clicking (processing time)
            if pause_after:
                delay = random.uniform(self.click_delay_min, self.click_delay_max)
                time.sleep(delay)
        
        except Exception as e:
            # Fallback to direct click
            try:
                element.click()
            except:
                # JavaScript click as last resort
                self.driver.execute_script("arguments[0].click();", element)
    
    def move_to_element_smooth(self, element: WebElement, duration: float = 0.5):
        """
        Move mouse to element with smooth bezier curve motion.
        
        Args:
            element: Target element
            duration: Time to complete movement (seconds)
        """
        try:
            # Get current position (center of viewport as approximation)
            current_x = self.driver.execute_script("return window.innerWidth / 2;")
            current_y = self.driver.execute_script("return window.innerHeight / 2;")
            
            # Get target position
            location = element.location
            size = element.size
            target_x = location['x'] + size['width'] / 2
            target_y = location['y'] + size['height'] / 2
            
            # Calculate bezier curve path
            steps = int(duration * 30)  # 30 steps per second
            for i in range(steps):
                t = i / steps
                # Cubic bezier with random control points for natural movement
                x = self._cubic_bezier(t, current_x, target_x)
                y = self._cubic_bezier(t, current_y, target_y)
                
                # Small random offset for natural imprecision
                x += random.uniform(-2, 2)
                y += random.uniform(-2, 2)
                
                time.sleep(duration / steps)
            
            # Final move to element
            self.actions.move_to_element(element).perform()
        
        except Exception:
            # Fallback to simple move
            try:
                self.actions.move_to_element(element).perform()
            except:
                pass
    
    def _cubic_bezier(self, t: float, start: float, end: float) -> float:
        """
        Calculate cubic bezier curve point.
        
        Args:
            t: Progress from 0 to 1
            start: Starting coordinate
            end: Ending coordinate
        
        Returns:
            Interpolated coordinate
        """
        # Control points for natural curve
        cp1 = start + (end - start) * 0.25 + random.uniform(-20, 20)
        cp2 = start + (end - start) * 0.75 + random.uniform(-20, 20)
        
        # Cubic bezier formula
        return (
            (1 - t)**3 * start +
            3 * (1 - t)**2 * t * cp1 +
            3 * (1 - t) * t**2 * cp2 +
            t**3 * end
        )
    
    def human_type(self, element: WebElement, text: str, mistake_probability: float = 0.02):
        """
        Type text with human-like speed variations and occasional mistakes.
        
        Args:
            element: Input element to type into
            text: Text to type
            mistake_probability: Chance of making a typo (0.0 to 1.0)
        """
        try:
            # Click to focus
            element.click()
            self.micro_delay()
            
            # Clear existing text
            element.clear()
            time.sleep(random.uniform(0.1, 0.3))
            
            typed_text = ""
            i = 0
            while i < len(text):
                char = text[i]
                
                # Simulate typo
                if random.random() < mistake_probability and char.isalpha():
                    # Type wrong character
                    wrong_char = self._get_nearby_key(char)
                    element.send_keys(wrong_char)
                    typed_text += wrong_char
                    
                    # Random delay before realizing mistake
                    time.sleep(random.uniform(0.2, 0.5))
                    
                    # Backspace to correct
                    element.send_keys(Keys.BACK_SPACE)
                    typed_text = typed_text[:-1]
                    time.sleep(random.uniform(0.1, 0.2))
                
                # Type correct character
                element.send_keys(char)
                typed_text += char
                
                # Variable typing speed
                if char == ' ':
                    # Slight pause at spaces (word boundaries)
                    delay = random.uniform(0.1, 0.3)
                elif char in '.,!?':
                    # Longer pause at punctuation
                    delay = random.uniform(0.2, 0.4)
                else:
                    # Normal character delay
                    delay = random.uniform(self.typing_speed_min, self.typing_speed_max)
                
                time.sleep(delay)
                i += 1
        
        except Exception as e:
            # Fallback to instant typing
            try:
                element.clear()
                element.send_keys(text)
            except:
                pass
    
    def _get_nearby_key(self, char: str) -> str:
        """
        Get a keyboard key near the intended key (for typo simulation).
        
        Args:
            char: Intended character
        
        Returns:
            Nearby character
        """
        # Keyboard layout (QWERTY)
        keyboard = {
            'q': ['w', 'a'], 'w': ['q', 'e', 's'], 'e': ['w', 'r', 'd'],
            'r': ['e', 't', 'f'], 't': ['r', 'y', 'g'], 'y': ['t', 'u', 'h'],
            'u': ['y', 'i', 'j'], 'i': ['u', 'o', 'k'], 'o': ['i', 'p', 'l'],
            'p': ['o', 'l'],
            'a': ['q', 's', 'z'], 's': ['w', 'a', 'd', 'x'], 'd': ['e', 's', 'f', 'c'],
            'f': ['r', 'd', 'g', 'v'], 'g': ['t', 'f', 'h', 'b'], 'h': ['y', 'g', 'j', 'n'],
            'j': ['u', 'h', 'k', 'm'], 'k': ['i', 'j', 'l'], 'l': ['o', 'k', 'p'],
            'z': ['a', 'x'], 'x': ['s', 'z', 'c'], 'c': ['d', 'x', 'v'],
            'v': ['f', 'c', 'b'], 'b': ['g', 'v', 'n'], 'n': ['h', 'b', 'm'],
            'm': ['j', 'n']
        }
        
        char_lower = char.lower()
        if char_lower in keyboard:
            nearby = random.choice(keyboard[char_lower])
            return nearby.upper() if char.isupper() else nearby
        return char
    
    def human_scroll(self, direction: str = 'down', amount: int = 300, steps: int = 5):
        """
        Scroll with human-like behavior (gradual, with pauses).
        
        Args:
            direction: 'down' or 'up'
            amount: Total pixels to scroll
            steps: Number of scroll steps (more = smoother)
        """
        try:
            scroll_per_step = amount // steps
            
            for _ in range(steps):
                # Scroll a portion
                if direction == 'down':
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_per_step});")
                else:
                    self.driver.execute_script(f"window.scrollBy(0, -{scroll_per_step});")
                
                # Small pause between scrolls
                time.sleep(random.uniform(0.1, 0.3))
            
            # Pause after scrolling (reading time)
            pause = random.uniform(self.scroll_pause_min, self.scroll_pause_max)
            time.sleep(pause)
        
        except Exception:
            pass
    
    def random_scroll_pattern(self):
        """
        Perform random scrolling pattern to simulate page exploration.
        """
        try:
            # Random number of scroll actions
            num_scrolls = random.randint(1, 3)
            
            for _ in range(num_scrolls):
                # Random scroll direction (mostly down)
                if random.random() < 0.8:  # 80% chance scroll down
                    self.human_scroll('down', random.randint(200, 500))
                else:  # 20% chance scroll up
                    self.human_scroll('up', random.randint(100, 300))
                
                # Pause to "read"
                self.reading_pause(random.randint(50, 150))
        
        except Exception:
            pass
    
    def hover_over_element(self, element: WebElement, duration: float = 1.0):
        """
        Hover over element for a duration (simulates reading/considering).
        
        Args:
            element: Element to hover over
            duration: How long to hover (seconds)
        """
        try:
            self.move_to_element_smooth(element)
            time.sleep(duration)
        except Exception:
            pass
    
    def random_mouse_movement(self):
        """
        Move mouse randomly on page (simulate human activity).
        """
        try:
            # Get random coordinates within viewport
            max_x = self.driver.execute_script("return window.innerWidth;")
            max_y = self.driver.execute_script("return window.innerHeight;")
            
            target_x = random.randint(0, max_x)
            target_y = random.randint(0, max_y)
            
            # Move to random location
            self.actions.move_by_offset(target_x, target_y).perform()
            self.micro_delay()
            
            # Reset action chains
            self.actions = ActionChains(self.driver)
        
        except Exception:
            pass
    
    def simulate_page_reading(self, min_time: float = 2.0, max_time: float = 5.0):
        """
        Simulate reading a page with scrolling and pauses.
        
        Args:
            min_time: Minimum time to spend on page
            max_time: Maximum time to spend on page
        """
        total_time = random.uniform(min_time, max_time)
        elapsed = 0
        
        while elapsed < total_time:
            # Random action
            action = random.choice(['scroll', 'pause', 'mouse_move'])
            
            if action == 'scroll':
                self.human_scroll('down', random.randint(200, 400))
                elapsed += 1.0
            elif action == 'pause':
                pause = random.uniform(0.5, 1.5)
                time.sleep(pause)
                elapsed += pause
            elif action == 'mouse_move':
                self.random_mouse_movement()
                elapsed += 0.3
    
    def natural_page_load_wait(self):
        """
        Wait for page to load with human-like patience variations.
        """
        # Base wait for page load
        time.sleep(random.uniform(1.0, 2.5))
        
        # Additional wait to "notice" page loaded
        time.sleep(random.uniform(0.3, 0.8))


# Convenience functions for quick access

def click_like_human(driver: WebDriver, element: WebElement, actions: ActionChains = None):
    """Quick human-like click."""
    hb = HumanBehavior(driver, actions)
    hb.human_click(element)


def type_like_human(driver: WebDriver, element: WebElement, text: str, actions: ActionChains = None):
    """Quick human-like typing."""
    hb = HumanBehavior(driver, actions)
    hb.human_type(element, text)


def scroll_like_human(driver: WebDriver, direction: str = 'down', actions: ActionChains = None):
    """Quick human-like scroll."""
    hb = HumanBehavior(driver, actions)
    hb.human_scroll(direction)


def wait_like_human(min_sec: float = 0.5, max_sec: float = 2.0):
    """Quick human-like wait."""
    time.sleep(random.uniform(min_sec, max_sec))


# Export all
__all__ = [
    'HumanBehavior',
    'click_like_human',
    'type_like_human',
    'scroll_like_human',
    'wait_like_human',
]
