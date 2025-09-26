"""
Terminal Theming Plugin for HyprRice

Provides theming support for popular terminal emulators including:
- Kitty
- Alacritty
- (Future: wezterm, foot, etc.)
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
class TerminalTheme:
    """Terminal theme data structure"""
    name: str
    background: str
    foreground: str
    cursor: str = None
    selection_background: str = None
    selection_foreground: str = None
    # Standard 16 colors
    black: str = "#000000"
    red: str = "#FF0000"
    green: str = "#00FF00"
    yellow: str = "#FFFF00"
    blue: str = "#0000FF"
    magenta: str = "#FF00FF"
    cyan: str = "#00FFFF"
    white: str = "#FFFFFF"
    bright_black: str = "#808080"
    bright_red: str = "#FF8080"
    bright_green: str = "#80FF80"
    bright_yellow: str = "#FFFF80"
    bright_blue: str = "#8080FF"
    bright_magenta: str = "#FF80FF"
    bright_cyan: str = "#80FFFF"
    bright_white: str = "#FFFFFF"


class TerminalThemingPlugin(PluginBase):
    """Plugin for theming terminal emulators"""
    
    def __init__(self):
        super().__init__()
        self.supported_terminals = ['kitty', 'alacritty']
        self.terminal_configs = {
            'kitty': Path.home() / '.config' / 'kitty' / 'kitty.conf',
            'alacritty': Path.home() / '.config' / 'alacritty' / 'alacritty.yml'
        }
        # Initialize available terminals immediately
        self.available_terminals = self._detect_available_terminals()
        
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Terminal Theming",
            version="1.0.0",
            description="Provides theming support for terminal emulators (kitty, alacritty)",
            author="HyprRice Team",
            dependencies=[],
            config_schema={
                "enabled_terminals": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["kitty", "alacritty"]},
                    "default": ["kitty", "alacritty"],
                    "description": "Which terminal emulators to theme"
                },
                "backup_configs": {
                    "type": "boolean", 
                    "default": True,
                    "description": "Create backups of original terminal configs"
                },
                "auto_reload": {
                    "type": "boolean",
                    "default": True, 
                    "description": "Automatically reload terminal configs after theming"
                }
            }
        )
    
    def register(self, app):
        """Register plugin with the main app."""
        super().register(app)
        self.app = app
        
        # Log available terminals (already detected in __init__)
        self.logger.info(f"Available terminals: {self.available_terminals}")
        
    def _detect_available_terminals(self) -> List[str]:
        """Detect which supported terminals are installed."""
        available = []
        for terminal in self.supported_terminals:
            if run_command(f"which {terminal}"):
                available.append(terminal)
        return available
    
    def _create_terminal_theme_from_hyprland(self, colors: Dict[str, str]) -> TerminalTheme:
        """Create terminal theme from Hyprland color scheme."""
        # Map Hyprland colors to terminal colors
        theme = TerminalTheme(
            name="HyprRice Theme",
            background=colors.get('background', '#1e1e2e'),
            foreground=colors.get('foreground', '#cdd6f4'),
            cursor=colors.get('cursor', colors.get('foreground', '#cdd6f4')),
            selection_background=colors.get('selection_background', '#313244'),
            selection_foreground=colors.get('selection_foreground', colors.get('foreground', '#cdd6f4')),
        )
        
        # Map standard colors
        color_mapping = {
            'black': colors.get('color0', '#45475a'),
            'red': colors.get('color1', '#f38ba8'),
            'green': colors.get('color2', '#a6e3a1'),
            'yellow': colors.get('color3', '#f9e2af'),
            'blue': colors.get('color4', '#89b4fa'),
            'magenta': colors.get('color5', '#f5c2e7'),
            'cyan': colors.get('color6', '#94e2d5'),
            'white': colors.get('color7', '#bac2de'),
            'bright_black': colors.get('color8', '#585b70'),
            'bright_red': colors.get('color9', '#f38ba8'),
            'bright_green': colors.get('color10', '#a6e3a1'),
            'bright_yellow': colors.get('color11', '#f9e2af'),
            'bright_blue': colors.get('color12', '#89b4fa'),
            'bright_magenta': colors.get('color13', '#f5c2e7'),
            'bright_cyan': colors.get('color14', '#94e2d5'),
            'bright_white': colors.get('color15', '#a6adc8'),
        }
        
        for attr, color in color_mapping.items():
            if color:
                setattr(theme, attr, color)
                
        return theme
    
    def _generate_kitty_config(self, theme: TerminalTheme) -> str:
        """Generate kitty configuration for the theme."""
        config = f"""# HyprRice Terminal Theme - Kitty
# Generated automatically by HyprRice Terminal Theming Plugin

# Basic colors
foreground {theme.foreground}
background {theme.background}
selection_foreground {theme.selection_foreground or theme.foreground}
selection_background {theme.selection_background or theme.background}

# Cursor colors
cursor {theme.cursor or theme.foreground}
cursor_text_color {theme.background}

# URL underline color when hovering with mouse
url_color {theme.blue}

# Kitty window border colors
active_border_color {theme.blue}
inactive_border_color {theme.bright_black}
bell_border_color {theme.red}

# OS Window titlebar colors
wayland_titlebar_color {theme.background}

# Tab bar colors
active_tab_foreground {theme.background}
active_tab_background {theme.blue}
inactive_tab_foreground {theme.foreground}
inactive_tab_background {theme.bright_black}
tab_bar_background {theme.background}

# Colors for marks (marked text in the terminal)
mark1_foreground {theme.background}
mark1_background {theme.blue}
mark2_foreground {theme.background}
mark2_background {theme.magenta}
mark3_foreground {theme.background}
mark3_background {theme.cyan}

# The 16 terminal colors

# black
color0 {theme.black}
color8 {theme.bright_black}

# red
color1 {theme.red}
color9 {theme.bright_red}

# green
color2 {theme.green}
color10 {theme.bright_green}

# yellow
color3 {theme.yellow}
color11 {theme.bright_yellow}

# blue
color4 {theme.blue}
color12 {theme.bright_blue}

# magenta
color5 {theme.magenta}
color13 {theme.bright_magenta}

# cyan
color6 {theme.cyan}
color14 {theme.bright_cyan}

# white
color7 {theme.white}
color15 {theme.bright_white}
"""
        return config
    
    def _generate_alacritty_config(self, theme: TerminalTheme) -> str:
        """Generate alacritty configuration for the theme."""
        config = f"""# HyprRice Terminal Theme - Alacritty
# Generated automatically by HyprRice Terminal Theming Plugin

colors:
  # Default colors
  primary:
    background: '{theme.background}'
    foreground: '{theme.foreground}'
    dim_foreground: '{theme.bright_black}'
    bright_foreground: '{theme.bright_white}'

  # Cursor colors
  cursor:
    text: '{theme.background}'
    cursor: '{theme.cursor or theme.foreground}'

  # Vi mode cursor colors
  vi_mode_cursor:
    text: '{theme.background}'
    cursor: '{theme.cursor or theme.foreground}'

  # Search colors
  search:
    matches:
      foreground: '{theme.background}'
      background: '{theme.yellow}'
    focused_match:
      foreground: '{theme.background}'
      background: '{theme.green}'

  # Keyboard regex hints
  hints:
    start:
      foreground: '{theme.background}'
      background: '{theme.yellow}'
    end:
      foreground: '{theme.background}'
      background: '{theme.green}'

  # Line indicator
  line_indicator:
    foreground: None
    background: None

  # Footer bar
  footer_bar:
    foreground: '{theme.foreground}'
    background: '{theme.bright_black}'

  # Selection colors
  selection:
    text: '{theme.selection_foreground or theme.foreground}'
    background: '{theme.selection_background or theme.bright_black}'

  # Normal colors
  normal:
    black:   '{theme.black}'
    red:     '{theme.red}'
    green:   '{theme.green}'
    yellow:  '{theme.yellow}'
    blue:    '{theme.blue}'
    magenta: '{theme.magenta}'
    cyan:    '{theme.cyan}'
    white:   '{theme.white}'

  # Bright colors
  bright:
    black:   '{theme.bright_black}'
    red:     '{theme.bright_red}'
    green:   '{theme.bright_green}'
    yellow:  '{theme.bright_yellow}'
    blue:    '{theme.bright_blue}'
    magenta: '{theme.bright_magenta}'
    cyan:    '{theme.bright_cyan}'
    white:   '{theme.bright_white}'

  # Dim colors
  dim:
    black:   '{theme.bright_black}'
    red:     '{theme.red}'
    green:   '{theme.green}'
    yellow:  '{theme.yellow}'
    blue:    '{theme.blue}'
    magenta: '{theme.magenta}'
    cyan:    '{theme.cyan}'
    white:   '{theme.white}'

  # Indexed Colors
  indexed_colors: []
"""
        return config
    
    def _backup_config(self, config_path: Path):
        """Create backup of existing terminal config."""
        if config_path.exists():
            backup_path = config_path.with_suffix(config_path.suffix + '.hyprrice-backup')
            try:
                import shutil
                shutil.copy2(config_path, backup_path)
                self.logger.info(f"Created backup: {backup_path}")
            except Exception as e:
                self.logger.error(f"Failed to create backup of {config_path}: {e}")
    
    def _apply_kitty_theme(self, theme: TerminalTheme):
        """Apply theme to kitty terminal."""
        config_path = self.terminal_configs['kitty']
        
        # Create config directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing config
        if self.config.get('backup_configs', True):
            self._backup_config(config_path)
        
        # Generate and write new config
        theme_config = self._generate_kitty_config(theme)
        
        try:
            with open(config_path, 'w') as f:
                f.write(theme_config)
            self.logger.info(f"Applied theme to kitty: {config_path}")
            
            # Reload kitty if requested
            if self.config.get('auto_reload', True):
                run_command("killall -SIGUSR1 kitty")
                
        except Exception as e:
            self.logger.error(f"Failed to apply kitty theme: {e}")
    
    def _apply_alacritty_theme(self, theme: TerminalTheme):
        """Apply theme to alacritty terminal."""
        config_path = self.terminal_configs['alacritty']
        
        # Create config directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing config
        if self.config.get('backup_configs', True):
            self._backup_config(config_path)
        
        # Generate and write new config
        theme_config = self._generate_alacritty_config(theme)
        
        try:
            with open(config_path, 'w') as f:
                f.write(theme_config)
            self.logger.info(f"Applied theme to alacritty: {config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to apply alacritty theme: {e}")
    
    def apply_theme(self, colors: Dict[str, str]):
        """Apply terminal theme based on color scheme."""
        # Create terminal theme from colors
        theme = self._create_terminal_theme_from_hyprland(colors)
        
        # Get enabled terminals from config
        enabled_terminals = self.config.get('enabled_terminals', ['kitty', 'alacritty'])
        
        # Apply to each enabled and available terminal
        for terminal in enabled_terminals:
            if terminal in self.available_terminals:
                if terminal == 'kitty':
                    self._apply_kitty_theme(theme)
                elif terminal == 'alacritty':
                    self._apply_alacritty_theme(theme)
            else:
                self.logger.warning(f"Terminal {terminal} is enabled but not available")
    
    # Event handlers
    def after_theme_change(self, context: Dict[str, Any]):
        """Apply terminal theme after Hyprland theme changes."""
        if 'colors' in context:
            self.logger.info("Applying terminal theme after theme change")
            self.apply_theme(context['colors'])
    
    def after_apply(self, context: Dict[str, Any]):
        """Apply terminal theme after configuration is applied."""
        if 'colors' in context:
            self.logger.info("Applying terminal theme after configuration apply")
            self.apply_theme(context['colors'])


# Plugin entry point - this is what the plugin manager will look for
plugin_class = TerminalThemingPlugin
