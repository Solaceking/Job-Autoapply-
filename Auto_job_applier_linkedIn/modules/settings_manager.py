"""
Settings manager to load and persist simple config values for the app.

This module provides a thin API to read search-related settings from
`config/search.py` and write updates back into that file.

It is intentionally conservative and only writes simple top-level
variables (str, bool, int, list).
"""
import re
import ast
from typing import Any, Dict

SEARCH_CONFIG_PATH = "config/search.py"
PERSONALS_CONFIG_PATH = "config/personals.py"
RESUME_CONFIG_PATH = "config/resume.py"


def _parse_value(value_str: str) -> Any:
    try:
        return ast.literal_eval(value_str)
    except Exception:
        # fallback: return the raw string without quotes
        return value_str.strip().strip('"').strip("'")


def load_search_settings() -> Dict[str, Any]:
    """Load top-level variables from config/search.py into a dict.

    Only parses simple assignments (strings, numbers, booleans, lists).
    """
    settings = {}
    try:
        with open(SEARCH_CONFIG_PATH, "r", encoding="utf-8") as f:
            src = f.read()

        # Find simple assignments like: key = value
        for m in re.finditer(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$", src, re.M):
            key, val = m.group(1), m.group(2).strip()
            # ignore block comments and triple-quoted strings
            if val.startswith("'''") or val.startswith('"""'):
                continue
            # stop at complex lines
            try:
                settings[key] = _parse_value(val)
            except Exception:
                continue

    except FileNotFoundError:
        return settings

    return settings


def save_search_settings(updates: Dict[str, Any]) -> None:
    """Apply updates to `config/search.py` by replacing top-level assignments.

    Only updates keys that already exist in the file. Other keys are appended
    at the end of the file.
    """
    try:
        with open(SEARCH_CONFIG_PATH, "r", encoding="utf-8") as f:
            src = f.read()

        appended = []
        for key, val in updates.items():
            # Prepare python literal string for value
            py_val = repr(val)
            pattern = rf"^({key})\s*=\s*.*$"
            if re.search(pattern, src, re.M):
                src = re.sub(pattern, f"{key} = {py_val}", src, flags=re.M)
            else:
                appended.append(f"{key} = {py_val}\n")

        if appended:
            # append at end before trailing comments if present
            src = src.rstrip() + "\n\n" + "".join(appended)

        with open(SEARCH_CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(src)

    except Exception as e:
        # best-effort: raise so caller can log
        raise


def load_personals_settings() -> Dict[str, Any]:
    """Load top-level variables from config/personals.py into a dict.
    
    Used for personal information (name, email, phone, etc.) that can be mapped
    to form fields.
    """
    return _load_config_file(PERSONALS_CONFIG_PATH)


def load_resume_settings() -> Dict[str, Any]:
    """Load resume file path and related info from config/resume.py.
    
    Common keys: resume_path (str), cover_letter_path (str), etc.
    """
    return _load_config_file(RESUME_CONFIG_PATH)


def _load_config_file(config_path: str) -> Dict[str, Any]:
    """Generic loader for config files with simple top-level assignments."""
    settings = {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            src = f.read()

        for m in re.finditer(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$", src, re.M):
            key, val = m.group(1), m.group(2).strip()
            if val.startswith("'''") or val.startswith('"""'):
                continue
            try:
                settings[key] = _parse_value(val)
            except Exception:
                continue

    except FileNotFoundError:
        pass

    return settings
