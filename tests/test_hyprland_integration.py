"""
Tests for Hyprland integration modules
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.hyprrice.hyprland.animations import AnimationManager
from src.hyprrice.hyprland.windows import WindowManager
from src.hyprrice.hyprland.display import DisplayManager
from src.hyprrice.hyprland.input import InputManager
from src.hyprrice.hyprland.workspaces import WorkspaceManager


class TestAnimationManager(unittest.TestCase):
    """Test AnimationManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test.conf")
        self.manager = AnimationManager(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('src.hyprrice.hyprland.animations.hyprctl')
    def test_get_animation_config(self, mock_hyprctl):
        """Test getting animation configuration."""
        mock_hyprctl.return_value = (0, "animations:enabled = true", "")
        
        config = self.manager.get_animation_config()
        
        self.assertIsInstance(config, dict)
        mock_hyprctl.assert_called_once()
    
    @patch('src.hyprrice.hyprland.animations.hyprctl')
    def test_set_animation_config(self, mock_hyprctl):
        """Test setting animation configuration."""
        mock_hyprctl.return_value = (0, "", "")
        
        config = {'animations:enabled': True}
        result = self.manager.set_animation_config(config)
        
        self.assertTrue(result)
        mock_hyprctl.assert_called()
    
    @patch('src.hyprrice.hyprland.animations.hyprctl')
    def test_apply_animations(self, mock_hyprctl):
        """Test applying animations."""
        mock_hyprctl.return_value = (0, "", "")
        
        config = {
            'animations_enabled': True,
            'animation_duration': 0.5,
            'animation_curve': 'ease-out'
        }
        result = self.manager.apply_animations(config)
        
        self.assertTrue(result)
        mock_hyprctl.assert_called()
    
    def test_set_animation_duration(self):
        """Test setting animation duration."""
        with patch.object(self.manager, 'set_animation_config') as mock_set:
            mock_set.return_value = True
            
            result = self.manager.set_animation_duration(0.5)
            
            self.assertTrue(result)
            mock_set.assert_called_once()
    
    def test_set_animation_curve(self):
        """Test setting animation curve."""
        with patch.object(self.manager, 'set_animation_config') as mock_set:
            mock_set.return_value = True
            
            result = self.manager.set_animation_curve('ease-out')
            
            self.assertTrue(result)
            mock_set.assert_called_once()
    
    def test_create_animation_preset(self):
        """Test creating animation preset."""
        config = {'animations:enabled': True}
        result = self.manager.create_animation_preset('test_preset', config)
        
        self.assertTrue(result)
        
        # Check if preset file was created
        preset_path = self.manager.presets_dir / "test_preset.json"
        self.assertTrue(preset_path.exists())
    
    def test_load_animation_preset(self):
        """Test loading animation preset."""
        # Create a preset first
        config = {'animations:enabled': True}
        self.manager.create_animation_preset('test_preset', config)
        
        # Load the preset
        loaded_config = self.manager.load_animation_preset('test_preset')
        
        self.assertEqual(loaded_config, config)
    
    def test_list_animation_presets(self):
        """Test listing animation presets."""
        # Create some presets
        config = {'animations:enabled': True}
        self.manager.create_animation_preset('preset1', config)
        self.manager.create_animation_preset('preset2', config)
        
        presets = self.manager.list_animation_presets()
        
        self.assertIn('preset1', presets)
        self.assertIn('preset2', presets)


class TestWindowManager(unittest.TestCase):
    """Test WindowManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test.conf")
        self.manager = WindowManager(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('src.hyprrice.hyprland.windows.hyprctl')
    def test_get_window_config(self, mock_hyprctl):
        """Test getting window configuration."""
        mock_hyprctl.return_value = (0, "general:border_size = 1", "")
        
        config = self.manager.get_window_config()
        
        self.assertIsInstance(config, dict)
        mock_hyprctl.assert_called()
    
    @patch('src.hyprrice.hyprland.windows.hyprctl')
    def test_set_window_config(self, mock_hyprctl):
        """Test setting window configuration."""
        mock_hyprctl.return_value = (0, "", "")
        
        config = {'general:border_size': 2}
        result = self.manager.set_window_config(config)
        
        self.assertTrue(result)
        mock_hyprctl.assert_called()
    
    @patch('src.hyprrice.hyprland.windows.hyprctl')
    def test_apply_window_config(self, mock_hyprctl):
        """Test applying window configuration."""
        mock_hyprctl.return_value = (0, "", "")
        
        config = {
            'border_size': 2,
            'border_color': '#ffffff',
            'gaps_in': 5,
            'gaps_out': 10
        }
        result = self.manager.apply_window_config(config)
        
        self.assertTrue(result)
        mock_hyprctl.assert_called()
    
    def test_set_border_size(self):
        """Test setting border size."""
        with patch.object(self.manager, 'set_window_config') as mock_set:
            mock_set.return_value = True
            
            result = self.manager.set_border_size(2)
            
            self.assertTrue(result)
            mock_set.assert_called_once()
    
    def test_set_border_color(self):
        """Test setting border color."""
        with patch.object(self.manager, 'set_window_config') as mock_set:
            mock_set.return_value = True
            
            result = self.manager.set_border_color('#ffffff')
            
            self.assertTrue(result)
            mock_set.assert_called_once()
    
    @patch('src.hyprrice.hyprland.windows.hyprctl')
    def test_get_window_list(self, mock_hyprctl):
        """Test getting window list."""
        mock_output = """
Window 0x12345678:
  mapped: 1
  hidden: 0
  at: 100,100
  size: 800,600
  workspace: 1
  floating: 0
  monitor: 0
  class: test-app
  title: Test Window
"""
        mock_hyprctl.return_value = (0, mock_output, "")
        
        windows = self.manager.get_window_list()
        
        self.assertIsInstance(windows, list)
        if windows:
            self.assertIn('address', windows[0])
            self.assertIn('class', windows[0])


class TestDisplayManager(unittest.TestCase):
    """Test DisplayManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test.conf")
        self.manager = DisplayManager(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('src.hyprrice.hyprland.display.hyprctl')
    def test_get_monitors(self, mock_hyprctl):
        """Test getting monitors."""
        mock_output = '[{"name": "eDP-1", "width": 1920, "height": 1080}]'
        mock_hyprctl.return_value = (0, mock_output, "")
        
        monitors = self.manager.get_monitors()
        
        self.assertIsInstance(monitors, list)
        if monitors:
            self.assertIn('name', monitors[0])
    
    @patch('src.hyprrice.hyprland.display.hyprctl')
    def test_set_monitor_resolution(self, mock_hyprctl):
        """Test setting monitor resolution."""
        mock_hyprctl.return_value = (0, "", "")
        
        result = self.manager.set_monitor_resolution('eDP-1', '1920x1080@60')
        
        self.assertTrue(result)
        mock_hyprctl.assert_called()
    
    @patch('src.hyprrice.hyprland.display.hyprctl')
    def test_toggle_vrr(self, mock_hyprctl):
        """Test toggling VRR."""
        mock_hyprctl.return_value = (0, "", "")
        
        result = self.manager.toggle_vrr(True)
        
        self.assertTrue(result)
        mock_hyprctl.assert_called()


class TestInputManager(unittest.TestCase):
    """Test InputManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test.conf")
        self.manager = InputManager(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('src.hyprrice.hyprland.input.hyprctl')
    def test_get_input_config(self, mock_hyprctl):
        """Test getting input configuration."""
        mock_hyprctl.return_value = (0, "input:repeat_rate = 25", "")
        
        config = self.manager.get_input_config()
        
        self.assertIsInstance(config, dict)
        mock_hyprctl.assert_called()
    
    @patch('src.hyprrice.hyprland.input.hyprctl')
    def test_set_input_config(self, mock_hyprctl):
        """Test setting input configuration."""
        mock_hyprctl.return_value = (0, "", "")
        
        config = {'input:repeat_rate': 25}
        result = self.manager.set_input_config(config)
        
        self.assertTrue(result)
        mock_hyprctl.assert_called()
    
    def test_set_keyboard_repeat_rate(self):
        """Test setting keyboard repeat rate."""
        with patch.object(self.manager, 'set_input_config') as mock_set:
            mock_set.return_value = True
            
            result = self.manager.set_keyboard_repeat_rate(25)
            
            self.assertTrue(result)
            mock_set.assert_called_once()
    
    def test_set_mouse_sensitivity(self):
        """Test setting mouse sensitivity."""
        with patch.object(self.manager, 'set_input_config') as mock_set:
            mock_set.return_value = True
            
            result = self.manager.set_mouse_sensitivity(0.5)
            
            self.assertTrue(result)
            mock_set.assert_called_once()


class TestWorkspaceManager(unittest.TestCase):
    """Test WorkspaceManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test.conf")
        self.manager = WorkspaceManager(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('src.hyprrice.hyprland.workspaces.hyprctl')
    def test_get_workspaces(self, mock_hyprctl):
        """Test getting workspaces."""
        mock_output = """
workspace 1 (1)
workspace 2 (2)
"""
        mock_hyprctl.return_value = (0, mock_output, "")
        
        workspaces = self.manager.get_workspaces()
        
        self.assertIsInstance(workspaces, list)
        if workspaces:
            self.assertIn('id', workspaces[0])
    
    @patch('src.hyprrice.hyprland.workspaces.hyprctl')
    def test_switch_to_workspace(self, mock_hyprctl):
        """Test switching to workspace."""
        mock_hyprctl.return_value = (0, "", "")
        
        result = self.manager.switch_to_workspace('1')
        
        self.assertTrue(result)
        mock_hyprctl.assert_called()
    
    @patch('src.hyprrice.hyprland.workspaces.hyprctl')
    def test_create_workspace(self, mock_hyprctl):
        """Test creating workspace."""
        mock_hyprctl.return_value = (0, "", "")
        
        result = self.manager.create_workspace('test-workspace')
        
        self.assertTrue(result)
        mock_hyprctl.assert_called()
    
    @patch('src.hyprrice.hyprland.workspaces.hyprctl')
    def test_get_active_workspace(self, mock_hyprctl):
        """Test getting active workspace."""
        mock_output = """
workspace 1 (1)
"""
        mock_hyprctl.return_value = (0, mock_output, "")
        
        workspace = self.manager.get_active_workspace()
        
        self.assertIsInstance(workspace, dict)
        if workspace:
            self.assertIn('id', workspace)


if __name__ == '__main__':
    unittest.main()








