"""
Tests for backup and history path handling fixes
"""

import unittest
import tempfile
import sys
import os
from pathlib import Path
from unittest.mock import Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hyprrice.backup_manager import BackupManager
from hyprrice.history import HistoryManager
from hyprrice.config import Config


class TestBackupPaths(unittest.TestCase):
    """Test backup and history path handling fixes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_backup_manager_with_config_object(self):
        """Test BackupManager with Config object."""
        config = Config()
        config.paths = Mock()
        config.paths.backup_dir = self.temp_dir
        
        backup_manager = BackupManager(config)
        self.assertIsNotNone(backup_manager.config)
        self.assertEqual(backup_manager.config.paths.backup_dir, self.temp_dir)
    
    def test_backup_manager_with_string_path(self):
        """Test BackupManager with string path (backward compatibility)."""
        backup_manager = BackupManager(self.temp_dir)
        self.assertIsNotNone(backup_manager.config)
        self.assertEqual(backup_manager.config.paths.backup_dir, self.temp_dir)
    
    def test_history_manager_with_config_object(self):
        """Test HistoryManager with Config object."""
        config = Config()
        config.paths = Mock()
        config.paths.backup_dir = self.temp_dir
        
        history_manager = HistoryManager(config)
        self.assertIsNotNone(history_manager.config)
        self.assertEqual(history_manager.config.paths.backup_dir, self.temp_dir)
    
    def test_history_manager_with_string_path(self):
        """Test HistoryManager with string path (backward compatibility)."""
        history_manager = HistoryManager(self.temp_dir)
        self.assertIsNotNone(history_manager.config)
        self.assertEqual(history_manager.config.paths.backup_dir, self.temp_dir)
    
    def test_history_manager_with_none_config(self):
        """Test HistoryManager with None config."""
        history_manager = HistoryManager(None)
        self.assertIsNone(history_manager.config)


if __name__ == '__main__':
    unittest.main()
