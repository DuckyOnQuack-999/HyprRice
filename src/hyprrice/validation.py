"""
DuckyCoder v4 Enhanced Validation Module for HyprRice
Provides comprehensive input validation and sanitization.
"""

import re
import logging
from typing import Any, List, Dict, Optional, Union, Tuple
from pathlib import Path

from .exceptions import HyprRiceError


class ValidationError(HyprRiceError):
    """Validation-related error."""
    pass


class InputValidator:
    """Comprehensive input validation and sanitization."""
    
    def __init__(self):
        self.logger = logging.getLogger('hyprrice.validation')
        
        # Color validation patterns
        self.color_patterns = {
            'hex_6': re.compile(r'^#[0-9a-fA-F]{6}$'),
            'hex_8': re.compile(r'^#[0-9a-fA-F]{8}$'),
            'hex_3': re.compile(r'^#[0-9a-fA-F]{3}$'),
            'hex_4': re.compile(r'^#[0-9a-fA-F]{4}$'),
            'rgb': re.compile(r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$'),
            'rgba': re.compile(r'^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)$'),
        }
        
        # Font validation pattern
        self.font_pattern = re.compile(r'^[a-zA-Z0-9\s\-_]+$')
        
        # Safe filename pattern (no directory traversal)
        self.safe_filename_pattern = re.compile(r'^[a-zA-Z0-9\-_\.]+$')
    
    def validate_color(self, color: str) -> bool:
        """
        Validate if a string is a valid color.
        
        Args:
            color: Color string to validate
            
        Returns:
            True if valid color, False otherwise
        """
        if not isinstance(color, str):
            return False
        
        color = color.strip()
        
        # Check all color patterns
        for pattern_name, pattern in self.color_patterns.items():
            if pattern.match(color):
                # Additional validation for RGB/RGBA values
                if pattern_name in ['rgb', 'rgba']:
                    return self._validate_rgb_values(color)
                return True
        
        return False
    
    def _validate_rgb_values(self, color: str) -> bool:
        """Validate RGB/RGBA color values are in valid range."""
        try:
            # Extract numbers from rgb()/rgba() string
            numbers = re.findall(r'[\d.]+', color)
            
            if color.startswith('rgb('):
                if len(numbers) != 3:
                    return False
                # Check RGB values (0-255)
                for value in numbers:
                    if not (0 <= int(value) <= 255):
                        return False
            
            elif color.startswith('rgba('):
                if len(numbers) != 4:
                    return False
                # Check RGB values (0-255) and alpha (0-1)
                for i, value in enumerate(numbers):
                    if i < 3:  # RGB values
                        if not (0 <= int(value) <= 255):
                            return False
                    else:  # Alpha value
                        if not (0 <= float(value) <= 1):
                            return False
            
            return True
        except (ValueError, IndexError):
            return False
    
    def validate_opacity(self, opacity: Union[int, float]) -> bool:
        """
        Validate opacity value.
        
        Args:
            opacity: Opacity value to validate
            
        Returns:
            True if valid opacity (0.0-1.0), False otherwise
        """
        try:
            opacity_float = float(opacity)
            return 0.0 <= opacity_float <= 1.0
        except (ValueError, TypeError):
            return False
    
    def validate_dimension(self, dimension: Union[int, float], min_val: float = 0, max_val: float = 10000) -> bool:
        """
        Validate dimension values (gaps, borders, etc.).
        
        Args:
            dimension: Dimension value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            True if valid dimension, False otherwise
        """
        try:
            dim_float = float(dimension)
            return min_val <= dim_float <= max_val
        except (ValueError, TypeError):
            return False
    
    def validate_font_family(self, font_family: str) -> bool:
        """
        Validate font family name.
        
        Args:
            font_family: Font family name to validate
            
        Returns:
            True if valid font family, False otherwise
        """
        if not isinstance(font_family, str):
            return False
        
        font_family = font_family.strip()
        
        # Check length
        if len(font_family) < 1 or len(font_family) > 100:
            return False
        
        # Check against safe pattern
        return bool(self.font_pattern.match(font_family))
    
    def validate_font_size(self, font_size: Union[int, float]) -> bool:
        """
        Validate font size.
        
        Args:
            font_size: Font size to validate
            
        Returns:
            True if valid font size (6-72), False otherwise
        """
        return self.validate_dimension(font_size, min_val=6, max_val=72)
    
    def validate_animation_duration(self, duration: Union[int, float]) -> bool:
        """
        Validate animation duration.
        
        Args:
            duration: Duration to validate
            
        Returns:
            True if valid duration (0.1-10.0), False otherwise
        """
        return self.validate_dimension(duration, min_val=0.1, max_val=10.0)
    
    def validate_filename(self, filename: str) -> bool:
        """
        Validate filename for security (no path traversal).
        
        Args:
            filename: Filename to validate
            
        Returns:
            True if safe filename, False otherwise
        """
        if not isinstance(filename, str):
            return False
        
        filename = filename.strip()
        
        # Check for directory traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return False
        
        # Check length
        if len(filename) < 1 or len(filename) > 255:
            return False
        
        # Check against safe pattern
        return bool(self.safe_filename_pattern.match(filename))
    
    def validate_position(self, position: str, valid_positions: List[str]) -> bool:
        """
        Validate position string against allowed values.
        
        Args:
            position: Position string to validate
            valid_positions: List of valid position values
            
        Returns:
            True if valid position, False otherwise
        """
        if not isinstance(position, str):
            return False
        
        return position.strip().lower() in [pos.lower() for pos in valid_positions]
    
    def validate_module_list(self, modules: List[str], valid_modules: List[str]) -> bool:
        """
        Validate list of modules against allowed values.
        
        Args:
            modules: List of module names to validate
            valid_modules: List of valid module names
            
        Returns:
            True if all modules are valid, False otherwise
        """
        if not isinstance(modules, list):
            return False
        
        valid_modules_lower = [mod.lower() for mod in valid_modules]
        
        for module in modules:
            if not isinstance(module, str):
                return False
            if module.strip().lower() not in valid_modules_lower:
                return False
        
        return True
    
    def sanitize_string(self, input_str: str, max_length: int = 1000) -> str:
        """
        Sanitize string input by removing potentially dangerous characters.
        
        Args:
            input_str: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(input_str, str):
            return ""
        
        # Remove control characters and limit length
        sanitized = ''.join(char for char in input_str if ord(char) >= 32)
        sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    def validate_configuration(self, config_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate entire configuration dictionary.
        
        Args:
            config_dict: Configuration dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate hyprland configuration
        if 'hyprland' in config_dict:
            hyprland_config = config_dict['hyprland']
            
            # Validate opacity
            if 'window_opacity' in hyprland_config:
                if not self.validate_opacity(hyprland_config['window_opacity']):
                    errors.append("Invalid window_opacity value (must be 0.0-1.0)")
            
            # Validate animation duration
            if 'animation_duration' in hyprland_config:
                if not self.validate_animation_duration(hyprland_config['animation_duration']):
                    errors.append("Invalid animation_duration value (must be 0.1-10.0)")
            
            # Validate border size
            if 'border_size' in hyprland_config:
                if not self.validate_dimension(hyprland_config['border_size'], 0, 20):
                    errors.append("Invalid border_size value (must be 0-20)")
            
            # Validate border color
            if 'border_color' in hyprland_config:
                if not self.validate_color(hyprland_config['border_color']):
                    errors.append("Invalid border_color value")
            
            # Validate gaps
            for gap_type in ['gaps_in', 'gaps_out']:
                if gap_type in hyprland_config:
                    if not self.validate_dimension(hyprland_config[gap_type], 0, 100):
                        errors.append(f"Invalid {gap_type} value (must be 0-100)")
        
        # Validate waybar configuration
        if 'waybar' in config_dict:
            waybar_config = config_dict['waybar']
            
            # Validate position
            if 'position' in waybar_config:
                valid_positions = ['top', 'bottom', 'left', 'right']
                if not self.validate_position(waybar_config['position'], valid_positions):
                    errors.append("Invalid waybar position")
            
            # Validate height
            if 'height' in waybar_config:
                if not self.validate_dimension(waybar_config['height'], 10, 200):
                    errors.append("Invalid waybar height (must be 10-200)")
            
            # Validate colors
            for color_field in ['background_color', 'border_color', 'text_color']:
                if color_field in waybar_config:
                    if not self.validate_color(waybar_config[color_field]):
                        errors.append(f"Invalid waybar {color_field}")
            
            # Validate font
            if 'font_family' in waybar_config:
                if not self.validate_font_family(waybar_config['font_family']):
                    errors.append("Invalid waybar font_family")
            
            if 'font_size' in waybar_config:
                if not self.validate_font_size(waybar_config['font_size']):
                    errors.append("Invalid waybar font_size")
            
            # Validate modules
            if 'modules' in waybar_config:
                valid_modules = [
                    'clock', 'battery', 'network', 'cpu', 'memory', 'tray',
                    'workspaces', 'window', 'custom/media', 'pulseaudio',
                    'backlight', 'temperature'
                ]
                if not self.validate_module_list(waybar_config['modules'], valid_modules):
                    errors.append("Invalid waybar modules")
        
        # Validate rofi configuration
        if 'rofi' in config_dict:
            rofi_config = config_dict['rofi']
            
            # Validate position and anchor
            valid_positions = ['center', 'north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest']
            
            if 'location' in rofi_config:
                if not self.validate_position(rofi_config['location'], valid_positions):
                    errors.append("Invalid rofi location")
            
            if 'anchor' in rofi_config:
                if not self.validate_position(rofi_config['anchor'], valid_positions):
                    errors.append("Invalid rofi anchor")
            
            # Validate width
            if 'width' in rofi_config:
                if not self.validate_dimension(rofi_config['width'], 10, 100):
                    errors.append("Invalid rofi width (must be 10-100)")
            
            # Validate colors
            for color_field in ['background_color', 'text_color', 'border_color']:
                if color_field in rofi_config:
                    if not self.validate_color(rofi_config[color_field]):
                        errors.append(f"Invalid rofi {color_field}")
        
        return len(errors) == 0, errors


# Convenience functions for common validations
def validate_hyprland_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate Hyprland configuration section."""
    validator = InputValidator()
    return validator.validate_configuration({'hyprland': config})


def validate_waybar_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate Waybar configuration section."""
    validator = InputValidator()
    return validator.validate_configuration({'waybar': config})


def validate_rofi_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate Rofi configuration section."""
    validator = InputValidator()
    return validator.validate_configuration({'rofi': config})


def sanitize_user_input(input_data: Any) -> Any:
    """Sanitize user input data."""
    validator = InputValidator()
    
    if isinstance(input_data, str):
        return validator.sanitize_string(input_data)
    elif isinstance(input_data, dict):
        return {
            key: sanitize_user_input(value)
            for key, value in input_data.items()
        }
    elif isinstance(input_data, list):
        return [sanitize_user_input(item) for item in input_data]
    else:
        return input_data