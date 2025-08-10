"""
DuckyCoder v4 Enhanced Security Module for HyprRice
Implements comprehensive security measures for command execution and plugin management.
"""

import os
import ast
import shlex
import hashlib
import logging
from typing import List, Dict, Any, Union, Optional
from pathlib import Path
from dataclasses import dataclass, field

from .exceptions import HyprRiceError


class SecurityError(HyprRiceError):
    """Security-related error."""
    pass


@dataclass
class SecurityConfig:
    """Security-specific configuration."""
    plugin_validation: bool = True
    allowed_commands: List[str] = field(default_factory=lambda: [
        'monitors', 'workspaces', 'clients', 'devices', 'layers',
        'version', 'reload', 'kill', 'dispatch', 'keyword'
    ])
    log_security_events: bool = True
    max_plugin_size: int = 1024 * 1024  # 1MB
    plugin_timeout: int = 30  # seconds
    allowed_config_dirs: List[str] = field(default_factory=lambda: [
        str(Path.home() / ".config"),
        str(Path.home() / ".hyprrice"),
    ])


class SecurityLogger:
    """Enhanced security logging utility."""
    
    def __init__(self):
        self.logger = logging.getLogger('hyprrice.security')
        
    def log_plugin_load(self, plugin_name: str, success: bool, reason: str = ""):
        """Log plugin loading events."""
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, f"Plugin {plugin_name} {'loaded' if success else 'failed'}: {reason}")
    
    def log_command_execution(self, command: str, user_initiated: bool = True):
        """Log command execution for audit trail."""
        self.logger.info(f"Command executed: {command} (user_initiated: {user_initiated})")
    
    def log_security_violation(self, violation_type: str, details: str):
        """Log security violations."""
        self.logger.error(f"SECURITY VIOLATION - {violation_type}: {details}")
    
    def log_file_access(self, file_path: str, operation: str, success: bool):
        """Log file access attempts."""
        status = "SUCCESS" if success else "DENIED"
        self.logger.info(f"File access {status}: {operation} on {file_path}")


class SecureCommandValidator:
    """Validates and sanitizes command execution."""
    
    def __init__(self, security_config: SecurityConfig):
        self.security_config = security_config
        self.security_logger = SecurityLogger()
    
    def validate_hyprctl_command(self, command: Union[str, List[str]]) -> List[str]:
        """
        Validate and sanitize hyprctl commands.
        
        Args:
            command: Command string or list to validate
            
        Returns:
            List of validated command parts
            
        Raises:
            SecurityError: If command is not allowed
        """
        if isinstance(command, str):
            # Sanitize and split command properly
            try:
                safe_command = shlex.split(command)
            except ValueError as e:
                self.security_logger.log_security_violation(
                    "COMMAND_PARSE_ERROR", 
                    f"Failed to parse command: {command}, error: {e}"
                )
                raise SecurityError(f"Invalid command syntax: {e}")
        elif isinstance(command, list):
            safe_command = command[:]
        else:
            raise SecurityError("Command must be string or list")
        
        if not safe_command:
            raise SecurityError("Empty command not allowed")
        
        # Validate against whitelist of allowed hyprctl commands
        base_command = safe_command[0]
        if base_command not in self.security_config.allowed_commands:
            self.security_logger.log_security_violation(
                "UNAUTHORIZED_COMMAND", 
                f"Command '{base_command}' not in allowed list: {self.security_config.allowed_commands}"
            )
            raise SecurityError(f"Command '{base_command}' not allowed")
        
        # Additional validation for specific commands
        if base_command == 'dispatch' and len(safe_command) > 1:
            # Validate dispatch subcommands
            dispatch_command = safe_command[1]
            allowed_dispatch = ['workspace', 'movetoworkspace', 'togglefloating', 'fullscreen']
            if dispatch_command not in allowed_dispatch:
                raise SecurityError(f"Dispatch command '{dispatch_command}' not allowed")
        
        self.security_logger.log_command_execution(' '.join(safe_command), user_initiated=True)
        return safe_command


class SecurePluginValidator:
    """Validates plugin code for security threats."""
    
    def __init__(self, security_config: SecurityConfig):
        self.security_config = security_config
        self.security_logger = SecurityLogger()
        
        # Define dangerous functions and modules
        self.dangerous_funcs = {
            'eval', 'exec', 'compile', '__import__', 'open', 'input'
        }
        self.dangerous_modules = {
            'os.system', 'subprocess.call', 'subprocess.run', 'subprocess.Popen',
            'socket', 'urllib', 'requests', 'shutil.rmtree'
        }
        self.dangerous_attrs = {
            '__subclasses__', '__globals__', '__builtins__'
        }
    
    def validate_plugin_code(self, plugin_path: str, allowed_hash: Optional[str] = None) -> bool:
        """
        Validate plugin code for security threats.
        
        Args:
            plugin_path: Path to plugin file
            allowed_hash: Expected SHA256 hash of the plugin (optional)
            
        Returns:
            True if plugin is safe, False otherwise
        """
        try:
            plugin_path_obj = Path(plugin_path)
            
            # Check file size
            if plugin_path_obj.stat().st_size > self.security_config.max_plugin_size:
                self.security_logger.log_security_violation(
                    "PLUGIN_SIZE_EXCEEDED",
                    f"Plugin {plugin_path} exceeds max size limit"
                )
                return False
            
            # Read and parse plugin code
            with open(plugin_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Verify plugin hash if provided
            if allowed_hash:
                file_hash = hashlib.sha256(code.encode()).hexdigest()
                if file_hash != allowed_hash:
                    self.security_logger.log_security_violation(
                        "PLUGIN_HASH_MISMATCH",
                        f"Plugin {plugin_path} hash mismatch. Expected: {allowed_hash}, Got: {file_hash}"
                    )
                    return False
            
            # Parse AST to check for dangerous operations
            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                self.security_logger.log_security_violation(
                    "PLUGIN_SYNTAX_ERROR",
                    f"Plugin {plugin_path} has syntax errors: {e}"
                )
                return False
            
            # Walk through AST nodes to detect dangerous patterns
            for node in ast.walk(tree):
                # Check for dangerous function calls
                if isinstance(node, ast.Call):
                    if hasattr(node.func, 'id') and node.func.id in self.dangerous_funcs:
                        self.security_logger.log_security_violation(
                            "DANGEROUS_FUNCTION",
                            f"Plugin {plugin_path} uses dangerous function: {node.func.id}"
                        )
                        return False
                
                # Check for dangerous imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.dangerous_modules:
                            self.security_logger.log_security_violation(
                                "DANGEROUS_IMPORT",
                                f"Plugin {plugin_path} imports dangerous module: {alias.name}"
                            )
                            return False
                
                # Check for dangerous attribute access
                if isinstance(node, ast.Attribute):
                    if node.attr in self.dangerous_attrs:
                        self.security_logger.log_security_violation(
                            "DANGEROUS_ATTRIBUTE",
                            f"Plugin {plugin_path} accesses dangerous attribute: {node.attr}"
                        )
                        return False
                
                # Check for dynamic code execution
                if isinstance(node, ast.Call) and hasattr(node.func, 'attr'):
                    if node.func.attr in {'exec', 'eval'}:
                        self.security_logger.log_security_violation(
                            "DYNAMIC_CODE_EXECUTION",
                            f"Plugin {plugin_path} attempts dynamic code execution"
                        )
                        return False
            
            return True
            
        except Exception as e:
            self.security_logger.log_security_violation(
                "PLUGIN_VALIDATION_ERROR",
                f"Error validating plugin {plugin_path}: {e}"
            )
            return False


class SecureFileManager:
    """Manages secure file operations with path validation."""
    
    def __init__(self, security_config: SecurityConfig):
        self.security_config = security_config
        self.security_logger = SecurityLogger()
    
    def validate_file_path(self, file_path: str, operation: str = "read") -> Path:
        """
        Validate file path for security threats.
        
        Args:
            file_path: Path to validate
            operation: Type of operation (read, write, backup)
            
        Returns:
            Validated Path object
            
        Raises:
            SecurityError: If path is not allowed
        """
        try:
            # Resolve to absolute path to prevent traversal attacks
            file_path_obj = Path(file_path).resolve()
            
            # Check if path is within allowed directories
            allowed = False
            for allowed_dir in self.security_config.allowed_config_dirs:
                try:
                    file_path_obj.relative_to(Path(allowed_dir).resolve())
                    allowed = True
                    break
                except ValueError:
                    continue
            
            if not allowed:
                self.security_logger.log_security_violation(
                    "PATH_TRAVERSAL_ATTEMPT",
                    f"File {file_path_obj} is outside allowed directories"
                )
                raise SecurityError(f"File {file_path_obj} is outside allowed directories")
            
            self.security_logger.log_file_access(str(file_path_obj), operation, True)
            return file_path_obj
            
        except Exception as e:
            self.security_logger.log_file_access(str(file_path), operation, False)
            raise SecurityError(f"Path validation failed for {file_path}: {e}")
    
    def secure_backup_file(self, file_path: str, backup_dir: str) -> str:
        """
        Create a secure backup of a file with path validation.
        
        Args:
            file_path: Source file path
            backup_dir: Backup directory path
            
        Returns:
            Path to backup file
            
        Raises:
            SecurityError: If paths are not allowed
        """
        # Validate source file path
        validated_file_path = self.validate_file_path(file_path, "backup_source")
        validated_backup_dir = self.validate_file_path(backup_dir, "backup_dest")
        
        if not validated_file_path.exists():
            raise FileNotFoundError(f"File not found: {validated_file_path}")
        
        # Create backup directory if it doesn't exist
        validated_backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate secure backup filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_name = f"{timestamp}_{validated_file_path.name}"
        backup_path = validated_backup_dir / backup_name
        
        # Copy file securely
        import shutil
        shutil.copy2(validated_file_path, backup_path)
        
        self.security_logger.log_file_access(str(backup_path), "backup_created", True)
        return str(backup_path)


# Convenience function for secure hyprctl execution
def secure_hyprctl(command: Union[str, List[str]], security_config: SecurityConfig) -> List[str]:
    """
    Secure wrapper for hyprctl command validation.
    
    Args:
        command: Command to validate
        security_config: Security configuration
        
    Returns:
        Validated command parts
    """
    validator = SecureCommandValidator(security_config)
    return validator.validate_hyprctl_command(command)