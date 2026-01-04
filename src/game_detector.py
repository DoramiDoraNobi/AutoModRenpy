"""
Game Location Detector Module
Recursively searches for Renpy game folder in APK assets
"""
import os
from typing import Optional, List
from pathlib import Path


class GameLocationDetector:
    """Detects Renpy game folder location in extracted APK"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.renpy_markers = ["options.rpyc", "script.rpyc", "screens.rpyc"]
    
    def detect_game_folder(self, apk_root: str) -> Optional[str]:
        """
        Detect game folder in extracted APK
        
        Args:
            apk_root: Root directory of extracted APK
            
        Returns:
            Path to game folder relative to apk_root, or None if not found
        """
        self._log_info(f"Searching for Renpy game folder in: {apk_root}")
        
        # Common locations to check first (optimization)
        common_paths = [
            "assets/game",
            "assets/x-game", 
            "assets/renpy/game",
            "game"
        ]
        
        for common_path in common_paths:
            full_path = os.path.join(apk_root, common_path)
            if self._is_renpy_game_folder(full_path):
                self._log_success(f"Found game folder at: {common_path}")
                return common_path
        
        # If not found in common locations, do recursive search
        self._log_info("Common locations not found, starting recursive search...")
        
        # Start from assets folder if it exists
        search_root = os.path.join(apk_root, "assets")
        if not os.path.exists(search_root):
            search_root = apk_root
        
        game_folder = self._recursive_search(search_root, apk_root)
        
        if game_folder:
            self._log_success(f"Found game folder at: {game_folder}")
            return game_folder
        
        self._log_error("Could not find Renpy game folder in APK")
        return None
    
    def _recursive_search(self, search_path: str, apk_root: str) -> Optional[str]:
        """
        Recursively search for game folder
        
        Args:
            search_path: Current directory to search
            apk_root: Root directory of APK for relative path calculation
            
        Returns:
            Relative path to game folder or None
        """
        try:
            for root, dirs, files in os.walk(search_path):
                # Check if current directory is a game folder
                if self._is_renpy_game_folder(root):
                    # Return relative path from apk_root
                    rel_path = os.path.relpath(root, apk_root)
                    return rel_path.replace('\\', '/')  # Normalize path separators
                
                # Optimization: Skip unlikely directories
                dirs[:] = [d for d in dirs if not self._should_skip_dir(d)]
        
        except Exception as e:
            self._log_error(f"Error during recursive search: {e}")
        
        return None
    
    def _is_renpy_game_folder(self, folder_path: str) -> bool:
        """
        Check if folder is a Renpy game folder by looking for marker files
        
        Args:
            folder_path: Path to check
            
        Returns:
            True if folder contains Renpy game markers
        """
        if not os.path.isdir(folder_path):
            return False
        
        try:
            files_in_folder = os.listdir(folder_path)
            
            # Heuristic 1: marker filenames
            for marker in self.renpy_markers:
                if marker in files_in_folder:
                    has_scripts = any(f.endswith(('.rpy', '.rpyc')) for f in files_in_folder)
                    has_rpa = any(f.endswith('.rpa') for f in files_in_folder)
                    if has_scripts or has_rpa:
                        return True
            
            # Heuristic 2: folder with many compiled scripts or any .rpa
            rpyc_count = sum(1 for f in files_in_folder if f.endswith('.rpyc'))
            rpy_count = sum(1 for f in files_in_folder if f.endswith('.rpy'))
            has_rpa = any(f.endswith('.rpa') for f in files_in_folder)
            if has_rpa or rpyc_count >= 3 or (rpyc_count + rpy_count) >= 5:
                return True

            # Heuristic 3: immediate child folders contain many scripts
            aggregated_rpyc = 0
            aggregated_rpy = 0
            aggregated_rpa = False
            for entry in os.scandir(folder_path):
                if not entry.is_dir():
                    continue
                try:
                    child_files = os.listdir(entry.path)
                except (PermissionError, OSError):
                    continue
                aggregated_rpyc += sum(1 for f in child_files if f.endswith('.rpyc'))
                aggregated_rpy += sum(1 for f in child_files if f.endswith('.rpy'))
                aggregated_rpa = aggregated_rpa or any(f.endswith('.rpa') for f in child_files)
                if aggregated_rpa or aggregated_rpyc >= 3 or (aggregated_rpyc + aggregated_rpy) >= 5:
                    return True
        
        except (PermissionError, OSError):
            pass
        
        return False
    
    def _should_skip_dir(self, dir_name: str) -> bool:
        """
        Check if directory should be skipped during search
        
        Args:
            dir_name: Directory name to check
            
        Returns:
            True if directory should be skipped
        """
        skip_dirs = {
            'res', 'META-INF', 'lib', 'kotlin', 'smali', 
            'original', 'unknown', '.git', '__pycache__'
        }
        return dir_name in skip_dirs
    
    def get_game_info(self, game_folder_path: str) -> dict:
        """
        Get information about the detected game folder
        
        Args:
            game_folder_path: Path to game folder
            
        Returns:
            Dictionary with game information
        """
        if not os.path.exists(game_folder_path):
            return {}
        
        info = {
            'path': game_folder_path,
            'rpy_files': [],
            'rpyc_files': [],
            'rpa_archives': [],
            'total_files': 0
        }
        
        try:
            for root, dirs, files in os.walk(game_folder_path):
                for file in files:
                    info['total_files'] += 1
                    
                    if file.endswith('.rpy'):
                        rel_path = os.path.relpath(os.path.join(root, file), game_folder_path)
                        info['rpy_files'].append(rel_path)
                    elif file.endswith('.rpyc'):
                        rel_path = os.path.relpath(os.path.join(root, file), game_folder_path)
                        info['rpyc_files'].append(rel_path)
                    elif file.endswith('.rpa'):
                        rel_path = os.path.relpath(os.path.join(root, file), game_folder_path)
                        info['rpa_archives'].append(rel_path)
        
        except Exception as e:
            self._log_error(f"Error gathering game info: {e}")
        
        return info
    
    def _log_info(self, message: str):
        """Log info message"""
        if self.logger:
            self.logger.info(message)
    
    def _log_success(self, message: str):
        """Log success message"""
        if self.logger:
            self.logger.success(message)
    
    def _log_error(self, message: str):
        """Log error message"""
        if self.logger:
            self.logger.error(message)
