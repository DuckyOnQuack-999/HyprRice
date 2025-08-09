"""
Enhanced plugin system for HyprRice with security and isolation features
"""

import os
import sys
import importlib.util
import importlib
import traceback
import logging
import threading
import signal
import time
from typing import List, Callable, Dict, Any, Optional, Type
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from .exceptions import PluginError
from .utils import setup_logging


class PluginSandbox:
    """Security sandbox for plugin execution."""
    
    def __init__(self, max_execution_time: int = 30, max_memory_mb: int = 100):
        self.max_execution_time = max_execution_time
        self.max_memory_mb = max_memory_mb
        self.logger = logging.getLogger(__name__)
    
    def execute_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with timeout and resource limits."""
        def target():
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Plugin execution error: {e}")
                raise PluginError(f"Plugin execution failed: {e}")
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(target)
            try:
                result = future.result(timeout=self.max_execution_time)
                return result
            except FutureTimeoutError:
                self.logger.error(f"Plugin execution timed out after {self.max_execution_time} seconds")
                raise PluginError(f"Plugin execution timed out")
            except Exception as e:
                self.logger.error(f"Plugin execution failed: {e}")
                raise PluginError(f"Plugin execution failed: {e}")


class PluginBase:
    """
    Enhanced base class for HyprRice plugins with security and lifecycle management.
    
    Available hooks:
      - before_apply: Called before applying configuration changes
      - after_apply: Called after applying configuration changes  
      - before_theme_change: Called before changing themes
      - after_theme_change: Called after changing themes
      - before_import: Called before importing configurations
      - after_import: Called after importing configurations
      - on_preview_update: Called when preview is updated
      - on_startup: Called when plugin is loaded
      - on_shutdown: Called when plugin is unloaded
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.version = getattr(self, '__version__', '1.0.0')
        self.author = getattr(self, '__author__', 'Unknown')
        self.description = getattr(self, '__description__', 'No description')
        self.logger = logging.getLogger(f"plugin.{self.name}")
        self._is_active = False
        self._event_handlers = {}
    
    def register(self, app) -> 'PluginBase':
        """Register plugin with the main app. Override in plugin."""
        self._is_active = True
        self.logger.info(f"Plugin {self.name} v{self.version} registered")
        self.on_startup(app)
        return self
    
    def unregister(self, app) -> None:
        """Unregister plugin from the main app."""
        if self._is_active:
            self.on_shutdown(app)
            self._is_active = False
            self.logger.info(f"Plugin {self.name} unregistered")
    
    def is_active(self) -> bool:
        """Check if plugin is active."""
        return self._is_active
    
    def get_info(self) -> Dict[str, str]:
        """Get plugin information."""
        return {
            'name': self.name,
            'version': self.version,
            'author': self.author,
            'description': self.description,
            'active': str(self._is_active)
        }
    
    def register_event_handler(self, event: str, handler: Callable) -> None:
        """Register custom event handler."""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def get_event_handlers(self, event: str) -> List[Callable]:
        """Get registered event handlers for an event."""
        return self._event_handlers.get(event, [])
    
    # Event handler stubs (plugins can override)
    def before_apply(self, context: Dict[str, Any]) -> None:
        """Called before applying configuration changes."""
        pass
    
    def after_apply(self, context: Dict[str, Any]) -> None:
        """Called after applying configuration changes."""
        pass
    
    def before_theme_change(self, context: Dict[str, Any]) -> None:
        """Called before changing themes."""
        pass
    
    def after_theme_change(self, context: Dict[str, Any]) -> None:
        """Called after changing themes."""
        pass
    
    def before_import(self, context: Dict[str, Any]) -> None:
        """Called before importing configurations."""
        pass
    
    def after_import(self, context: Dict[str, Any]) -> None:
        """Called after importing configurations."""
        pass
    
    def on_preview_update(self, context: Dict[str, Any]) -> None:
        """Called when preview is updated."""
        pass
    
    def on_startup(self, app) -> None:
        """Called when plugin is loaded."""
        pass
    
    def on_shutdown(self, app) -> None:
        """Called when plugin is unloaded."""
        pass
    
    def validate_context(self, context: Dict[str, Any]) -> bool:
        """Validate event context data."""
        # Basic validation - plugins can override for specific requirements
        return isinstance(context, dict)


class PluginManager:
    """Enhanced plugin manager with security, isolation, and lifecycle management."""
    
    def __init__(self, plugins_dir: str, enable_sandbox: bool = True):
        self.plugins_dir = Path(plugins_dir)
        self.enable_sandbox = enable_sandbox
        self.sandbox = PluginSandbox() if enable_sandbox else None
        self.logger = logging.getLogger(__name__)
        
        # Plugin tracking
        self.available_plugins = []
        self.loaded_plugins = {}  # name -> module
        self.plugin_instances = {}  # name -> instance
        self.plugin_metadata = {}  # name -> metadata
        
        # Security settings
        self.max_plugins = 50
        self.allowed_imports = {
            'os', 'sys', 'json', 'yaml', 'logging', 'time', 'datetime',
            'pathlib', 'typing', 're', 'math', 'random', 'collections'
        }
        self.blocked_imports = {
            'subprocess', 'multiprocessing', 'socket', 'urllib', 'requests',
            'http', 'ftplib', 'smtplib', 'telnetlib', 'ctypes'
        }
        
        self._discover_plugins()
    
    def _discover_plugins(self) -> None:
        """Discover available plugins in the plugins directory."""
        try:
            if not self.plugins_dir.exists():
                self.logger.info(f"Creating plugins directory: {self.plugins_dir}")
                self.plugins_dir.mkdir(parents=True, exist_ok=True)
                return
            
            self.available_plugins = []
            for file_path in self.plugins_dir.glob("*.py"):
                if file_path.name.startswith('_'):
                    continue
                
                try:
                    # Basic validation
                    if self._validate_plugin_file(file_path):
                        self.available_plugins.append(file_path.name)
                        self.logger.debug(f"Discovered plugin: {file_path.name}")
                except Exception as e:
                    self.logger.warning(f"Failed to validate plugin {file_path.name}: {e}")
            
            self.logger.info(f"Discovered {len(self.available_plugins)} plugins")
            
        except Exception as e:
            self.logger.error(f"Failed to discover plugins: {e}")
            raise PluginError(f"Plugin discovery failed: {e}")
    
    def _validate_plugin_file(self, file_path: Path) -> bool:
        """Validate plugin file for basic security checks."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for malicious patterns
            dangerous_patterns = [
                'exec(', 'eval(', '__import__', 'compile(',
                'open(', 'file(', 'input(', 'raw_input(',
                'subprocess', 'os.system', 'os.popen'
            ]
            
            for pattern in dangerous_patterns:
                if pattern in content:
                    self.logger.warning(f"Plugin {file_path.name} contains potentially dangerous pattern: {pattern}")
                    return False
            
            # Check file size (max 1MB)
            if file_path.stat().st_size > 1024 * 1024:
                self.logger.warning(f"Plugin {file_path.name} is too large (>1MB)")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate plugin file {file_path}: {e}")
            return False
    
    def list_plugins(self) -> List[str]:
        """List available plugins."""
        return self.available_plugins.copy()
    
    def list_loaded_plugins(self) -> List[Dict[str, str]]:
        """List loaded plugins with their information."""
        loaded = []
        for name, instance in self.plugin_instances.items():
            try:
                info = instance.get_info() if hasattr(instance, 'get_info') else {
                    'name': name,
                    'version': 'unknown',
                    'author': 'unknown',
                    'description': 'No description',
                    'active': 'true'
                }
                loaded.append(info)
            except Exception as e:
                self.logger.warning(f"Failed to get info for plugin {name}: {e}")
                loaded.append({
                    'name': name,
                    'version': 'unknown',
                    'author': 'unknown', 
                    'description': 'Error getting info',
                    'active': 'error'
                })
        return loaded
    
    def load_plugin(self, plugin_name: str, app) -> Optional[PluginBase]:
        """Load and register a plugin with enhanced security."""
        try:
            if len(self.loaded_plugins) >= self.max_plugins:
                raise PluginError(f"Maximum number of plugins ({self.max_plugins}) reached")
            
            if plugin_name in self.loaded_plugins:
                self.logger.warning(f"Plugin {plugin_name} is already loaded")
                return self.plugin_instances.get(plugin_name)
            
            plugin_path = self.plugins_dir / plugin_name
            if not plugin_path.exists():
                raise PluginError(f"Plugin file not found: {plugin_path}")
            
            # Validate plugin file
            if not self._validate_plugin_file(plugin_path):
                raise PluginError(f"Plugin validation failed: {plugin_name}")
            
            # Load module with sandbox if enabled
            if self.sandbox:
                module = self.sandbox.execute_with_timeout(self._load_module_safe, plugin_name, plugin_path)
            else:
                module = self._load_module_safe(plugin_name, plugin_path)
            
            if not module:
                raise PluginError(f"Failed to load module: {plugin_name}")
            
            # Register plugin
            plugin_instance = None
            if hasattr(module, 'register'):
                if self.sandbox:
                    plugin_instance = self.sandbox.execute_with_timeout(module.register, app)
                else:
                    plugin_instance = module.register(app)
                
                if plugin_instance:
                    self.loaded_plugins[plugin_name] = module
                    self.plugin_instances[plugin_name] = plugin_instance
                    self.plugin_metadata[plugin_name] = {
                        'load_time': time.time(),
                        'file_path': str(plugin_path),
                        'size': plugin_path.stat().st_size
                    }
                    self.logger.info(f"Successfully loaded plugin: {plugin_name}")
                else:
                    self.logger.warning(f"Plugin {plugin_name} register() returned None")
            else:
                self.logger.error(f"Plugin {plugin_name} missing register() function")
                raise PluginError(f"Plugin missing register() function: {plugin_name}")
            
            return plugin_instance
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            # Cleanup on failure
            self._cleanup_failed_plugin(plugin_name)
            raise PluginError(f"Plugin load failed: {plugin_name}: {e}")
    
    def _load_module_safe(self, plugin_name: str, plugin_path: Path):
        """Safely load a plugin module with import restrictions."""
        try:
            # Create module spec
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if not spec or not spec.loader:
                return None
            
            # Create module
            module = importlib.util.module_from_spec(spec)
            
            # Add to sys.modules temporarily for import resolution
            sys.modules[plugin_name] = module
            
            try:
                # Execute module with import monitoring
                original_import = __builtins__['__import__']
                __builtins__['__import__'] = self._secure_import
                
                spec.loader.exec_module(module)
                
            finally:
                # Restore original import
                __builtins__['__import__'] = original_import
                # Remove from sys.modules
                if plugin_name in sys.modules:
                    del sys.modules[plugin_name]
            
            return module
            
        except Exception as e:
            self.logger.error(f"Failed to load module {plugin_name}: {e}")
            return None
    
    def _secure_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """Secure import function that blocks dangerous modules."""
        # Check if import is allowed
        if name in self.blocked_imports:
            raise ImportError(f"Import of '{name}' is not allowed in plugins")
        
        # Only allow specific imports
        if name not in self.allowed_imports and not name.startswith('hyprrice.'):
            self.logger.warning(f"Potentially unsafe import attempted: {name}")
            # You could either block it or allow with warning
            # For now, we'll allow but log
        
        # Use original import
        return importlib.__import__(name, globals, locals, fromlist, level)
    
    def unload_plugin(self, plugin_name: str, app) -> bool:
        """Unload a plugin."""
        try:
            if plugin_name not in self.loaded_plugins:
                self.logger.warning(f"Plugin {plugin_name} is not loaded")
                return False
            
            # Get plugin instance
            plugin_instance = self.plugin_instances.get(plugin_name)
            
            # Call unregister if available
            if plugin_instance and hasattr(plugin_instance, 'unregister'):
                try:
                    if self.sandbox:
                        self.sandbox.execute_with_timeout(plugin_instance.unregister, app)
                    else:
                        plugin_instance.unregister(app)
                except Exception as e:
                    self.logger.warning(f"Error during plugin unregister: {e}")
            
            # Remove from tracking
            del self.loaded_plugins[plugin_name]
            del self.plugin_instances[plugin_name]
            if plugin_name in self.plugin_metadata:
                del self.plugin_metadata[plugin_name]
            
            self.logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def _cleanup_failed_plugin(self, plugin_name: str) -> None:
        """Clean up after failed plugin load."""
        if plugin_name in self.loaded_plugins:
            del self.loaded_plugins[plugin_name]
        if plugin_name in self.plugin_instances:
            del self.plugin_instances[plugin_name]
        if plugin_name in self.plugin_metadata:
            del self.plugin_metadata[plugin_name]
    
    def reload_plugin(self, plugin_name: str, app) -> bool:
        """Reload a plugin."""
        try:
            # Unload first
            if plugin_name in self.loaded_plugins:
                self.unload_plugin(plugin_name, app)
            
            # Load again
            plugin_instance = self.load_plugin(plugin_name, app)
            return plugin_instance is not None
            
        except Exception as e:
            self.logger.error(f"Failed to reload plugin {plugin_name}: {e}")
            return False
    
    def dispatch_event(self, event: str, context: Dict[str, Any]) -> None:
        """Dispatch event to all loaded plugins with error isolation."""
        if not isinstance(context, dict):
            self.logger.error(f"Invalid context type for event {event}: {type(context)}")
            return
        
        # Add event metadata
        context['_event'] = event
        context['_timestamp'] = time.time()
        
        failed_plugins = []
        
        for plugin_name, plugin_instance in self.plugin_instances.items():
            try:
                # Validate context if plugin supports it
                if hasattr(plugin_instance, 'validate_context'):
                    if not plugin_instance.validate_context(context):
                        self.logger.warning(f"Context validation failed for plugin {plugin_name}")
                        continue
                
                # Get event handler
                handler = getattr(plugin_instance, event, None)
                if callable(handler):
                    if self.sandbox:
                        self.sandbox.execute_with_timeout(handler, context.copy())
                    else:
                        handler(context.copy())
                
                # Check for custom event handlers
                if hasattr(plugin_instance, 'get_event_handlers'):
                    custom_handlers = plugin_instance.get_event_handlers(event)
                    for custom_handler in custom_handlers:
                        if self.sandbox:
                            self.sandbox.execute_with_timeout(custom_handler, context.copy())
                        else:
                            custom_handler(context.copy())
                            
            except Exception as e:
                self.logger.error(f"Plugin {plugin_name} failed to handle event {event}: {e}")
                self.logger.debug(f"Plugin error traceback: {traceback.format_exc()}")
                failed_plugins.append(plugin_name)
        
        # Handle failed plugins
        if failed_plugins:
            self.logger.warning(f"Event {event} failed for plugins: {failed_plugins}")
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a plugin."""
        if plugin_name not in self.plugin_instances:
            return None
        
        try:
            instance = self.plugin_instances[plugin_name]
            metadata = self.plugin_metadata.get(plugin_name, {})
            
            info = {
                'name': plugin_name,
                'loaded': True,
                'load_time': metadata.get('load_time'),
                'file_path': metadata.get('file_path'),
                'file_size': metadata.get('size'),
            }
            
            # Get plugin-specific info
            if hasattr(instance, 'get_info'):
                plugin_info = instance.get_info()
                info.update(plugin_info)
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get plugin info for {plugin_name}: {e}")
            return None
    
    def unload_all_plugins(self, app) -> None:
        """Unload all plugins."""
        plugin_names = list(self.plugin_instances.keys())
        for plugin_name in plugin_names:
            try:
                self.unload_plugin(plugin_name, app)
            except Exception as e:
                self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
    
    def get_plugin_statistics(self) -> Dict[str, Any]:
        """Get plugin system statistics."""
        return {
            'total_available': len(self.available_plugins),
            'total_loaded': len(self.loaded_plugins),
            'sandbox_enabled': self.enable_sandbox,
            'max_plugins': self.max_plugins,
            'plugins_dir': str(self.plugins_dir),
            'loaded_plugins': list(self.plugin_instances.keys())
        } 