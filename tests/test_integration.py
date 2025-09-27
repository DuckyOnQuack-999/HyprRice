"""
Integration tests for HyprRice
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
from hyprrice.history import HistoryManager, BackupManager
from hyprrice.gui.theme_manager import ThemeManager
from hyprrice.hyprland.animations import AnimationManager
from hyprrice.hyprland.windows import WindowManager
from hyprrice.hyprland.display import DisplayManager
from hyprrice.hyprland.input import InputManager
from hyprrice.hyprland.workspaces import WorkspaceManager


class TestIntegration(unittest.TestCase):
    """Test integration between components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_config_theme_integration(self):
        """Test configuration and theme integration."""
        # Create theme manager
        theme_manager = ThemeManager(self.config, self.temp_dir)
        
        # Create test theme
        theme_file = Path(self.temp_dir) / 'test_theme.hyprrice'
        theme_data = {
            'name': 'test_theme',
            'description': 'Test theme',
            'hyprland': {
                'animations': {
                    'enabled': True,
                    'duration': 0.5,
                    'curve': 'easeOutCubic'
                },
                'windows': {
                    'opacity': 0.8,
                    'border_size': 3,
                    'border_color': '#00FF00'
                }
            },
            'waybar': {
                'modules': ['clock', 'battery', 'network', 'workspaces']
            },
            'rofi': {
                'theme': 'dark',
                'width': 60,
                'height': 40
            }
        }
        
        import json
        theme_file.write_text(json.dumps(theme_data))
        
        # Apply theme
        result = theme_manager.apply_theme('test_theme')
        self.assertTrue(result)
        
        # Verify config was updated
        self.assertTrue(self.config.hyprland.animations.enabled)
        self.assertEqual(self.config.hyprland.animations.duration, 0.5)
        self.assertEqual(self.config.hyprland.animations.curve, 'easeOutCubic')
        self.assertEqual(self.config.hyprland.windows.opacity, 0.8)
        self.assertEqual(self.config.hyprland.windows.border_size, 3)
        self.assertEqual(self.config.hyprland.windows.border_color, '#00FF00')
        self.assertIn('clock', self.config.waybar.modules)
        self.assertIn('battery', self.config.waybar.modules)
        self.assertIn('network', self.config.waybar.modules)
        self.assertIn('workspaces', self.config.waybar.modules)
        self.assertEqual(self.config.rofi.theme, 'dark')
        self.assertEqual(self.config.rofi.width, 60)
        self.assertEqual(self.config.rofi.height, 40)
    
    def test_hyprland_managers_integration(self):
        """Test Hyprland managers integration."""
        # Mock hyprctl calls
        with patch('hyprrice.hyprland.animations.subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout='', returncode=0)
            
            # Test AnimationManager
            anim_manager = AnimationManager()
            anim_manager.set_animation_config({
                'enabled': True,
                'duration': 0.3,
                'curve': 'easeOutCubic'
            })
            anim_manager.apply_animations()
            
            # Test WindowManager
            window_manager = WindowManager()
            window_manager.set_window_config({
                'opacity': 0.9,
                'border_size': 2,
                'border_color': '#FF0000'
            })
            window_manager.apply_window_config()
            
            # Test DisplayManager
            display_manager = DisplayManager()
            display_manager.set_display_config({
                'max_render_time': 8,
                'tearing': False
            })
            display_manager.apply_display_config()
            
            # Test InputManager
            input_manager = InputManager()
            input_manager.set_input_config({
                'keyboard_repeat_rate': 25,
                'keyboard_repeat_delay': 600
            })
            input_manager.apply_input_config()
            
            # Test WorkspaceManager
            workspace_manager = WorkspaceManager()
            workspace_manager.set_workspace_config({
                'workspace_1': 'monitor:DP-1',
                'workspace_2': 'monitor:DP-2'
            })
            
            # Verify all managers work together
            self.assertIsNotNone(anim_manager)
            self.assertIsNotNone(window_manager)
            self.assertIsNotNone(display_manager)
            self.assertIsNotNone(input_manager)
            self.assertIsNotNone(workspace_manager)
    
    def test_gui_config_integration(self):
        """Test GUI and configuration integration."""
        # Mock QApplication to avoid GUI initialization
        with patch('PyQt6.QtWidgets.QApplication'):
            from hyprrice.main_gui import HyprRiceGUI
            gui = HyprRiceGUI(self.config)
            
            # Test config application through GUI
            with patch.object(gui, 'history_manager') as mock_history:
                result = gui.apply_config()
                
                # Verify history was updated
                mock_history.add_entry.assert_called_once()
                self.assertTrue(result)
            
            # Test config saving through GUI
            with patch('builtins.open', mock_open()):
                result = gui.save_config()
                self.assertTrue(result)
            
            # Test config loading through GUI
            with patch('builtins.open', mock_open('{}')):
                result = gui.load_config()
                self.assertTrue(result)
    
    def test_backup_history_integration(self):
        """Test backup and history integration."""
        # Create history manager
        history_manager = HistoryManager(self.temp_dir)
        
        # Create backup manager
        backup_manager = BackupManager(self.temp_dir)
        
        # Test history operations
        history_manager.add_entry('test_action', 'Test description', self.config)
        self.assertEqual(len(history_manager._history), 1)
        
        # Test backup operations
        backup_manager.create_backup('test_backup', 'Test backup description', self.config)
        self.assertEqual(len(backup_manager._backups), 1)
        
        # Test integration between history and backup
        # Create backup from current state
        backup_manager.create_backup('current_state', 'Current state backup', self.config)
        
        # Add more history entries
        history_manager.add_entry('action2', 'Second action', self.config)
        history_manager.add_entry('action3', 'Third action', self.config)
        
        # Create another backup
        backup_manager.create_backup('after_actions', 'After actions backup', self.config)
        
        # Verify both systems work together
        self.assertEqual(len(history_manager._history), 3)
        self.assertEqual(len(backup_manager._backups), 2)


def mock_open(content=''):
    """Mock open function for testing."""
    return unittest.mock.mock_open(read_data=content)


if __name__ == '__main__':
    unittest.main()
