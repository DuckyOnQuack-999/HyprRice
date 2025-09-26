"""
Backup and history management for HyprRice
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from .config import Config
from .utils import backup_file, restore_file, list_backups, cleanup_old_backups


@dataclass
class HistoryEntry:
    """Represents a single history entry."""
    timestamp: str
    action: str
    description: str
    config_snapshot: Dict[str, Any]
    file_path: Optional[str] = None


class BackupManager:
    """Manages configuration backups and history."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.history: List[HistoryEntry] = []
        self.undo_stack: List[HistoryEntry] = []
        self.redo_stack: List[HistoryEntry] = []
        self.max_history_size = 100
        self.max_undo_stack_size = 50
        
        # Load existing history
        self._load_history()
    
    def create_backup(self, description: str = "Manual backup") -> bool:
        """Create a backup of the current configuration."""
        try:
            config_path = self.config._get_default_config_path()
            backup_dir = self.config.paths.backup_dir
            
            # Create backup
            backup_path = backup_file(config_path, backup_dir)
            
            # Add to history
            self._add_history_entry(
                action="backup",
                description=description,
                file_path=backup_path
            )
            
            # Cleanup old backups
            cleanup_old_backups(backup_dir, self.config.general.backup_retention)
            
            self.logger.info(f"Backup created: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return False
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore configuration from a backup."""
        try:
            config_path = self.config._get_default_config_path()
            backup_dir = self.config.paths.backup_dir
            backup_path = os.path.join(backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                self.logger.error(f"Backup not found: {backup_path}")
                return False
            
            # Create backup before restoring
            self.create_backup("Pre-restore backup")
            
            # Restore backup
            restore_file(backup_path, config_path)
            
            # Reload configuration
            self.config = Config.load(config_path)
            
            # Add to history
            self._add_history_entry(
                action="restore",
                description=f"Restored from {backup_name}"
            )
            
            self.logger.info(f"Configuration restored from: {backup_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring backup: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, str]]:
        """List available backups."""
        try:
            backup_dir = self.config.paths.backup_dir
            return list_backups(backup_dir)
        except Exception as e:
            self.logger.error(f"Error listing backups: {e}")
            return []
    
    def delete_backup(self, backup_name: str) -> bool:
        """Delete a backup."""
        try:
            backup_dir = self.config.paths.backup_dir
            backup_path = os.path.join(backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                self.logger.error(f"Backup not found: {backup_path}")
                return False
            
            os.unlink(backup_path)
            
            # Add to history
            self._add_history_entry(
                action="delete_backup",
                description=f"Deleted backup {backup_name}"
            )
            
            self.logger.info(f"Backup deleted: {backup_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting backup: {e}")
            return False
    
    def save_state(self, action: str, description: str = "") -> None:
        """Save current state for undo/redo functionality."""
        try:
            # Create snapshot of current config
            config_snapshot = self.config._to_dict()
            
            # Add to undo stack
            entry = HistoryEntry(
                timestamp=datetime.now().isoformat(),
                action=action,
                description=description,
                config_snapshot=config_snapshot
            )
            
            self.undo_stack.append(entry)
            
            # Limit undo stack size
            if len(self.undo_stack) > self.max_undo_stack_size:
                self.undo_stack.pop(0)
            
            # Clear redo stack when new action is performed
            self.redo_stack.clear()
            
            # Add to history
            self._add_history_entry(
                action=action,
                description=description,
                config_snapshot=config_snapshot
            )
            
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")
    
    def undo(self) -> bool:
        """Undo the last action."""
        try:
            if not self.undo_stack:
                self.logger.warning("Nothing to undo")
                return False
            
            # Get last entry from undo stack
            entry = self.undo_stack.pop()
            
            # Save current state to redo stack
            current_snapshot = self.config._to_dict()
            redo_entry = HistoryEntry(
                timestamp=datetime.now().isoformat(),
                action="redo",
                description=f"Redo: {entry.description}",
                config_snapshot=current_snapshot
            )
            self.redo_stack.append(redo_entry)
            
            # Restore previous state
            self._restore_config_snapshot(entry.config_snapshot)
            
            # Add to history
            self._add_history_entry(
                action="undo",
                description=f"Undid: {entry.description}"
            )
            
            self.logger.info(f"Undid: {entry.description}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error undoing: {e}")
            return False
    
    def redo(self) -> bool:
        """Redo the last undone action."""
        try:
            if not self.redo_stack:
                self.logger.warning("Nothing to redo")
                return False
            
            # Get last entry from redo stack
            entry = self.redo_stack.pop()
            
            # Save current state to undo stack
            current_snapshot = self.config._to_dict()
            undo_entry = HistoryEntry(
                timestamp=datetime.now().isoformat(),
                action="undo",
                description=f"Undo: {entry.description}",
                config_snapshot=current_snapshot
            )
            self.undo_stack.append(undo_entry)
            
            # Restore state
            self._restore_config_snapshot(entry.config_snapshot)
            
            # Add to history
            self._add_history_entry(
                action="redo",
                description=f"Redid: {entry.description}"
            )
            
            self.logger.info(f"Redid: {entry.description}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error redoing: {e}")
            return False
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return len(self.redo_stack) > 0
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent history entries."""
        try:
            recent_history = self.history[-limit:] if limit > 0 else self.history
            return [asdict(entry) for entry in recent_history]
        except Exception as e:
            self.logger.error(f"Error getting history: {e}")
            return []
    
    def clear_history(self) -> bool:
        """Clear all history."""
        try:
            self.history.clear()
            self.undo_stack.clear()
            self.redo_stack.clear()
            self._save_history()
            self.logger.info("History cleared")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing history: {e}")
            return False
    
    def export_history(self, file_path: str) -> bool:
        """Export history to a file."""
        try:
            history_data = {
                'exported_at': datetime.now().isoformat(),
                'history': [asdict(entry) for entry in self.history]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2)
            
            self.logger.info(f"History exported to: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting history: {e}")
            return False
    
    def import_history(self, file_path: str) -> bool:
        """Import history from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            if 'history' not in history_data:
                self.logger.error("Invalid history file format")
                return False
            
            # Clear existing history
            self.history.clear()
            
            # Import history entries
            for entry_data in history_data['history']:
                entry = HistoryEntry(**entry_data)
                self.history.append(entry)
            
            # Save imported history
            self._save_history()
            
            self.logger.info(f"History imported from: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing history: {e}")
            return False
    
    def _add_history_entry(self, action: str, description: str, 
                          config_snapshot: Optional[Dict[str, Any]] = None,
                          file_path: Optional[str] = None) -> None:
        """Add an entry to the history."""
        try:
            # Create config snapshot if not provided
            if config_snapshot is None:
                config_snapshot = self.config._to_dict()
            
            entry = HistoryEntry(
                timestamp=datetime.now().isoformat(),
                action=action,
                description=description,
                config_snapshot=config_snapshot,
                file_path=file_path
            )
            
            self.history.append(entry)
            
            # Limit history size
            if len(self.history) > self.max_history_size:
                self.history.pop(0)
            
            # Save history
            self._save_history()
            
        except Exception as e:
            self.logger.error(f"Error adding history entry: {e}")
    
    def _restore_config_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Restore configuration from a snapshot."""
        try:
            # Create new config from snapshot
            new_config = Config._from_dict(snapshot)
            
            # Update current config
            self.config.general = new_config.general
            self.config.paths = new_config.paths
            self.config.gui = new_config.gui
            self.config.hyprland = new_config.hyprland
            self.config.waybar = new_config.waybar
            self.config.rofi = new_config.rofi
            self.config.notifications = new_config.notifications
            self.config.clipboard = new_config.clipboard
            self.config.lockscreen = new_config.lockscreen
            
            # Save configuration
            self.config.save()
            
        except Exception as e:
            self.logger.error(f"Error restoring config snapshot: {e}")
            raise
    
    def _load_history(self) -> None:
        """Load history from file."""
        try:
            history_file = Path(self.config.paths.backup_dir) / "history.json"
            if not history_file.exists():
                return
            
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            if 'history' in history_data:
                for entry_data in history_data['history']:
                    entry = HistoryEntry(**entry_data)
                    self.history.append(entry)
            
            self.logger.info(f"Loaded {len(self.history)} history entries")
            
        except Exception as e:
            self.logger.error(f"Error loading history: {e}")
    
    def _save_history(self) -> None:
        """Save history to file."""
        try:
            history_file = Path(self.config.paths.backup_dir) / "history.json"
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            history_data = {
                'saved_at': datetime.now().isoformat(),
                'history': [asdict(entry) for entry in self.history]
            }
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error saving history: {e}")
    
    def auto_backup(self) -> bool:
        """Create automatic backup if enabled."""
        if not self.config.general.auto_backup:
            return False
        
        return self.create_backup("Automatic backup")
    
    def get_backup_info(self, backup_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific backup."""
        try:
            backup_dir = self.config.paths.backup_dir
            backup_path = os.path.join(backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                return None
            
            stat = os.stat(backup_path)
            return {
                'name': backup_name,
                'path': backup_path,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting backup info: {e}")
            return None








