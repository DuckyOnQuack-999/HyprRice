"""
Integration tests for GUI components
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hyprrice.config import Config
from hyprrice.main_gui import HyprRiceGUI
from hyprrice.gui.tabs import (
    HyprlandTab, WaybarTab, RofiTab, NotificationsTab,
    ClipboardTab, LockscreenTab, ThemesTab, SettingsTab, PluginsTab
)
from hyprrice.gui.theme_manager import ThemeManager
from hyprrice.gui.preview import PreviewWindow


class TestHyprRiceGUI(unittest.TestCase):
    """Test main GUI application."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        
        # Mock QApplication to avoid GUI initialization
        with patch('hyprrice.gui.gui.QApplication'):
            self.gui = HyprRiceGUI(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        # Re-enable performance monitoring
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
        shutil.rmtree(self.temp_dir)
    
    def test_gui_initialization(self):
        """Test GUI initialization."""
        self.assertIsNotNone(self.gui)
        self.assertEqual(self.gui.config, self.config)
        self.assertIsNotNone(self.gui.history_manager)
    
    def test_menu_creation(self):
        """Test menu creation."""
        # Mock QMenuBar
        with patch.object(self.gui, 'menuBar') as mock_menu_bar:
            mock_menu = Mock()
            mock_menu_bar.return_value = mock_menu
            
            self.gui._create_menu()
            
            # Verify menu was created
            mock_menu_bar.assert_called_once()
    
    def test_tab_creation(self):
        """Test tab creation."""
        # Mock QTabWidget
        with patch.object(self.gui, 'tab_widget') as mock_tab_widget:
            self.gui._create_tabs()
            
            # Verify tabs were added
            self.assertGreater(mock_tab_widget.addTab.call_count, 0)
    
    def test_undo_redo(self):
        """Test undo/redo functionality."""
        # Test undo when no history
        result = self.gui.undo()
        self.assertFalse(result)
        
        # Test redo when no history
        result = self.gui.redo()
        self.assertFalse(result)
    
    def test_show_help(self):
        """Test help dialog."""
        # Mock QMessageBox
        with patch('hyprrice.gui.gui.QMessageBox') as mock_message_box:
            mock_box = Mock()
            mock_message_box.return_value = mock_box
            
            self.gui.show_help()
            
            # Verify help dialog was shown
            mock_message_box.assert_called_once()
            mock_box.exec_.assert_called_once()
    
    def test_apply_config(self):
        """Test applying configuration."""
        # Mock config application
        with patch.object(self.gui, 'history_manager') as mock_history:
            result = self.gui.apply_config()
            
            # Verify history was updated
            mock_history.add_entry.assert_called_once()
    
    def test_save_config(self):
        """Test saving configuration."""
        # Mock file operations
        with patch('builtins.open', mock_open()) as mock_file:
            result = self.gui.save_config()
            
            # Verify file was opened for writing
            mock_file.assert_called_once()
    
    def test_load_config(self):
        """Test loading configuration."""
        # Mock file operations
        with patch('builtins.open', mock_open('{}')):
            result = self.gui.load_config()
            
            # Verify file was opened for reading
            self.assertTrue(result)


class TestHyprlandTab(unittest.TestCase):
    """Test HyprlandTab functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.config = Config()
        self.tab = HyprlandTab(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Re-enable performance monitoring
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
    
    def test_tab_initialization(self):
        """Test tab initialization."""
        self.assertIsNotNone(self.tab)
        self.assertEqual(self.tab.config, self.config)
    
    def test_apply_config(self):
        """Test applying configuration."""
        # Mock hyprland managers
        with patch.object(self.tab, 'animation_manager') as mock_anim, \
             patch.object(self.tab, 'window_manager') as mock_window, \
             patch.object(self.tab, 'display_manager') as mock_display, \
             patch.object(self.tab, 'input_manager') as mock_input, \
             patch.object(self.tab, 'workspace_manager') as mock_workspace:
            
            result = self.tab.apply_config()
            
            # Verify all managers were called
            mock_anim.apply_animations.assert_called_once()
            mock_window.apply_window_config.assert_called_once()
            mock_display.apply_display_config.assert_called_once()
            mock_input.apply_input_config.assert_called_once()
            mock_workspace.set_workspace_config.assert_called_once()
    
    def test_preview_config(self):
        """Test previewing configuration."""
        # Mock preview window
        with patch('hyprrice.gui.tabs.PreviewWindow') as mock_preview:
            mock_window = Mock()
            mock_preview.return_value = mock_window
            
            self.tab.preview_config()
            
            # Verify preview window was created and shown
            mock_preview.assert_called_once()
            mock_window.show.assert_called_once()


class TestWaybarTab(unittest.TestCase):
    """Test WaybarTab functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.config = Config()
        self.tab = WaybarTab(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Re-enable performance monitoring
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
    
    def test_tab_initialization(self):
        """Test tab initialization."""
        self.assertIsNotNone(self.tab)
        self.assertEqual(self.tab.config, self.config)
    
    def test_apply_config(self):
        """Test applying configuration."""
        # Mock waybar config file operations
        with patch('builtins.open', mock_open()):
            result = self.tab.apply_config()
            
            # Verify config was applied
            self.assertTrue(result)
    
    def test_preview_config(self):
        """Test previewing configuration."""
        # Mock preview window
        with patch('hyprrice.gui.tabs.PreviewWindow') as mock_preview:
            mock_window = Mock()
            mock_preview.return_value = mock_window
            
            self.tab.preview_config()
            
            # Verify preview window was created and shown
            mock_preview.assert_called_once()
            mock_window.show.assert_called_once()


class TestRofiTab(unittest.TestCase):
    """Test RofiTab functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.config = Config()
        self.tab = RofiTab(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Re-enable performance monitoring
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
    
    def test_tab_initialization(self):
        """Test tab initialization."""
        self.assertIsNotNone(self.tab)
        self.assertEqual(self.tab.config, self.config)
    
    def test_apply_config(self):
        """Test applying configuration."""
        # Mock rofi config file operations
        with patch('builtins.open', mock_open()):
            result = self.tab.apply_config()
            
            # Verify config was applied
            self.assertTrue(result)
    
    def test_preview_config(self):
        """Test previewing configuration."""
        # Mock preview window
        with patch('hyprrice.gui.tabs.PreviewWindow') as mock_preview:
            mock_window = Mock()
            mock_preview.return_value = mock_window
            
            self.tab.preview_config()
            
            # Verify preview window was created and shown
            mock_preview.assert_called_once()
            mock_window.show.assert_called_once()


class TestNotificationsTab(unittest.TestCase):
    """Test NotificationsTab functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.config = Config()
        self.tab = NotificationsTab(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Re-enable performance monitoring
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
    
    def test_tab_initialization(self):
        """Test tab initialization."""
        self.assertIsNotNone(self.tab)
        self.assertEqual(self.tab.config, self.config)
    
    def test_apply_config(self):
        """Test applying configuration."""
        # Mock dunst config file operations
        with patch('builtins.open', mock_open()):
            result = self.tab.apply_config()
            
            # Verify config was applied
            self.assertTrue(result)
    
    def test_preview_config(self):
        """Test previewing configuration."""
        # Mock preview window
        with patch('hyprrice.gui.tabs.PreviewWindow') as mock_preview:
            mock_window = Mock()
            mock_preview.return_value = mock_window
            
            self.tab.preview_config()
            
            # Verify preview window was created and shown
            mock_preview.assert_called_once()
            mock_window.show.assert_called_once()


class TestClipboardTab(unittest.TestCase):
    """Test ClipboardTab functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.config = Config()
        self.tab = ClipboardTab(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Re-enable performance monitoring
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
    
    def test_tab_initialization(self):
        """Test tab initialization."""
        self.assertIsNotNone(self.tab)
        self.assertEqual(self.tab.config, self.config)
    
    def test_apply_config(self):
        """Test applying configuration."""
        # Mock clipboard manager config file operations
        with patch('builtins.open', mock_open()):
            result = self.tab.apply_config()
            
            # Verify config was applied
            self.assertTrue(result)
    
    def test_preview_config(self):
        """Test previewing configuration."""
        # Mock preview window
        with patch('hyprrice.gui.tabs.PreviewWindow') as mock_preview:
            mock_window = Mock()
            mock_preview.return_value = mock_window
            
            self.tab.preview_config()
            
            # Verify preview window was created and shown
            mock_preview.assert_called_once()
            mock_window.show.assert_called_once()


class TestLockscreenTab(unittest.TestCase):
    """Test LockscreenTab functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.config = Config()
        self.tab = LockscreenTab(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Re-enable performance monitoring
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
    
    def test_tab_initialization(self):
        """Test tab initialization."""
        self.assertIsNotNone(self.tab)
        self.assertEqual(self.tab.config, self.config)
    
    def test_apply_config(self):
        """Test applying configuration."""
        # Mock lockscreen daemon config file operations
        with patch('builtins.open', mock_open()):
            result = self.tab.apply_config()
            
            # Verify config was applied
            self.assertTrue(result)
    
    def test_preview_config(self):
        """Test previewing configuration."""
        # Mock preview window
        with patch('hyprrice.gui.tabs.PreviewWindow') as mock_preview:
            mock_window = Mock()
            mock_preview.return_value = mock_window
            
            self.tab.preview_config()
            
            # Verify preview window was created and shown
            mock_preview.assert_called_once()
            mock_window.show.assert_called_once()


class TestThemesTab(unittest.TestCase):
    """Test ThemesTab functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.config = Config()
        self.tab = ThemesTab(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Re-enable performance monitoring
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
    
    def test_tab_initialization(self):
        """Test tab initialization."""
        self.assertIsNotNone(self.tab)
        self.assertEqual(self.tab.config, self.config)
    
    def test_apply_theme(self):
        """Test applying theme."""
        # Mock theme manager
        with patch.object(self.tab, 'theme_manager') as mock_theme:
            mock_theme.apply_theme.return_value = True
            
            result = self.tab.apply_theme('test_theme')
            
            # Verify theme was applied
            mock_theme.apply_theme.assert_called_once_with('test_theme')
            self.assertTrue(result)
    
    def test_preview_theme(self):
        """Test previewing theme."""
        # Mock theme manager
        with patch.object(self.tab, 'theme_manager') as mock_theme:
            mock_theme.preview_theme.return_value = True
            
            result = self.tab.preview_theme('test_theme')
            
            # Verify theme was previewed
            mock_theme.preview_theme.assert_called_once_with('test_theme')
            self.assertTrue(result)
    
    def test_import_theme(self):
        """Test importing theme."""
        # Mock theme manager
        with patch.object(self.tab, 'theme_manager') as mock_theme:
            mock_theme.import_theme.return_value = True
            
            result = self.tab.import_theme('test_theme.hyprrice')
            
            # Verify theme was imported
            mock_theme.import_theme.assert_called_once_with('test_theme.hyprrice')
            self.assertTrue(result)
    
    def test_export_theme(self):
        """Test exporting theme."""
        # Mock theme manager
        with patch.object(self.tab, 'theme_manager') as mock_theme:
            mock_theme.export_theme.return_value = True
            
            result = self.tab.export_theme('test_theme', 'test_theme.hyprrice')
            
            # Verify theme was exported
            mock_theme.export_theme.assert_called_once_with('test_theme', 'test_theme.hyprrice')
            self.assertTrue(result)


class TestSettingsTab(unittest.TestCase):
    """Test SettingsTab functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.config = Config()
        self.tab = SettingsTab(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Re-enable performance monitoring
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
    
    def test_tab_initialization(self):
        """Test tab initialization."""
        self.assertIsNotNone(self.tab)
        self.assertEqual(self.tab.config, self.config)
    
    def test_apply_settings(self):
        """Test applying settings."""
        # Mock settings application
        with patch.object(self.tab, 'config') as mock_config:
            result = self.tab.apply_settings()
            
            # Verify settings were applied
            self.assertTrue(result)
    
    def test_reset_settings(self):
        """Test resetting settings."""
        # Mock settings reset
        with patch.object(self.tab, 'config') as mock_config:
            result = self.tab.reset_settings()
            
            # Verify settings were reset
            self.assertTrue(result)


class TestPluginsTab(unittest.TestCase):
    """Test PluginsTab functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.config = Config()
        self.tab = PluginsTab(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Re-enable performance monitoring
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
    
    def test_tab_initialization(self):
        """Test tab initialization."""
        self.assertIsNotNone(self.tab)
        self.assertEqual(self.tab.config, self.config)
    
    def test_load_plugins(self):
        """Test loading plugins."""
        # Mock plugin manager
        with patch.object(self.tab, 'plugin_manager') as mock_plugin:
            mock_plugin.load_plugins.return_value = True
            
            result = self.tab.load_plugins()
            
            # Verify plugins were loaded
            mock_plugin.load_plugins.assert_called_once()
            self.assertTrue(result)
    
    def test_enable_plugin(self):
        """Test enabling plugin."""
        # Mock plugin manager
        with patch.object(self.tab, 'plugin_manager') as mock_plugin:
            mock_plugin.enable_plugin.return_value = True
            
            result = self.tab.enable_plugin('test_plugin')
            
            # Verify plugin was enabled
            mock_plugin.enable_plugin.assert_called_once_with('test_plugin')
            self.assertTrue(result)
    
    def test_disable_plugin(self):
        """Test disabling plugin."""
        # Mock plugin manager
        with patch.object(self.tab, 'plugin_manager') as mock_plugin:
            mock_plugin.disable_plugin.return_value = True
            
            result = self.tab.disable_plugin('test_plugin')
            
            # Verify plugin was disabled
            mock_plugin.disable_plugin.assert_called_once_with('test_plugin')
            self.assertTrue(result)


class TestThemeManager(unittest.TestCase):
    """Test ThemeManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.theme_manager = ThemeManager(self.config, self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        # Re-enable performance monitoring
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
        shutil.rmtree(self.temp_dir)
    
    def test_theme_manager_initialization(self):
        """Test theme manager initialization."""
        self.assertIsNotNone(self.theme_manager)
        self.assertEqual(self.theme_manager.config, self.config)
        self.assertEqual(self.theme_manager.themes_dir, self.temp_dir)
    
    def test_list_themes(self):
        """Test listing themes."""
        # Create test theme file
        theme_file = Path(self.temp_dir) / 'test_theme.hyprrice'
        theme_file.write_text('{"name": "test_theme", "description": "Test theme"}')
        
        themes = self.theme_manager.list_themes()
        
        self.assertIn('test_theme', themes)
    
    def test_get_theme_info(self):
        """Test getting theme information."""
        # Create test theme file
        theme_file = Path(self.temp_dir) / 'test_theme.hyprrice'
        theme_data = {
            'name': 'test_theme',
            'description': 'Test theme',
            'author': 'Test Author',
            'version': '1.0.0'
        }
        theme_file.write_text(json.dumps(theme_data))
        
        info = self.theme_manager.get_theme_info('test_theme')
        
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'test_theme')
        self.assertEqual(info['description'], 'Test theme')
    
    def test_apply_theme(self):
        """Test applying theme."""
        # Create test theme file
        theme_file = Path(self.temp_dir) / 'test_theme.hyprrice'
        theme_data = {
            'name': 'test_theme',
            'description': 'Test theme',
            'hyprland': {
                'animations': {
                    'enabled': True,
                    'duration': 0.3
                }
            }
        }
        theme_file.write_text(json.dumps(theme_data))
        
        result = self.theme_manager.apply_theme('test_theme')
        
        self.assertTrue(result)
        self.assertTrue(self.config.hyprland.animations.enabled)
        self.assertEqual(self.config.hyprland.animations.duration, 0.3)
    
    def test_preview_theme(self):
        """Test previewing theme."""
        # Create test theme file
        theme_file = Path(self.temp_dir) / 'test_theme.hyprrice'
        theme_data = {
            'name': 'test_theme',
            'description': 'Test theme',
            'hyprland': {
                'animations': {
                    'enabled': True,
                    'duration': 0.3
                }
            }
        }
        theme_file.write_text(json.dumps(theme_data))
        
        preview_config = self.theme_manager.preview_theme('test_theme')
        
        self.assertIsNotNone(preview_config)
        self.assertTrue(preview_config.hyprland.animations.enabled)
        self.assertEqual(preview_config.hyprland.animations.duration, 0.3)
    
    def test_import_theme(self):
        """Test importing theme."""
        # Create test theme file
        theme_file = Path(self.temp_dir) / 'test_theme.hyprrice'
        theme_data = {
            'name': 'test_theme',
            'description': 'Test theme',
            'hyprland': {
                'animations': {
                    'enabled': True,
                    'duration': 0.3
                }
            }
        }
        theme_file.write_text(json.dumps(theme_data))
        
        result = self.theme_manager.import_theme(str(theme_file))
        
        self.assertTrue(result)
    
    def test_export_theme(self):
        """Test exporting theme."""
        # Set up config with theme data
        self.config.hyprland.animations.enabled = True
        self.config.hyprland.animations.duration = 0.3
        
        export_file = Path(self.temp_dir) / 'exported_theme.hyprrice'
        
        result = self.theme_manager.export_theme('exported_theme', str(export_file))
        
        self.assertTrue(result)
        self.assertTrue(export_file.exists())
    
    def test_delete_theme(self):
        """Test deleting theme."""
        # Create test theme file
        theme_file = Path(self.temp_dir) / 'test_theme.hyprrice'
        theme_file.write_text('{"name": "test_theme", "description": "Test theme"}')
        
        result = self.theme_manager.delete_theme('test_theme')
        
        self.assertTrue(result)
        self.assertFalse(theme_file.exists())


class TestPreviewWindow(unittest.TestCase):
    """Test PreviewWindow functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable performance monitoring for tests
        from hyprrice.performance import disable_auto_monitoring
        disable_auto_monitoring()
        
        # Create a proper QApplication for testing
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.config = Config()
        
        # Mock QWidget to avoid GUI initialization
        with patch('hyprrice.gui.preview.QWidget'):
            self.preview = PreviewWindow(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Re-enable performance monitoring
        try:
            from hyprrice.performance import performance_monitor, enable_auto_monitoring
            performance_monitor.stop_monitoring()
            enable_auto_monitoring()
        except:
            pass
    
    def test_preview_initialization(self):
        """Test preview window initialization."""
        self.assertIsNotNone(self.preview)
        self.assertEqual(self.preview.config, self.config)
    
    def test_show_preview(self):
        """Test showing preview."""
        # Mock show method
        with patch.object(self.preview, 'show') as mock_show:
            self.preview.show_preview()
            
            # Verify show was called
            mock_show.assert_called_once()
    
    def test_update_preview(self):
        """Test updating preview."""
        # Mock update method
        with patch.object(self.preview, 'update') as mock_update:
            self.preview.update_preview()
            
            # Verify update was called
            mock_update.assert_called_once()


def mock_open(content=''):
    """Mock open function for testing."""
    return unittest.mock.mock_open(read_data=content)


if __name__ == '__main__':
    unittest.main()
