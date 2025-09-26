"""
Configuration Migration System for HyprRice

Handles version migration of configuration files, ensuring backward
compatibility and smooth upgrades.
"""

import json
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import logging
import re

from .exceptions import ConfigError, ValidationError
from .security import SecureFileHandler


@dataclass
class MigrationStep:
    """Represents a single migration step."""
    from_version: str
    to_version: str
    description: str
    migration_func: Callable[[Dict[str, Any]], Dict[str, Any]]
    required: bool = True
    backup_required: bool = True


class VersionManager:
    """Manages version comparison and validation."""
    
    VERSION_PATTERN = re.compile(r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9]+))?$')
    
    @classmethod
    def parse_version(cls, version_str: str) -> tuple:
        """Parse version string into components."""
        match = cls.VERSION_PATTERN.match(version_str)
        if not match:
            raise ValidationError(f"Invalid version format: {version_str}")
        
        major, minor, patch, suffix = match.groups()
        return (int(major), int(minor), int(patch), suffix or "")
    
    @classmethod
    def compare_versions(cls, version1: str, version2: str) -> int:
        """Compare two versions. Returns -1, 0, or 1."""
        v1 = cls.parse_version(version1)
        v2 = cls.parse_version(version2)
        
        # Compare major, minor, patch
        for i in range(3):
            if v1[i] < v2[i]:
                return -1
            elif v1[i] > v2[i]:
                return 1
        
        # Compare suffix
        if v1[3] == "" and v2[3] != "":
            return 1  # Release version > pre-release
        elif v1[3] != "" and v2[3] == "":
            return -1  # Pre-release < release version
        elif v1[3] < v2[3]:
            return -1
        elif v1[3] > v2[3]:
            return 1
        
        return 0
    
    @classmethod
    def is_version_compatible(cls, current: str, required: str) -> bool:
        """Check if current version is compatible with required version."""
        return cls.compare_versions(current, required) >= 0


class ConfigMigrator:
    """Handles configuration migration between versions."""
    
    CURRENT_VERSION = "1.0.0"
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.file_handler = SecureFileHandler()
        self.migration_steps: List[MigrationStep] = []
        self._register_migrations()
    
    def _register_migrations(self):
        """Register all migration steps."""
        
        # Migration from 0.1.0 to 0.2.0
        self.migration_steps.append(MigrationStep(
            from_version="0.1.0",
            to_version="0.2.0",
            description="Add plugin system configuration",
            migration_func=self._migrate_0_1_0_to_0_2_0
        ))
        
        # Migration from 0.2.0 to 0.3.0
        self.migration_steps.append(MigrationStep(
            from_version="0.2.0",
            to_version="0.3.0",
            description="Restructure theme configuration",
            migration_func=self._migrate_0_2_0_to_0_3_0
        ))
        
        # Migration from 0.3.0 to 1.0.0
        self.migration_steps.append(MigrationStep(
            from_version="0.3.0",
            to_version="1.0.0",
            description="Add security and performance settings",
            migration_func=self._migrate_0_3_0_to_1_0_0
        ))
    
    def get_config_version(self, config_data: Dict[str, Any]) -> str:
        """Get version from configuration data."""
        # Try different version locations
        version_locations = [
            ['version'],
            ['meta', 'version'],
            ['general', 'version'],
            ['_version']
        ]
        
        for location in version_locations:
            try:
                data = config_data
                for key in location:
                    data = data[key]
                return str(data)
            except (KeyError, TypeError):
                continue
        
        # Default to oldest version if not found
        return "0.1.0"
    
    def set_config_version(self, config_data: Dict[str, Any], version: str):
        """Set version in configuration data."""
        if 'meta' not in config_data:
            config_data['meta'] = {}
        config_data['meta']['version'] = version
        config_data['meta']['migrated_at'] = datetime.now().isoformat()
    
    def needs_migration(self, config_data: Dict[str, Any]) -> bool:
        """Check if configuration needs migration."""
        current_version = self.get_config_version(config_data)
        return VersionManager.compare_versions(current_version, self.CURRENT_VERSION) < 0
    
    def get_migration_path(self, from_version: str, to_version: str = None) -> List[MigrationStep]:
        """Get migration path from one version to another."""
        to_version = to_version or self.CURRENT_VERSION
        
        if VersionManager.compare_versions(from_version, to_version) >= 0:
            return []  # No migration needed
        
        # Find migration path
        path = []
        current_version = from_version
        
        while VersionManager.compare_versions(current_version, to_version) < 0:
            # Find next migration step
            next_step = None
            for step in self.migration_steps:
                if step.from_version == current_version:
                    next_step = step
                    break
            
            if next_step is None:
                raise ConfigError(f"No migration path from {current_version} to {to_version}")
            
            path.append(next_step)
            current_version = next_step.to_version
        
        return path
    
    def migrate_config(self, config_data: Dict[str, Any], target_version: str = None) -> Dict[str, Any]:
        """Migrate configuration to target version."""
        target_version = target_version or self.CURRENT_VERSION
        current_version = self.get_config_version(config_data)
        
        if VersionManager.compare_versions(current_version, target_version) >= 0:
            self.logger.info(f"Configuration is already at version {current_version}")
            return config_data
        
        self.logger.info(f"Migrating configuration from {current_version} to {target_version}")
        
        # Get migration path
        migration_path = self.get_migration_path(current_version, target_version)
        
        # Apply migrations
        migrated_data = config_data.copy()
        for step in migration_path:
            self.logger.info(f"Applying migration: {step.description}")
            
            try:
                migrated_data = step.migration_func(migrated_data)
                self.set_config_version(migrated_data, step.to_version)
                self.logger.info(f"Successfully migrated to version {step.to_version}")
            except Exception as e:
                raise ConfigError(f"Migration failed at step {step.description}: {e}")
        
        return migrated_data
    
    def migrate_config_file(self, config_path: Path, backup: bool = True) -> bool:
        """Migrate configuration file in place."""
        if not config_path.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")
        
        # Load current configuration
        config_data = self.file_handler.safe_read_yaml(config_path)
        
        if not self.needs_migration(config_data):
            self.logger.info("Configuration is up to date")
            return False
        
        # Create backup if requested
        if backup:
            backup_path = self._create_backup(config_path)
            self.logger.info(f"Created backup: {backup_path}")
        
        # Migrate configuration
        migrated_data = self.migrate_config(config_data)
        
        # Write migrated configuration
        self.file_handler.safe_write_yaml(migrated_data, config_path)
        
        self.logger.info(f"Successfully migrated {config_path}")
        return True
    
    def _create_backup(self, config_path: Path) -> Path:
        """Create backup of configuration file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = config_path.with_suffix(f".backup_{timestamp}{config_path.suffix}")
        shutil.copy2(config_path, backup_path)
        return backup_path
    
    # Migration functions
    def _migrate_0_1_0_to_0_2_0(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from 0.1.0 to 0.2.0 - Add plugin system."""
        migrated = config_data.copy()
        
        # Add plugins section
        if 'plugins' not in migrated:
            migrated['plugins'] = {
                'enabled': True,
                'auto_load': ['terminal_theming', 'notification_theming'],
                'security_level': 'medium',
                'sandbox_enabled': True
            }
        
        # Add performance section
        if 'performance' not in migrated:
            migrated['performance'] = {
                'monitoring_enabled': True,
                'cache_size': 1000,
                'cache_ttl': 300
            }
        
        return migrated
    
    def _migrate_0_2_0_to_0_3_0(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from 0.2.0 to 0.3.0 - Restructure themes."""
        migrated = config_data.copy()
        
        # Restructure theme configuration
        if 'themes' in migrated and isinstance(migrated['themes'], list):
            # Convert old list format to new dict format
            old_themes = migrated['themes']
            migrated['themes'] = {
                'current': old_themes[0] if old_themes else 'default',
                'available': old_themes,
                'auto_apply': True,
                'backup_on_change': True
            }
        
        # Update color format
        if 'colors' in migrated:
            colors = migrated['colors']
            for key, value in colors.items():
                if isinstance(value, str) and not value.startswith('#'):
                    # Convert named colors to hex
                    colors[key] = self._convert_named_color_to_hex(value)
        
        return migrated
    
    def _migrate_0_3_0_to_1_0_0(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from 0.3.0 to 1.0.0 - Add security settings."""
        migrated = config_data.copy()
        
        # Add security section
        if 'security' not in migrated:
            migrated['security'] = {
                'input_validation': True,
                'path_restrictions': True,
                'command_sanitization': True,
                'file_size_limits': True
            }
        
        # Update plugin configuration
        if 'plugins' in migrated:
            plugins = migrated['plugins']
            if 'sandbox_enabled' not in plugins:
                plugins['sandbox_enabled'] = True
            if 'security_level' not in plugins:
                plugins['security_level'] = 'medium'
        
        # Add backup encryption option
        if 'general' in migrated:
            general = migrated['general']
            if 'encrypt_backups' not in general:
                general['encrypt_backups'] = False
        
        return migrated
    
    def _convert_named_color_to_hex(self, color_name: str) -> str:
        """Convert named color to hex format."""
        color_map = {
            'red': '#ff0000',
            'green': '#00ff00',
            'blue': '#0000ff',
            'white': '#ffffff',
            'black': '#000000',
            'yellow': '#ffff00',
            'cyan': '#00ffff',
            'magenta': '#ff00ff'
        }
        
        return color_map.get(color_name.lower(), color_name)


class BackupManager:
    """Manages configuration backups during migration."""
    
    def __init__(self, backup_dir: Path):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def create_migration_backup(self, config_path: Path, version: str) -> Path:
        """Create a backup before migration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pre_migration_{version}_{timestamp}_{config_path.name}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(config_path, backup_path)
        
        # Create metadata file
        metadata = {
            'original_path': str(config_path),
            'version': version,
            'created_at': datetime.now().isoformat(),
            'backup_type': 'pre_migration'
        }
        
        metadata_path = backup_path.with_suffix('.metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Created migration backup: {backup_path}")
        return backup_path
    
    def list_migration_backups(self) -> List[Dict[str, Any]]:
        """List all migration backups."""
        backups = []
        
        for backup_file in self.backup_dir.glob("pre_migration_*"):
            if backup_file.suffix == '.json':
                continue  # Skip metadata files
            
            metadata_file = backup_file.with_suffix('.metadata.json')
            if metadata_file.exists():
                try:
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    
                    backups.append({
                        'path': backup_file,
                        'metadata': metadata
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to read metadata for {backup_file}: {e}")
        
        return sorted(backups, key=lambda x: x['metadata']['created_at'], reverse=True)
    
    def restore_backup(self, backup_path: Path, target_path: Path) -> bool:
        """Restore a backup to target location."""
        try:
            shutil.copy2(backup_path, target_path)
            self.logger.info(f"Restored backup {backup_path} to {target_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            return False


def migrate_user_config(config_path: str = None) -> bool:
    """Convenience function to migrate user configuration."""
    if config_path is None:
        config_path = Path.home() / ".config" / "hyprrice" / "config.yaml"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        logging.getLogger(__name__).info("No configuration file found, skipping migration")
        return False
    
    migrator = ConfigMigrator()
    return migrator.migrate_config_file(config_path)


def check_migration_needed(config_path: str = None) -> bool:
    """Check if configuration migration is needed."""
    if config_path is None:
        config_path = Path.home() / ".config" / "hyprrice" / "config.yaml"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        return False
    
    try:
        migrator = ConfigMigrator()
        file_handler = SecureFileHandler()
        config_data = file_handler.safe_read_yaml(config_path)
        return migrator.needs_migration(config_data)
    except Exception as e:
        logging.getLogger(__name__).error(f"Error checking migration status: {e}")
        return False


def migrate_config(config_path: str = None) -> bool:
    """Convenience function to migrate configuration."""
    return migrate_user_config(config_path)


if __name__ == "__main__":
    # Command-line interface for migration
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="HyprRice Configuration Migration Tool")
    parser.add_argument("config_path", nargs="?", help="Path to configuration file")
    parser.add_argument("--check", action="store_true", help="Check if migration is needed")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup")
    parser.add_argument("--target-version", help="Target version for migration")
    
    args = parser.parse_args()
    
    if args.check:
        needed = check_migration_needed(args.config_path)
        print("Migration needed" if needed else "No migration needed")
        sys.exit(0 if not needed else 1)
    
    try:
        migrator = ConfigMigrator()
        config_path = Path(args.config_path) if args.config_path else Path.home() / ".config" / "hyprrice" / "config.yaml"
        
        if migrator.migrate_config_file(config_path, backup=not args.no_backup):
            print("Migration completed successfully")
        else:
            print("No migration was needed")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
