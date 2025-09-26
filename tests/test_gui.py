"""
Tests for GUI functionality
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hyprrice.config import Config
from hyprrice.main_gui import HyprRiceGUI
from hyprrice.history import HistoryManager, BackupManager


class TestHyprRiceGUI(unittest.TestCase):
    """Test HyprRiceGUI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.config.paths.config_dir = self.temp_dir
        
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.gui = HyprRiceGUI(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        # Stop performance monitoring if it's running
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()  # Re-enable for other tests
        except:
            pass
        shutil.rmtree(self.temp_dir)
    
    def test_gui_initialization(self):
        """Test GUI initialization."""
        self.assertIsNotNone(self.gui)
        self.assertEqual(self.gui.config, self.config)
        self.assertIsNotNone(self.gui.history_manager)
        self.assertIsNotNone(self.gui.backup_manager)
    
    def test_setup_ui(self):
        """Test UI setup."""
        self.gui.setup_ui()
        
        # Check if main components are created
        self.assertIsNotNone(self.gui.centralWidget())
        self.assertIsNotNone(self.gui.menuBar())
        self.assertIsNotNone(self.gui.statusBar())
    
    def test_setup_shortcuts(self):
        """Test keyboard shortcuts setup."""
        self.gui.setup_shortcuts()
        
        # Check if shortcuts are created (we can't easily test the actual shortcuts
        # without a full QApplication, but we can test that the method runs without error)
        self.assertTrue(True)  # Method executed without exception
    
    def test_validate_config(self):
        """Test configuration validation."""
        # Test with valid config
        result = self.gui.validate_config()
        self.assertTrue(result)
        
        # Test with invalid config
        self.config.hyprland.window_opacity = 2.0  # Invalid value
        result = self.gui.validate_config()
        self.assertFalse(result)
    
    def test_show_error(self):
        """Test error dialog display."""
        with patch('PyQt5.QtWidgets.QMessageBox') as mock_msgbox:
            mock_msgbox.return_value.exec_.return_value = None
            
            self.gui.show_error("Test Error", "Test message")
            
            mock_msgbox.assert_called_once()
    
    def test_show_warning(self):
        """Test warning dialog display."""
        with patch('PyQt5.QtWidgets.QMessageBox') as mock_msgbox:
            mock_msgbox.return_value.exec_.return_value = None
            
            self.gui.show_warning("Test Warning", "Test message")
            
            mock_msgbox.assert_called_once()
    
    def test_show_info(self):
        """Test info dialog display."""
        with patch('PyQt5.QtWidgets.QMessageBox') as mock_msgbox:
            mock_msgbox.return_value.exec_.return_value = None
            
            self.gui.show_info("Test Info", "Test message")
            
            mock_msgbox.assert_called_once()
    
    def test_handle_exception(self):
        """Test exception handling."""
        with patch.object(self.gui, 'show_error') as mock_show_error:
            test_exception = Exception("Test exception")
            
            self.gui.handle_exception("test operation", test_exception)
            
            mock_show_error.assert_called_once()
    
    def test_show_progress(self):
        """Test progress indicator."""
        self.gui.show_progress("Test progress")
        
        self.assertTrue(self.gui.progress_bar.isVisible())
        self.assertEqual(self.gui.status_label.text(), "Test progress")
    
    def test_hide_progress(self):
        """Test hiding progress indicator."""
        self.gui.show_progress("Test progress")
        self.gui.hide_progress()
        
        self.assertFalse(self.gui.progress_bar.isVisible())
        self.assertEqual(self.gui.status_label.text(), "Ready")
    
    def test_auto_save(self):
        """Test auto-save functionality."""
        with patch.object(self.gui.config, 'save') as mock_save:
            self.gui.auto_save()
            mock_save.assert_called_once()
    
    def test_undo_redo(self):
        """Test undo/redo functionality."""
        with patch.object(self.gui.history_manager, 'undo') as mock_undo:
            mock_undo.return_value = True
            
            self.gui.undo()
            mock_undo.assert_called_once()
        
        with patch.object(self.gui.history_manager, 'redo') as mock_redo:
            mock_redo.return_value = True
            
            self.gui.redo()
            mock_redo.assert_called_once()
    
    def test_backup_config(self):
        """Test backup configuration."""
        with patch.object(self.gui.backup_manager, 'create_backup') as mock_backup:
            mock_backup.return_value = True
            
            self.gui.backup_config()
            mock_backup.assert_called_once_with("Manual backup")
    
    def test_restore_config(self):
        """Test restore configuration."""
        with patch.object(self.gui.backup_manager, 'list_backups') as mock_list:
            mock_list.return_value = []
            
            # Should show "No backups" message
            with patch('PyQt5.QtWidgets.QMessageBox') as mock_msgbox:
                self.gui.restore_config()
                mock_msgbox.assert_called()
    
    def test_check_dependencies(self):
        """Test dependency checking."""
        with patch('hyprrice.utils.check_dependencies') as mock_check:
            mock_check.return_value = True
            
            with patch('PyQt5.QtWidgets.QMessageBox') as mock_msgbox:
                self.gui.check_dependencies()
                mock_msgbox.assert_called()
    
    def test_show_about(self):
        """Test about dialog."""
        with patch('PyQt5.QtWidgets.QMessageBox.about') as mock_about:
            self.gui.show_about()
            mock_about.assert_called_once()
    
    def test_show_help(self):
        """Test help dialog."""
        with patch('PyQt5.QtWidgets.QDialog') as mock_dialog:
            mock_dialog.return_value.exec_.return_value = None
            
            self.gui.show_help()
            mock_dialog.assert_called_once()
    
    def test_close_event(self):
        """Test close event handling."""
        with patch.object(self.gui.config, 'save') as mock_save:
            from PyQt5.QtGui import QCloseEvent
            
            # Mock the close event
            event = MagicMock()
            
            self.gui.closeEvent(event)
            
            mock_save.assert_called_once()
            event.accept.assert_called_once()
    
    def test_refresh_all_tabs(self):
        """Test refreshing all tabs."""
        # Mock tab objects
        mock_tab = MagicMock()
        mock_tab.refresh = MagicMock()
        
        self.gui.hyprland_tab = mock_tab
        self.gui.waybar_tab = mock_tab
        self.gui.rofi_tab = mock_tab
        self.gui.notifications_tab = mock_tab
        self.gui.clipboard_tab = mock_tab
        self.gui.lockscreen_tab = mock_tab
        self.gui.themes_tab = mock_tab
        self.gui.settings_tab = mock_tab
        self.gui.plugins_tab = mock_tab
        
        self.gui.refresh_all_tabs()
        
        # Check that refresh was called on tabs
        self.assertEqual(mock_tab.refresh.call_count, 9)
    
    def test_show_question(self):
        """Test question dialog."""
        with patch('PyQt5.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = 0  # Yes button
            
            result = self.gui.show_question("Test Question", "Test message")
            
            mock_question.assert_called_once()
            self.assertEqual(result, 0)


class TestGUIIntegration(unittest.TestCase):
    """Test GUI integration with other components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.config.paths.config_dir = self.temp_dir
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_gui_with_history_manager(self):
        """Test GUI integration with history manager."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        
        gui = HyprRiceGUI(self.config)
        
        self.assertIsInstance(gui.history_manager, HistoryManager)
        self.assertEqual(gui.history_manager.config, self.config)
        
        # Cleanup
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
    
    def test_gui_with_backup_manager(self):
        """Test GUI integration with backup manager."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        
        gui = HyprRiceGUI(self.config)
        
        self.assertIsInstance(gui.backup_manager, BackupManager)
        
        # Cleanup
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
    
    def test_gui_config_validation(self):
        """Test GUI configuration validation integration."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        
        gui = HyprRiceGUI(self.config)
        
        # Test valid config
        result = gui.validate_config()
        self.assertTrue(result)
        
        # Cleanup
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
            
            # Test invalid config
            self.config.hyprland.window_opacity = 2.0
            result = gui.validate_config()
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
