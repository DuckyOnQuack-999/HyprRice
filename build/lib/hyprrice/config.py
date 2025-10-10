"""
Configuration management for HyprRice
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from .exceptions import ConfigError
from .security import input_validator, SecureFileHandler


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
    
    # Hyprbars (titlebars + buttons)
    hyprbars_enabled: bool = False
    hyprbars_height: int = 30
    hyprbars_buttons_size: int = 12
    hyprbars_buttons_gap: int = 8
    hyprbars_buttons_color: str = "#ffffff"
    hyprbars_buttons_hover_color: str = "#ff6b6b"
    hyprbars_title_color: str = "#ffffff"
    hyprbars_title_font: str = "JetBrainsMono Nerd Font"
    hyprbars_title_size: int = 12
    
    # Hyprexpo (exposure / effects plugin)
    hyprexpo_enabled: bool = False
    hyprexpo_workspace_method: str = "first 1"  # first 1, all, or specific workspace
    hyprexpo_workspace_gaps: int = 5
    hyprexpo_workspace_rounding: int = 5
    hyprexpo_workspace_shadow: bool = True
    hyprexpo_workspace_shadow_color: str = "#000000"
    hyprexpo_workspace_shadow_size: int = 4
    hyprexpo_workspace_shadow_offset: str = "0 4"
    
    # Glow via shadows
    glow_enabled: bool = False
    glow_color: str = "#ff6b6b"
    glow_size: int = 8
    glow_offset: str = "0 0"
    glow_opacity: float = 0.8
    glow_blur: int = 4
    
    # Blur shaders
    blur_shaders_enabled: bool = False
    blur_shader_type: str = "kawase"  # kawase, gaussian, or custom
    blur_shader_passes: int = 3
    blur_shader_size: int = 4
    blur_shader_noise: float = 0.0
    blur_shader_contrast: float = 1.0
    blur_shader_brightness: float = 0.0
    blur_shader_vibrancy: float = 0.0
    blur_shader_vibrancy_darkness: float = 0.0
    
    # Sourced configuration files
    sourced_files: list = field(default_factory=lambda: [
        "~/.config/hypr/rules.conf",
        "~/.config/hypr/workspace.conf",
        "~/.config/hypr/exec.conf",
        "~/.config/hypr/colors.conf",
        "~/.config/hypr/general.conf",
        "~/.config/hypr/plugins.conf"
    ])


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
    manager: str = "cliphist"  # cliphist or wl-clipboard
    history_size: int = 100
    auto_sync: bool = True
    sync_interval: int = 30  # seconds
    include_images: bool = True
    include_text: bool = True
    include_files: bool = True
    exclude_patterns: list = field(default_factory=lambda: [
        "password", "secret", "token", "key"
    ])
    max_item_size: int = 1024 * 1024  # 1MB


@dataclass
class LockscreenConfig:
    """Lockscreen configuration."""
    daemon: str = "hyprlock"  # hyprlock or swaylock
    background: str = "~/.config/hyprlock/background.jpg"
    timeout: int = 300  # seconds
    grace_period: int = 5  # seconds
    fade_in: bool = True
    fade_out: bool = True
    fade_time: float = 0.5
    show_clock: bool = True
    clock_format: str = "%H:%M:%S"
    show_date: bool = True
    date_format: str = "%Y-%m-%d"
    font_family: str = "JetBrainsMono Nerd Font"
    font_size: int = 24
    text_color: str = "#ffffff"
    background_color: str = "#000000"
    border_color: str = "#5e81ac"
    border_size: int = 2
    blur_background: bool = True
    blur_size: int = 8
    animation_duration: float = 0.3


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
        """Expand all path configurations with security validation."""
        for field_name in self.paths.__dataclass_fields__:
            path_value = getattr(self.paths, field_name)
            if isinstance(path_value, str) and path_value.startswith("~"):
                try:
                    # Validate path before expansion
                    expanded_path = os.path.expanduser(path_value)
                    validated_path = input_validator.validate_path(expanded_path)
                    setattr(self.paths, field_name, str(validated_path))
                except Exception as e:
                    # Log error but don't fail completely - use safe default
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Invalid path {path_value} for {field_name}: {e}")
                    # Set to a safe default path
                    safe_default = os.path.expanduser(f"~/.config/hyprrice/{field_name}")
                    setattr(self.paths, field_name, safe_default)
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from file with security validation."""
        if config_path is None:
            config_path = cls._get_default_config_path()
        
        config_path = Path(config_path)
        
        if not config_path.exists():
            # Create default configuration
            config = cls()
            config.save(config_path)
            return config
        
        try:
            # Use secure file handler
            secure_handler = SecureFileHandler()
            data = secure_handler.safe_read_yaml(config_path)
            
            return cls._from_dict(data)
        except Exception as e:
            raise ConfigError(f"Failed to load configuration from {config_path}: {e}")
    
    def save(self, config_path: Optional[str] = None) -> None:
        """Save configuration to file with security validation."""
        if config_path is None:
            config_path = self._get_default_config_path()
        
        config_path = Path(config_path)
        
        try:
            # Use secure file handler
            secure_handler = SecureFileHandler()
            data = self._to_dict()
            secure_handler.safe_write_yaml(data, config_path)
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
        
        # Validate Hyprland values
        if not 0 <= self.hyprland.window_opacity <= 1:
            raise ConfigError("Window opacity must be between 0 and 1")
        
        if self.hyprland.border_size < 0:
            raise ConfigError("Border size must be non-negative")
        
        if self.hyprland.gaps_in < 0 or self.hyprland.gaps_out < 0:
            raise ConfigError("Gaps must be non-negative")
        
        if not 0.1 <= self.hyprland.animation_duration <= 5.0:
            raise ConfigError("Animation duration must be between 0.1 and 5.0 seconds")
        
        if self.hyprland.blur_size < 0:
            raise ConfigError("Blur size must be non-negative")
        
        # Validate Waybar values
        if self.waybar.height < 10 or self.waybar.height > 100:
            raise ConfigError("Waybar height must be between 10 and 100 pixels")
        
        if self.waybar.font_size < 8 or self.waybar.font_size > 32:
            raise ConfigError("Waybar font size must be between 8 and 32")
        
        # Validate Rofi values
        if self.rofi.width < 10 or self.rofi.width > 100:
            raise ConfigError("Rofi width must be between 10 and 100 percent")
        
        if self.rofi.font_size < 8 or self.rofi.font_size > 32:
            raise ConfigError("Rofi font size must be between 8 and 32")
        
        # Validate notification values
        if self.notifications.timeout < 100 or self.notifications.timeout > 30000:
            raise ConfigError("Notification timeout must be between 100 and 30000 milliseconds")
        
        if self.notifications.font_size < 8 or self.notifications.font_size > 32:
            raise ConfigError("Notification font size must be between 8 and 32")
        
        # Validate clipboard values
        if self.clipboard.history_size < 10 or self.clipboard.history_size > 10000:
            raise ConfigError("Clipboard history size must be between 10 and 10000")
        
        if self.clipboard.sync_interval < 1 or self.clipboard.sync_interval > 3600:
            raise ConfigError("Clipboard sync interval must be between 1 and 3600 seconds")
        
        # Validate lockscreen values
        if self.lockscreen.timeout < 0 or self.lockscreen.timeout > 3600:
            raise ConfigError("Lockscreen timeout must be between 0 and 3600 seconds")
        
        if self.lockscreen.grace_period < 0 or self.lockscreen.grace_period > 60:
            raise ConfigError("Lockscreen grace period must be between 0 and 60 seconds")
        
        if self.lockscreen.font_size < 8 or self.lockscreen.font_size > 48:
            raise ConfigError("Lockscreen font size must be between 8 and 48")
        
        if not 0.1 <= self.lockscreen.animation_duration <= 2.0:
            raise ConfigError("Lockscreen animation duration must be between 0.1 and 2.0 seconds")
        
        # Validate GUI values
        if self.gui.window_width < 800 or self.gui.window_width > 3840:
            raise ConfigError("GUI window width must be between 800 and 3840 pixels")
        
        if self.gui.window_height < 600 or self.gui.window_height > 2160:
            raise ConfigError("GUI window height must be between 600 and 2160 pixels")
        
        if self.gui.auto_save_interval < 5 or self.gui.auto_save_interval > 300:
            raise ConfigError("Auto-save interval must be between 5 and 300 seconds")
        
        # Validate general values
        if self.general.backup_retention < 1 or self.general.backup_retention > 100:
            raise ConfigError("Backup retention must be between 1 and 100")
        
        return True 
