"""
Theme management system for HyprRice.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from ..config import Config
from ..exceptions import ThemeError


class ThemeManager(QObject):
    """Manages themes for HyprRice."""
    
    theme_loaded = pyqtSignal(str)
    theme_saved = pyqtSignal(str)
    theme_deleted = pyqtSignal(str)
    
    def __init__(self, themes_dir: Optional[str] = None):
        super().__init__()
        self.themes_dir = Path(themes_dir or "~/.hyprrice/themes").expanduser()
        self.themes_dir.mkdir(parents=True, exist_ok=True)
    
    def list_themes(self) -> List[str]:
        """List all available themes."""
        themes = []
        for theme_file in self.themes_dir.glob("*.hyprrice"):
            themes.append(theme_file.stem)
        return sorted(themes)
    
    def get_theme_info(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific theme."""
        theme_file = self.themes_dir / f"{theme_name}.hyprrice"
        if not theme_file.exists():
            return None
        
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                theme_data = yaml.safe_load(f)
            return theme_data
        except Exception as e:
            raise ThemeError(f"Failed to load theme info for '{theme_name}': {e}")
    
    def load_theme(self, theme_name: str, config: Config) -> bool:
        """Load a theme and apply it to the configuration."""
        theme_file = self.themes_dir / f"{theme_name}.hyprrice"
        if not theme_file.exists():
            raise ThemeError(f"Theme '{theme_name}' not found")
        
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                theme_data = yaml.safe_load(f)
            
            # Apply theme to config
            self._apply_theme_to_config(theme_data, config)
            self.theme_loaded.emit(theme_name)
            return True
            
        except Exception as e:
            raise ThemeError(f"Failed to load theme '{theme_name}': {e}")
    
    def save_theme(self, theme_name: str, config: Config, description: str = "", author: str = "") -> bool:
        """Save current configuration as a theme."""
        try:
            # Create theme data
            theme_data = {
                'name': theme_name,
                'version': '1.0.0',
                'description': description or f"Theme created from current configuration",
                'author': author or "HyprRice User",
                'config': self._extract_config_data(config)
            }
            
            # Save theme file
            theme_file = self.themes_dir / f"{theme_name}.hyprrice"
            with open(theme_file, 'w', encoding='utf-8') as f:
                yaml.dump(theme_data, f, default_flow_style=False, indent=2)
            
            self.theme_saved.emit(theme_name)
            return True
            
        except Exception as e:
            raise ThemeError(f"Failed to save theme '{theme_name}': {e}")
    
    def import_theme(self, file_path: str) -> bool:
        """Import a theme from a file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise ThemeError(f"File not found: {file_path}")
            
            # Read theme data
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    theme_data = json.load(f)
                else:
                    theme_data = yaml.safe_load(f)
            
            # Get theme name
            theme_name = theme_data.get('name', file_path.stem)
            
            # Save to themes directory
            theme_file = self.themes_dir / f"{theme_name}.hyprrice"
            with open(theme_file, 'w', encoding='utf-8') as f:
                yaml.dump(theme_data, f, default_flow_style=False, indent=2)
            
            return True
            
        except Exception as e:
            raise ThemeError(f"Failed to import theme: {e}")
    
    def export_theme(self, config: Config, file_path: str) -> bool:
        """Export current configuration as a theme file."""
        try:
            file_path = Path(file_path)
            
            # Create theme data
            theme_data = {
                'name': file_path.stem,
                'version': '1.0.0',
                'description': f"Theme exported from current configuration",
                'author': "HyprRice User",
                'config': self._extract_config_data(config)
            }
            
            # Save based on file extension
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    json.dump(theme_data, f, indent=2)
                else:
                    yaml.dump(theme_data, f, default_flow_style=False, indent=2)
            
            return True
            
        except Exception as e:
            raise ThemeError(f"Failed to export theme: {e}")
    
    def preview_theme(self, theme_name: str, config: Config) -> bool:
        """Preview a theme without applying it permanently."""
        try:
            # Load theme into config
            self.load_theme(theme_name, config)
            return True
            
        except Exception as e:
            raise ThemeError(f"Failed to preview theme '{theme_name}': {e}")
    
    def create_theme_template(self) -> Dict[str, Any]:
        """Create a template for new themes."""
        return {
            'name': 'New Theme',
            'version': '1.0.0',
            'description': 'A new HyprRice theme',
            'author': 'HyprRice User',
            'config': {
                'hyprland': {
                    'animations_enabled': True,
                    'animation_duration': 0.5,
                    'animation_curve': 'ease-out',
                    'window_opacity': 1.0,
                    'border_size': 1,
                    'border_color': '#ffffff',
                    'gaps_in': 5,
                    'gaps_out': 10,
                    'blur_enabled': True
                },
                'waybar': {
                    'position': 'top',
                    'height': 30,
                    'background_color': 'rgba(43, 48, 59, 0.5)',
                    'text_color': '#ffffff',
                    'font_family': 'JetBrainsMono Nerd Font',
                    'font_size': 13
                },
                'rofi': {
                    'theme': 'default',
                    'width': 40,
                    'location': 'center',
                    'background_color': '#2e3440',
                    'text_color': '#eceff4',
                    'border_color': '#5e81ac',
                    'font_family': 'JetBrainsMono Nerd Font',
                    'font_size': 14
                }
            }
        }
    
    def get_theme_validation_errors(self, theme_data: Dict[str, Any]) -> List[str]:
        """Validate theme data and return list of errors."""
        errors = []
        
        # Required fields
        required_fields = ['name', 'version']
        for field in required_fields:
            if field not in theme_data:
                errors.append(f"Missing required field: {field}")
        
        return errors
    
    def _apply_theme_to_config(self, theme_data: Dict[str, Any], config: Config):
        """Apply theme data to configuration object."""
        if 'config' not in theme_data:
            return
        
        theme_config = theme_data['config']
        
        # Apply Hyprland settings
        if 'hyprland' in theme_config:
            hyprland_config = theme_config['hyprland']
            for key, value in hyprland_config.items():
                if hasattr(config.hyprland, key):
                    setattr(config.hyprland, key, value)
        
        # Apply Waybar settings
        if 'waybar' in theme_config:
            waybar_config = theme_config['waybar']
            for key, value in waybar_config.items():
                if hasattr(config.waybar, key):
                    setattr(config.waybar, key, value)
        
        # Apply Rofi settings
        if 'rofi' in theme_config:
            rofi_config = theme_config['rofi']
            for key, value in rofi_config.items():
                if hasattr(config.rofi, key):
                    setattr(config.rofi, key, value)
    
    def _extract_config_data(self, config: Config) -> Dict[str, Any]:
        """Extract configuration data for theme creation."""
        return {
            'hyprland': config.hyprland.__dict__,
            'waybar': config.waybar.__dict__,
            'rofi': config.rofi.__dict__,
            'notifications': config.notifications.__dict__,
            'clipboard': config.clipboard.__dict__,
            'lockscreen': config.lockscreen.__dict__
        }