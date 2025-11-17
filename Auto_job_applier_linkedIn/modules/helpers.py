"""
Helper utility functions for LinkedIn Auto Job Applier
Provides logging, file system, and utility functions
"""

import os
import sys
from datetime import datetime
from pathlib import Path


def print_lg(message: str, level: str = "INFO"):
    """
    Print log message with timestamp and level.
    
    Args:
        message: The message to log
        level: Log level (INFO, WARNING, ERROR, SUCCESS, DEBUG)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")
    
    # Also write to log file if logs directory exists
    try:
        log_dir = Path("logs")
        if log_dir.exists():
            log_file = log_dir / "application.log"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [{level}] {message}\n")
    except Exception:
        pass  # Silently fail if logging to file fails


def critical_error_log(message: str, exception: Exception = None):
    """
    Log critical error and optionally exit.
    
    Args:
        message: Error message
        exception: Optional exception object
    """
    error_msg = f"CRITICAL ERROR: {message}"
    if exception:
        error_msg += f"\nException: {str(exception)}"
    
    print_lg(error_msg, "ERROR")
    
    # Write to error log
    try:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        error_file = log_dir / "errors.log"
        with open(error_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
            f.write(f"{error_msg}\n")
            if exception:
                import traceback
                f.write(f"\nTraceback:\n{traceback.format_exc()}\n")
            f.write(f"{'='*60}\n")
    except Exception:
        pass


def make_directories():
    """
    Create necessary directories for the application.
    Creates: logs/, data/, output/
    """
    directories = ["logs", "data", "output"]
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True, parents=True)
        except Exception as e:
            print_lg(f"Failed to create directory '{directory}': {e}", "WARNING")


def truncate_for_csv(text: str, max_length: int = 32767) -> str:
    """
    Truncate text to fit within CSV cell limits.
    Excel has a 32,767 character limit per cell.
    
    Args:
        text: Text to truncate
        max_length: Maximum length (default: 32767 for Excel)
    
    Returns:
        Truncated text
    """
    if not text:
        return ""
    
    text = str(text)
    if len(text) <= max_length:
        return text
    
    # Truncate and add indicator
    return text[:max_length-3] + "..."


def find_default_profile_directory() -> str:
    """
    Find the default Chrome profile directory.
    
    Returns:
        Path to Chrome profile directory or empty string if not found
    """
    if sys.platform == "win32":
        # Windows
        base_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Chrome\User Data"),
        ]
    elif sys.platform == "darwin":
        # macOS
        base_paths = [
            os.path.expanduser("~/Library/Application Support/Google/Chrome"),
        ]
    else:
        # Linux
        base_paths = [
            os.path.expanduser("~/.config/google-chrome"),
            os.path.expanduser("~/.config/chromium"),
        ]
    
    for base_path in base_paths:
        if os.path.exists(base_path):
            default_profile = os.path.join(base_path, "Default")
            if os.path.exists(default_profile):
                return default_profile
    
    return ""


def safe_string(text, default="") -> str:
    """
    Convert text to safe string, handling None and errors.
    
    Args:
        text: Text to convert
        default: Default value if conversion fails
    
    Returns:
        Safe string
    """
    try:
        if text is None:
            return default
        return str(text).strip()
    except Exception:
        return default


def sanitize_filename(filename: str) -> str:
    """
    Remove invalid characters from filename.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    import re
    # Remove invalid characters for Windows/Linux/macOS
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def get_timestamp() -> str:
    """
    Get current timestamp as formatted string.
    
    Returns:
        Timestamp string (YYYY-MM-DD_HH-MM-SS)
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def ensure_file_exists(filepath: str, default_content: str = ""):
    """
    Ensure a file exists, creating it with default content if it doesn't.
    
    Args:
        filepath: Path to the file
        default_content: Content to write if file doesn't exist
    """
    path = Path(filepath)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(default_content, encoding="utf-8")


def read_file_safe(filepath: str, default: str = "") -> str:
    """
    Safely read a file, returning default if it fails.
    
    Args:
        filepath: Path to the file
        default: Default value if read fails
    
    Returns:
        File contents or default
    """
    try:
        return Path(filepath).read_text(encoding="utf-8")
    except Exception:
        return default


def write_file_safe(filepath: str, content: str) -> bool:
    """
    Safely write content to a file.
    
    Args:
        filepath: Path to the file
        content: Content to write
    
    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        print_lg(f"Failed to write file '{filepath}': {e}", "ERROR")
        return False
