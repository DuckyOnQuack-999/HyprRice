"""
Input validation and sanitization module for HyprRice
Implements comprehensive validation with security focus and GDPR compliance
"""

import re
import os
import shlex
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Union
from datetime import datetime

from .exceptions import ValidationError, HyprRiceError


class InputValidator:
    """Comprehensive input validation with security and compliance features."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audit_log = logging.getLogger(f"{__name__}.audit")
        
        # Security patterns
        self.COMMAND_INJECTION_PATTERNS = [
            r'[;&|`$]',  # Command separators and substitutions
            r'\.\./',    # Path traversal
            r'eval\s*\(',  # Code evaluation
            r'exec\s*\(',  # Code execution
            r'import\s+os',  # OS imports
            r'__import__',   # Dynamic imports
        ]
        
        # Allowed patterns for different types
        self.PATTERNS = {
            'color_hex': re.compile(r'^#[0-9a-fA-F]{6}$|^#[0-9a-fA-F]{8}$|^#[0-9a-fA-F]{3}$|^#[0-9a-fA-F]{4}$'),
            'color_rgb': re.compile(r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$'),
            'color_rgba': re.compile(r'^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)$'),
            'filename': re.compile(r'^[a-zA-Z0-9._-]+$'),
            'path_component': re.compile(r'^[a-zA-Z0-9._/-]+$'),
            'version': re.compile(r'^\d+\.\d+\.\d+$'),
            'cpu_governor': re.compile(r'^[a-z_]+$'),
            'frequency': re.compile(r'^(\d+|min|max)$'),
            'duration': re.compile(r'^\d+$'),
            'hyprctl_command': re.compile(r'^[a-zA-Z0-9_-]+$'),
        }
    
    def validate_input(self, input_value: Any, validation_type: str, 
                      context: str = "", allow_empty: bool = False) -> Any:
        """
        Comprehensive input validation with audit logging.
        
        Args:
            input_value: Value to validate
            validation_type: Type of validation to perform
            context: Context for audit logging
            allow_empty: Whether empty values are allowed
            
        Returns:
            Validated and sanitized input
            
        Raises:
            ValidationError: If validation fails
        """
        start_time = datetime.now()
        
        try:
            # Log validation attempt
            self.audit_log.info(f"Validation attempt: type={validation_type}, context={context}")
            
            # Handle None/empty values
            if input_value is None or input_value == "":
                if allow_empty:
                    return input_value
                raise ValidationError(f"Empty value not allowed for {validation_type}")
            
            # Convert to string for pattern matching
            str_value = str(input_value).strip()
            
            # Check for command injection patterns
            if self._contains_injection_patterns(str_value):
                self.audit_log.warning(f"Security violation: injection pattern detected in {context}")
                raise ValidationError(f"Security violation: invalid characters detected")
            
            # Perform type-specific validation
            validated_value = self._validate_by_type(str_value, validation_type)
            
            # Log successful validation
            duration = (datetime.now() - start_time).total_seconds()
            self.audit_log.info(f"Validation success: type={validation_type}, duration={duration:.3f}s")
            
            return validated_value
            
        except ValidationError:
            # Log validation failure
            duration = (datetime.now() - start_time).total_seconds()
            self.audit_log.error(f"Validation failed: type={validation_type}, context={context}, duration={duration:.3f}s")
            raise
        except Exception as e:
            self.audit_log.error(f"Validation error: {e}")
            raise ValidationError(f"Validation system error: {e}")
    
    def _contains_injection_patterns(self, value: str) -> bool:
        """Check for command injection patterns."""
        for pattern in self.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    def _validate_by_type(self, value: str, validation_type: str) -> Any:
        """Perform type-specific validation."""
        
        if validation_type == "color":
            return self._validate_color(value)
        elif validation_type == "path":
            return self._validate_path(value)
        elif validation_type == "filename":
            return self._validate_filename(value)
        elif validation_type == "command":
            return self._validate_command(value)
        elif validation_type == "cpu_governor":
            return self._validate_cpu_governor(value)
        elif validation_type == "frequency":
            return self._validate_frequency(value)
        elif validation_type == "duration":
            return self._validate_duration(value)
        elif validation_type == "version":
            return self._validate_version(value)
        elif validation_type == "hyprctl_command":
            return self._validate_hyprctl_command(value)
        elif validation_type == "integer":
            return self._validate_integer(value)
        elif validation_type == "float":
            return self._validate_float(value)
        elif validation_type == "boolean":
            return self._validate_boolean(value)
        else:
            raise ValidationError(f"Unknown validation type: {validation_type}")
    
    def _validate_color(self, value: str) -> str:
        """Validate color values (hex, rgb, rgba)."""
        if (self.PATTERNS['color_hex'].match(value) or 
            self.PATTERNS['color_rgb'].match(value) or 
            self.PATTERNS['color_rgba'].match(value)):
            return value
        raise ValidationError(f"Invalid color format: {value}")
    
    def _validate_path(self, value: str) -> str:
        """Validate file paths with security checks."""
        # Prevent path traversal
        if '..' in value or value.startswith('/') and not value.startswith('/home/'):
            raise ValidationError("Path traversal or unauthorized access detected")
        
        # Expand user path
        expanded_path = os.path.expanduser(value)
        
        # Additional security check
        if not self.PATTERNS['path_component'].match(value.replace('/', '').replace('~', '')):
            raise ValidationError(f"Invalid path characters: {value}")
        
        return expanded_path
    
    def _validate_filename(self, value: str) -> str:
        """Validate filenames."""
        if not self.PATTERNS['filename'].match(value):
            raise ValidationError(f"Invalid filename: {value}")
        if len(value) > 255:
            raise ValidationError("Filename too long")
        return value
    
    def _validate_command(self, value: str) -> List[str]:
        """Validate and sanitize shell commands."""
        try:
            # Use shlex to safely parse command
            parsed = shlex.split(value)
            
            # Validate each component
            for component in parsed:
                if self._contains_injection_patterns(component):
                    raise ValidationError("Command injection detected")
            
            return parsed
        except ValueError as e:
            raise ValidationError(f"Invalid command syntax: {e}")
    
    def _validate_cpu_governor(self, value: str) -> str:
        """Validate CPU governor names."""
        if not self.PATTERNS['cpu_governor'].match(value):
            raise ValidationError(f"Invalid CPU governor: {value}")
        
        # Check against known governors
        valid_governors = ['performance', 'powersave', 'userspace', 'ondemand', 'conservative', 'schedutil']
        if value not in valid_governors:
            self.logger.warning(f"Unknown CPU governor: {value}")
        
        return value
    
    def _validate_frequency(self, value: str) -> str:
        """Validate CPU frequency values."""
        if not self.PATTERNS['frequency'].match(value):
            raise ValidationError(f"Invalid frequency: {value}")
        
        if value.isdigit():
            freq = int(value)
            if freq < 100000 or freq > 10000000:  # 100MHz to 10GHz
                raise ValidationError(f"Frequency out of range: {value}")
        
        return value
    
    def _validate_duration(self, value: str) -> int:
        """Validate duration values."""
        if not self.PATTERNS['duration'].match(value):
            raise ValidationError(f"Invalid duration: {value}")
        
        duration = int(value)
        if duration < 1 or duration > 3600:  # 1 second to 1 hour
            raise ValidationError(f"Duration out of range: {value}")
        
        return duration
    
    def _validate_version(self, value: str) -> str:
        """Validate version strings."""
        if not self.PATTERNS['version'].match(value):
            raise ValidationError(f"Invalid version format: {value}")
        return value
    
    def _validate_hyprctl_command(self, value: str) -> str:
        """Validate hyprctl commands."""
        if not self.PATTERNS['hyprctl_command'].match(value):
            raise ValidationError(f"Invalid hyprctl command: {value}")
        
        # Whitelist of allowed commands
        allowed_commands = [
            'monitors', 'workspaces', 'clients', 'devices', 'version',
            'reload', 'kill', 'splash', 'hyprpaper', 'notify',
            'keyword', 'dispatch'
        ]
        
        base_command = value.split()[0] if ' ' in value else value
        if base_command not in allowed_commands:
            raise ValidationError(f"Unauthorized hyprctl command: {base_command}")
        
        return value
    
    def _validate_integer(self, value: str) -> int:
        """Validate integer values."""
        try:
            return int(value)
        except ValueError:
            raise ValidationError(f"Invalid integer: {value}")
    
    def _validate_float(self, value: str) -> float:
        """Validate float values."""
        try:
            return float(value)
        except ValueError:
            raise ValidationError(f"Invalid float: {value}")
    
    def _validate_boolean(self, value: str) -> bool:
        """Validate boolean values."""
        if value.lower() in ('true', '1', 'yes', 'on'):
            return True
        elif value.lower() in ('false', '0', 'no', 'off'):
            return False
        else:
            raise ValidationError(f"Invalid boolean: {value}")


# Global validator instance
validator = InputValidator()


def validate_input(input_value: Any, validation_type: str, 
                  context: str = "", allow_empty: bool = False) -> Any:
    """Convenience function for input validation."""
    return validator.validate_input(input_value, validation_type, context, allow_empty)


def sanitize_command(command: Union[str, List[str]]) -> List[str]:
    """Sanitize shell commands for safe execution."""
    if isinstance(command, str):
        return validate_input(command, "command", "shell_command")
    elif isinstance(command, list):
        return [validate_input(str(cmd), "command", "shell_command_component") for cmd in command]
    else:
        raise ValidationError("Command must be string or list")