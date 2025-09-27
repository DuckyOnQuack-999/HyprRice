"""
Tests for backup and history management system
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.hyprrice.backup import (
    HistoryManager, BackupManager, CommandManager,
    HistoryEntry, BackupEntry, Command, UndoCommand, RedoCommand
)
from src.hyprrice.config import Config


class TestHistoryManager(unittest.TestCase):
    """Test HistoryManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.history_manager = HistoryManager(self.temp_dir, max_entries=5)
        self.config = Config()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_add_entry(self):
        """Test adding history entry."""
        result = self.history_manager.add_entry(
            'test_action', 'Test description', self.config
        )
        
        self.assertTrue(result)
        self.assertEqual(len(self.history_manager._history), 1)
        self.assertEqual(self.history_manager._current_index, 0)
    
    def test_undo_redo(self):
        """Test undo and redo functionality."""
        # Add some entries
        self.history_manager.add_entry('action1', 'First action', self.config)
        self.history_manager.add_entry('action2', 'Second action', self.config)
        self.history_manager.add_entry('action3', 'Third action', self.config)
        
        # Test undo
        self.assertTrue(self.history_manager.can_undo())
        entry = self.history_manager.undo()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.action, 'action2')
        self.assertEqual(self.history_manager._current_index, 1)
        
        # Test redo
        self.assertTrue(self.history_manager.can_redo())
        entry = self.history_manager.redo()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.action, 'action3')
        self.assertEqual(self.history_manager._current_index, 2)
    
    def test_cannot_undo_redo(self):
        """Test undo/redo limits."""
        # Test undo when nothing to undo
        entry = self.history_manager.undo()
        self.assertIsNone(entry)
        self.assertFalse(self.history_manager.can_undo())
        
        # Test redo when nothing to redo
        entry = self.history_manager.redo()
        self.assertIsNone(entry)
        self.assertFalse(self.history_manager.can_redo())
    
    def test_branching_history(self):
        """Test history branching when adding entry after undo."""
        # Add entries
        self.history_manager.add_entry('action1', 'First action', self.config)
        self.history_manager.add_entry('action2', 'Second action', self.config)
        self.history_manager.add_entry('action3', 'Third action', self.config)
        
        # Undo to middle
        self.history_manager.undo()
        
        # Add new entry (should create branch)
        self.history_manager.add_entry('action4', 'Fourth action', self.config)
        
        # Should have 3 entries now (action1, action2, action4)
        self.assertEqual(len(self.history_manager._history), 3)
        self.assertEqual(self.history_manager._current_index, 2)
    
    def test_max_entries_limit(self):
        """Test maximum entries limit."""
        # Add more entries than max
        for i in range(7):  # max_entries is 5
            self.history_manager.add_entry(f'action{i}', f'Action {i}', self.config)
        
        # Should have only max_entries
        self.assertEqual(len(self.history_manager._history), 5)
    
    def test_clear_history(self):
        """Test clearing history."""
        # Add some entries
        self.history_manager.add_entry('action1', 'First action', self.config)
        self.history_manager.add_entry('action2', 'Second action', self.config)
        
        # Clear history
        result = self.history_manager.clear_history()
        
        self.assertTrue(result)
        self.assertEqual(len(self.history_manager._history), 0)
        self.assertEqual(self.history_manager._current_index, -1)
    
    def test_get_current_entry(self):
        """Test getting current entry."""
        # Add entry
        self.history_manager.add_entry('test_action', 'Test description', self.config)
        
        # Get current entry
        entry = self.history_manager.get_current_entry()
        
        self.assertIsNotNone(entry)
        self.assertEqual(entry.action, 'test_action')
    
    def test_get_history(self):
        """Test getting complete history."""
        # Add entries
        self.history_manager.add_entry('action1', 'First action', self.config)
        self.history_manager.add_entry('action2', 'Second action', self.config)
        
        # Get history
        history = self.history_manager.get_history()
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].action, 'action1')
        self.assertEqual(history[1].action, 'action2')


class TestBackupManager(unittest.TestCase):
    """Test BackupManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.backup_manager = BackupManager(self.temp_dir, max_backups=3)
        self.config = Config()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_backup(self):
        """Test creating backup."""
        result = self.backup_manager.create_backup(
            'test_backup', 'Test backup description', self.config
        )
        
        self.assertTrue(result)
        self.assertEqual(len(self.backup_manager._backups), 1)
        
        # Check if backup directory was created
        backup_dirs = list(Path(self.temp_dir).glob('*_test_backup'))
        self.assertEqual(len(backup_dirs), 1)
    
    def test_list_backups(self):
        """Test listing backups."""
        # Create some backups
        self.backup_manager.create_backup('backup1', 'First backup', self.config)
        self.backup_manager.create_backup('backup2', 'Second backup', self.config)
        
        backups = self.backup_manager.list_backups()
        
        self.assertEqual(len(backups), 2)
        self.assertEqual(backups[0].name, 'backup1')
        self.assertEqual(backups[1].name, 'backup2')
    
    def test_restore_backup(self):
        """Test restoring backup."""
        # Create backup
        self.backup_manager.create_backup('test_backup', 'Test backup', self.config)
        
        # Restore backup
        result = self.backup_manager.restore_backup('test_backup')
        
        self.assertTrue(result)
    
    def test_delete_backup(self):
        """Test deleting backup."""
        # Create backup
        self.backup_manager.create_backup('test_backup', 'Test backup', self.config)
        
        # Delete backup
        result = self.backup_manager.delete_backup('test_backup')
        
        self.assertTrue(result)
        self.assertEqual(len(self.backup_manager._backups), 0)
    
    def test_get_backup_info(self):
        """Test getting backup information."""
        # Create backup
        self.backup_manager.create_backup('test_backup', 'Test backup', self.config)
        
        # Get backup info
        info = self.backup_manager.get_backup_info('test_backup')
        
        self.assertIsNotNone(info)
        self.assertEqual(info.name, 'test_backup')
        self.assertEqual(info.description, 'Test backup')
    
    def test_max_backups_limit(self):
        """Test maximum backups limit."""
        # Create more backups than max
        for i in range(5):  # max_backups is 3
            self.backup_manager.create_backup(f'backup{i}', f'Backup {i}', self.config)
        
        # Should have only max_backups
        self.assertEqual(len(self.backup_manager._backups), 3)
    
    def test_error_handling(self):
        """Test error handling."""
        # Test restoring non-existent backup
        result = self.backup_manager.restore_backup('nonexistent')
        self.assertFalse(result)
        
        # Test deleting non-existent backup
        result = self.backup_manager.delete_backup('nonexistent')
        self.assertFalse(result)
        
        # Test getting info for non-existent backup
        info = self.backup_manager.get_backup_info('nonexistent')
        self.assertIsNone(info)


class TestCommandManager(unittest.TestCase):
    """Test CommandManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.history_manager = HistoryManager(self.temp_dir)
        self.command_manager = CommandManager(self.history_manager)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_execute_command(self):
        """Test executing command."""
        class TestCommand(Command):
            def execute(self):
                return True
            
            def get_description(self):
                return "Test command"
        
        command = TestCommand(self.config)
        result = self.command_manager.execute_command(command)
        
        self.assertTrue(result)
        self.assertEqual(len(self.history_manager._history), 1)
    
    def test_undo_last_command(self):
        """Test undoing last command."""
        # Add entry to history
        self.history_manager.add_entry('test_action', 'Test description', self.config)
        
        # Undo last command
        result = self.command_manager.undo_last_command()
        
        self.assertTrue(result)
    
    def test_redo_last_command(self):
        """Test redoing last command."""
        # Add entry to history
        self.history_manager.add_entry('test_action', 'Test description', self.config)
        
        # Undo then redo
        self.command_manager.undo_last_command()
        result = self.command_manager.redo_last_command()
        
        self.assertTrue(result)


class TestCommandClasses(unittest.TestCase):
    """Test Command base classes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
    
    def test_command_base(self):
        """Test Command base class."""
        class TestCommand(Command):
            def execute(self):
                return True
            
            def get_description(self):
                return "Test command"
        
        command = TestCommand(self.config)
        
        self.assertEqual(command.get_action_name(), 'TestCommand')
        self.assertEqual(command.get_description(), 'Test command')
        self.assertEqual(command.get_config(), self.config)
        self.assertEqual(command.get_file_paths(), [])
        self.assertEqual(command.get_metadata(), {})
    
    def test_undo_command(self):
        """Test UndoCommand class."""
        # Create history entry
        entry = HistoryEntry(
            timestamp='2023-01-01T00:00:00',
            action='test_action',
            description='Test description',
            config_snapshot={},
            file_paths=[],
            metadata={}
        )
        
        undo_command = UndoCommand(entry)
        
        self.assertEqual(undo_command.get_description(), 'Undo: test_action - Test description')
    
    def test_redo_command(self):
        """Test RedoCommand class."""
        # Create history entry
        entry = HistoryEntry(
            timestamp='2023-01-01T00:00:00',
            action='test_action',
            description='Test description',
            config_snapshot={},
            file_paths=[],
            metadata={}
        )
        
        redo_command = RedoCommand(entry)
        
        self.assertEqual(redo_command.get_description(), 'Redo: test_action - Test description')


if __name__ == '__main__':
    unittest.main()






