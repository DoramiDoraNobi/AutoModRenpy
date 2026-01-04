"""
Mod Processor Module
Handles mod structure detection, conflict resolution, and script merging
"""
import os
import shutil
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from enum import Enum


class ConflictStrategy(Enum):
    """Strategies for handling file conflicts"""
    NEW_FILE = "new_file"  # Create new file with prefix (recommended)
    REPLACE = "replace"      # Overwrite original file
    SKIP = "skip"           # Skip conflicting file


class ModFile:
    """Represents a file in a mod"""
    
    def __init__(self, source_path: str, target_path: str, is_script: bool = False):
        self.source_path = source_path
        self.target_path = target_path
        self.is_script = is_script
        self.filename = os.path.basename(source_path)
        self.conflicts = False
        self.strategy = ConflictStrategy.NEW_FILE
    
    def __repr__(self):
        return f"ModFile({self.filename}, conflicts={self.conflicts})"


class ModProcessor:
    """Process mods with intelligent structure detection and conflict resolution"""
    
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        self.mod_prefix = config.get('mod_prefix', 'z')
    
    def detect_mod_structure(self, mod_folder: str) -> Tuple[bool, Optional[str]]:
        """
        Detect if mod has a 'game/' subdirectory structure
        
        Args:
            mod_folder: Path to mod folder
            
        Returns:
            Tuple of (has_game_subfolder, game_folder_path)
        """
        self._log_info(f"Analyzing mod structure: {os.path.basename(mod_folder)}")
        
        # Check for game/ subdirectory
        game_subfolder = os.path.join(mod_folder, 'game')
        if os.path.exists(game_subfolder) and os.path.isdir(game_subfolder):
            self._log_success(f"Found 'game/' subfolder in mod")
            return True, game_subfolder
        
        # Check for other common patterns
        for pattern in ['Game', 'GAME', 'renpy/game']:
            alt_path = os.path.join(mod_folder, pattern)
            if os.path.exists(alt_path) and os.path.isdir(alt_path):
                self._log_success(f"Found '{pattern}' subfolder in mod")
                return True, alt_path
        
        # No game subfolder found, use root
        self._log_info("No 'game/' subfolder found, using mod root")
        return False, mod_folder
    
    def scan_mod_files(self, mod_source_dir: str, game_target_dir: str, 
                       mod_priority: int = 1) -> List[ModFile]:
        """
        Scan mod directory and prepare file list with conflict detection
        
        Args:
            mod_source_dir: Source directory of mod files
            game_target_dir: Target game directory in APK
            mod_priority: Priority number for load order (higher = later)
            
        Returns:
            List of ModFile objects
        """
        mod_files = []
        
        for root, dirs, files in os.walk(mod_source_dir):
            for filename in files:
                source_path = os.path.join(root, filename)
                
                # Calculate relative path from mod source
                rel_path = os.path.relpath(source_path, mod_source_dir)
                
                # Target path in game directory
                target_path = os.path.join(game_target_dir, rel_path)
                
                # Check if it's a Renpy script
                is_script = filename.endswith(('.rpy', '.rpyc'))
                
                # Create ModFile object
                mod_file = ModFile(source_path, target_path, is_script)
                
                # Check for conflicts
                if os.path.exists(target_path):
                    mod_file.conflicts = True
                    self._log_warning(f"Conflict detected: {rel_path}")
                
                mod_files.append(mod_file)
        
        self._log_info(f"Found {len(mod_files)} files in mod")
        conflicts = sum(1 for f in mod_files if f.conflicts)
        if conflicts > 0:
            self._log_warning(f"{conflicts} files have conflicts")
        
        return mod_files
    
    def apply_conflict_strategy(self, mod_file: ModFile, strategy: ConflictStrategy, 
                                mod_priority: int = 1) -> str:
        """
        Apply conflict resolution strategy and return final target path
        
        Args:
            mod_file: ModFile object
            strategy: ConflictStrategy to apply
            mod_priority: Mod priority number for naming
            
        Returns:
            Final target path for the file
        """
        if not mod_file.conflicts:
            return mod_file.target_path
        
        if strategy == ConflictStrategy.REPLACE:
            # Overwrite existing file
            return mod_file.target_path
        
        elif strategy == ConflictStrategy.SKIP:
            # Return empty path to indicate skip
            return ""
        
        elif strategy == ConflictStrategy.NEW_FILE:
            # Create new file with prefix
            dir_path = os.path.dirname(mod_file.target_path)
            filename = os.path.basename(mod_file.target_path)
            
            # Add prefix to filename
            # Format: z{priority:02d}_originalname.rpy
            new_filename = f"{self.mod_prefix}{mod_priority:02d}_{filename}"
            new_path = os.path.join(dir_path, new_filename)
            
            return new_path
        
        return mod_file.target_path
    
    def install_mod_files(self, mod_files: List[ModFile], mod_priority: int = 1, 
                         default_strategy: ConflictStrategy = ConflictStrategy.NEW_FILE) -> Dict[str, int]:
        """
        Install mod files to target locations
        
        Args:
            mod_files: List of ModFile objects to install
            mod_priority: Mod priority number
            default_strategy: Default conflict resolution strategy
            
        Returns:
            Dictionary with installation statistics
        """
        stats = {
            'installed': 0,
            'skipped': 0,
            'replaced': 0,
            'new_files': 0,
            'errors': 0
        }
        
        for mod_file in mod_files:
            try:
                # Determine strategy
                strategy = mod_file.strategy if mod_file.conflicts else default_strategy
                
                # Get final target path
                target_path = self.apply_conflict_strategy(mod_file, strategy, mod_priority)
                
                if not target_path:
                    # Skip file
                    stats['skipped'] += 1
                    self._log_info(f"Skipped: {mod_file.filename}")
                    continue
                
                # Ensure target directory exists
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                # Copy file
                shutil.copy2(mod_file.source_path, target_path)
                
                # Update stats
                stats['installed'] += 1
                if mod_file.conflicts:
                    if strategy == ConflictStrategy.REPLACE:
                        stats['replaced'] += 1
                    elif strategy == ConflictStrategy.NEW_FILE:
                        stats['new_files'] += 1
                
                self._log_info(f"Installed: {os.path.basename(target_path)}")
            
            except Exception as e:
                stats['errors'] += 1
                self._log_error(f"Error installing {mod_file.filename}: {e}")
        
        return stats
    
    def prepare_multiple_mods(self, mod_folders: List[str], game_target_dir: str) -> List[Tuple[int, List[ModFile]]]:
        """
        Prepare multiple mods with priority ordering
        
        Args:
            mod_folders: List of mod folder paths (in priority order)
            game_target_dir: Target game directory
            
        Returns:
            List of tuples (priority, mod_files)
        """
        all_mods = []
        
        for priority, mod_folder in enumerate(mod_folders, start=1):
            # Detect mod structure
            has_game_subfolder, source_dir = self.detect_mod_structure(mod_folder)
            
            # Scan mod files
            mod_files = self.scan_mod_files(source_dir, game_target_dir, priority)
            
            all_mods.append((priority, mod_files))
        
        return all_mods
    
    def get_conflict_report(self, all_mods: List[Tuple[int, List[ModFile]]]) -> Dict[str, List[str]]:
        """
        Generate conflict report showing which files conflict across mods
        
        Args:
            all_mods: List of (priority, mod_files) tuples
            
        Returns:
            Dictionary mapping conflicting files to mod priorities
        """
        conflict_map = {}
        
        for priority, mod_files in all_mods:
            for mod_file in mod_files:
                if mod_file.conflicts:
                    key = os.path.basename(mod_file.target_path)
                    if key not in conflict_map:
                        conflict_map[key] = []
                    conflict_map[key].append(f"Mod {priority}")
        
        return conflict_map
    
    def reorder_mods(self, all_mods: List[Tuple[int, List[ModFile]]], 
                    new_order: List[int]) -> List[Tuple[int, List[ModFile]]]:
        """
        Reorder mods based on new priority list
        
        Args:
            all_mods: Current list of (priority, mod_files)
            new_order: New order of priorities (e.g., [2, 1, 3] means mod 2 first)
            
        Returns:
            Reordered list with updated priorities
        """
        reordered = []
        
        for new_priority, old_priority in enumerate(new_order, start=1):
            # Find mod with old priority
            for priority, mod_files in all_mods:
                if priority == old_priority:
                    reordered.append((new_priority, mod_files))
                    break
        
        return reordered
    
    def _log_info(self, message: str):
        """Log info message"""
        if self.logger:
            self.logger.info(message)
    
    def _log_success(self, message: str):
        """Log success message"""
        if self.logger:
            self.logger.success(message)
    
    def _log_warning(self, message: str):
        """Log warning message"""
        if self.logger:
            self.logger.warning(message)
    
    def _log_error(self, message: str):
        """Log error message"""
        if self.logger:
            self.logger.error(message)
