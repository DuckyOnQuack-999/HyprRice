"""
Tests for plugin system
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
from hyprrice.plugins import PluginManager, Plugin, PluginError


class TestPluginManager(unittest.TestCase):
    """Test PluginManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.plugin_manager = PluginManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_plugin_manager_initialization(self):
        """Test plugin manager initialization."""
        self.assertIsNotNone(self.plugin_manager)
        self.assertEqual(self.plugin_manager.plugins_dir, self.temp_dir)
        self.assertEqual(len(self.plugin_manager._plugins), 0)
    
    def test_load_plugins(self):
        """Test loading plugins."""
        # Create test plugin directory
        plugin_dir = Path(self.temp_dir) / 'test_plugin'
        plugin_dir.mkdir()
        
        # Create plugin file
        plugin_file = plugin_dir / 'plugin.py'
        plugin_file.write_text('''
class TestPlugin:
    def __init__(self):
        self.name = "test_plugin"
        self.version = "1.0.0"
        self.description = "Test plugin"
    
    def initialize(self, config):
        pass
    
    def cleanup(self):
        pass
''')
        
        # Mock importlib to load the plugin
        with patch('hyprrice.plugins.importlib.util.spec_from_file_location') as mock_spec, \
             patch('hyprrice.plugins.importlib.util.module_from_spec') as mock_module:
            
            mock_spec.return_value = Mock()
            mock_module.return_value = Mock()
            
            result = self.plugin_manager.load_plugins()
            
            # Verify plugins were loaded
            self.assertTrue(result)
    
    def test_enable_plugin(self):
        """Test enabling plugin."""
        # Mock plugin
        mock_plugin = Mock()
        mock_plugin.name = 'test_plugin'
        mock_plugin.initialize.return_value = True
        
        self.plugin_manager._plugins['test_plugin'] = mock_plugin
        
        result = self.plugin_manager.enable_plugin('test_plugin')
        
        # Verify plugin was enabled
        self.assertTrue(result)
        mock_plugin.initialize.assert_called_once_with(self.config)
    
    def test_disable_plugin(self):
        """Test disabling plugin."""
        # Mock plugin
        mock_plugin = Mock()
        mock_plugin.name = 'test_plugin'
        mock_plugin.cleanup.return_value = True
        
        self.plugin_manager._plugins['test_plugin'] = mock_plugin
        
        result = self.plugin_manager.disable_plugin('test_plugin')
        
        # Verify plugin was disabled
        self.assertTrue(result)
        mock_plugin.cleanup.assert_called_once()
    
    def test_get_plugin(self):
        """Test getting plugin."""
        # Mock plugin
        mock_plugin = Mock()
        mock_plugin.name = 'test_plugin'
        
        self.plugin_manager._plugins['test_plugin'] = mock_plugin
        
        plugin = self.plugin_manager.get_plugin('test_plugin')
        
        # Verify plugin was returned
        self.assertEqual(plugin, mock_plugin)
    
    def test_list_plugins(self):
        """Test listing plugins."""
        # Mock plugins
        mock_plugin1 = Mock()
        mock_plugin1.name = 'plugin1'
        mock_plugin1.version = '1.0.0'
        mock_plugin1.description = 'Plugin 1'
        
        mock_plugin2 = Mock()
        mock_plugin2.name = 'plugin2'
        mock_plugin2.version = '2.0.0'
        mock_plugin2.description = 'Plugin 2'
        
        self.plugin_manager._plugins = {
            'plugin1': mock_plugin1,
            'plugin2': mock_plugin2
        }
        
        plugins = self.plugin_manager.list_plugins()
        
        # Verify plugins were listed
        self.assertEqual(len(plugins), 2)
        self.assertIn('plugin1', plugins)
        self.assertIn('plugin2', plugins)
    
    def test_plugin_error_handling(self):
        """Test plugin error handling."""
        # Test enabling non-existent plugin
        result = self.plugin_manager.enable_plugin('nonexistent')
        self.assertFalse(result)
        
        # Test disabling non-existent plugin
        result = self.plugin_manager.disable_plugin('nonexistent')
        self.assertFalse(result)
        
        # Test getting non-existent plugin
        plugin = self.plugin_manager.get_plugin('nonexistent')
        self.assertIsNone(plugin)
    
    def test_plugin_validation(self):
        """Test plugin validation."""
        # Test valid plugin
        valid_plugin = Mock()
        valid_plugin.name = 'valid_plugin'
        valid_plugin.version = '1.0.0'
        valid_plugin.description = 'Valid plugin'
        valid_plugin.initialize = Mock()
        valid_plugin.cleanup = Mock()
        
        result = self.plugin_manager._validate_plugin(valid_plugin)
        self.assertTrue(result)
        
        # Test invalid plugin (missing name)
        invalid_plugin = Mock()
        invalid_plugin.version = '1.0.0'
        invalid_plugin.description = 'Invalid plugin'
        invalid_plugin.initialize = Mock()
        invalid_plugin.cleanup = Mock()
        
        result = self.plugin_manager._validate_plugin(invalid_plugin)
        self.assertFalse(result)
        
        # Test invalid plugin (missing initialize method)
        invalid_plugin2 = Mock()
        invalid_plugin2.name = 'invalid_plugin2'
        invalid_plugin2.version = '1.0.0'
        invalid_plugin2.description = 'Invalid plugin 2'
        invalid_plugin2.cleanup = Mock()
        
        result = self.plugin_manager._validate_plugin(invalid_plugin2)
        self.assertFalse(result)
        
        # Test invalid plugin (missing cleanup method)
        invalid_plugin3 = Mock()
        invalid_plugin3.name = 'invalid_plugin3'
        invalid_plugin3.version = '1.0.0'
        invalid_plugin3.description = 'Invalid plugin 3'
        invalid_plugin3.initialize = Mock()
        
        result = self.plugin_manager._validate_plugin(invalid_plugin3)
        self.assertFalse(result)


class TestPlugin(unittest.TestCase):
    """Test Plugin base class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        class TestPlugin(Plugin):
            def __init__(self):
                super().__init__()
                self.name = "test_plugin"
                self.version = "1.0.0"
                self.description = "Test plugin"
        
        plugin = TestPlugin()
        
        self.assertEqual(plugin.name, "test_plugin")
        self.assertEqual(plugin.version, "1.0.0")
        self.assertEqual(plugin.description, "Test plugin")
        self.assertFalse(plugin.enabled)
    
    def test_plugin_enable_disable(self):
        """Test plugin enable/disable."""
        class TestPlugin(Plugin):
            def __init__(self):
                super().__init__()
                self.name = "test_plugin"
                self.version = "1.0.0"
                self.description = "Test plugin"
            
            def initialize(self, config):
                return True
            
            def cleanup(self):
                return True
        
        plugin = TestPlugin()
        
        # Test enable
        result = plugin.enable(self.config)
        self.assertTrue(result)
        self.assertTrue(plugin.enabled)
        
        # Test disable
        result = plugin.disable()
        self.assertTrue(result)
        self.assertFalse(plugin.enabled)
    
    def test_plugin_error_handling(self):
        """Test plugin error handling."""
        class TestPlugin(Plugin):
            def __init__(self):
                super().__init__()
                self.name = "test_plugin"
                self.version = "1.0.0"
                self.description = "Test plugin"
            
            def initialize(self, config):
                raise Exception("Test error")
            
            def cleanup(self):
                raise Exception("Test error")
        
        plugin = TestPlugin()
        
        # Test enable with error
        result = plugin.enable(self.config)
        self.assertFalse(result)
        self.assertFalse(plugin.enabled)
        
        # Test disable with error
        result = plugin.disable()
        self.assertFalse(result)
    
    def test_plugin_metadata(self):
        """Test plugin metadata."""
        class TestPlugin(Plugin):
            def __init__(self):
                super().__init__()
                self.name = "test_plugin"
                self.version = "1.0.0"
                self.description = "Test plugin"
                self.author = "Test Author"
                self.license = "MIT"
                self.dependencies = ["dependency1", "dependency2"]
        
        plugin = TestPlugin()
        
        metadata = plugin.get_metadata()
        
        self.assertEqual(metadata['name'], "test_plugin")
        self.assertEqual(metadata['version'], "1.0.0")
        self.assertEqual(metadata['description'], "Test plugin")
        self.assertEqual(metadata['author'], "Test Author")
        self.assertEqual(metadata['license'], "MIT")
        self.assertEqual(metadata['dependencies'], ["dependency1", "dependency2"])


class TestPluginError(unittest.TestCase):
    """Test PluginError exception."""
    
    def test_plugin_error_creation(self):
        """Test PluginError creation."""
        error = PluginError("Test error message")
        
        self.assertEqual(str(error), "Test error message")
        self.assertIsInstance(error, Exception)
    
    def test_plugin_error_with_details(self):
        """Test PluginError with details."""
        error = PluginError("Test error message", details={"plugin": "test_plugin"})
        
        self.assertEqual(str(error), "Test error message")
        self.assertEqual(error.details, {"plugin": "test_plugin"})


class TestPluginSystemIntegration(unittest.TestCase):
    """Test plugin system integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.plugin_manager = PluginManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_plugin_lifecycle(self):
        """Test complete plugin lifecycle."""
        # Create test plugin
        class TestPlugin(Plugin):
            def __init__(self):
                super().__init__()
                self.name = "test_plugin"
                self.version = "1.0.0"
                self.description = "Test plugin"
                self.initialized = False
                self.cleaned_up = False
            
            def initialize(self, config):
                self.initialized = True
                return True
            
            def cleanup(self):
                self.cleaned_up = True
                return True
        
        # Create plugin instance
        plugin = TestPlugin()
        
        # Add plugin to manager
        self.plugin_manager._plugins['test_plugin'] = plugin
        
        # Test enable
        result = self.plugin_manager.enable_plugin('test_plugin')
        self.assertTrue(result)
        self.assertTrue(plugin.enabled)
        self.assertTrue(plugin.initialized)
        
        # Test disable
        result = self.plugin_manager.disable_plugin('test_plugin')
        self.assertTrue(result)
        self.assertFalse(plugin.enabled)
        self.assertTrue(plugin.cleaned_up)
    
    def test_plugin_dependencies(self):
        """Test plugin dependencies."""
        # Create dependent plugin
        class DependentPlugin(Plugin):
            def __init__(self):
                super().__init__()
                self.name = "dependent_plugin"
                self.version = "1.0.0"
                self.description = "Dependent plugin"
                self.dependencies = ["base_plugin"]
            
            def initialize(self, config):
                return True
            
            def cleanup(self):
                return True
        
        # Create base plugin
        class BasePlugin(Plugin):
            def __init__(self):
                super().__init__()
                self.name = "base_plugin"
                self.version = "1.0.0"
                self.description = "Base plugin"
            
            def initialize(self, config):
                return True
            
            def cleanup(self):
                return True
        
        # Add plugins to manager
        base_plugin = BasePlugin()
        dependent_plugin = DependentPlugin()
        
        self.plugin_manager._plugins = {
            'base_plugin': base_plugin,
            'dependent_plugin': dependent_plugin
        }
        
        # Test dependency resolution
        dependencies = self.plugin_manager._resolve_dependencies('dependent_plugin')
        
        self.assertIn('base_plugin', dependencies)
        self.assertIn('dependent_plugin', dependencies)
    
    def test_plugin_hot_reload(self):
        """Test plugin hot reload."""
        # Create test plugin
        class TestPlugin(Plugin):
            def __init__(self):
                super().__init__()
                self.name = "test_plugin"
                self.version = "1.0.0"
                self.description = "Test plugin"
                self.reload_count = 0
            
            def initialize(self, config):
                return True
            
            def cleanup(self):
                return True
            
            def reload(self):
                self.reload_count += 1
                return True
        
        plugin = TestPlugin()
        self.plugin_manager._plugins['test_plugin'] = plugin
        
        # Test hot reload
        result = self.plugin_manager.hot_reload_plugin('test_plugin')
        
        self.assertTrue(result)
        self.assertEqual(plugin.reload_count, 1)
    
    def test_plugin_sandboxing(self):
        """Test plugin sandboxing."""
        # Create test plugin with restricted access
        class SandboxedPlugin(Plugin):
            def __init__(self):
                super().__init__()
                self.name = "sandboxed_plugin"
                self.version = "1.0.0"
                self.description = "Sandboxed plugin"
                self.sandboxed = True
            
            def initialize(self, config):
                # Plugin should not have access to system resources
                try:
                    import os
                    os.system('echo "This should be blocked"')
                    return False
                except:
                    return True
            
            def cleanup(self):
                return True
        
        plugin = SandboxedPlugin()
        self.plugin_manager._plugins['sandboxed_plugin'] = plugin
        
        # Test sandboxed plugin
        result = self.plugin_manager.enable_plugin('sandboxed_plugin')
        
        # Should succeed (sandboxed)
        self.assertTrue(result)
    
    def test_plugin_marketplace(self):
        """Test plugin marketplace functionality."""
        # Mock marketplace data
        marketplace_data = {
            'plugins': [
                {
                    'name': 'marketplace_plugin',
                    'version': '1.0.0',
                    'description': 'Plugin from marketplace',
                    'author': 'Marketplace Author',
                    'download_url': 'https://example.com/plugin.hyprrice',
                    'rating': 4.5,
                    'downloads': 1000
                }
            ]
        }
        
        # Mock marketplace API
        with patch('hyprrice.plugins.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = marketplace_data
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            # Test marketplace search
            plugins = self.plugin_manager.search_marketplace('test')
            
            self.assertEqual(len(plugins), 1)
            self.assertEqual(plugins[0]['name'], 'marketplace_plugin')
        
        # Test plugin installation from marketplace
        with patch('hyprrice.plugins.requests.get') as mock_get, \
             patch('builtins.open', mock_open()) as mock_file:
            
            mock_response = Mock()
            mock_response.content = b'plugin content'
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = self.plugin_manager.install_from_marketplace('marketplace_plugin')
            
            self.assertTrue(result)
            mock_file.assert_called_once()


def mock_open(content=''):
    """Mock open function for testing."""
    return unittest.mock.mock_open(read_data=content)


if __name__ == '__main__':
    unittest.main()








