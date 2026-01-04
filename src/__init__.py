"""
Initialize src package
"""
__version__ = "1.0.0"
__author__ = "AutoModRenpy"

from .utils import Config, Logger, Cache
from .game_detector import GameLocationDetector
from .unrpa_extractor import UnRPAExtractor
from .apk_handler import APKHandler
from .mod_processor import ModProcessor, ConflictStrategy, ModFile
from .script_validator import ScriptValidator, ValidationIssue
from .backup_manager import BackupManager, BackupEntry

__all__ = [
    'Config',
    'Logger',
    'Cache',
    'GameLocationDetector',
    'UnRPAExtractor',
    'APKHandler',
    'ModProcessor',
    'ConflictStrategy',
    'ModFile',
    'ScriptValidator',
    'ValidationIssue',
    'BackupManager',
    'BackupEntry'
]
