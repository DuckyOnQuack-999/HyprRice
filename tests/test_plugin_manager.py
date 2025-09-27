import os
import tempfile
from src.hyprrice.plugins import EnhancedPluginManager

def test_plugin_manager_load():
    """Test basic plugin manager functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create plugin manager
        pm = EnhancedPluginManager(tmpdir, enable_sandbox=False)
        
        # Test that manager initializes correctly
        assert pm.plugins_dir.name == os.path.basename(tmpdir)
        
        # Test listing available plugins (should be empty)
        available_plugins = pm.list_available_plugins()
        assert isinstance(available_plugins, list)
        
        # Test listing loaded plugins (should be empty)
        loaded_plugins = pm.list_loaded_plugins()
        assert isinstance(loaded_plugins, list)
        assert len(loaded_plugins) == 0 
