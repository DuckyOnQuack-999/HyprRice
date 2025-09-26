"""
Tests for error handling and edge cases
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
from hyprrice.exceptions import (
    HyprRiceError, ConfigError, ThemeError, PluginError,
    HyprlandError, ValidationError, FileError, NetworkError
)
from hyprrice.gui.theme_manager import ThemeManager
from hyprrice.hyprland.animations import AnimationManager
from hyprrice.hyprland.windows import WindowManager
from hyprrice.hyprland.display import DisplayManager
from hyprrice.hyprland.input import InputManager
from hyprrice.hyprland.workspaces import WorkspaceManager


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_config_error_handling(self):
        """Test configuration error handling."""
        # Test invalid config file
        invalid_config_file = Path(self.temp_dir) / 'invalid_config.yaml'
        invalid_config_file.write_text('invalid: yaml: content: [')
        
        config = Config()
        
        # Should raise ConfigError
        with self.assertRaises(ConfigError):
            config.load(str(invalid_config_file))
        
        # Test missing config file
        missing_config_file = Path(self.temp_dir) / 'missing_config.yaml'
        
        with self.assertRaises(FileError):
            config.load(str(missing_config_file))
        
        # Test permission denied
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with self.assertRaises(FileError):
                config.save(str(Path(self.temp_dir) / 'config.yaml'))
    
    def test_theme_error_handling(self):
        """Test theme error handling."""
        theme_manager = ThemeManager(self.config, self.temp_dir)
        
        # Test invalid theme file
        invalid_theme_file = Path(self.temp_dir) / 'invalid_theme.hyprrice'
        invalid_theme_file.write_text('invalid json content')
        
        with self.assertRaises(ThemeError):
            theme_manager.get_theme_info('invalid_theme')
        
        # Test missing theme file
        with self.assertRaises(ThemeError):
            theme_manager.get_theme_info('nonexistent_theme')
        
        # Test invalid theme data
        invalid_theme_data_file = Path(self.temp_dir) / 'invalid_data_theme.hyprrice'
        invalid_theme_data = {
            'name': 'invalid_theme',
            'description': 'Invalid theme',
            'hyprland': {
                'animations': {
                    'enabled': 'invalid_boolean'  # Should be boolean
                }
            }
        }
        
        import json
        invalid_theme_data_file.write_text(json.dumps(invalid_theme_data))
        
        with self.assertRaises(ValidationError):
            theme_manager.apply_theme('invalid_data_theme')
        
        # Test theme import error
        with patch('builtins.open', side_effect=IOError("File not found")):
            with self.assertRaises(ThemeError):
                theme_manager.import_theme('nonexistent_theme.hyprrice')
        
        # Test theme export error
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with self.assertRaises(ThemeError):
                theme_manager.export_theme('test_theme', 'nonexistent_path.hyprrice')
    
    def test_hyprland_error_handling(self):
        """Test Hyprland error handling."""
        # Test AnimationManager errors
        anim_manager = AnimationManager()
        
        # Test hyprctl command failure
        with patch('hyprrice.hyprland.animations.subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout='', returncode=1)
            
            with self.assertRaises(HyprlandError):
                anim_manager.get_animation_config()
        
        # Test hyprctl command timeout
        with patch('hyprrice.hyprland.animations.subprocess.run') as mock_run:
            mock_run.side_effect = TimeoutError("Command timed out")
            
            with self.assertRaises(HyprlandError):
                anim_manager.set_animation_config({'enabled': True})
        
        # Test WindowManager errors
        window_manager = WindowManager()
        
        # Test invalid window config
        with self.assertRaises(ValidationError):
            window_manager.set_window_config({'invalid_key': 'invalid_value'})
        
        # Test DisplayManager errors
        display_manager = DisplayManager()
        
        # Test invalid monitor resolution
        with self.assertRaises(ValidationError):
            display_manager.set_monitor_resolution('invalid_monitor', 'invalid_resolution')
        
        # Test InputManager errors
        input_manager = InputManager()
        
        # Test invalid input config
        with self.assertRaises(ValidationError):
            input_manager.set_input_config({'invalid_key': 'invalid_value'})
        
        # Test WorkspaceManager errors
        workspace_manager = WorkspaceManager()
        
        # Test invalid workspace number
        with self.assertRaises(ValidationError):
            workspace_manager.switch_to_workspace(-1)
        
        # Test invalid workspace name
        with self.assertRaises(ValidationError):
            workspace_manager.rename_workspace(1, '')
    
    def test_network_error_handling(self):
        """Test network error handling."""
        # Test theme marketplace network errors
        theme_manager = ThemeManager(self.config, self.temp_dir)
        
        # Test network timeout
        with patch('hyprrice.gui.theme_manager.requests.get') as mock_get:
            mock_get.side_effect = TimeoutError("Network timeout")
            
            with self.assertRaises(NetworkError):
                theme_manager.search_marketplace('test')
        
        # Test network connection error
        with patch('hyprrice.gui.theme_manager.requests.get') as mock_get:
            mock_get.side_effect = ConnectionError("Connection failed")
            
            with self.assertRaises(NetworkError):
                theme_manager.install_from_marketplace('test_theme')
        
        # Test HTTP error
        with patch('hyprrice.gui.theme_manager.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = Exception("404 Not Found")
            mock_get.return_value = mock_response
            
            with self.assertRaises(NetworkError):
                theme_manager.install_from_marketplace('nonexistent_theme')
    
    def test_validation_error_handling(self):
        """Test validation error handling."""
        # Test color validation
        with self.assertRaises(ValidationError):
            self.config.hyprland.windows.border_color = 'invalid_color'
        
        # Test numeric validation
        with self.assertRaises(ValidationError):
            self.config.hyprland.animations.duration = -1.0
        
        # Test string validation
        with self.assertRaises(ValidationError):
            self.config.hyprland.animations.curve = ''
        
        # Test list validation
        with self.assertRaises(ValidationError):
            self.config.waybar.modules = 'invalid_list'
        
        # Test boolean validation
        with self.assertRaises(ValidationError):
            self.config.hyprland.animations.enabled = 'invalid_boolean'
    
    def test_file_error_handling(self):
        """Test file error handling."""
        # Test file not found
        with self.assertRaises(FileError):
            with open('nonexistent_file.txt', 'r') as f:
                f.read()
        
        # Test permission denied
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with self.assertRaises(FileError):
                with open('restricted_file.txt', 'w') as f:
                    f.write('test')
        
        # Test disk full
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            with self.assertRaises(FileError):
                with open('large_file.txt', 'w') as f:
                    f.write('test')
    
    def test_plugin_error_handling(self):
        """Test plugin error handling."""
        # Test plugin loading error
        with patch('hyprrice.plugins.importlib.util.spec_from_file_location') as mock_spec:
            mock_spec.return_value = None
            
            with self.assertRaises(PluginError):
                from hyprrice.plugins import PluginManager
                plugin_manager = PluginManager(self.temp_dir)
                plugin_manager.load_plugins()
        
        # Test plugin initialization error
        class FailingPlugin:
            def __init__(self):
                self.name = "failing_plugin"
                self.version = "1.0.0"
                self.description = "Failing plugin"
            
            def initialize(self, config):
                raise Exception("Plugin initialization failed")
            
            def cleanup(self):
                pass
        
        with self.assertRaises(PluginError):
            plugin = FailingPlugin()
            plugin.initialize(self.config)
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test empty configuration
        empty_config = Config()
        self.assertIsNotNone(empty_config)
        
        # Test maximum values
        self.config.hyprland.animations.duration = 10.0  # Maximum duration
        self.config.hyprland.windows.opacity = 1.0  # Maximum opacity
        self.config.hyprland.windows.border_size = 10  # Maximum border size
        
        # Test minimum values
        self.config.hyprland.animations.duration = 0.0  # Minimum duration
        self.config.hyprland.windows.opacity = 0.0  # Minimum opacity
        self.config.hyprland.windows.border_size = 0  # Minimum border size
        
        # Test special characters in strings
        self.config.hyprland.windows.border_color = '#FF0000'
        self.config.hyprland.animations.curve = 'easeOutCubic'
        
        # Test unicode characters
        self.config.waybar.modules = ['时钟', '电池', '网络']
        
        # Test very long strings
        long_string = 'A' * 10000
        self.config.hyprland.windows.rules.append({
            'class': long_string,
            'title': long_string
        })
    
    def test_concurrent_error_handling(self):
        """Test error handling in concurrent operations."""
        import threading
        import queue
        
        # Test concurrent file access
        def file_operation():
            try:
                with open(Path(self.temp_dir) / 'test_file.txt', 'w') as f:
                    f.write('test')
            except Exception as e:
                return str(e)
            return None
        
        # Start multiple threads
        threads = []
        results = queue.Queue()
        
        for i in range(10):
            thread = threading.Thread(target=lambda: results.put(file_operation()))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        errors = []
        while not results.empty():
            error = results.get()
            if error:
                errors.append(error)
        
        # Should have some errors due to concurrent access
        self.assertGreater(len(errors), 0)
    
    def test_memory_error_handling(self):
        """Test memory error handling."""
        # Test large data handling
        try:
            # Create very large config
            large_config = Config()
            for i in range(100000):
                large_config.hyprland.windows.rules.append({
                    'class': f'Class{i}',
                    'title': f'Title{i}',
                    'opacity': 0.9
                })
        except MemoryError:
            # Should handle memory errors gracefully
            pass
        
        # Test memory cleanup
        import gc
        gc.collect()
    
    def test_timeout_error_handling(self):
        """Test timeout error handling."""
        # Test hyprctl timeout
        with patch('hyprrice.hyprland.animations.subprocess.run') as mock_run:
            mock_run.side_effect = TimeoutError("Command timed out")
            
            anim_manager = AnimationManager()
            
            with self.assertRaises(HyprlandError):
                anim_manager.get_animation_config()
        
        # Test network timeout
        with patch('hyprrice.gui.theme_manager.requests.get') as mock_get:
            mock_get.side_effect = TimeoutError("Network timeout")
            
            theme_manager = ThemeManager(self.config, self.temp_dir)
            
            with self.assertRaises(NetworkError):
                theme_manager.search_marketplace('test')
    
    def test_recovery_from_errors(self):
        """Test recovery from errors."""
        # Test config recovery
        config = Config()
        
        # Simulate config corruption
        try:
            config.load('nonexistent_config.yaml')
        except FileError:
            # Should recover by using default config
            self.assertIsNotNone(config)
        
        # Test theme recovery
        theme_manager = ThemeManager(self.config, self.temp_dir)
        
        # Simulate theme loading error
        try:
            theme_manager.get_theme_info('nonexistent_theme')
        except ThemeError:
            # Should recover by returning None or default theme
            pass
        
        # Test hyprland recovery
        anim_manager = AnimationManager()
        
        # Simulate hyprctl error
        with patch('hyprrice.hyprland.animations.subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout='', returncode=1)
            
            try:
                anim_manager.get_animation_config()
            except HyprlandError:
                # Should recover by using default config
                pass


if __name__ == '__main__':
    unittest.main()








