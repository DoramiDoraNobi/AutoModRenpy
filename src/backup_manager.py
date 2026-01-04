"""
Backup Manager Module
Handles backup and restoration of original APK files
"""
import os
import shutil
import json
from datetime import datetime
from typing import List, Dict, Optional


class BackupEntry:
    """Represents a backup entry"""
    
    def __init__(self, original_apk: str, backup_path: str, timestamp: str, 
                 game_name: str = "", notes: str = ""):
        self.original_apk = original_apk
        self.backup_path = backup_path
        self.timestamp = timestamp
        self.game_name = game_name
        self.notes = notes
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'original_apk': self.original_apk,
            'backup_path': self.backup_path,
            'timestamp': self.timestamp,
            'game_name': self.game_name,
            'notes': self.notes
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'BackupEntry':
        """Create BackupEntry from dictionary"""
        return BackupEntry(
            data.get('original_apk', ''),
            data.get('backup_path', ''),
            data.get('timestamp', ''),
            data.get('game_name', ''),
            data.get('notes', '')
        )


class BackupManager:
    """Manage backups of original APK files"""
    
    def __init__(self, backup_dir: str, logger=None):
        self.backup_dir = backup_dir
        self.logger = logger
        self.index_file = os.path.join(backup_dir, 'backup_index.json')
        
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
        
        # Load backup index
        self.backups = self._load_index()
    
    def create_backup(self, apk_path: str, game_name: str = "", notes: str = "") -> Optional[BackupEntry]:
        """
        Create backup of APK file
        
        Args:
            apk_path: Path to APK file to backup
            game_name: Optional name of the game
            notes: Optional notes about the backup
            
        Returns:
            BackupEntry object if successful, None otherwise
        """
        try:
            if not os.path.exists(apk_path):
                self._log_error(f"APK file not found: {apk_path}")
                return None
            
            self._log_info(f"Creating backup of: {os.path.basename(apk_path)}")
            
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_name = os.path.basename(apk_path)
            backup_filename = f"{timestamp}_{original_name}"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Copy APK to backup location
            shutil.copy2(apk_path, backup_path)
            
            # Create backup entry
            entry = BackupEntry(
                original_apk=apk_path,
                backup_path=backup_path,
                timestamp=timestamp,
                game_name=game_name or os.path.splitext(original_name)[0],
                notes=notes
            )
            
            # Add to index
            self.backups.append(entry)
            self._save_index()
            
            self._log_success(f"Backup created: {backup_filename}")
            return entry
        
        except Exception as e:
            self._log_error(f"Error creating backup: {e}")
            return None
    
    def restore_backup(self, backup_entry: BackupEntry, restore_path: str) -> bool:
        """
        Restore APK from backup
        
        Args:
            backup_entry: BackupEntry to restore
            restore_path: Path where APK should be restored
            
        Returns:
            True if restoration successful
        """
        try:
            if not os.path.exists(backup_entry.backup_path):
                self._log_error(f"Backup file not found: {backup_entry.backup_path}")
                return False
            
            self._log_info(f"Restoring backup: {os.path.basename(backup_entry.backup_path)}")
            
            # Copy backup to restore location
            shutil.copy2(backup_entry.backup_path, restore_path)
            
            self._log_success(f"Backup restored to: {restore_path}")
            return True
        
        except Exception as e:
            self._log_error(f"Error restoring backup: {e}")
            return False
    
    def delete_backup(self, backup_entry: BackupEntry) -> bool:
        """
        Delete a backup
        
        Args:
            backup_entry: BackupEntry to delete
            
        Returns:
            True if deletion successful
        """
        try:
            if os.path.exists(backup_entry.backup_path):
                os.remove(backup_entry.backup_path)
                self._log_info(f"Deleted backup: {os.path.basename(backup_entry.backup_path)}")
            
            # Remove from index
            self.backups = [b for b in self.backups if b.backup_path != backup_entry.backup_path]
            self._save_index()
            
            return True
        
        except Exception as e:
            self._log_error(f"Error deleting backup: {e}")
            return False
    
    def get_backups_for_game(self, game_name: str) -> List[BackupEntry]:
        """
        Get all backups for a specific game
        
        Args:
            game_name: Name of the game
            
        Returns:
            List of BackupEntry objects
        """
        return [b for b in self.backups if game_name.lower() in b.game_name.lower()]
    
    def get_all_backups(self) -> List[BackupEntry]:
        """Get all backups"""
        return self.backups
    
    def get_backup_by_path(self, backup_path: str) -> Optional[BackupEntry]:
        """Get backup entry by backup path"""
        for backup in self.backups:
            if backup.backup_path == backup_path:
                return backup
        return None
    
    def cleanup_old_backups(self, max_backups_per_game: int = 5) -> int:
        """
        Clean up old backups, keeping only the most recent ones per game
        
        Args:
            max_backups_per_game: Maximum number of backups to keep per game
            
        Returns:
            Number of backups deleted
        """
        deleted_count = 0
        
        # Group backups by game name
        game_backups = {}
        for backup in self.backups:
            game_name = backup.game_name
            if game_name not in game_backups:
                game_backups[game_name] = []
            game_backups[game_name].append(backup)
        
        # Sort and delete old backups
        for game_name, backups in game_backups.items():
            # Sort by timestamp (newest first)
            backups.sort(key=lambda b: b.timestamp, reverse=True)
            
            # Delete old backups beyond the limit
            for old_backup in backups[max_backups_per_game:]:
                if self.delete_backup(old_backup):
                    deleted_count += 1
        
        if deleted_count > 0:
            self._log_info(f"Cleaned up {deleted_count} old backups")
        
        return deleted_count
    
    def get_backup_size_info(self) -> Dict[str, any]:
        """
        Get information about backup directory size
        
        Returns:
            Dictionary with size information
        """
        total_size = 0
        file_count = 0
        
        for backup in self.backups:
            if os.path.exists(backup.backup_path):
                total_size += os.path.getsize(backup.backup_path)
                file_count += 1
        
        return {
            'total_size': total_size,
            'total_size_formatted': self._format_bytes(total_size),
            'file_count': file_count,
            'backup_dir': self.backup_dir
        }
    
    def _load_index(self) -> List[BackupEntry]:
        """Load backup index from file"""
        if not os.path.exists(self.index_file):
            return []
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return [BackupEntry.from_dict(entry) for entry in data]
        
        except Exception as e:
            self._log_error(f"Error loading backup index: {e}")
            return []
    
    def _save_index(self):
        """Save backup index to file"""
        try:
            data = [backup.to_dict() for backup in self.backups]
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            self._log_error(f"Error saving backup index: {e}")
    
    def _format_bytes(self, bytes_size: int) -> str:
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
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
