"""
Backup and history management for HyprRice
"""

import os
import json
import shutil
import logging
import gzip
import pickle
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, asdict

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

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
    
    def __init__(self, config_or_backup_dir, compression_enabled=False, encryption_enabled=False):
        # Handle both Config object and backup_dir string for backward compatibility
        if isinstance(config_or_backup_dir, Config):
            self.config = config_or_backup_dir
        else:
            # If string path provided, create a minimal config-like object
            self.config = type('Config', (), {'paths': type('Paths', (), {'backup_dir': config_or_backup_dir})()})()
        self.logger = logging.getLogger(__name__)
        self.history: List[HistoryEntry] = []
        self.undo_stack: List[HistoryEntry] = []
        self.redo_stack: List[HistoryEntry] = []
        self.max_history_size = 100
        self.max_undo_stack_size = 50
        
        # Compression and encryption settings
        self.compression_enabled = compression_enabled
        self.encryption_enabled = encryption_enabled
        self.encryption_key = None
        
        # Initialize encryption key if encryption is enabled
        if self.encryption_enabled and CRYPTOGRAPHY_AVAILABLE:
            self.encryption_key = self._generate_encryption_key()
        elif self.encryption_enabled and not CRYPTOGRAPHY_AVAILABLE:
            self.logger.warning("Cryptography not available. Encryption disabled.")
            self.encryption_enabled = False
        
        # Load existing history
        self._load_history()
    
    def create_backup(self, description: str = "Manual backup") -> bool:
        """Create a backup of the current configuration."""
        try:
            config_path = self.config._get_default_config_path()
            backup_dir = self.config.paths.backup_dir
            
            # Create timestamped backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"hyprrice_backup_{timestamp}.json"
            
            if self.compression_enabled:
                backup_filename += ".gz"
            
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Ensure backup directory exists
            os.makedirs(backup_dir, exist_ok=True)
            
            # Read configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = f.read()
            
            # Create backup data
            backup_data = {
                "timestamp": timestamp,
                "description": description,
                "config_data": config_data,
                "compression_enabled": self.compression_enabled,
                "encryption_enabled": self.encryption_enabled
            }
            
            # Prepare data for writing
            data_to_write = json.dumps(backup_data, indent=2)
            
            # Write backup with encryption and compression
            if self.encryption_enabled and self.compression_enabled:
                # Encrypt first, then compress
                encrypted_data = self._encrypt_data(data_to_write)
                if encrypted_data is None:
                    raise Exception("Failed to encrypt backup data")
                
                with gzip.open(backup_path, 'wb') as f:
                    f.write(encrypted_data)
                    
            elif self.encryption_enabled:
                # Encrypt only
                encrypted_data = self._encrypt_data(data_to_write)
                if encrypted_data is None:
                    raise Exception("Failed to encrypt backup data")
                
                with open(backup_path, 'wb') as f:
                    f.write(encrypted_data)
                    
            elif self.compression_enabled:
                # Compress only
                with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                    f.write(data_to_write)
            else:
                # Plain text
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(data_to_write)
            
            # Add to history
            self._add_history_entry(
                action="backup",
                description=description,
                file_path=backup_path
            )
            
            # Cleanup old backups
            cleanup_old_backups(backup_dir, getattr(self.config.general, 'backup_retention', 10))
            
            compression_info = "(compressed)" if self.compression_enabled else ""
            encryption_info = "(encrypted)" if self.encryption_enabled else ""
            self.logger.info(f"Backup created: {backup_path} {compression_info} {encryption_info}")
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
            
            # Read backup data
            backup_data = None
            
            # Check if the backup is encrypted by attempting to read metadata
            try:
                if backup_path.endswith('.gz'):
                    # Try reading as compressed first
                    with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                        backup_data = json.load(f)
                else:
                    # Try reading as plain text first
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                # If JSON decode fails, try reading as binary (encrypted)
                try:
                    with open(backup_path, 'rb') as f:
                        encrypted_data = f.read()
                    
                    # Try decompressing first if it's a .gz file
                    if backup_path.endswith('.gz'):
                        encrypted_data = gzip.decompress(encrypted_data)
                    
                    # Decrypt the data
                    decrypted_data = self._decrypt_data(encrypted_data)
                    if decrypted_data is None:
                        raise Exception("Failed to decrypt backup data")
                    
                    backup_data = json.loads(decrypted_data)
                    
                except Exception as decrypt_error:
                    self.logger.error(f"Failed to read backup file: {decrypt_error}")
                    # Try legacy restore
                    restore_file(backup_path, config_path)
                    return True
            
            # Extract configuration data
            if isinstance(backup_data, dict) and 'config_data' in backup_data:
                # New compressed format
                config_data = backup_data['config_data']
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(config_data)
            else:
                # Legacy format - restore file directly
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
    
    def enable_compression(self):
        """Enable gzip compression for new backups."""
        self.compression_enabled = True
        self.logger.info("Backup compression enabled")
    
    def disable_compression(self):
        """Disable gzip compression for new backups."""
        self.compression_enabled = False
        self.logger.info("Backup compression disabled")
    
    def is_compression_enabled(self) -> bool:
        """Check if backup compression is enabled."""
        return self.compression_enabled
    
    def get_backup_info(self, backup_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific backup."""
        try:
            backup_dir = self.config.paths.backup_dir
            backup_path = os.path.join(backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                return None
            
            # Read backup metadata
            if backup_path.endswith('.gz'):
                with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                    backup_data = json.load(f)
            else:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
            
            # Get file stats
            stat = os.stat(backup_path)
            
            info = {
                "name": backup_name,
                "path": backup_path,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "is_compressed": backup_name.endswith('.gz')
            }
            
            if isinstance(backup_data, dict):
                info.update({
                    "timestamp": backup_data.get("timestamp"),
                    "description": backup_data.get("description"),
                    "compression_enabled": backup_data.get("compression_enabled", False)
                })
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting backup info: {e}")
            return None
    
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
    
    def _generate_encryption_key(self) -> Optional[Fernet]:
        """Generate a new encryption key using a random password."""
        if not CRYPTOGRAPHY_AVAILABLE:
            return None
        
        try:
            # Generate a random password
            password = base64.b64encode(os.urandom(32)).decode('utf-8')
            
            # Derive key from password using PBKDF2
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Store the password and salt for future use (in practice, you'd store this securely)
            self.logger.info("Encryption key generated successfully")
            return Fernet(key)
            
        except Exception as e:
            self.logger.error(f"Error generating encryption key: {e}")
            return None
    
    def _encrypt_data(self, data: str) -> Optional[bytes]:
        """Encrypt data using Fernet."""
        if not self.encryption_enabled or not self.encryption_key:
            return data.encode()
        
        try:
            return self.encryption_key.encrypt(data.encode())
        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}")
            return None
    
    def _decrypt_data(self, encrypted_data: bytes) -> Optional[str]:
        """Decrypt data using Fernet."""
        try:
            return self.encryption_key.decrypt(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}")
            return None
    
    def enable_encryption(self):
        """Enable encryption for new backups."""
        if not CRYPTOGRAPHY_AVAILABLE:
            self.logger.error("Cryptography library not available. Cannot enable encryption.")
            return False
        
        self.encryption_enabled = True
        self.encryption_key = self._generate_encryption_key()
        if self.encryption_key:
            self.logger.info("Backup encryption enabled")
            return True
        else:
            self.logger.error("Failed to generate encryption key")
            self.encryption_enabled = False
            return False
    
    def disable_encryption(self):
        """Disable encryption for new backups."""
        self.encryption_enabled = False
        self.encryption_key = None
        self.logger.info("Backup encryption disabled")
    
    def is_encryption_enabled(self) -> bool:
        """Check if backup encryption is enabled."""
        return self.encryption_enabled
    
    def set_encryption_key(self, password: str, salt: bytes = None) -> bool:
        """Set encryption key from password."""
        if not CRYPTOGRAPHY_AVAILABLE:
            self.logger.error("Cryptography library not available.")
            return False
        
        try:
            if salt is None:
                salt = os.urandom(16)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            self.encryption_key = Fernet(key)
            self.encryption_enabled = True
            self.logger.info("Encryption key set from password")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting encryption key: {e}")
            return False





