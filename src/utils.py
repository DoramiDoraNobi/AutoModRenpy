"""
AutoModRenpy - Utility functions and helpers
"""
import os
import json
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for AutoModRenpy"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file not found at {self.config_path}")
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
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)


class Logger:
    """Simple logging utility"""
    
    def __init__(self, log_file: Optional[str] = None, verbose: bool = True):
        self.log_file = log_file
        self.verbose = verbose
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
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
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')


def calculate_file_hash(file_path: str) -> str:
    """Calculate MD5 hash of a file"""
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def ensure_dir(directory: str):
    """Ensure directory exists"""
    os.makedirs(directory, exist_ok=True)


def clean_temp_dir(temp_dir: str):
    """Clean temporary directory"""
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
        self.cache_file = cache_file
        self.max_entries = max_entries
        ensure_dir(os.path.dirname(cache_file))
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
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2)
    
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
