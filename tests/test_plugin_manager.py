import os
import tempfile
from src.hyprrice.plugins import PluginManager

def test_plugin_manager_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_path = os.path.join(tmpdir, "dummy.py")
        with open(plugin_path, "w") as f:
            f.write("def register(app):\n    app._dummy_loaded = True\n")
        pm = PluginManager(tmpdir)
        assert "dummy.py" in pm.list_plugins()
        class DummyApp:
            pass
        app = DummyApp()
        pm.load_plugin("dummy.py", app)
        assert hasattr(app, "_dummy_loaded") and app._dummy_loaded 