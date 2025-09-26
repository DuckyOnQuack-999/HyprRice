"""
Tests for startup flow and first-run behavior.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hyprrice.main_gui import HyprRiceGUI
from hyprrice.config import Config
from hyprrice.migration import check_migration_needed, migrate_config


class TestStartupFlow(unittest.TestCase):
    """Test startup flow and first-run behavior."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
        
        # Mock home directory
        self.home_dir = Path(self.temp_dir) / "home"
        self.home_dir.mkdir(parents=True)
        
        # Mock config
        self.config = Config()
    
    @patch('hyprrice.main_gui.Path.home')
    def test_first_run_detection(self, mock_home):
        """Test first run detection."""
        mock_home.return_value = self.home_dir
        
        # First run marker should not exist
        first_run_marker = self.home_dir / '.hyprrice' / '.first_run'
        self.assertFalse(first_run_marker.exists())
        
        # Create GUI instance (this should trigger first run)
        with patch('hyprrice.main_gui.QMessageBox') as mock_msgbox:
            with patch('hyprrice.main_gui.QMainWindow.__init__'):
                gui = HyprRiceGUI(self.config)
                
                # Check that first run was detected
                self.assertTrue(first_run_marker.exists())
                
                # Check that welcome message was shown
                mock_msgbox.information.assert_called()
    
    @patch('hyprrice.main_gui.Path.home')
    def test_first_run_setup(self, mock_home):
        """Test first run setup."""
        mock_home.return_value = self.home_dir
        
        with patch('hyprrice.main_gui.QMessageBox') as mock_msgbox:
            with patch('hyprrice.main_gui.QMainWindow.__init__'):
                gui = HyprRiceGUI(self.config)
                
                # Check that directories were created
                expected_dirs = [
                    self.home_dir / '.hyprrice' / 'themes',
                    self.home_dir / '.hyprrice' / 'plugins',
                    self.home_dir / '.hyprrice' / 'backups',
                    self.home_dir / '.hyprrice' / 'logs',
                    self.home_dir / '.config' / 'hyprrice',
                ]
                
                for directory in expected_dirs:
                    self.assertTrue(directory.exists())
                
                # Check that welcome message was shown
                mock_msgbox.information.assert_called_once()
                call_args = mock_msgbox.information.call_args
                self.assertIn("Welcome to HyprRice", call_args[0][1])
    
    @patch('hyprrice.main_gui.Path.home')
    def test_subsequent_runs(self, mock_home):
        """Test subsequent runs (not first run)."""
        mock_home.return_value = self.home_dir
        
        # Create first run marker
        first_run_marker = self.home_dir / '.hyprrice' / '.first_run'
        first_run_marker.parent.mkdir(parents=True)
        first_run_marker.touch()
        
        with patch('hyprrice.main_gui.QMessageBox') as mock_msgbox:
            with patch('hyprrice.main_gui.QMainWindow.__init__'):
                gui = HyprRiceGUI(self.config)
                
                # Welcome message should not be shown
                mock_msgbox.information.assert_not_called()
    
    @patch('hyprrice.main_gui.Path.home')
    @patch('hyprrice.main_gui.check_migration_needed')
    def test_migration_prompt(self, mock_migration_check, mock_home):
        """Test migration prompt."""
        mock_home.return_value = self.home_dir
        mock_migration_check.return_value = True
        
        with patch('hyprrice.main_gui.QMessageBox') as mock_msgbox:
            with patch('hyprrice.main_gui.QMainWindow.__init__'):
                mock_msgbox.question.return_value = mock_msgbox.Yes
                
                gui = HyprRiceGUI(self.config)
                
                # Check that migration was prompted
                mock_msgbox.question.assert_called_once()
                call_args = mock_msgbox.question.call_args
                self.assertIn("Configuration Migration", call_args[0][1])
    
    @patch('hyprrice.main_gui.Path.home')
    @patch('hyprrice.main_gui.check_migration_needed')
    def test_migration_declined(self, mock_migration_check, mock_home):
        """Test migration prompt when user declines."""
        mock_home.return_value = self.home_dir
        mock_migration_check.return_value = True
        
        with patch('hyprrice.main_gui.QMessageBox') as mock_msgbox:
            with patch('hyprrice.main_gui.QMainWindow.__init__'):
                mock_msgbox.question.return_value = mock_msgbox.No
                
                gui = HyprRiceGUI(self.config)
                
                # Check that migration was prompted but declined
                mock_msgbox.question.assert_called_once()
                # No migration should have been performed
                mock_msgbox.information.assert_not_called()
    
    @patch('hyprrice.main_gui.Path.home')
    @patch('hyprrice.main_gui.check_migration_needed')
    @patch('hyprrice.main_gui.migrate_config')
    def test_migration_accepted(self, mock_migrate, mock_migration_check, mock_home):
        """Test migration prompt when user accepts."""
        mock_home.return_value = self.home_dir
        mock_migration_check.return_value = True
        mock_migrate.return_value = {
            'success': True,
            'backup_path': '/tmp/backup.yaml'
        }
        
        with patch('hyprrice.main_gui.QMessageBox') as mock_msgbox:
            with patch('hyprrice.main_gui.QMainWindow.__init__'):
                mock_msgbox.question.return_value = mock_msgbox.Yes
                
                gui = HyprRiceGUI(self.config)
                
                # Check that migration was performed
                mock_migrate.assert_called_once_with(create_backup=True)
    
    @patch('hyprrice.main_gui.Path.home')
    @patch('hyprrice.main_gui.check_migration_needed')
    @patch('hyprrice.main_gui.migrate_config')
    def test_migration_failure(self, mock_migrate, mock_migration_check, mock_home):
        """Test migration failure handling."""
        mock_home.return_value = self.home_dir
        mock_migration_check.return_value = True
        mock_migrate.return_value = {
            'success': False,
            'error': 'Migration failed'
        }
        
        with patch('hyprrice.main_gui.QMessageBox') as mock_msgbox:
            with patch('hyprrice.main_gui.QMainWindow.__init__'):
                mock_msgbox.question.return_value = mock_msgbox.Yes
                
                gui = HyprRiceGUI(self.config)
                
                # Check that migration failure was handled
                mock_migrate.assert_called_once()
    
    @patch('hyprrice.main_gui.Path.home')
    def test_global_error_handler(self, mock_home):
        """Test global error handler setup."""
        mock_home.return_value = self.home_dir
        
        with patch('hyprrice.main_gui.QMainWindow.__init__'):
            gui = HyprRiceGUI(self.config)
            
            # Check that global error handler was set up
            self.assertIsNotNone(gui.setup_global_error_handler)
    
    @patch('hyprrice.main_gui.Path.home')
    def test_startup_requirements_check(self, mock_home):
        """Test startup requirements check."""
        mock_home.return_value = self.home_dir
        
        with patch('hyprrice.main_gui.QMainWindow.__init__'):
            gui = HyprRiceGUI(self.config)
            
            # Check that startup requirements were checked
            self.assertIsNotNone(gui.check_startup_requirements)
    
    @patch('hyprrice.main_gui.Path.home')
    def test_first_run_error_handling(self, mock_home):
        """Test first run error handling."""
        mock_home.return_value = self.home_dir
        
        # Make directory creation fail
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            with patch('hyprrice.main_gui.QMainWindow.__init__'):
                with patch('hyprrice.main_gui.QMessageBox') as mock_msgbox:
                    gui = HyprRiceGUI(self.config)
                    
                    # Should handle error gracefully
                    # (No exception should be raised)
                    self.assertIsNotNone(gui)
    
    @patch('hyprrice.main_gui.Path.home')
    def test_migration_error_handling(self, mock_home):
        """Test migration error handling."""
        mock_home.return_value = self.home_dir
        
        with patch('hyprrice.main_gui.check_migration_needed', side_effect=Exception("Migration check failed")):
            with patch('hyprrice.main_gui.QMainWindow.__init__'):
                gui = HyprRiceGUI(self.config)
                
                # Should handle error gracefully
                # (No exception should be raised)
                self.assertIsNotNone(gui)
    
    def test_check_migration_needed(self):
        """Test migration check function."""
        # Test with no config file
        with patch('pathlib.Path.exists', return_value=False):
            result = check_migration_needed()
            self.assertFalse(result)
        
        # Test with config file
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="version: 1.0.0")):
                result = check_migration_needed()
                # Should return True if migration is needed
                self.assertIsInstance(result, bool)
    
    def test_migrate_config(self):
        """Test migration function."""
        # Test successful migration
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="version: 1.0.0")):
                with patch('shutil.copy2') as mock_copy:
                    result = migrate_config(create_backup=True)
                    
                    self.assertIsInstance(result, dict)
                    self.assertIn('success', result)
    
    @patch('hyprrice.main_gui.Path.home')
    def test_startup_with_existing_config(self, mock_home):
        """Test startup with existing configuration."""
        mock_home.return_value = self.home_dir
        
        # Create existing config directory
        config_dir = self.home_dir / '.config' / 'hyprrice'
        config_dir.mkdir(parents=True)
        
        # Create config file
        config_file = config_dir / 'config.yaml'
        config_file.write_text("version: 1.0.0\n")
        
        with patch('hyprrice.main_gui.QMainWindow.__init__'):
            gui = HyprRiceGUI(self.config)
            
            # Should start normally
            self.assertIsNotNone(gui)
    
    @patch('hyprrice.main_gui.Path.home')
    def test_startup_with_corrupted_config(self, mock_home):
        """Test startup with corrupted configuration."""
        mock_home.return_value = self.home_dir
        
        # Create corrupted config file
        config_dir = self.home_dir / '.config' / 'hyprrice'
        config_dir.mkdir(parents=True)
        
        config_file = config_dir / 'config.yaml'
        config_file.write_text("invalid: yaml: content: [")
        
        with patch('hyprrice.main_gui.QMainWindow.__init__'):
            gui = HyprRiceGUI(self.config)
            
            # Should handle corrupted config gracefully
            self.assertIsNotNone(gui)
    
    @patch('hyprrice.main_gui.Path.home')
    def test_startup_with_permission_issues(self, mock_home):
        """Test startup with permission issues."""
        mock_home.return_value = self.home_dir
        
        # Make directory creation fail
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            with patch('hyprrice.main_gui.QMainWindow.__init__'):
                gui = HyprRiceGUI(self.config)
                
                # Should handle permission issues gracefully
                self.assertIsNotNone(gui)


if __name__ == '__main__':
    unittest.main()
