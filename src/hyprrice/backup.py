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
    file_paths: List[str]
    metadata: Dict[str, Any]


@dataclass
class BackupEntry:
    """Represents a backup entry."""
    timestamp: str
    name: str
    description: str
    file_paths: List[str]
    size: int
    metadata: Dict[str, Any]


class HistoryManager:
    """Manages configuration history and undo/redo functionality."""
    
    def __init__(self, history_dir: str, max_entries: int = 50):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.max_entries = max_entries
        self.logger = logging.getLogger(__name__)
        
        # In-memory history for quick access
        self._history: List[HistoryEntry] = []
        self._current_index = -1
        
        # Load existing history
        self._load_history()
    
    def add_entry(self, action: str, description: str, config: Config, 
                  file_paths: List[str] = None, metadata: Dict[str, Any] = None) -> bool:
        """Add a new history entry."""
        try:
            if file_paths is None:
                file_paths = []
            if metadata is None:
                metadata = {}
            
            # Create history entry
            entry = HistoryEntry(
                timestamp=datetime.now().isoformat(),
                action=action,
                description=description,
                config_snapshot=asdict(config),
                file_paths=file_paths,
                metadata=metadata
            )
            
            # Remove any entries after current index (when branching)
            if self._current_index < len(self._history) - 1:
                self._history = self._history[:self._current_index + 1]
            
            # Add new entry
            self._history.append(entry)
            self._current_index = len(self._history) - 1
            
            # Save to disk
            self._save_entry(entry)
            
            # Cleanup old entries
            self._cleanup_old_entries()
            
            self.logger.debug(f"Added history entry: {action} - {description}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding history entry: {e}")
            return False
    
    def undo(self) -> Optional[HistoryEntry]:
        """Undo the last action."""
        if self._current_index < 0:
            self.logger.warning("Nothing to undo")
            return None
        
        # Move to previous state
        self._current_index -= 1
        
        # Return the entry we're restoring to (or None if going to initial state)
        if self._current_index >= 0:
            entry = self._history[self._current_index]
            self.logger.info(f"Undoing to: {entry.action} - {entry.description}")
            return entry
        else:
            self.logger.info("Undoing to initial state")
            return None
    
    def redo(self) -> Optional[HistoryEntry]:
        """Redo the next action."""
        if self._current_index >= len(self._history) - 1:
            self.logger.warning("Nothing to redo")
            return None
        
        self._current_index += 1
        entry = self._history[self._current_index]
        
        self.logger.info(f"Redoing: {entry.action} - {entry.description}")
        return entry
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self._current_index > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return self._current_index < len(self._history) - 1
    
    def get_current_entry(self) -> Optional[HistoryEntry]:
        """Get the current history entry."""
        if 0 <= self._current_index < len(self._history):
            return self._history[self._current_index]
        return None
    
    def get_history(self) -> List[HistoryEntry]:
        """Get the complete history."""
        return self._history.copy()
    
    def clear_history(self) -> bool:
        """Clear all history."""
        try:
            # Clear in-memory history
            self._history.clear()
            self._current_index = -1
            
            # Remove history files
            for history_file in self.history_dir.glob("*.json"):
                history_file.unlink()
            
            self.logger.info("History cleared")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing history: {e}")
            return False
    
    def _load_history(self) -> None:
        """Load history from disk."""
        try:
            history_files = sorted(self.history_dir.glob("*.json"))
            self._history = []
            
            for history_file in history_files:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    entry = HistoryEntry(**data)
                    self._history.append(entry)
            
            self._current_index = len(self._history) - 1
            self.logger.debug(f"Loaded {len(self._history)} history entries")
            
        except Exception as e:
            self.logger.error(f"Error loading history: {e}")
            self._history = []
            self._current_index = -1
    
    def _save_entry(self, entry: HistoryEntry) -> None:
        """Save a history entry to disk."""
        try:
            timestamp = entry.timestamp.replace(':', '-').replace('.', '-')
            history_file = self.history_dir / f"{timestamp}.json"
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(entry), f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving history entry: {e}")
    
    def _cleanup_old_entries(self) -> None:
        """Remove old history entries if limit is exceeded."""
        if len(self._history) <= self.max_entries:
            return
        
        # Remove oldest entries
        entries_to_remove = len(self._history) - self.max_entries
        for i in range(entries_to_remove):
            entry = self._history[i]
            timestamp = entry.timestamp.replace(':', '-').replace('.', '-')
            history_file = self.history_dir / f"{timestamp}.json"
            
            if history_file.exists():
                history_file.unlink()
        
        # Update in-memory history
        self._history = self._history[entries_to_remove:]
        self._current_index = len(self._history) - 1


class BackupManager:
    """Manages configuration backups."""
    
    def __init__(self, backup_dir: str, max_backups: int = 10):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.max_backups = max_backups
        self.logger = logging.getLogger(__name__)
        
        # Backup metadata file
        self.metadata_file = self.backup_dir / "backups.json"
        self._backups: List[BackupEntry] = []
        
        # Load existing backups
        self._load_backups()
    
    def create_backup(self, name: str, description: str, config: Config, 
                     file_paths: List[str] = None, metadata: Dict[str, Any] = None) -> bool:
        """Create a new backup."""
        try:
            if file_paths is None:
                file_paths = []
            if metadata is None:
                metadata = {}
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_name = f"{timestamp}_{name}"
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            # Backup configuration file
            config_backup_path = backup_path / "config.yaml"
            config.save(str(config_backup_path))
            
            # Backup additional files
            backed_up_files = [str(config_backup_path)]
            for file_path in file_paths:
                if os.path.exists(file_path):
                    file_name = Path(file_path).name
                    file_backup_path = backup_path / file_name
                    shutil.copy2(file_path, file_backup_path)
                    backed_up_files.append(str(file_backup_path))
            
            # Calculate total size
            total_size = sum(os.path.getsize(f) for f in backed_up_files if os.path.exists(f))
            
            # Create backup entry
            backup_entry = BackupEntry(
                timestamp=timestamp,
                name=name,
                description=description,
                file_paths=backed_up_files,
                size=total_size,
                metadata=metadata
            )
            
            # Add to backups list
            self._backups.append(backup_entry)
            
            # Save metadata
            self._save_backups()
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            self.logger.info(f"Backup created: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return False
    
    def restore_backup(self, backup_name: str, target_config_path: str = None) -> bool:
        """Restore a backup."""
        try:
            # Find backup entry
            backup_entry = None
            for entry in self._backups:
                if entry.name == backup_name or entry.timestamp in backup_name:
                    backup_entry = entry
                    break
            
            if not backup_entry:
                self.logger.error(f"Backup not found: {backup_name}")
                return False
            
            # Find backup directory
            backup_path = None
            for path in self.backup_dir.iterdir():
                if path.is_dir() and backup_entry.timestamp in path.name:
                    backup_path = path
                    break
            
            if not backup_path:
                self.logger.error(f"Backup directory not found for: {backup_name}")
                return False
            
            # Restore configuration file
            config_backup_path = backup_path / "config.yaml"
            if config_backup_path.exists():
                if target_config_path is None:
                    target_config_path = Config._get_default_config_path()
                
                shutil.copy2(config_backup_path, target_config_path)
                self.logger.info(f"Configuration restored from backup: {backup_name}")
            
            # Restore additional files
            for file_path in backup_entry.file_paths:
                if file_path.endswith("config.yaml"):
                    continue  # Already handled
                
                file_name = Path(file_path).name
                source_path = backup_path / file_name
                if source_path.exists():
                    # Try to determine original location
                    original_path = self._guess_original_path(file_name)
                    if original_path:
                        shutil.copy2(source_path, original_path)
                        self.logger.info(f"File restored: {file_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring backup: {backup_name}: {e}")
            return False
    
    def list_backups(self) -> List[BackupEntry]:
        """List all available backups."""
        return self._backups.copy()
    
    def delete_backup(self, backup_name: str) -> bool:
        """Delete a backup."""
        try:
            # Find backup entry
            backup_entry = None
            for i, entry in enumerate(self._backups):
                if entry.name == backup_name or entry.timestamp in backup_name:
                    backup_entry = entry
                    backup_index = i
                    break
            
            if not backup_entry:
                self.logger.error(f"Backup not found: {backup_name}")
                return False
            
            # Find and remove backup directory
            for path in self.backup_dir.iterdir():
                if path.is_dir() and backup_entry.timestamp in path.name:
                    shutil.rmtree(path)
                    break
            
            # Remove from backups list
            self._backups.pop(backup_index)
            
            # Save metadata
            self._save_backups()
            
            self.logger.info(f"Backup deleted: {backup_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting backup: {e}")
            return False
    
    def get_backup_info(self, backup_name: str) -> Optional[BackupEntry]:
        """Get information about a specific backup."""
        for entry in self._backups:
            if entry.name == backup_name or entry.timestamp in backup_name:
                return entry
        return None
    
    def _load_backups(self) -> None:
        """Load backup metadata from disk."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._backups = [BackupEntry(**entry) for entry in data]
            else:
                self._backups = []
                
            self.logger.debug(f"Loaded {len(self._backups)} backup entries")
            
        except Exception as e:
            self.logger.error(f"Error loading backups: {e}")
            self._backups = []
    
    def _save_backups(self) -> None:
        """Save backup metadata to disk."""
        try:
            data = [asdict(entry) for entry in self._backups]
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving backup metadata: {e}")
    
    def _cleanup_old_backups(self) -> None:
        """Remove old backups if limit is exceeded."""
        if len(self._backups) <= self.max_backups:
            return
        
        # Sort by timestamp (oldest first)
        sorted_backups = sorted(self._backups, key=lambda x: x.timestamp)
        
        # Remove oldest backups
        backups_to_remove = len(self._backups) - self.max_backups
        for i in range(backups_to_remove):
            backup_entry = sorted_backups[i]
            self.delete_backup(backup_entry.name)
    
    def _guess_original_path(self, file_name: str) -> Optional[str]:
        """Guess the original path for a backed up file."""
        # Common file locations
        common_paths = [
            "~/.config/hypr/hyprland.conf",
            "~/.config/waybar/config",
            "~/.config/rofi/config.rasi",
            "~/.config/dunst/dunstrc",
            "~/.config/mako/config",
        ]
        
        for path in common_paths:
            if Path(path).name == file_name:
                return os.path.expanduser(path)
        
        return None


class CommandManager:
    """Manages command pattern for undo/redo functionality."""
    
    def __init__(self, history_manager: HistoryManager):
        self.history_manager = history_manager
        self.logger = logging.getLogger(__name__)
    
    def execute_command(self, command: 'Command') -> bool:
        """Execute a command and add it to history."""
        try:
            if command.execute():
                # Add to history
                self.history_manager.add_entry(
                    action=command.get_action_name(),
                    description=command.get_description(),
                    config=command.get_config(),
                    file_paths=command.get_file_paths(),
                    metadata=command.get_metadata()
                )
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return False
    
    def undo_last_command(self) -> bool:
        """Undo the last command."""
        entry = self.history_manager.undo()
        if entry:
            # Create and execute undo command
            undo_command = UndoCommand(entry)
            return undo_command.execute()
        elif self.history_manager._current_index == -1:
            # Successfully undone to initial state
            return True
        return False
    
    def redo_last_command(self) -> bool:
        """Redo the last command."""
        entry = self.history_manager.redo()
        if entry:
            # Create and execute redo command
            redo_command = RedoCommand(entry)
            return redo_command.execute()
        return False


class Command:
    """Base class for commands."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def execute(self) -> bool:
        """Execute the command."""
        # TODO: Implement backup command execution
        return True
    
    def undo(self) -> bool:
        """Undo the command."""
        # TODO: Implement backup command undo
        return True
    
    def get_action_name(self) -> str:
        """Get the action name."""
        return self.__class__.__name__
    
    def get_description(self) -> str:
        """Get the command description."""
        return f"Execute {self.get_action_name()}"
    
    def get_config(self) -> Config:
        """Get the configuration."""
        return self.config
    
    def get_file_paths(self) -> List[str]:
        """Get affected file paths."""
        return []
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get command metadata."""
        return {}


class UndoCommand(Command):
    """Command to undo a previous action."""
    
    def __init__(self, history_entry: HistoryEntry):
        super().__init__(None)
        self.history_entry = history_entry
    
    def execute(self) -> bool:
        """Execute the undo command."""
        try:
            # Restore configuration from snapshot
            if self.history_entry.config_snapshot:
                # This would need to be implemented based on the specific action
                pass
            
            # Restore files if any
            for file_path in self.history_entry.file_paths:
                # Implementation would depend on the specific file restoration logic
                pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing undo command: {e}")
            return False
    
    def get_description(self) -> str:
        """Get the undo command description."""
        return f"Undo: {self.history_entry.action} - {self.history_entry.description}"


class RedoCommand(Command):
    """Command to redo a previous action."""
    
    def __init__(self, history_entry: HistoryEntry):
        super().__init__(None)
        self.history_entry = history_entry
    
    def execute(self) -> bool:
        """Execute the redo command."""
        try:
            # Re-apply the action
            if self.history_entry.config_snapshot:
                # This would need to be implemented based on the specific action
                pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing redo command: {e}")
            return False
    
    def get_description(self) -> str:
        """Get the redo command description."""
        return f"Redo: {self.history_entry.action} - {self.history_entry.description}"






