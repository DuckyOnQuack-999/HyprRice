import os
import importlib.util
from typing import List, Callable, Dict, Any

class PluginBase:
    """
    Base class for HyprRice plugins. Plugins can override event handler methods or register handlers dynamically.
    Available hooks:
      - before_apply
      - after_apply
      - before_theme_change
      - after_theme_change
      - before_import
      - after_import
      - on_preview_update
    """
    def register(self, app):
        """Register plugin with the main app. Override in plugin."""
        pass

    # Event handler stubs (plugins can override)
    def before_apply(self, context: Dict[str, Any]): pass
    def after_apply(self, context: Dict[str, Any]): pass
    def before_theme_change(self, context: Dict[str, Any]): pass
    def after_theme_change(self, context: Dict[str, Any]): pass
    def before_import(self, context: Dict[str, Any]): pass
    def after_import(self, context: Dict[str, Any]): pass
    def on_preview_update(self, context: Dict[str, Any]): pass

class PluginManager:
    def __init__(self, plugins_dir):
        self.plugins_dir = plugins_dir
        self.plugins = []
        self.loaded_plugins = []
        self.plugin_instances = []
        self._discover_plugins()

    def _discover_plugins(self):
        if not os.path.isdir(self.plugins_dir):
            return
        for fname in os.listdir(self.plugins_dir):
            if fname.endswith('.py') and not fname.startswith('_'):
                self.plugins.append(fname)

    def list_plugins(self) -> List[str]:
        return self.plugins

    def load_plugin(self, plugin_name: str, app):
        plugin_path = os.path.join(self.plugins_dir, plugin_name)
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        if not spec or not spec.loader:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        plugin_instance = None
        if hasattr(module, 'register'):
            plugin_instance = module.register(app)
            self.loaded_plugins.append(plugin_name)
            if plugin_instance:
                self.plugin_instances.append(plugin_instance)
        return module

    def dispatch_event(self, event: str, context: Dict[str, Any]):
        """Call the event handler on all loaded plugins."""
        for plugin in self.plugin_instances:
            handler = getattr(plugin, event, None)
            if callable(handler):
                handler(context) 