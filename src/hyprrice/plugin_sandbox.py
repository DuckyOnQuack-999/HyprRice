"""
Plugin Sandboxing System for HyprRice

Provides secure execution environment for plugins with restricted access
to system resources and APIs.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Set
import logging
import threading
import time
from contextlib import contextmanager
import resource

from .exceptions import SecurityError, PluginError
from .security import input_validator


class SandboxLimits:
    """Resource limits for sandboxed plugins."""
    
    def __init__(self):
        # Memory limit (in bytes) - 100MB
        self.memory_limit = 100 * 1024 * 1024
        
        # CPU time limit (in seconds) - 30 seconds
        self.cpu_time_limit = 30
        
        # File descriptor limit
        self.fd_limit = 50
        
        # Maximum file size (in bytes) - 10MB
        self.file_size_limit = 10 * 1024 * 1024
        
        # Network operations allowed
        self.allow_network = False
        
        # Filesystem write operations allowed
        self.allow_file_write = True
        
        # System command execution allowed
        self.allow_subprocess = False
        
        # Allowed modules for import
        self.allowed_modules = {
            'os', 'sys', 'json', 'yaml', 'pathlib', 'logging', 'time', 'datetime',
            'collections', 're', 'math', 'random', 'hashlib', 'base64', 'uuid',
            'dataclasses', 'typing', 'functools', 'itertools'
        }
        
        # Blocked modules
        self.blocked_modules = {
            'subprocess', 'multiprocessing', 'threading', 'socket', 'urllib',
            'http', 'ftplib', 'telnetlib', 'smtplib', 'poplib', 'imaplib',
            'ctypes', 'gc', 'importlib', '__builtin__', 'builtins'
        }


class SandboxedImporter:
    """Custom importer that restricts module imports."""
    
    def __init__(self, limits: SandboxLimits):
        self.limits = limits
        self.logger = logging.getLogger(__name__)
        self.original_import = __builtins__['__import__']
        
    def __call__(self, name, globals=None, locals=None, fromlist=(), level=0):
        """Override import function with restrictions."""
        # Check if module is explicitly blocked
        if name in self.limits.blocked_modules:
            raise ImportError(f"Module '{name}' is not allowed in sandbox")
        
        # Check if module is in allowed list (for strict mode)
        if hasattr(self.limits, 'strict_mode') and self.limits.strict_mode:
            if name not in self.limits.allowed_modules:
                raise ImportError(f"Module '{name}' is not in allowed modules list")
        
        # Log import attempt
        self.logger.debug(f"Plugin importing module: {name}")
        
        # Call original import
        return self.original_import(name, globals, locals, fromlist, level)


class FileSystemGuard:
    """Guards filesystem operations for sandboxed plugins."""
    
    def __init__(self, limits: SandboxLimits, allowed_paths: Set[Path]):
        self.limits = limits
        self.allowed_paths = allowed_paths
        self.logger = logging.getLogger(__name__)
        
    def check_path_access(self, path: Path, operation: str) -> bool:
        """Check if path access is allowed."""
        try:
            resolved_path = path.resolve()
            
            # Check if path is within allowed directories
            for allowed_path in self.allowed_paths:
                try:
                    resolved_path.relative_to(allowed_path)
                    return True
                except ValueError:
                    continue
            
            self.logger.warning(f"Plugin attempted {operation} on restricted path: {path}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking path access: {e}")
            return False
    
    def safe_open(self, original_open):
        """Wrapper for open() function with path restrictions."""
        def wrapped_open(file, mode='r', *args, **kwargs):
            path = Path(file)
            
            # Check write operations
            if any(m in mode for m in ['w', 'a', 'x']) and not self.limits.allow_file_write:
                raise PermissionError("File write operations not allowed in sandbox")
            
            # Check path access
            if not self.check_path_access(path, f"open (mode: {mode})"):
                raise PermissionError(f"Access denied to path: {path}")
            
            return original_open(file, mode, *args, **kwargs)
        
        return wrapped_open


class PluginSandbox:
    """Secure execution environment for plugins."""
    
    def __init__(self, plugin_path: Path, limits: SandboxLimits = None):
        self.plugin_path = plugin_path
        self.limits = limits or SandboxLimits()
        self.logger = logging.getLogger(__name__)
        
        # Sandbox state
        self.is_active = False
        self.original_builtins = {}
        self.temp_dir = None
        self.allowed_paths = set()
        
        # Thread safety
        self.lock = threading.Lock()
        
        self._setup_allowed_paths()
    
    def _setup_allowed_paths(self):
        """Setup allowed filesystem paths for the plugin."""
        # Plugin's own directory
        self.allowed_paths.add(self.plugin_path.parent)
        
        # Temporary directory (will be created)
        # Standard config directories
        home = Path.home()
        config_dirs = [
            home / '.config' / 'hyprrice',
            home / '.hyprrice',
            home / '.config' / 'hypr',
            home / '.config' / 'waybar',
            home / '.config' / 'rofi'
        ]
        
        for config_dir in config_dirs:
            if config_dir.exists():
                self.allowed_paths.add(config_dir)
    
    @contextmanager
    def activate(self):
        """Context manager to activate sandbox."""
        with self.lock:
            if self.is_active:
                raise RuntimeError("Sandbox is already active")
            
            self.logger.info(f"Activating sandbox for plugin: {self.plugin_path}")
            
            try:
                self._enter_sandbox()
                self.is_active = True
                yield self
            finally:
                self._exit_sandbox()
                self.is_active = False
    
    def _enter_sandbox(self):
        """Enter the sandbox environment."""
        # Set resource limits
        self._set_resource_limits()
        
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix='hyprrice_plugin_'))
        self.allowed_paths.add(self.temp_dir)
        
        # Setup import restrictions
        self._setup_import_restrictions()
        
        # Setup filesystem guards
        self._setup_filesystem_guards()
        
        # Restrict dangerous builtins
        self._restrict_builtins()
    
    def _exit_sandbox(self):
        """Exit the sandbox environment."""
        # Restore original builtins
        self._restore_builtins()
        
        # Cleanup temporary directory
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                self.logger.warning(f"Failed to cleanup temp dir: {e}")
        
        self.logger.info("Sandbox deactivated")
    
    def _set_resource_limits(self):
        """Set system resource limits."""
        try:
            # Memory limit
            resource.setrlimit(resource.RLIMIT_AS, (self.limits.memory_limit, self.limits.memory_limit))
            
            # CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (self.limits.cpu_time_limit, self.limits.cpu_time_limit))
            
            # File descriptor limit
            resource.setrlimit(resource.RLIMIT_NOFILE, (self.limits.fd_limit, self.limits.fd_limit))
            
            # File size limit
            resource.setrlimit(resource.RLIMIT_FSIZE, (self.limits.file_size_limit, self.limits.file_size_limit))
            
        except Exception as e:
            self.logger.warning(f"Failed to set resource limits: {e}")
    
    def _setup_import_restrictions(self):
        """Setup import restrictions."""
        # Store original import
        self.original_builtins['__import__'] = __builtins__['__import__']
        
        # Install custom importer
        sandboxed_importer = SandboxedImporter(self.limits)
        __builtins__['__import__'] = sandboxed_importer
    
    def _setup_filesystem_guards(self):
        """Setup filesystem access guards."""
        fs_guard = FileSystemGuard(self.limits, self.allowed_paths)
        
        # Store original open
        self.original_builtins['open'] = __builtins__['open']
        
        # Install guarded open
        __builtins__['open'] = fs_guard.safe_open(__builtins__['open'])
    
    def _restrict_builtins(self):
        """Restrict access to dangerous builtin functions."""
        dangerous_builtins = ['exec', 'eval', 'compile', '__import__']
        
        if not self.limits.allow_subprocess:
            dangerous_builtins.extend(['subprocess', 'os.system', 'os.popen'])
        
        for builtin_name in dangerous_builtins:
            if builtin_name in __builtins__:
                self.original_builtins[builtin_name] = __builtins__[builtin_name]
                
                # Replace with restricted version
                if builtin_name in ['exec', 'eval']:
                    __builtins__[builtin_name] = self._create_restricted_exec(builtin_name)
                elif builtin_name == 'compile':
                    __builtins__[builtin_name] = self._restricted_compile
    
    def _create_restricted_exec(self, func_name: str):
        """Create restricted version of exec/eval."""
        def restricted_func(*args, **kwargs):
            raise SecurityError(f"{func_name}() is not allowed in sandbox")
        return restricted_func
    
    def _restricted_compile(self, *args, **kwargs):
        """Restricted version of compile()."""
        raise SecurityError("compile() is not allowed in sandbox")
    
    def _restore_builtins(self):
        """Restore original builtin functions."""
        for name, func in self.original_builtins.items():
            __builtins__[name] = func
        self.original_builtins.clear()
    
    def load_plugin_module(self, module_name: str):
        """Load plugin module within sandbox."""
        if not self.is_active:
            raise RuntimeError("Sandbox must be active to load plugins")
        
        try:
            # Construct module path
            module_file = self.plugin_path / f"{module_name}.py"
            
            if not module_file.exists():
                raise PluginError(f"Plugin module not found: {module_file}")
            
            # Validate file size
            input_validator.validate_file_size(module_file)
            
            # Load module spec
            spec = importlib.util.spec_from_file_location(module_name, module_file)
            if spec is None:
                raise PluginError(f"Could not load spec for module: {module_name}")
            
            # Create module
            module = importlib.util.module_from_spec(spec)
            
            # Execute module in sandbox
            spec.loader.exec_module(module)
            
            return module
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin module {module_name}: {e}")
            raise PluginError(f"Plugin loading failed: {e}")


class SecurePluginManager:
    """Plugin manager with sandboxing support."""
    
    def __init__(self, plugins_dir: Path):
        self.plugins_dir = Path(plugins_dir)
        self.logger = logging.getLogger(__name__)
        self.loaded_plugins = {}
        self.sandboxes = {}
    
    def load_plugin_secure(self, plugin_name: str, limits: SandboxLimits = None) -> Any:
        """Load plugin in secure sandbox."""
        try:
            plugin_path = self.plugins_dir / plugin_name
            
            if not plugin_path.exists():
                raise PluginError(f"Plugin directory not found: {plugin_path}")
            
            # Create sandbox
            sandbox = PluginSandbox(plugin_path, limits)
            
            # Load plugin in sandbox
            with sandbox.activate():
                plugin_module = sandbox.load_plugin_module(plugin_name)
                
                # Get plugin class
                if hasattr(plugin_module, 'plugin_class'):
                    plugin_class = plugin_module.plugin_class
                    plugin_instance = plugin_class()
                    
                    # Store plugin and sandbox
                    self.loaded_plugins[plugin_name] = plugin_instance
                    self.sandboxes[plugin_name] = sandbox
                    
                    self.logger.info(f"Successfully loaded plugin: {plugin_name}")
                    return plugin_instance
                else:
                    raise PluginError(f"Plugin {plugin_name} does not define plugin_class")
                    
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            raise
    
    def unload_plugin(self, plugin_name: str):
        """Unload plugin and cleanup sandbox."""
        if plugin_name in self.loaded_plugins:
            del self.loaded_plugins[plugin_name]
        
        if plugin_name in self.sandboxes:
            # Sandbox cleanup is handled by context manager
            del self.sandboxes[plugin_name]
        
        self.logger.info(f"Unloaded plugin: {plugin_name}")
    
    def execute_plugin_method(self, plugin_name: str, method_name: str, *args, **kwargs):
        """Execute plugin method in sandbox."""
        if plugin_name not in self.loaded_plugins:
            raise PluginError(f"Plugin not loaded: {plugin_name}")
        
        plugin = self.loaded_plugins[plugin_name]
        sandbox = self.sandboxes.get(plugin_name)
        
        if not hasattr(plugin, method_name):
            raise PluginError(f"Plugin {plugin_name} has no method {method_name}")
        
        try:
            if sandbox:
                with sandbox.activate():
                    method = getattr(plugin, method_name)
                    return method(*args, **kwargs)
            else:
                # Fallback to direct execution (less secure)
                method = getattr(plugin, method_name)
                return method(*args, **kwargs)
                
        except Exception as e:
            self.logger.error(f"Error executing {plugin_name}.{method_name}: {e}")
            raise PluginError(f"Plugin method execution failed: {e}")


# Factory function for creating sandboxes with different security levels
def create_sandbox(security_level: str = 'medium') -> SandboxLimits:
    """Create sandbox with predefined security levels."""
    limits = SandboxLimits()
    
    if security_level == 'strict':
        limits.memory_limit = 50 * 1024 * 1024  # 50MB
        limits.cpu_time_limit = 10  # 10 seconds
        limits.fd_limit = 20
        limits.allow_network = False
        limits.allow_file_write = False
        limits.allow_subprocess = False
        limits.strict_mode = True
        
    elif security_level == 'medium':
        limits.memory_limit = 100 * 1024 * 1024  # 100MB
        limits.cpu_time_limit = 30  # 30 seconds
        limits.fd_limit = 50
        limits.allow_network = False
        limits.allow_file_write = True
        limits.allow_subprocess = False
        
    elif security_level == 'relaxed':
        limits.memory_limit = 200 * 1024 * 1024  # 200MB
        limits.cpu_time_limit = 60  # 60 seconds
        limits.fd_limit = 100
        limits.allow_network = True
        limits.allow_file_write = True
        limits.allow_subprocess = True
        
    return limits
