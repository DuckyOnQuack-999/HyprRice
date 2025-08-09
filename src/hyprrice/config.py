"""
Configuration management for HyprRice
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from .exceptions import ConfigError


@dataclass
class GeneralConfig:
    """General application configuration."""
    auto_backup: bool = True
    backup_retention: int = 10
    live_preview: bool = True
    theme: str = "auto"
    language: str = "en"


@dataclass
class PathsConfig:
    """Path configuration."""
    hyprland_config: str = "~/.config/hypr/hyprland.conf"
    waybar_config: str = "~/.config/waybar/"
    rofi_config: str = "~/.config/rofi/"
    dunst_config: str = "~/.config/dunst/"
    mako_config: str = "~/.config/mako/"
    backup_dir: str = "~/.hyprrice/backups/"
    log_dir: str = "~/.hyprrice/logs/"
    theme_dir: str = "~/.hyprrice/themes/"


@dataclass
class GUIConfig:
    """GUI configuration."""
    theme: str = "dark"
    window_width: int = 1200
    window_height: int = 800
    show_tooltips: bool = True
    show_status_bar: bool = True
    auto_save: bool = True
    auto_save_interval: int = 30  # seconds


@dataclass
class HyprlandConfig:
    """Hyprland-specific configuration."""
    animations_enabled: bool = True
    animation_duration: float = 0.5
    animation_curve: str = "ease-out"
    window_opacity: float = 1.0
    border_size: int = 1
    border_color: str = "#ffffff"
    gaps_in: int = 5
    gaps_out: int = 10
    smart_gaps: bool = True
    smart_borders: bool = True
    blur_enabled: bool = True
    blur_size: int = 8
    blur_passes: int = 1


@dataclass
class WaybarConfig:
    """Waybar-specific configuration."""
    position: str = "top"
    height: int = 30
    background_color: str = "rgba(43, 48, 59, 0.5)"
    border_color: str = "rgba(100, 115, 245, 0.5)"
    text_color: str = "#ffffff"
    font_family: str = "JetBrainsMono Nerd Font"
    font_size: int = 13
    modules: list = field(default_factory=lambda: [
        "clock", "battery", "network", "cpu", "memory", "tray"
    ])


@dataclass
class RofiConfig:
    """Rofi-specific configuration."""
    theme: str = "default"
    width: int = 40
    location: str = "center"
    anchor: str = "center"
    background_color: str = "#2e3440"
    text_color: str = "#eceff4"
    border_color: str = "#5e81ac"
    font_family: str = "JetBrainsMono Nerd Font"
    font_size: int = 14


@dataclass
class NotificationConfig:
    """Notification daemon configuration."""
    daemon: str = "dunst"  # dunst or mako
    position: str = "top-right"
    timeout: int = 5000
    background_color: str = "#2e3440"
    text_color: str = "#eceff4"
    border_color: str = "#5e81ac"
    font_family: str = "JetBrainsMono Nerd Font"
    font_size: int = 12


@dataclass
class ClipboardConfig:
    """Clipboard manager configuration."""
    manager: str = "cliphist"  # cliphist, wl-clipboard, clipman
    history_size: int = 100
    max_item_size: int = 1024  # KB
    enable_images: bool = True
    enable_primary_selection: bool = True
    persist_history: bool = True
    exclude_patterns: List[str] = field(default_factory=lambda: ["password", "secret"])


@dataclass
class LockscreenConfig:
    """Lockscreen configuration."""
    locker: str = "hyprlock"  # hyprlock, swaylock
    background_type: str = "image"  # image, color, blur
    background_path: str = ""
    background_color: str = "#000000"
    timeout: int = 300  # seconds
    grace_period: int = 5  # seconds
    show_failed_attempts: bool = True
    keyboard_layout: str = "us"
    input_field_color: str = "#ffffff"
    text_color: str = "#ffffff"
    font_family: str = "JetBrainsMono Nerd Font"
    font_size: int = 14


@dataclass
class Config:
    """Main configuration class."""
    general: GeneralConfig = field(default_factory=GeneralConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    gui: GUIConfig = field(default_factory=GUIConfig)
    hyprland: HyprlandConfig = field(default_factory=HyprlandConfig)
    waybar: WaybarConfig = field(default_factory=WaybarConfig)
    rofi: RofiConfig = field(default_factory=RofiConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    clipboard: ClipboardConfig = field(default_factory=ClipboardConfig)
    lockscreen: LockscreenConfig = field(default_factory=LockscreenConfig)
    
    def __post_init__(self):
        """Expand paths after initialization."""
        self._expand_paths()
    
    def _expand_paths(self):
        """Expand all path configurations."""
        for field_name in self.paths.__dataclass_fields__:
            path_value = getattr(self.paths, field_name)
            if isinstance(path_value, str) and path_value.startswith("~"):
                expanded_path = os.path.expanduser(path_value)
                setattr(self.paths, field_name, expanded_path)
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from file."""
        if config_path is None:
            config_path = cls._get_default_config_path()
        
        config_path = Path(config_path)
        
        if not config_path.exists():
            # Create default configuration
            config = cls()
            config.save(config_path)
            return config
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            return cls._from_dict(data)
        except Exception as e:
            raise ConfigError(f"Failed to load configuration from {config_path}: {e}")
    
    def save(self, config_path: Optional[str] = None) -> None:
        """Save configuration to file."""
        if config_path is None:
            config_path = self._get_default_config_path()
        
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            data = self._to_dict()
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ConfigError(f"Failed to save configuration to {config_path}: {e}")
    
    def _to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'general': self.general.__dict__,
            'paths': self.paths.__dict__,
            'gui': self.gui.__dict__,
            'hyprland': self.hyprland.__dict__,
            'waybar': self.waybar.__dict__,
            'rofi': self.rofi.__dict__,
            'notifications': self.notifications.__dict__,
            'clipboard': self.clipboard.__dict__,
            'lockscreen': self.lockscreen.__dict__,
        }
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create configuration from dictionary."""
        config = cls()
        
        if 'general' in data:
            for key, value in data['general'].items():
                if hasattr(config.general, key):
                    setattr(config.general, key, value)
        
        if 'paths' in data:
            for key, value in data['paths'].items():
                if hasattr(config.paths, key):
                    setattr(config.paths, key, value)
        
        if 'gui' in data:
            for key, value in data['gui'].items():
                if hasattr(config.gui, key):
                    setattr(config.gui, key, value)
        
        if 'hyprland' in data:
            for key, value in data['hyprland'].items():
                if hasattr(config.hyprland, key):
                    setattr(config.hyprland, key, value)
        
        if 'waybar' in data:
            for key, value in data['waybar'].items():
                if hasattr(config.waybar, key):
                    setattr(config.waybar, key, value)
        
        if 'rofi' in data:
            for key, value in data['rofi'].items():
                if hasattr(config.rofi, key):
                    setattr(config.rofi, key, value)
        
        if 'notifications' in data:
            for key, value in data['notifications'].items():
                if hasattr(config.notifications, key):
                    setattr(config.notifications, key, value)
        
        if 'clipboard' in data:
            for key, value in data['clipboard'].items():
                if hasattr(config.clipboard, key):
                    setattr(config.clipboard, key, value)
        
        if 'lockscreen' in data:
            for key, value in data['lockscreen'].items():
                if hasattr(config.lockscreen, key):
                    setattr(config.lockscreen, key, value)
        
        config._expand_paths()
        return config
    
    @staticmethod
    def _get_default_config_path() -> str:
        """Get default configuration file path."""
        return os.path.expanduser("~/.config/hyprrice/config.yaml")
    
    def get_path(self, path_name: str) -> str:
        """Get expanded path by name."""
        return getattr(self.paths, path_name)
    
    def validate(self) -> bool:
        """Validate configuration."""
        # Validate paths
        required_paths = ['hyprland_config', 'waybar_config', 'rofi_config']
        for path_name in required_paths:
            path = self.get_path(path_name)
            if not path:
                raise ConfigError(f"Required path '{path_name}' is not set")
        
        # Validate values
        if not 0 <= self.hyprland.window_opacity <= 1:
            raise ConfigError("Window opacity must be between 0 and 1")
        
        if self.hyprland.border_size < 0:
            raise ConfigError("Border size must be non-negative")
        
        if self.hyprland.gaps_in < 0 or self.hyprland.gaps_out < 0:
            raise ConfigError("Gaps must be non-negative")
        
        # Validate clipboard settings
        if self.clipboard.history_size <= 0:
            raise ConfigError("Clipboard history size must be positive")
        
        if self.clipboard.max_item_size <= 0:
            raise ConfigError("Clipboard max item size must be positive")
        
        # Validate lockscreen settings
        if self.lockscreen.timeout < 0:
            raise ConfigError("Lockscreen timeout must be non-negative")
        
        if self.lockscreen.grace_period < 0:
            raise ConfigError("Grace period must be non-negative")
        
        return True 