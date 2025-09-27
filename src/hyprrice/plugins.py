import os
import json
import importlib.util
import logging
from abc import ABC, abstractmethod
from typing import List, Callable, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from .exceptions import PluginError
from .plugin_sandbox import SecurePluginManager, create_sandbox

@dataclass
class PluginMetadata:
    """Plugin metadata structure"""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = None
    config_schema: Dict[str, Any] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.config_schema is None:
            self.config_schema = {}

class PluginBase(ABC):
    """
    Enhanced abstract base class for HyprRice plugins with comprehensive lifecycle management.
    
    Available hooks:
      - before_apply: Called before applying configuration to Hyprland
      - after_apply: Called after applying configuration to Hyprland
      - before_theme_change: Called before changing themes
      - after_theme_change: Called after changing themes
      - before_import: Called before importing configuration
      - after_import: Called after importing configuration
      - on_preview_update: Called when preview is updated
      - on_startup: Called when plugin is loaded
      - on_shutdown: Called when plugin is unloaded
      - on_config_change: Called when plugin configuration changes
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"plugin.{self.__class__.__name__}")
        self.config = {}
        self.enabled = True
        
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata. Must be implemented by plugins."""
        pass
    
    def register(self, app):
        """Register plugin with the main app. Override in plugin."""
        self.logger.info(f"Registering plugin: {self.metadata.name}")
        
    def configure(self, config: Dict[str, Any]):
        """Configure the plugin with settings."""
        self.config = config
        self.on_config_change(config)
        
    def get_config_schema(self) -> Dict[str, Any]:
        """Return configuration schema for this plugin."""
        return self.metadata.config_schema
        
    def validate_dependencies(self) -> List[str]:
        """Validate plugin dependencies. Return list of missing dependencies."""
        missing = []
        for dep in self.metadata.dependencies:
            try:
                importlib.import_module(dep)
            except ImportError:
                missing.append(dep)
        return missing

    # Event handler stubs (plugins can override)
    def before_apply(self, context: Dict[str, Any]): pass
    def after_apply(self, context: Dict[str, Any]): pass
    def before_theme_change(self, context: Dict[str, Any]): pass
    def after_theme_change(self, context: Dict[str, Any]): pass
    def before_import(self, context: Dict[str, Any]): pass
    def after_import(self, context: Dict[str, Any]): pass
    def on_preview_update(self, context: Dict[str, Any]): pass
    def on_startup(self, context: Dict[str, Any]): pass
    def on_shutdown(self, context: Dict[str, Any]): pass
    def on_config_change(self, config: Dict[str, Any]): pass

class EnhancedPluginManager:
    """Enhanced plugin manager with comprehensive plugin lifecycle management and sandboxing."""
    
    def __init__(self, plugins_dir: str, config_dir: str = None, enable_sandbox: bool = True, security_level: str = 'medium'):
        self.plugins_dir = Path(plugins_dir)
        self.config_dir = Path(config_dir) if config_dir else self.plugins_dir / "config"
        self.logger = logging.getLogger("PluginManager")
        
        # Sandboxing configuration
        self.enable_sandbox = enable_sandbox
        self.security_level = security_level
        self.secure_manager = None
        
        if self.enable_sandbox:
            self.secure_manager = SecurePluginManager(self.plugins_dir)
        
        # Plugin storage
        self.available_plugins = {}  # name -> plugin file path
        self.loaded_plugins = {}     # name -> plugin instance
        self.plugin_metadata = {}    # name -> PluginMetadata
        self.plugin_configs = {}     # name -> config dict
        
        # Event handlers
        self.event_handlers = {
            'before_apply': [],
            'after_apply': [],
            'before_theme_change': [],
            'after_theme_change': [],
            'before_import': [],
            'after_import': [],
            'on_preview_update': [],
        }
        
        # Initialize
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._load_plugin_configs()
        self._discover_plugins()
        
    def _discover_plugins(self):
        """Discover all available plugins."""
        if not self.plugins_dir.exists():
            self.logger.warning(f"Plugins directory does not exist: {self.plugins_dir}")
            return
            
        for plugin_file in self.plugins_dir.glob("*.py"):
            if plugin_file.name.startswith('_'):
                continue
                
            plugin_name = plugin_file.stem
            self.available_plugins[plugin_name] = plugin_file
            
            # Try to load metadata without loading the plugin
            try:
                metadata = self._extract_plugin_metadata(plugin_file)
                if metadata:
                    self.plugin_metadata[plugin_name] = metadata
            except Exception as e:
                self.logger.error(f"Failed to extract metadata from {plugin_name}: {e}")
                
        self.logger.info(f"Discovered {len(self.available_plugins)} plugins")
    
    def _extract_plugin_metadata(self, plugin_file: Path) -> Optional[PluginMetadata]:
        """Extract plugin metadata without loading the plugin."""
        try:
            spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for plugin class
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, PluginBase) and 
                    attr != PluginBase):
                    plugin_class = attr
                    break
                    
            if plugin_class:
                # Create temporary instance to get metadata
                temp_instance = plugin_class()
                return temp_instance.metadata
                
        except Exception as e:
            self.logger.error(f"Failed to extract metadata from {plugin_file}: {e}")
            
        return None
    
    def _load_plugin_configs(self):
        """Load plugin configurations from disk."""
        config_file = self.config_dir / "plugin_configs.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self.plugin_configs = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load plugin configs: {e}")
    
    def _save_plugin_configs(self):
        """Save plugin configurations to disk."""
        config_file = self.config_dir / "plugin_configs.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(self.plugin_configs, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save plugin configs: {e}")
    
    def list_available_plugins(self) -> List[Dict[str, Any]]:
        """List all available plugins with their metadata."""
        plugins = []
        for name, path in self.available_plugins.items():
            metadata = self.plugin_metadata.get(name)
            plugins.append({
                'name': name,
                'path': str(path),
                'loaded': name in self.loaded_plugins,
                'enabled': metadata.enabled if metadata else True,
                'metadata': asdict(metadata) if metadata else None
            })
        return plugins
    
    def list_loaded_plugins(self) -> List[str]:
        """List names of currently loaded plugins."""
        return list(self.loaded_plugins.keys())
    
    def load_plugin(self, plugin_name: str, app=None) -> bool:
        """Load and register a plugin with optional sandboxing."""
        if plugin_name in self.loaded_plugins:
            self.logger.warning(f"Plugin {plugin_name} is already loaded")
            return True
            
        if plugin_name not in self.available_plugins:
            raise PluginError(f"Plugin {plugin_name} not found")
        
        try:
            if self.enable_sandbox and self.secure_manager:
                # Load plugin securely with sandboxing
                limits = create_sandbox(self.security_level)
                plugin_instance = self.secure_manager.load_plugin_secure(plugin_name, limits)
            else:
                # Load plugin without sandboxing (legacy mode)
                plugin_instance = self._load_plugin_unsafe(plugin_name)
            
            # Validate dependencies
            missing_deps = plugin_instance.validate_dependencies()
            if missing_deps:
                raise PluginError(f"Plugin {plugin_name} has missing dependencies: {missing_deps}")
            
            # Configure plugin
            config = self.plugin_configs.get(plugin_name, {})
            plugin_instance.configure(config)
            
            # Register with app
            if app:
                plugin_instance.register(app)
            
            # Store plugin
            self.loaded_plugins[plugin_name] = plugin_instance
            self.plugin_metadata[plugin_name] = plugin_instance.metadata
            
            # Register event handlers
            self._register_plugin_handlers(plugin_name, plugin_instance)
            
            # Call startup hook
            plugin_instance.on_startup({'app': app})
            
            self.logger.info(f"Successfully loaded plugin: {plugin_name} (sandbox: {self.enable_sandbox})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            raise PluginError(f"Failed to load plugin {plugin_name}: {e}")
    
    def _load_plugin_unsafe(self, plugin_name: str) -> PluginBase:
        """Load plugin without sandboxing (for backward compatibility)."""
        plugin_path = self.available_plugins[plugin_name]
        
        # Load the plugin module
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the plugin class
        plugin_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, PluginBase) and 
                attr != PluginBase):
                plugin_class = attr
                break
                
        if not plugin_class:
            raise PluginError(f"No valid plugin class found in {plugin_name}")
        
        # Create plugin instance
        return plugin_class()
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name not in self.loaded_plugins:
            self.logger.warning(f"Plugin {plugin_name} is not loaded")
            return True
            
        try:
            plugin_instance = self.loaded_plugins[plugin_name]
            
            # Call shutdown hook
            plugin_instance.on_shutdown({})
            
            # Unregister event handlers
            self._unregister_plugin_handlers(plugin_name)
            
            # Remove from loaded plugins
            del self.loaded_plugins[plugin_name]
            
            self.logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def _register_plugin_handlers(self, plugin_name: str, plugin_instance: PluginBase):
        """Register plugin event handlers."""
        for event_name in self.event_handlers:
            handler = getattr(plugin_instance, event_name, None)
            if handler and callable(handler):
                self.event_handlers[event_name].append((plugin_name, handler))
    
    def _unregister_plugin_handlers(self, plugin_name: str):
        """Unregister plugin event handlers."""
        for event_name, handlers in self.event_handlers.items():
            self.event_handlers[event_name] = [
                (name, handler) for name, handler in handlers 
                if name != plugin_name
            ]
    
    def configure_plugin(self, plugin_name: str, config: Dict[str, Any]):
        """Configure a plugin."""
        self.plugin_configs[plugin_name] = config
        self._save_plugin_configs()
        
        if plugin_name in self.loaded_plugins:
            self.loaded_plugins[plugin_name].configure(config)
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get plugin configuration."""
        return self.plugin_configs.get(plugin_name, {})
    
    def emit_event(self, event_name: str, context: Dict[str, Any]):
        """Emit an event to all registered handlers."""
        if event_name not in self.event_handlers:
            return
            
        for plugin_name, handler in self.event_handlers[event_name]:
            try:
                handler(context)
            except Exception as e:
                self.logger.error(f"Error in plugin {plugin_name} handling {event_name}: {e}")
    
    def reload_plugin(self, plugin_name: str, app=None) -> bool:
        """Reload a plugin."""
        if plugin_name in self.loaded_plugins:
            self.unload_plugin(plugin_name)
        return self.load_plugin(plugin_name, app)
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        if plugin_name in self.plugin_metadata:
            self.plugin_metadata[plugin_name].enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        if plugin_name in self.plugin_metadata:
            self.plugin_metadata[plugin_name].enabled = False
            if plugin_name in self.loaded_plugins:
                self.unload_plugin(plugin_name)
            return True
        return False

# Backward compatibility aliases
PluginManager = EnhancedPluginManager
Plugin = PluginBase

# Import exception for backward compatibility
from .exceptions import PluginError 
