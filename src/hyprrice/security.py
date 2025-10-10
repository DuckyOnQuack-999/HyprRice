"""
Security utilities for HyprRice

Provides input validation, sanitization, and security checks to prevent
common vulnerabilities like path traversal, command injection, etc.
"""

import os
import re
import shutil
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml
import json
from .exceptions import ValidationError, FileError, SecurityError


class InputValidator:
    """Validates and sanitizes user inputs."""
    
    # Safe characters for different contexts
    SAFE_FILENAME_CHARS = re.compile(r'^[a-zA-Z0-9._-]+$')
    SAFE_PATH_CHARS = re.compile(r'^[a-zA-Z0-9._/-]+$')
    SAFE_COLOR_HEX = re.compile(r'^#[0-9A-Fa-f]{6}$')
    SAFE_THEME_NAME = re.compile(r'^[a-zA-Z0-9._\s-]+$')
    
    # Maximum lengths
    MAX_FILENAME_LENGTH = 255
    MAX_PATH_LENGTH = 4096
    MAX_THEME_NAME_LENGTH = 100
    MAX_CONFIG_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_filename(self, filename: str) -> str:
        """
        Validate and sanitize filename.
        
        Args:
            filename: The filename to validate
            
        Returns:
            Sanitized filename
            
        Raises:
            ValidationError: If filename is invalid
        """
        if not filename or not filename.strip():
            raise ValidationError("Filename cannot be empty")
        
        filename = filename.strip()
        
        if len(filename) > self.MAX_FILENAME_LENGTH:
            raise ValidationError(f"Filename too long (max {self.MAX_FILENAME_LENGTH} chars)")
        
        # Check for dangerous patterns
        dangerous_patterns = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for pattern in dangerous_patterns:
            if pattern in filename:
                raise ValidationError(f"Filename contains illegal character: {pattern}")
        
        if not self.SAFE_FILENAME_CHARS.match(filename):
            raise ValidationError("Filename contains invalid characters")
        
        return filename
    
    def is_valid_filename(self, filename: str) -> bool:
        """
        Check if filename is valid without raising exceptions.
        
        Args:
            filename: The filename to check
            
        Returns:
            True if filename is valid, False otherwise
        """
        try:
            self.validate_filename(filename)
            return True
        except ValidationError:
            return False
    
    def validate_path(self, path: Union[str, Path], base_dir: Optional[Path] = None) -> Path:
        """
        Validate file path to prevent path traversal attacks.
        
        Args:
            path: Path to validate
            base_dir: Base directory to restrict path within
            
        Returns:
            Validated and resolved path
            
        Raises:
            SecurityError: If path is potentially dangerous
        """
        if not path:
            raise ValidationError("Path cannot be empty")
        
        path = Path(path).resolve()
        
        # Check path length
        if len(str(path)) > self.MAX_PATH_LENGTH:
            raise ValidationError(f"Path too long (max {self.MAX_PATH_LENGTH} chars)")
        
        # Check for path traversal
        if '..' in path.parts:
            raise SecurityError("Path traversal detected")
        
        # If base directory specified, ensure path is within it
        if base_dir:
            base_dir = Path(base_dir).resolve()
            try:
                path.relative_to(base_dir)
            except ValueError:
                raise SecurityError(f"Path outside allowed directory: {base_dir}")
        
        return path
    
    def validate_color(self, color: str) -> str:
        """
        Validate color hex code.
        
        Args:
            color: Color hex code to validate
            
        Returns:
            Validated color code
            
        Raises:
            ValidationError: If color format is invalid
        """
        if not color or not color.strip():
            raise ValidationError("Color cannot be empty")
        
        color = color.strip().upper()
        
        if not self.SAFE_COLOR_HEX.match(color):
            raise ValidationError("Invalid color format. Expected #RRGGBB")
        
        return color
    
    def validate_theme_name(self, name: str) -> str:
        """
        Validate theme name.
        
        Args:
            name: Theme name to validate
            
        Returns:
            Validated theme name
            
        Raises:
            ValidationError: If theme name is invalid
        """
        if not name or not name.strip():
            raise ValidationError("Theme name cannot be empty")
        
        name = name.strip()
        
        if len(name) > self.MAX_THEME_NAME_LENGTH:
            raise ValidationError(f"Theme name too long (max {self.MAX_THEME_NAME_LENGTH} chars)")
        
        if not self.SAFE_THEME_NAME.match(name):
            raise ValidationError("Theme name contains invalid characters")
        
        return name
    
    def validate_file_extension(self, file_path: Path, allowed_extensions: List[str]) -> bool:
        """
        Validate file extension.
        
        Args:
            file_path: Path to file
            allowed_extensions: List of allowed extensions (e.g., ['.yaml', '.yml'])
            
        Returns:
            True if file extension is valid
            
        Raises:
            ValidationError: If file extension is invalid
        """
        if not file_path.exists():
            raise FileError(f"File does not exist: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise ValidationError(f"Invalid file extension: {file_extension}. Expected: {allowed_extensions}")
        
        return True
    
    def validate_file_size(self, file_path: Path, max_size: int = None) -> bool:
        """
        Validate file size.
        
        Args:
            file_path: Path to file
            max_size: Maximum allowed size in bytes
            
        Returns:
            True if file size is valid
            
        Raises:
            ValidationError: If file is too large
        """
        if not file_path.exists():
            raise FileError(f"File does not exist: {file_path}")
        
        max_size = max_size or self.MAX_CONFIG_SIZE
        file_size = file_path.stat().st_size
        
        if file_size > max_size:
            raise ValidationError(f"File too large: {file_size} bytes (max {max_size})")
        
        return True


class ConfigSanitizer:
    """Sanitizes configuration data."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = InputValidator()
    
    def sanitize_config(self, data: Any) -> Any:
        """
        Sanitize configuration data (alias for sanitize_yaml_data).
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data
        """
        return self.sanitize_yaml_data(data)
    
    def sanitize_yaml_data(self, data: Any) -> Any:
        """
        Recursively sanitize YAML data.
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data
        """
        if isinstance(data, dict):
            return {self._sanitize_key(k): self.sanitize_yaml_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_yaml_data(item) for item in data]
        elif isinstance(data, str):
            return self._sanitize_string(data)
        else:
            return data
    
    def _sanitize_key(self, key: str) -> str:
        """Sanitize dictionary key."""
        if not isinstance(key, str):
            return str(key)
        
        # Remove dangerous characters from keys
        key = re.sub(r'[^\w._-]', '_', key)
        return key[:100]  # Limit key length
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize string value."""
        if not isinstance(value, str):
            return str(value)
        
        # Remove null bytes and control characters
        value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', value)
        
        # Limit string length
        if len(value) > 10000:
            value = value[:10000]
            
        return value
    
    def validate_theme_schema(self, theme_data: Dict[str, Any]) -> List[str]:
        """
        Validate theme data against expected schema.
        
        Args:
            theme_data: Theme data to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Required fields
        required_fields = ['name', 'version']
        for field in required_fields:
            if field not in theme_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate theme name
        if 'name' in theme_data:
            try:
                self.validator.validate_theme_name(theme_data['name'])
            except ValidationError as e:
                errors.append(f"Invalid theme name: {e}")
        
        # Validate version format
        if 'version' in theme_data:
            version = theme_data['version']
            if not isinstance(version, str) or not re.match(r'^\d+\.\d+\.\d+$', version):
                errors.append("Invalid version format. Expected: X.Y.Z")
        
        # Validate colors section
        if 'colors' in theme_data:
            colors_errors = self._validate_colors_section(theme_data['colors'])
            errors.extend(colors_errors)
        
        return errors
    
    def _validate_colors_section(self, colors: Dict[str, Any]) -> List[str]:
        """Validate colors section of theme."""
        errors = []
        
        if not isinstance(colors, dict):
            return ["Colors section must be a dictionary"]
        
        for key, value in colors.items():
            if isinstance(value, str):
                try:
                    self.validator.validate_color(value)
                except ValidationError as e:
                    errors.append(f"Invalid color '{key}': {e}")
        
        return errors


class SecureFileHandler:
    """Handles file operations securely."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.validator = InputValidator()
        self.sanitizer = ConfigSanitizer()
        self.base_dir = base_dir
    
    def safe_read_yaml(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Safely read and parse YAML file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Parsed YAML data
            
        Raises:
            ValidationError: If file is invalid
            FileError: If file cannot be read
        """
        file_path = self.validator.validate_path(file_path, self.base_dir)
        
        # Validate file type and size
        self.validator.validate_file_size(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Use safe_load to prevent code execution
                data = yaml.safe_load(f)
            
            # Sanitize the loaded data
            if isinstance(data, dict):
                data = self.sanitizer.sanitize_yaml_data(data)
            
            return data
            
        except yaml.YAMLError as e:
            raise ValidationError(f"Invalid YAML format: {e}")
        except Exception as e:
            raise FileError(f"Failed to read file: {e}")
    
    def safe_write_yaml(self, data: Dict[str, Any], file_path: Union[str, Path]) -> None:
        """
        Safely write YAML file.
        
        Args:
            data: Data to write
            file_path: Path to write to
            
        Raises:
            ValidationError: If data or path is invalid
            FileError: If file cannot be written
        """
        file_path = self.validator.validate_path(file_path, self.base_dir)
        
        # Sanitize data before writing
        sanitized_data = self.sanitizer.sanitize_yaml_data(data)
        
        try:
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if file exists
            if file_path.exists():
                backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                shutil.copy2(file_path, backup_path)
            
            # Write file atomically
            temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                yaml.dump(sanitized_data, f, default_flow_style=False, indent=2)
            
            # Atomic rename
            temp_path.replace(file_path)
            
        except Exception as e:
            # Clean up temp file if it exists
            if 'temp_path' in locals() and temp_path.exists():
                temp_path.unlink()
            raise FileError(f"Failed to write file: {e}")
    
    def safe_read_json(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Safely read and parse JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data
        """
        file_path = self.validator.validate_path(file_path, self.base_dir)
        
        # Validate file size
        self.validator.validate_file_size(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Sanitize the loaded data
            if isinstance(data, dict):
                data = self.sanitizer.sanitize_yaml_data(data)
            
            return data
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise FileError(f"Failed to read file: {e}")


def sanitize_hyprctl_command(command: str) -> str:
    """
    Sanitize hyprctl command to prevent injection attacks.
    
    Args:
        command: Command to sanitize
        
    Returns:
        Sanitized command
        
    Raises:
        SecurityError: If command contains dangerous patterns
    """
    if not command or not command.strip():
        raise ValidationError("Command cannot be empty")
    
    command = command.strip()
    
    # Whitelist of allowed hyprctl commands
    allowed_commands = [
        'monitors', 'workspaces', 'clients', 'devices', 'decorations',
        'binds', 'activewindow', 'layers', 'version', 'kill', 'splash',
        'hyprpaper', 'reload', 'setcursor', 'getoption', 'keyword',
        'seterror', 'setprop', 'notify', 'dismissnotify', 'plugin'
    ]
    
    # Extract base command
    base_command = command.split()[0] if command.split() else ''
    
    if base_command not in allowed_commands:
        raise SecurityError(f"Command not allowed: {base_command}")
    
    # Check for dangerous characters
    dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '{', '}', '[', ']', '<', '>']
    for char in dangerous_chars:
        if char in command:
            raise SecurityError(f"Dangerous character in command: {char}")
    
    # Limit command length
    if len(command) > 1000:
        raise SecurityError("Command too long")
    
    return command


# Global instances
input_validator = InputValidator()
config_sanitizer = ConfigSanitizer()
