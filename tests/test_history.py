"""
Tests for history management system
"""

import unittest
import tempfile
import os
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hyprrice.history import HistoryManager, BackupManager, Command, ConfigChangeCommand
from hyprrice.config import Config


class TestHistoryManager(unittest.TestCase):
    """Test HistoryManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.history_manager = HistoryManager(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_history_manager_initialization(self):
        """Test HistoryManager initialization."""
        self.assertIsNotNone(self.history_manager)
        self.assertEqual(self.history_manager.config, self.config)
        self.assertEqual(len(self.history_manager._undo_stack), 0)
        self.assertEqual(len(self.history_manager._redo_stack), 0)
    
    def test_execute_command(self):
        """Test executing a command."""
        class TestCommand(Command):
            def __init__(self):
                super().__init__("Test command")
                self.executed = False
                self.undone = False
            
            def execute(self):
                self.executed = True
            
            def undo(self):
                self.undone = True
        
        command = TestCommand()
        self.history_manager.execute(command)
        
        self.assertTrue(command.executed)
        self.assertEqual(len(self.history_manager._undo_stack), 1)
        self.assertEqual(len(self.history_manager._redo_stack), 0)
    
    def test_undo_command(self):
        """Test undoing a command."""
        class TestCommand(Command):
            def __init__(self):
                super().__init__("Test command")
                self.executed = False
                self.undone = False
            
            def execute(self):
                self.executed = True
            
            def undo(self):
                self.undone = True
        
        command = TestCommand()
        self.history_manager.execute(command)
        
        # Undo the command
        result = self.history_manager.undo()
        
        self.assertTrue(result)
        self.assertTrue(command.undone)
        self.assertEqual(len(self.history_manager._undo_stack), 0)
        self.assertEqual(len(self.history_manager._redo_stack), 1)
    
    def test_redo_command(self):
        """Test redoing a command."""
        class TestCommand(Command):
            def __init__(self):
                super().__init__("Test command")
                self.executed = False
                self.undone = False
            
            def execute(self):
                self.executed = True
            
            def undo(self):
                self.undone = True
        
        command = TestCommand()
        self.history_manager.execute(command)
        self.history_manager.undo()
        
        # Redo the command
        result = self.history_manager.redo()
        
        self.assertTrue(result)
        self.assertEqual(len(self.history_manager._undo_stack), 1)
        self.assertEqual(len(self.history_manager._redo_stack), 0)
    
    def test_cannot_undo_when_empty(self):
        """Test that undo fails when stack is empty."""
        result = self.history_manager.undo()
        self.assertFalse(result)
    
    def test_cannot_redo_when_empty(self):
        """Test that redo fails when stack is empty."""
        result = self.history_manager.redo()
        self.assertFalse(result)
    
    def test_can_undo_redo(self):
        """Test can_undo and can_redo methods."""
        class TestCommand(Command):
            def execute(self):
                pass
            
            def undo(self):
                pass
        
        # Initially cannot undo or redo
        self.assertFalse(self.history_manager.can_undo())
        self.assertFalse(self.history_manager.can_redo())
        
        # After executing command, can undo but not redo
        command = TestCommand()
        self.history_manager.execute(command)
        self.assertTrue(self.history_manager.can_undo())
        self.assertFalse(self.history_manager.can_redo())
        
        # After undo, can redo but not undo
        self.history_manager.undo()
        self.assertFalse(self.history_manager.can_undo())
        self.assertTrue(self.history_manager.can_redo())
    
    def test_clear_history(self):
        """Test clearing history."""
        class TestCommand(Command):
            def execute(self):
                pass
            
            def undo(self):
                pass
        
        # Add some commands
        for i in range(3):
            command = TestCommand()
            self.history_manager.execute(command)
        
        # Clear history
        self.history_manager.clear()
        
        self.assertEqual(len(self.history_manager._undo_stack), 0)
        self.assertEqual(len(self.history_manager._redo_stack), 0)
        self.assertFalse(self.history_manager.can_undo())
        self.assertFalse(self.history_manager.can_redo())
    
    def test_max_history_limit(self):
        """Test maximum history limit."""
        class TestCommand(Command):
            def execute(self):
                pass
            
            def undo(self):
                pass
        
        # Set max history to 3
        self.history_manager.max_history = 3
        
        # Add more commands than max
        for i in range(5):
            command = TestCommand()
            self.history_manager.execute(command)
        
        # Should only have max_history commands
        self.assertEqual(len(self.history_manager._undo_stack), 3)
    
    def test_redo_stack_cleared_on_new_command(self):
        """Test that redo stack is cleared when new command is executed."""
        class TestCommand(Command):
            def execute(self):
                pass
            
            def undo(self):
                pass
        
        # Execute command and undo it
        command1 = TestCommand()
        self.history_manager.execute(command1)
        self.history_manager.undo()
        
        # Now redo stack has one command
        self.assertEqual(len(self.history_manager._redo_stack), 1)
        
        # Execute new command
        command2 = TestCommand()
        self.history_manager.execute(command2)
        
        # Redo stack should be cleared
        self.assertEqual(len(self.history_manager._redo_stack), 0)
        self.assertEqual(len(self.history_manager._undo_stack), 2)


class TestBackupManager(unittest.TestCase):
    """Test BackupManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.backup_manager = BackupManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_backup_manager_initialization(self):
        """Test BackupManager initialization."""
        self.assertIsNotNone(self.backup_manager)
        self.assertEqual(self.backup_manager.backup_dir, self.temp_dir)
        self.assertEqual(self.backup_manager.max_backups, 10)
    
    def test_create_backup(self):
        """Test creating a backup."""
        with patch.object(self.config, 'save') as mock_save:
            result = self.backup_manager.create_backup(self.config, "Test backup")
            
            self.assertIsNotNone(result)
            self.assertTrue(os.path.exists(result))
            mock_save.assert_called_once()
    
    def test_restore_backup(self):
        """Test restoring a backup."""
        # Create a backup first
        backup_path = self.backup_manager.create_backup(self.config, "Test backup")
        
        # Restore the backup
        result = self.backup_manager.restore_backup(backup_path)
        
        self.assertTrue(result)
    
    def test_restore_nonexistent_backup(self):
        """Test restoring a non-existent backup."""
        result = self.backup_manager.restore_backup("/nonexistent/path.yaml")
        self.assertFalse(result)
    
    def test_list_backups(self):
        """Test listing backups."""
        # Create some backups
        self.backup_manager.create_backup(self.config, "Backup 1")
        self.backup_manager.create_backup(self.config, "Backup 2")
        
        backups = self.backup_manager.list_backups()
        
        self.assertIsInstance(backups, list)
        self.assertEqual(len(backups), 2)
        
        # Check backup structure
        for backup in backups:
            self.assertIn('path', backup)
            self.assertIn('filename', backup)
            self.assertIn('size', backup)
            self.assertIn('modified', backup)
            self.assertIn('description', backup)
    
    def test_delete_backup(self):
        """Test deleting a backup."""
        # Create a backup
        backup_path = self.backup_manager.create_backup(self.config, "Test backup")
        
        # Delete the backup
        result = self.backup_manager.delete_backup(backup_path)
        
        self.assertTrue(result)
        self.assertFalse(os.path.exists(backup_path))
    
    def test_delete_nonexistent_backup(self):
        """Test deleting a non-existent backup."""
        result = self.backup_manager.delete_backup("/nonexistent/path.yaml")
        self.assertFalse(result)
    
    def test_cleanup_old_backups(self):
        """Test cleanup of old backups."""
        # Set max backups to 2
        self.backup_manager.max_backups = 2
        
        # Create more backups than max
        for i in range(4):
            self.backup_manager.create_backup(self.config, f"Backup {i}")
        
        # Should only have max_backups
        backups = self.backup_manager.list_backups()
        self.assertEqual(len(backups), 2)
    
    def test_extract_description(self):
        """Test extracting description from filename."""
        # Test with description
        filename = "2023-01-01_12-00-00_Test_Backup.yaml"
        description = self.backup_manager._extract_description(filename)
        self.assertEqual(description, "Test Backup")
        
        # Test without description
        filename = "2023-01-01_12-00-00.yaml"
        description = self.backup_manager._extract_description(filename)
        self.assertEqual(description, "Backup")
        
        # Test with invalid filename
        filename = "invalid.yaml"
        description = self.backup_manager._extract_description(filename)
        self.assertEqual(description, "Backup")


class TestConfigChangeCommand(unittest.TestCase):
    """Test ConfigChangeCommand functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.old_state = {'test': 'old_value'}
        self.new_state = {'test': 'new_value'}
        
        # Mock config manager
        self.config_manager = MagicMock()
        self.config_manager.load_state = MagicMock()
        
        self.command = ConfigChangeCommand(
            self.config_manager, self.old_state, self.new_state
        )
    
    def test_config_change_command_initialization(self):
        """Test ConfigChangeCommand initialization."""
        self.assertEqual(self.command.config_manager, self.config_manager)
        self.assertEqual(self.command.old_config_state, self.old_state)
        self.assertEqual(self.command.new_config_state, self.new_state)
    
    def test_execute_command(self):
        """Test executing ConfigChangeCommand."""
        # Execute should do nothing (change already applied)
        self.command.execute()
        
        # No calls to load_state since change is already applied
        self.config_manager.load_state.assert_not_called()
    
    def test_undo_command(self):
        """Test undoing ConfigChangeCommand."""
        self.command.undo()
        
        # Should load old state
        self.config_manager.load_state.assert_called_once_with(self.old_state)
    
    def test_redo_command(self):
        """Test redoing ConfigChangeCommand."""
        self.command.redo()
        
        # Should load new state
        self.config_manager.load_state.assert_called_once_with(self.new_state)


if __name__ == '__main__':
    unittest.main()
