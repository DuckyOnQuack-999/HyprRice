"""
Theme management for HyprRice
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..config import Config
from ..utils import validate_color


class ThemeManager:
    """Manages HyprRice themes and their application."""
    
    def __init__(self, themes_dir: str):
        self.themes_dir = Path(themes_dir)
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Default themes
        self._default_themes = {
            "minimal": {
                "name": "Minimal",
                "description": "Clean and minimal theme with subtle colors",
                "author": "HyprRice Team",
                "version": "1.0.0",
                "colors": {
                    "primary": "#2e3440",
                    "secondary": "#3b4252",
                    "accent": "#5e81ac",
                    "text": "#eceff4",
                    "background": "#2e3440",
                    "surface": "#3b4252"
                },
                "hyprland": {
                    "border_color": "#5e81ac",
                    "gaps_in": 5,
                    "gaps_out": 10,
                    "blur_enabled": True,
                    "blur_size": 8
                },
                "waybar": {
                    "background_color": "rgba(46, 52, 64, 0.8)",
                    "text_color": "#eceff4",
                    "border_color": "rgba(100, 115, 245, 0.5)"
                },
                "rofi": {
                    "background_color": "#2e3440",
                    "text_color": "#eceff4",
                    "border_color": "#5e81ac"
                }
            },
            "cyberpunk": {
                "name": "Cyberpunk",
                "description": "Neon cyberpunk theme with vibrant colors",
                "author": "HyprRice Team",
                "version": "1.0.0",
                "colors": {
                    "primary": "#ff00cc",
                    "secondary": "#00fff7",
                    "accent": "#ff0080",
                    "text": "#00fff7",
                    "background": "#0a0a0a",
                    "surface": "#1a1a1a"
                },
                "hyprland": {
                    "border_color": "#ff00cc",
                    "gaps_in": 8,
                    "gaps_out": 15,
                    "blur_enabled": True,
                    "blur_size": 12
                },
                "waybar": {
                    "background_color": "rgba(10, 10, 10, 0.9)",
                    "text_color": "#00fff7",
                    "border_color": "rgba(255, 0, 204, 0.8)"
                },
                "rofi": {
                    "background_color": "#0a0a0a",
                    "text_color": "#00fff7",
                    "border_color": "#ff00cc"
                }
            },
            "pastel": {
                "name": "Pastel",
                "description": "Soft pastel theme with gentle colors",
                "author": "HyprRice Team",
                "version": "1.0.0",
                "colors": {
                    "primary": "#ffd1dc",
                    "secondary": "#b5ead7",
                    "accent": "#c7ceea",
                    "text": "#2d3748",
                    "background": "#fefefe",
                    "surface": "#f7fafc"
                },
                "hyprland": {
                    "border_color": "#c7ceea",
                    "gaps_in": 6,
                    "gaps_out": 12,
                    "blur_enabled": True,
                    "blur_size": 6
                },
                "waybar": {
                    "background_color": "rgba(255, 255, 255, 0.8)",
                    "text_color": "#2d3748",
                    "border_color": "rgba(199, 206, 234, 0.6)"
                },
                "rofi": {
                    "background_color": "#fefefe",
                    "text_color": "#2d3748",
                    "border_color": "#c7ceea"
                }
            }
        }
        
        # Create default theme files if they don't exist
        self._create_default_themes()
    
    def _create_default_themes(self):
        """Create default theme files if they don't exist."""
        for theme_name, theme_data in self._default_themes.items():
            theme_file = self.themes_dir / f"{theme_name}.hyprrice"
            if not theme_file.exists():
                try:
                    with open(theme_file, 'w', encoding='utf-8') as f:
                        yaml.dump(theme_data, f, default_flow_style=False, indent=2)
                except Exception as e:
                    self.logger.error(f"Failed to create default theme {theme_name}: {e}")
    
    def list_themes(self) -> List[str]:
        """List available themes."""
        try:
            themes = []
            for theme_file in self.themes_dir.glob("*.hyprrice"):
                themes.append(theme_file.stem)
            return sorted(themes)
        except Exception as e:
            self.logger.error(f"Error listing themes: {e}")
            return list(self._default_themes.keys())
    
    def get_theme_info(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Get theme information."""
        try:
            theme_file = self.themes_dir / f"{theme_name}.hyprrice"
            if not theme_file.exists():
                return None
            
            with open(theme_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading theme {theme_name}: {e}")
            return None
    
    def apply_theme(self, theme_name: str, config: Config) -> bool:
        """Apply a theme to the configuration."""
        try:
            theme_data = self.get_theme_info(theme_name)
            if not theme_data:
                self.logger.error(f"Theme {theme_name} not found")
                return False
            
            # Apply Hyprland settings
            if 'hyprland' in theme_data:
                hyprland_theme = theme_data['hyprland']
                if 'border_color' in hyprland_theme:
                    config.hyprland.border_color = hyprland_theme['border_color']
                if 'gaps_in' in hyprland_theme:
                    config.hyprland.gaps_in = hyprland_theme['gaps_in']
                if 'gaps_out' in hyprland_theme:
                    config.hyprland.gaps_out = hyprland_theme['gaps_out']
                if 'blur_enabled' in hyprland_theme:
                    config.hyprland.blur_enabled = hyprland_theme['blur_enabled']
                if 'blur_size' in hyprland_theme:
                    config.hyprland.blur_size = hyprland_theme['blur_size']
            
            # Apply Waybar settings
            if 'waybar' in theme_data:
                waybar_theme = theme_data['waybar']
                if 'background_color' in waybar_theme:
                    config.waybar.background_color = waybar_theme['background_color']
                if 'text_color' in waybar_theme:
                    config.waybar.text_color = waybar_theme['text_color']
                if 'border_color' in waybar_theme:
                    config.waybar.border_color = waybar_theme['border_color']
            
            # Apply Rofi settings
            if 'rofi' in theme_data:
                rofi_theme = theme_data['rofi']
                if 'background_color' in rofi_theme:
                    config.rofi.background_color = rofi_theme['background_color']
                if 'text_color' in rofi_theme:
                    config.rofi.text_color = rofi_theme['text_color']
                if 'border_color' in rofi_theme:
                    config.rofi.border_color = rofi_theme['border_color']
            
            # Set theme name
            config.general.theme = theme_name
            
            # Save configuration
            config.save()
            
            self.logger.info(f"Theme {theme_name} applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying theme {theme_name}: {e}")
            return False
    
    def preview_theme(self, theme_name: str, config: Config) -> bool:
        """Preview a theme without saving."""
        try:
            theme_data = self.get_theme_info(theme_name)
            if not theme_data:
                return False
            
            # Create a temporary config for preview
            preview_config = Config()
            
            # Apply theme to preview config
            return self.apply_theme(theme_name, preview_config)
            
        except Exception as e:
            self.logger.error(f"Error previewing theme {theme_name}: {e}")
            return False
    
    def get_custom_themes(self) -> List[str]:
        """Get list of custom (user-created) themes."""
        try:
            custom_themes = []
            for theme_file in self.themes_dir.glob("*.hyprrice"):
                theme_name = theme_file.stem
                if theme_name not in self._default_themes:
                    custom_themes.append(theme_name)
            return sorted(custom_themes)
        except Exception as e:
            self.logger.error(f"Error getting custom themes: {e}")
            return []
    
    def get_theme_preview(self, theme_name: str) -> str:
        """Get a text preview of the theme."""
        try:
            theme_data = self.get_theme_info(theme_name)
            if not theme_data:
                return f"Theme {theme_name} not found"
            
            preview = f"Theme: {theme_data.get('name', theme_name)}\n"
            preview += f"Description: {theme_data.get('description', 'No description')}\n"
            preview += f"Author: {theme_data.get('author', 'Unknown')}\n"
            preview += f"Version: {theme_data.get('version', '1.0.0')}\n"
            
            if 'colors' in theme_data:
                preview += "\nColors:\n"
                for color_name, color_value in theme_data['colors'].items():
                    preview += f"  {color_name}: {color_value}\n"
            
            return preview
            
        except Exception as e:
            self.logger.error(f"Error getting theme preview: {e}")
            return f"Error loading theme {theme_name}"
    
    def import_theme(self, file_path: str) -> bool:
        """Import a theme from a file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.logger.error(f"Theme file not found: {file_path}")
                return False
            
            # Load theme data
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    theme_data = json.load(f)
                else:
                    theme_data = yaml.safe_load(f)
            
            # Validate theme data
            if not self._validate_theme_data(theme_data):
                self.logger.error("Invalid theme data")
                return False
            
            # Generate theme name from filename
            theme_name = file_path.stem
            
            # Save theme
            theme_file = self.themes_dir / f"{theme_name}.hyprrice"
            with open(theme_file, 'w', encoding='utf-8') as f:
                yaml.dump(theme_data, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Theme {theme_name} imported successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing theme: {e}")
            return False
    
    def export_theme(self, config_or_theme_name, file_path: str) -> bool:
        """Export current configuration as a theme or export existing theme by name."""
        try:
            file_path = Path(file_path)
            
            # Check if first parameter is a theme name (string) or config object
            if isinstance(config_or_theme_name, str):
                # Export existing theme by name
                theme_name = config_or_theme_name
                theme_data = self.load_theme(theme_name)
                if not theme_data:
                    self.logger.error(f"Theme {theme_name} not found for export")
                    return False
            else:
                # Export from config object (original behavior)
                config = config_or_theme_name
                # Create theme data from current config
                theme_data = {
                    "name": "Custom Theme",
                    "description": "Exported from current configuration",
                    "author": "User",
                    "version": "1.0.0",
                    "colors": {
                        "primary": config.hyprland.border_color,
                        "text": config.waybar.text_color,
                        "background": config.waybar.background_color
                    },
                    "hyprland": {
                        "border_color": config.hyprland.border_color,
                        "gaps_in": config.hyprland.gaps_in,
                        "gaps_out": config.hyprland.gaps_out,
                        "blur_enabled": config.hyprland.blur_enabled,
                        "blur_size": config.hyprland.blur_size
                    },
                    "waybar": {
                        "background_color": config.waybar.background_color,
                        "text_color": config.waybar.text_color,
                        "border_color": config.waybar.border_color
                    },
                    "rofi": {
                        "background_color": config.rofi.background_color,
                        "text_color": config.rofi.text_color,
                        "border_color": config.rofi.border_color
                    }
                }
            
            # Save theme
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    json.dump(theme_data, f, indent=2)
                else:
                    yaml.dump(theme_data, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Theme exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting theme: {e}")
            return False
    
    def delete_theme(self, theme_name: str) -> bool:
        """Delete a custom theme."""
        try:
            if theme_name in self._default_themes:
                self.logger.error("Cannot delete default themes")
                return False
            
            theme_file = self.themes_dir / f"{theme_name}.hyprrice"
            if not theme_file.exists():
                self.logger.error(f"Theme {theme_name} not found")
                return False
            
            theme_file.unlink()
            self.logger.info(f"Theme {theme_name} deleted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting theme {theme_name}: {e}")
            return False
    
    def _validate_theme_data(self, theme_data: Dict[str, Any]) -> bool:
        """Validate theme data structure with comprehensive schema checking."""
        try:
            # Define the expected schema
            required_fields = ['name', 'version']
            optional_sections = ['description', 'author', 'tags', 'colors', 'hyprland', 'waybar', 'rofi', 'notifications', 'lockscreen']
            
            # Check required fields
            for field in required_fields:
                if field not in theme_data:
                    self.logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate version format
            version = theme_data['version']
            if not isinstance(version, str) or not version.count('.') >= 1:
                self.logger.error(f"Invalid version format: {version}. Expected format: X.Y.Z")
                return False
            
            # Validate name
            if not isinstance(theme_data['name'], str) or len(theme_data['name'].strip()) == 0:
                self.logger.error("Theme name must be a non-empty string")
                return False
            
            # Validate colors section if present
            if 'colors' in theme_data:
                if not self._validate_colors_section(theme_data['colors']):
                    return False
            
            # Validate hyprland section if present
            if 'hyprland' in theme_data:
                if not self._validate_hyprland_section(theme_data['hyprland']):
                    return False
            
            # Validate waybar section if present
            if 'waybar' in theme_data:
                if not self._validate_waybar_section(theme_data['waybar']):
                    return False
            
            # Validate rofi section if present
            if 'rofi' in theme_data:
                if not self._validate_rofi_section(theme_data['rofi']):
                    return False
            
            # Validate tags if present
            if 'tags' in theme_data:
                if not isinstance(theme_data['tags'], list):
                    self.logger.error("Tags must be a list")
                    return False
                for tag in theme_data['tags']:
                    if not isinstance(tag, str):
                        self.logger.error(f"Invalid tag type: {type(tag)}. Tags must be strings")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating theme data: {e}")
            return False
    
    def _validate_colors_section(self, colors: Dict[str, Any]) -> bool:
        """Validate the colors section of theme data."""
        if not isinstance(colors, dict):
            self.logger.error("Colors section must be a dictionary")
            return False
        
        # Common color names to validate
        common_colors = ['primary', 'secondary', 'accent', 'text', 'background', 'surface']
        
        for color_name, color_value in colors.items():
            if not isinstance(color_value, str):
                self.logger.error(f"Color {color_name} must be a string")
                return False
            
            if not validate_color(color_value):
                self.logger.error(f"Invalid color {color_name}: {color_value}")
                return False
        
        return True
    
    def _validate_hyprland_section(self, hyprland: Dict[str, Any]) -> bool:
        """Validate the hyprland section of theme data."""
        if not isinstance(hyprland, dict):
            self.logger.error("Hyprland section must be a dictionary")
            return False
        
        # Validate specific hyprland settings
        numeric_fields = ['gaps_in', 'gaps_out', 'blur_size', 'border_size']
        for field in numeric_fields:
            if field in hyprland:
                if not isinstance(hyprland[field], (int, float)) or hyprland[field] < 0:
                    self.logger.error(f"Hyprland {field} must be a non-negative number")
                    return False
        
        # Validate boolean fields
        boolean_fields = ['blur_enabled', 'animations_enabled']
        for field in boolean_fields:
            if field in hyprland and not isinstance(hyprland[field], bool):
                self.logger.error(f"Hyprland {field} must be a boolean")
                return False
        
        # Validate color fields
        color_fields = ['border_color', 'active_border_color', 'inactive_border_color']
        for field in color_fields:
            if field in hyprland:
                if not isinstance(hyprland[field], str) or not validate_color(hyprland[field]):
                    self.logger.error(f"Hyprland {field} must be a valid color")
                    return False
        
        # Validate animation duration
        if 'animation_duration' in hyprland:
            duration = hyprland['animation_duration']
            if not isinstance(duration, (int, float)) or duration < 0 or duration > 10:
                self.logger.error("Animation duration must be between 0 and 10 seconds")
                return False
        
        return True
    
    def _validate_waybar_section(self, waybar: Dict[str, Any]) -> bool:
        """Validate the waybar section of theme data."""
        if not isinstance(waybar, dict):
            self.logger.error("Waybar section must be a dictionary")
            return False
        
        # Validate color fields
        color_fields = ['background_color', 'text_color', 'border_color', 'urgent_color']
        for field in color_fields:
            if field in waybar:
                color_value = waybar[field]
                if not isinstance(color_value, str):
                    self.logger.error(f"Waybar {field} must be a string")
                    return False
                
                # Support rgba() format for waybar
                if not (validate_color(color_value) or color_value.startswith('rgba(') or color_value.startswith('rgb(')):
                    self.logger.error(f"Waybar {field} must be a valid color or rgba/rgb value")
                    return False
        
        # Validate numeric fields
        numeric_fields = ['height', 'border_radius']
        for field in numeric_fields:
            if field in waybar:
                if not isinstance(waybar[field], (int, float)) or waybar[field] < 0:
                    self.logger.error(f"Waybar {field} must be a non-negative number")
                    return False
        
        # Validate margin (can be string or number)
        if 'margin' in waybar:
            margin = waybar['margin']
            if not (isinstance(margin, (int, float, str))):
                self.logger.error("Waybar margin must be a number or string")
                return False
            if isinstance(margin, (int, float)) and margin < 0:
                self.logger.error("Waybar margin must be a non-negative number")
                return False
        
        return True
    
    def _validate_rofi_section(self, rofi: Dict[str, Any]) -> bool:
        """Validate the rofi section of theme data."""
        if not isinstance(rofi, dict):
            self.logger.error("Rofi section must be a dictionary")
            return False
        
        # Validate color fields
        color_fields = ['background', 'foreground', 'selected_background', 'selected_foreground', 'border_color']
        for field in color_fields:
            if field in rofi:
                if not isinstance(rofi[field], str) or not validate_color(rofi[field]):
                    self.logger.error(f"Rofi {field} must be a valid color")
                    return False
        
        # Validate numeric fields
        numeric_fields = ['width', 'border_width', 'padding']
        for field in numeric_fields:
            if field in rofi:
                if not isinstance(rofi[field], (int, float)) or rofi[field] < 0:
                    self.logger.error(f"Rofi {field} must be a non-negative number")
                    return False
        
        # Validate font
        if 'font' in rofi:
            if not isinstance(rofi['font'], str) or len(rofi['font'].strip()) == 0:
                self.logger.error("Rofi font must be a non-empty string")
                return False
        
        return True
    
    def get_theme_validation_errors(self, theme_data: Dict[str, Any]) -> List[str]:
        """Get detailed validation errors for theme data."""
        errors = []
        
        # Capture validation errors
        handler = logging.StreamHandler()
        handler.setLevel(logging.ERROR)
        
        # Temporarily add handler to capture errors
        logger = logging.getLogger(__name__)
        original_level = logger.level
        logger.setLevel(logging.ERROR)
        logger.addHandler(handler)
        
        try:
            # Validate and capture errors
            self._validate_theme_data(theme_data)
        except Exception as e:
            errors.append(str(e))
        finally:
            logger.removeHandler(handler)
            logger.setLevel(original_level)
        
        return errors
    
    def create_theme_template(self) -> Dict[str, Any]:
        """Create a template for a new theme with all possible sections."""
        return {
            "name": "New Theme",
            "description": "A custom theme created with HyprRice",
            "author": "User",
            "version": "1.0.0",
            "tags": ["custom"],
            "colors": {
                "primary": "#5e81ac",
                "secondary": "#3b4252",
                "accent": "#88c0d0",
                "text": "#eceff4",
                "background": "#2e3440",
                "surface": "#3b4252",
                "error": "#bf616a",
                "warning": "#ebcb8b",
                "success": "#a3be8c"
            },
            "hyprland": {
                "border_color": "#5e81ac",
                "active_border_color": "#88c0d0",
                "inactive_border_color": "#4c566a",
                "gaps_in": 5,
                "gaps_out": 10,
                "border_size": 2,
                "blur_enabled": True,
                "blur_size": 8,
                "blur_passes": 3,
                "animations_enabled": True,
                "animation_duration": 0.5,
                "animation_curve": "easeOutQuart",
                "rounding": 8
            },
            "waybar": {
                "background_color": "rgba(46, 52, 64, 0.9)",
                "text_color": "#eceff4",
                "border_color": "rgba(94, 129, 172, 0.8)",
                "urgent_color": "#bf616a",
                "height": 30,
                "border_radius": 8,
                "margin": 5,
                "font_family": "JetBrainsMono Nerd Font",
                "font_size": 12
            },
            "rofi": {
                "background": "#2e3440",
                "foreground": "#eceff4",
                "selected_background": "#5e81ac",
                "selected_foreground": "#eceff4",
                "border_color": "#5e81ac",
                "width": 600,
                "border_width": 2,
                "padding": 10,
                "font": "JetBrainsMono Nerd Font 12"
            },
            "notifications": {
                "background": "rgba(46, 52, 64, 0.9)",
                "text_color": "#eceff4",
                "border_color": "#5e81ac",
                "timeout": 5000,
                "font": "JetBrainsMono Nerd Font 11"
            },
            "lockscreen": {
                "background": "#2e3440",
                "text_color": "#eceff4",
                "input_background": "#3b4252",
                "input_border": "#5e81ac",
                "font": "JetBrainsMono Nerd Font 14"
            }
        } 

    def save_theme(self, theme_name: str, config: Config, description: str = "") -> bool:
        """Save current configuration as a theme."""
        try:
            theme_data = self._create_theme_from_config(config, description or f"Theme: {theme_name}")
            theme_data['name'] = theme_name
            
            theme_file = self.themes_dir / f"{theme_name}.hyprrice"
            with open(theme_file, 'w', encoding='utf-8') as f:
                yaml.dump(theme_data, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Saved theme: {theme_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving theme {theme_name}: {e}")
            return False
    
    def load_theme(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Load theme data from file."""
        try:
            theme_file = self.themes_dir / f"{theme_name}.hyprrice"
            if not theme_file.exists():
                # Check default themes
                if theme_name in self._default_themes:
                    return self._default_themes[theme_name].copy()
                return None
            
            with open(theme_file, 'r', encoding='utf-8') as f:
                theme_data = yaml.safe_load(f)
            
            return theme_data
            
        except Exception as e:
            self.logger.error(f"Error loading theme {theme_name}: {e}")
            return None
    
    def _create_theme_from_config(self, config: Config, description: str = "") -> Dict[str, Any]:
        """Create theme data from current configuration."""
        theme_data = {
            "name": "Custom Theme",
            "description": description or "Exported from current configuration",
            "author": "User",
            "version": "1.0.0",
            "general": {},
            "colors": {},
            "hyprland": {},
            "waybar": {},
            "rofi": {},
            "notifications": {},
            "lockscreen": {}
        }
        
        # Extract hyprland settings
        if hasattr(config, 'hyprland'):
            hyprland = config.hyprland
            theme_data["hyprland"] = {
                "border_color": getattr(hyprland, 'border_color', '#5e81ac'),
                "gaps_in": getattr(hyprland, 'gaps_in', 5),
                "gaps_out": getattr(hyprland, 'gaps_out', 10),
                "border_size": getattr(hyprland, 'border_size', 2),
                "blur_enabled": getattr(hyprland, 'blur_enabled', True),
                "blur_size": getattr(hyprland, 'blur_size', 8),
                "animations_enabled": getattr(hyprland, 'animations_enabled', True),
                "rounding": getattr(hyprland, 'rounding', 8)
            }
        
        # Extract waybar settings
        if hasattr(config, 'waybar'):
            waybar = config.waybar
            theme_data["waybar"] = {
                "background_color": getattr(waybar, 'background_color', 'rgba(46, 52, 64, 0.8)'),
                "text_color": getattr(waybar, 'text_color', '#eceff4'),
                "border_color": getattr(waybar, 'border_color', 'rgba(94, 129, 172, 0.8)'),
                "height": getattr(waybar, 'height', 30)
            }
        
        # Extract rofi settings
        if hasattr(config, 'rofi'):
            rofi = config.rofi
            theme_data["rofi"] = {
                "background": getattr(rofi, 'background_color', '#2e3440'),
                "foreground": getattr(rofi, 'text_color', '#eceff4'),
                "border_color": getattr(rofi, 'border_color', '#5e81ac'),
                "width": getattr(rofi, 'width', 600)
            }
        
        # Extract color scheme if available
        if hasattr(config, 'colors'):
            colors = config.colors
            theme_data["colors"] = {
                "primary": getattr(colors, 'primary', '#5e81ac'),
                "secondary": getattr(colors, 'secondary', '#3b4252'),
                "accent": getattr(colors, 'accent', '#88c0d0'),
                "text": getattr(colors, 'text', '#eceff4'),
                "background": getattr(colors, 'background', '#2e3440')
            }
        
        return theme_data
    
    def _apply_theme_to_config(self, theme_data: Dict[str, Any], config: Config) -> bool:
        """Apply theme data to configuration object."""
        try:
            # Apply hyprland settings
            if 'hyprland' in theme_data and hasattr(config, 'hyprland'):
                hyprland_data = theme_data['hyprland']
                hyprland_config = config.hyprland
                
                for key, value in hyprland_data.items():
                    if hasattr(hyprland_config, key):
                        setattr(hyprland_config, key, value)
            
            # Apply waybar settings
            if 'waybar' in theme_data and hasattr(config, 'waybar'):
                waybar_data = theme_data['waybar']
                waybar_config = config.waybar
                
                for key, value in waybar_data.items():
                    if hasattr(waybar_config, key):
                        setattr(waybar_config, key, value)
            
            # Apply rofi settings
            if 'rofi' in theme_data and hasattr(config, 'rofi'):
                rofi_data = theme_data['rofi']
                rofi_config = config.rofi
                
                # Map theme keys to config keys
                key_mapping = {
                    'background': 'background_color',
                    'foreground': 'text_color',
                    'selected_background': 'selected_background_color',
                    'selected_foreground': 'selected_text_color'
                }
                
                for theme_key, value in rofi_data.items():
                    config_key = key_mapping.get(theme_key, theme_key)
                    if hasattr(rofi_config, config_key):
                        setattr(rofi_config, config_key, value)
            
            # Apply colors if available
            if 'colors' in theme_data and hasattr(config, 'colors'):
                colors_data = theme_data['colors']
                colors_config = config.colors
                
                for key, value in colors_data.items():
                    if hasattr(colors_config, key):
                        setattr(colors_config, key, value)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying theme to config: {e}")
            return False
    
    def _validate_theme_name(self, theme_name: str) -> bool:
        """Validate theme name."""
        if not theme_name or not isinstance(theme_name, str):
            return False
        
        # Check for valid characters (alphanumeric, underscore, hyphen)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', theme_name):
            return False
        
        # Check length
        if len(theme_name) < 1 or len(theme_name) > 50:
            return False
        
        # Check for reserved names
        reserved_names = ['default', 'none', 'auto', 'system']
        if theme_name.lower() in reserved_names:
            return False
        
        return True 
