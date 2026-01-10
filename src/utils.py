"""
AutoModRenpy - Utility functions and helpers
"""
import os
import sys
import json
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

def get_app_root() -> str:
    """
    Get the application root directory.
    If running as script, returns the directory containing main.py.
    If running as frozen exe, returns the directory containing the exe.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        # Assuming src/utils.py is 1 level deep from root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(script_dir)

def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to a resource.
    Resolves relative to app root.
    """
    return os.path.join(get_app_root(), relative_path)

class Config:
    """Configuration manager for AutoModRenpy"""
    
    def __init__(self, config_path: str = "config.json"):
        # Resolve config path relative to app root if it's relative
        if not os.path.isabs(config_path):
            self.config_path = get_resource_path(config_path)
        else:
            self.config_path = config_path

        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Don't spam warning if creating default
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value and save"""
        self.config[key] = value
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")


class Logger:
    """Simple logging utility"""
    
    def __init__(self, log_file: Optional[str] = None, verbose: bool = True):
        self.log_file = log_file
        if log_file and not os.path.isabs(log_file):
            self.log_file = get_resource_path(log_file)

        self.verbose = verbose
        if self.log_file:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def info(self, message: str):
        """Log info message"""
        self._log("INFO", message)
    
    def warning(self, message: str):
        """Log warning message"""
        self._log("WARNING", message)
    
    def error(self, message: str):
        """Log error message"""
        self._log("ERROR", message)
    
    def success(self, message: str):
        """Log success message"""
        self._log("SUCCESS", message)
    
    def _log(self, level: str, message: str):
        """Internal logging method"""
        log_message = f"[{level}] {message}"
        
        if self.verbose:
            print(log_message)
        
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_message + '\n')
            except Exception:
                pass


def calculate_file_hash(file_path: str) -> str:
    """Calculate MD5 hash of a file"""
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def ensure_dir(directory: str):
    """Ensure directory exists"""
    # If directory is relative, make it absolute relative to app root
    if not os.path.isabs(directory):
        directory = get_resource_path(directory)
    os.makedirs(directory, exist_ok=True)


def clean_temp_dir(temp_dir: str):
    """Clean temporary directory"""
    if not os.path.isabs(temp_dir):
        temp_dir = get_resource_path(temp_dir)

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    ensure_dir(temp_dir)


def get_file_extension(file_path: str) -> str:
    """Get file extension in lowercase"""
    return Path(file_path).suffix.lower()


def is_renpy_script(file_path: str) -> bool:
    """Check if file is a Renpy script"""
    ext = get_file_extension(file_path)
    return ext in ['.rpy', '.rpyc']


def is_rpa_archive(file_path: str) -> bool:
    """Check if file is an RPA archive"""
    return get_file_extension(file_path) == '.rpa'


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to be safe for filesystem"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def format_bytes(bytes_size: int) -> str:
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


class Cache:
    """Simple file-based cache for game locations"""
    
    def __init__(self, cache_file: str, max_entries: int = 100):
        if not os.path.isabs(cache_file):
            self.cache_file = get_resource_path(cache_file)
        else:
            self.cache_file = cache_file

        self.max_entries = max_entries
        ensure_dir(os.path.dirname(self.cache_file))
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, str]:
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        return self.cache.get(key)
    
    def set(self, key: str, value: str):
        """Set value in cache"""
        self.cache[key] = value
        
        # Limit cache size
        if len(self.cache) > self.max_entries:
            # Remove oldest entries (first items)
            items = list(self.cache.items())
            self.cache = dict(items[-self.max_entries:])
        
        self._save_cache()
    
    def clear(self):
        """Clear all cache"""
        self.cache = {}
        self._save_cache()
