"""
Notification Theming Plugin for HyprRice

Provides theming support for popular notification daemons including:
- Mako (Wayland)
- Dunst (X11/Wayland)
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

from src.hyprrice.plugins import PluginBase, PluginMetadata
from src.hyprrice.utils import run_command


@dataclass
class NotificationTheme:
    """Notification theme data structure"""
    name: str
    background_color: str
    text_color: str
    border_color: str
    progress_color: str = None
    # Urgency-specific colors
    low_background: str = None
    low_text: str = None
    low_border: str = None
    normal_background: str = None
    normal_text: str = None
    normal_border: str = None
    critical_background: str = None
    critical_text: str = None
    critical_border: str = None
    # Additional styling
    border_radius: int = 5
    border_width: int = 2
    padding: int = 10
    margin: int = 5
    font: str = "monospace 11"
    max_visible: int = 5


class NotificationThemingPlugin(PluginBase):
    """Plugin for theming notification daemons"""
    
    def __init__(self):
        super().__init__()
        self.supported_daemons = ['mako', 'dunst']
        self.daemon_configs = {
            'mako': Path.home() / '.config' / 'mako' / 'config',
            'dunst': Path.home() / '.config' / 'dunst' / 'dunstrc'
        }
        
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Notification Theming",
            version="1.0.0",
            description="Provides theming support for notification daemons (mako, dunst)",
            author="HyprRice Team",
            dependencies=[],
            config_schema={
                "enabled_daemons": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["mako", "dunst"]},
                    "default": ["mako"],
                    "description": "Which notification daemons to theme"
                },
                "backup_configs": {
                    "type": "boolean", 
                    "default": True,
                    "description": "Create backups of original notification configs"
                },
                "auto_reload": {
                    "type": "boolean",
                    "default": True, 
                    "description": "Automatically reload notification daemons after theming"
                },
                "border_radius": {
                    "type": "integer",
                    "default": 5,
                    "description": "Border radius for notifications"
                },
                "border_width": {
                    "type": "integer", 
                    "default": 2,
                    "description": "Border width for notifications"
                },
                "max_visible": {
                    "type": "integer",
                    "default": 5,
                    "description": "Maximum visible notifications"
                },
                "font": {
                    "type": "string",
                    "default": "monospace 11",
                    "description": "Font for notifications"
                }
            }
        )
    
    def register(self, app):
        """Register plugin with the main app."""
        super().register(app)
        self.app = app
        
        # Check which notification daemons are available
        self.available_daemons = self._detect_available_daemons()
        self.logger.info(f"Available notification daemons: {self.available_daemons}")
        
    def _detect_available_daemons(self) -> List[str]:
        """Detect which supported notification daemons are installed."""
        available = []
        for daemon in self.supported_daemons:
            if run_command(f"which {daemon}"):
                available.append(daemon)
        return available
    
    def _create_notification_theme_from_hyprland(self, colors: Dict[str, str]) -> NotificationTheme:
        """Create notification theme from Hyprland color scheme."""
        # Map Hyprland colors to notification colors
        theme = NotificationTheme(
            name="HyprRice Notification Theme",
            background_color=colors.get('background', '#1e1e2e'),
            text_color=colors.get('foreground', '#cdd6f4'),
            border_color=colors.get('color4', '#89b4fa'),  # Blue
            progress_color=colors.get('color2', '#a6e3a1'),  # Green
            
            # Low urgency (subtle)
            low_background=colors.get('background', '#1e1e2e'),
            low_text=colors.get('color7', '#bac2de'),  # Muted white
            low_border=colors.get('color8', '#585b70'),  # Bright black
            
            # Normal urgency (default)
            normal_background=colors.get('background', '#1e1e2e'),
            normal_text=colors.get('foreground', '#cdd6f4'),
            normal_border=colors.get('color4', '#89b4fa'),  # Blue
            
            # Critical urgency (attention-grabbing)
            critical_background=colors.get('color1', '#f38ba8'),  # Red background
            critical_text=colors.get('background', '#1e1e2e'),  # Dark text on red
            critical_border=colors.get('color9', '#f38ba8'),  # Bright red
            
            # Styling from config
            border_radius=self.config.get('border_radius', 5),
            border_width=self.config.get('border_width', 2),
            padding=10,
            margin=5,
            font=self.config.get('font', 'monospace 11'),
            max_visible=self.config.get('max_visible', 5)
        )
                
        return theme
    
    def _generate_mako_config(self, theme: NotificationTheme) -> str:
        """Generate mako configuration for the theme."""
        config = f"""# HyprRice Notification Theme - Mako
# Generated automatically by HyprRice Notification Theming Plugin

# Default appearance
background-color={theme.background_color}
text-color={theme.text_color}
border-color={theme.border_color}
progress-color={theme.progress_color}

# Border and padding
border-radius={theme.border_radius}
border-size={theme.border_width}
padding={theme.padding}
margin={theme.margin}

# Font
font={theme.font}

# Behavior
max-visible={theme.max_visible}
sort=-time
layer=overlay
anchor=top-right
width=350
height=100
markup=1
actions=1
history=1
text-alignment=left
default-timeout=5000
ignore-timeout=1

# Grouping
group-by=summary

# Low urgency notifications
[urgency=low]
background-color={theme.low_background}
text-color={theme.low_text}
border-color={theme.low_border}
default-timeout=3000

# Normal urgency notifications  
[urgency=normal]
background-color={theme.normal_background}
text-color={theme.normal_text}
border-color={theme.normal_border}
default-timeout=5000

# Critical urgency notifications
[urgency=critical]
background-color={theme.critical_background}
text-color={theme.critical_text}
border-color={theme.critical_border}
default-timeout=0
ignore-timeout=0

# Application-specific overrides
[app-name="volume"]
group-by=app-name
default-timeout=1000

[app-name="brightness"]
group-by=app-name
default-timeout=1000

[app-name="screenshot"]
default-timeout=2000

[app-name="battery"]
urgency=critical
"""
        return config
    
    def _generate_dunst_config(self, theme: NotificationTheme) -> str:
        """Generate dunst configuration for the theme."""
        config = f"""# HyprRice Notification Theme - Dunst
# Generated automatically by HyprRice Notification Theming Plugin

[global]
    # Display
    monitor = 0
    follow = none
    
    # Geometry
    width = 350
    height = 100
    origin = top-right
    offset = 10x50
    scale = 0
    notification_limit = {theme.max_visible}
    
    # Progress bar
    progress_bar = true
    progress_bar_height = 10
    progress_bar_frame_width = 1
    progress_bar_min_width = 150
    progress_bar_max_width = 300
    
    # Text
    font = {theme.font}
    line_height = 0
    markup = full
    format = "<b>%s</b>\\n%b"
    alignment = left
    vertical_alignment = center
    show_age_threshold = 60
    ellipsize = middle
    ignore_newline = no
    stack_duplicates = true
    hide_duplicate_count = false
    show_indicators = yes
    
    # Icons
    icon_position = left
    min_icon_size = 32
    max_icon_size = 128
    icon_path = /usr/share/icons/gnome/16x16/status/:/usr/share/icons/gnome/16x16/devices/
    
    # History
    sticky_history = yes
    history_length = 20
    
    # Misc/Advanced
    dmenu = /usr/bin/dmenu -p dunst:
    browser = /usr/bin/xdg-open
    always_run_script = true
    title = Dunst
    class = Dunst
    corner_radius = {theme.border_radius}
    ignore_dbusclose = false
    
    # Wayland
    force_xwayland = false
    
    # Legacy
    force_xinerama = false
    
    # Mouse
    mouse_left_click = close_current
    mouse_middle_click = do_action, close_current
    mouse_right_click = close_all

[experimental]
    per_monitor_dpi = false

[urgency_low]
    background = "{theme.low_background}"
    foreground = "{theme.low_text}"
    frame_color = "{theme.low_border}"
    timeout = 3
    
[urgency_normal]
    background = "{theme.normal_background}"
    foreground = "{theme.normal_text}"
    frame_color = "{theme.normal_border}"
    timeout = 5
    
[urgency_critical]
    background = "{theme.critical_background}"
    foreground = "{theme.critical_text}"
    frame_color = "{theme.critical_border}"
    timeout = 0

# Application-specific rules
[volume]
    appname = "volume"
    timeout = 1
    
[brightness]
    appname = "brightness"
    timeout = 1
    
[screenshot]
    appname = "screenshot"
    timeout = 2
"""
        return config
    
    def _backup_config(self, config_path: Path):
        """Create backup of existing notification config."""
        if config_path.exists():
            backup_path = config_path.with_suffix(config_path.suffix + '.hyprrice-backup')
            try:
                import shutil
                shutil.copy2(config_path, backup_path)
                self.logger.info(f"Created backup: {backup_path}")
            except Exception as e:
                self.logger.error(f"Failed to create backup of {config_path}: {e}")
    
    def _apply_mako_theme(self, theme: NotificationTheme):
        """Apply theme to mako notification daemon."""
        config_path = self.daemon_configs['mako']
        
        # Create config directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing config
        if self.config.get('backup_configs', True):
            self._backup_config(config_path)
        
        # Generate and write new config
        theme_config = self._generate_mako_config(theme)
        
        try:
            with open(config_path, 'w') as f:
                f.write(theme_config)
            self.logger.info(f"Applied theme to mako: {config_path}")
            
            # Reload mako if requested
            if self.config.get('auto_reload', True):
                run_command("makoctl reload")
                
        except Exception as e:
            self.logger.error(f"Failed to apply mako theme: {e}")
    
    def _apply_dunst_theme(self, theme: NotificationTheme):
        """Apply theme to dunst notification daemon."""
        config_path = self.daemon_configs['dunst']
        
        # Create config directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing config
        if self.config.get('backup_configs', True):
            self._backup_config(config_path)
        
        # Generate and write new config
        theme_config = self._generate_dunst_config(theme)
        
        try:
            with open(config_path, 'w') as f:
                f.write(theme_config)
            self.logger.info(f"Applied theme to dunst: {config_path}")
            
            # Reload dunst if requested
            if self.config.get('auto_reload', True):
                run_command("killall dunst && dunst &")
                
        except Exception as e:
            self.logger.error(f"Failed to apply dunst theme: {e}")
    
    def apply_theme(self, colors: Dict[str, str]):
        """Apply notification theme based on color scheme."""
        # Create notification theme from colors
        theme = self._create_notification_theme_from_hyprland(colors)
        
        # Get enabled daemons from config
        enabled_daemons = self.config.get('enabled_daemons', ['mako'])
        
        # Apply to each enabled and available daemon
        for daemon in enabled_daemons:
            if daemon in self.available_daemons:
                if daemon == 'mako':
                    self._apply_mako_theme(theme)
                elif daemon == 'dunst':
                    self._apply_dunst_theme(theme)
            else:
                self.logger.warning(f"Notification daemon {daemon} is enabled but not available")
    
    # Event handlers
    def after_theme_change(self, context: Dict[str, Any]):
        """Apply notification theme after Hyprland theme changes."""
        if 'colors' in context:
            self.logger.info("Applying notification theme after theme change")
            self.apply_theme(context['colors'])
    
    def after_apply(self, context: Dict[str, Any]):
        """Apply notification theme after configuration is applied."""
        if 'colors' in context:
            self.logger.info("Applying notification theme after configuration apply")
            self.apply_theme(context['colors'])


# Plugin entry point
plugin_class = NotificationThemingPlugin
