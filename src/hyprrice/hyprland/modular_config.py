"""
Modular Hyprland configuration generator

Generates separate configuration files for colors, general settings, and plugins
to provide better organization and modularity.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from ..config import Config, HyprlandConfig
from ..exceptions import HyprRiceError


class ModularConfigGenerator:
    """Generates modular Hyprland configuration files."""
    
    def __init__(self, config: Config):
        self.config = config
        self.hypr_config = config.hyprland
        self.logger = logging.getLogger(__name__)
        
        # Get Hyprland config directory
        if self.hypr_config.sourced_files:
            self.hypr_dir = Path(self.hypr_config.sourced_files[0]).parent.expanduser()
        else:
            # Fallback to default Hyprland config directory
            self.hypr_dir = Path.home() / ".config" / "hypr"
        self.hypr_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all_configs(self) -> Dict[str, str]:
        """Generate all modular configuration files."""
        configs = {}
        
        try:
            # Generate colors.conf
            colors_path = self.hypr_dir / "colors.conf"
            colors_content = self._generate_colors_config()
            configs['colors.conf'] = colors_content
            
            # Generate general.conf
            general_path = self.hypr_dir / "general.conf"
            general_content = self._generate_general_config()
            configs['general.conf'] = general_content
            
            # Generate plugins.conf
            plugins_path = self.hypr_dir / "plugins.conf"
            plugins_content = self._generate_plugins_config()
            configs['plugins.conf'] = plugins_content
            
            # Write all files
            for filename, content in configs.items():
                file_path = self.hypr_dir / filename
                # Ensure directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)
                self.logger.info(f"Generated {filename}")
            
            return configs
            
        except Exception as e:
            self.logger.error(f"Failed to generate modular configs: {e}")
            raise HyprRiceError(f"Failed to generate modular configs: {e}")
    
    def _generate_colors_config(self) -> str:
        """Generate colors.conf with all color definitions."""
        content = [
            "# HyprRice Generated Colors Configuration",
            "# This file contains all color definitions",
            "",
            "# General Colors",
            f"$primary = {self.hypr_config.border_color}",
            f"$secondary = {self.hypr_config.hyprbars_buttons_color}",
            f"$accent = {self.hypr_config.hyprbars_buttons_hover_color}",
            f"$text = {self.hypr_config.hyprbars_title_color}",
            "",
            "# Hyprbars Colors",
            f"$hyprbars_bg = rgba(00000000)",
            f"$hyprbars_border = {self.hypr_config.border_color}",
            f"$hyprbars_text = {self.hypr_config.hyprbars_title_color}",
            f"$hyprbars_button = {self.hypr_config.hyprbars_buttons_color}",
            f"$hyprbars_button_hover = {self.hypr_config.hyprbars_buttons_hover_color}",
            "",
            "# Hyprexpo Colors",
            f"$hyprexpo_bg = rgba(00000000)",
            f"$hyprexpo_border = {self.hypr_config.border_color}",
            f"$hyprexpo_shadow = {self.hypr_config.hyprexpo_workspace_shadow_color}",
            "",
            "# Glow Colors",
            f"$glow_color = {self.hypr_config.glow_color}",
            "",
            "# Blur Shader Colors",
            "$blur_shader_bg = rgba(00000000)",
            "",
            "# Window Colors",
            f"$window_border = {self.hypr_config.border_color}",
            f"$window_border_active = {self.hypr_config.hyprbars_buttons_hover_color}",
            "",
            "# Workspace Colors",
            "$workspace_bg = rgba(00000000)",
            f"$workspace_border = {self.hypr_config.border_color}",
            f"$workspace_border_active = {self.hypr_config.hyprbars_buttons_hover_color}",
            "",
            "# Group Colors",
            "$group_bg = rgba(00000000)",
            f"$group_border = {self.hypr_config.border_color}",
            f"$group_border_active = {self.hypr_config.hyprbars_buttons_hover_color}",
            "",
            "# Decoration Colors",
            f"$decoration_border = {self.hypr_config.border_color}",
            f"$decoration_border_active = {self.hypr_config.hyprbars_buttons_hover_color}",
            "",
            "# Animation Colors",
            f"$animation_color = {self.hypr_config.hyprbars_buttons_hover_color}",
            "",
            "# Special Colors",
            "$special_bg = rgba(00000000)",
            f"$special_border = {self.hypr_config.border_color}",
            f"$special_border_active = {self.hypr_config.hyprbars_buttons_hover_color}",
            "",
            "# Urgent Colors",
            "$urgent_bg = rgba(ff000000)",
            "$urgent_border = rgba(ff0000ff)",
            "$urgent_text = rgba(ffffffff)",
            "",
            "# Dim Colors",
            "$dim_bg = rgba(00000000)",
            "$dim_border = rgba(00000000)",
            "",
            "# Lock Colors",
            "$lock_bg = rgba(00000000)",
            "$lock_border = rgba(00000000)",
            "",
            "# Input Colors",
            "$input_bg = rgba(00000000)",
            f"$input_border = {self.hypr_config.border_color}",
            f"$input_border_active = {self.hypr_config.hyprbars_buttons_hover_color}",
            "",
            "# Misc Colors",
            "$misc_bg = rgba(00000000)",
            f"$misc_border = {self.hypr_config.border_color}",
            f"$misc_border_active = {self.hypr_config.hyprbars_buttons_hover_color}",
        ]
        
        return "\n".join(content)
    
    def _generate_general_config(self) -> str:
        """Generate general.conf with general WM settings."""
        content = [
            "# HyprRice Generated General Configuration",
            "# This file contains general window manager settings",
            "",
            "# General Settings",
            f"general:border_size = {self.hypr_config.border_size}",
            f"general:gaps_in = {self.hypr_config.gaps_in}",
            f"general:gaps_out = {self.hypr_config.gaps_out}",
            f"general:col.active_border = $window_border_active",
            f"general:col.inactive_border = $window_border",
            f"general:col.group_border = $group_border",
            f"general:col.group_border_active = $group_border_active",
            f"general:col.group_border_locked_active = $group_border_active",
            f"general:col.group_border_locked = $group_border",
            f"general:col.urgent_border = $urgent_border",
            f"general:col.urgent_bg = $urgent_bg",
            f"general:col.urgent_text = $urgent_text",
            f"general:col.special_border = $special_border",
            f"general:col.special_border_active = $special_border_active",
            f"general:col.special_bg = $special_bg",
            f"general:col.dim_bg = $dim_bg",
            f"general:col.dim_border = $dim_border",
            f"general:col.lock_bg = $lock_bg",
            f"general:col.lock_border = $lock_border",
            f"general:col.input_bg = $input_bg",
            f"general:col.input_border = $input_border",
            f"general:col.input_border_active = $input_border_active",
            f"general:col.misc_bg = $misc_bg",
            f"general:col.misc_border = $misc_border",
            f"general:col.misc_border_active = $misc_border_active",
            f"general:col.workspace_bg = $workspace_bg",
            f"general:col.workspace_border = $workspace_border",
            f"general:col.workspace_border_active = $workspace_border_active",
            f"general:col.decoration_border = $decoration_border",
            f"general:col.decoration_border_active = $decoration_border_active",
            f"general:col.animation_color = $animation_color",
            f"general:col.group_bg = $group_bg",
            f"general:col.group_border = $group_border",
            f"general:col.group_border_active = $group_border_active",
            f"general:col.group_border_locked_active = $group_border_active",
            f"general:col.group_border_locked = $group_border",
            f"general:col.urgent_border = $urgent_border",
            f"general:col.urgent_bg = $urgent_bg",
            f"general:col.urgent_text = $urgent_text",
            f"general:col.special_border = $special_border",
            f"general:col.special_border_active = $special_border_active",
            f"general:col.special_bg = $special_bg",
            f"general:col.dim_bg = $dim_bg",
            f"general:col.dim_border = $dim_border",
            f"general:col.lock_bg = $lock_bg",
            f"general:col.lock_border = $lock_border",
            f"general:col.input_bg = $input_bg",
            f"general:col.input_border = $input_border",
            f"general:col.input_border_active = $input_border_active",
            f"general:col.misc_bg = $misc_bg",
            f"general:col.misc_border = $misc_border",
            f"general:col.misc_border_active = $misc_border_active",
            f"general:col.workspace_bg = $workspace_bg",
            f"general:col.workspace_border = $workspace_border",
            f"general:col.workspace_border_active = $workspace_border_active",
            f"general:col.decoration_border = $decoration_border",
            f"general:col.decoration_border_active = $decoration_border_active",
            f"general:col.animation_color = $animation_color",
            "",
            "# Layout Settings",
            "general:layout = dwindle",
            "",
            "# Border Settings",
            f"general:border_size = {self.hypr_config.border_size}",
            f"general:gaps_in = {self.hypr_config.gaps_in}",
            f"general:gaps_out = {self.hypr_config.gaps_out}",
            "",
            "# Smart Settings",
            f"general:smart_gaps = {str(self.hypr_config.smart_gaps).lower()}",
            f"general:smart_borders = {str(self.hypr_config.smart_borders).lower()}",
            "",
            "# Window Settings",
            f"general:window_opacity = {self.hypr_config.window_opacity}",
            "",
            "# Animation Settings",
            f"general:animations_enabled = {str(self.hypr_config.animations_enabled).lower()}",
            f"general:animation_duration = {self.hypr_config.animation_duration}",
            f"general:animation_curve = {self.hypr_config.animation_curve}",
            "",
            "# Blur Settings",
            f"general:blur_enabled = {str(self.hypr_config.blur_enabled).lower()}",
            f"general:blur_size = {self.hypr_config.blur_size}",
            f"general:blur_passes = {self.hypr_config.blur_passes}",
            "",
            "# Glow Settings",
            f"general:glow_enabled = {str(self.hypr_config.glow_enabled).lower()}",
            f"general:glow_color = {self.hypr_config.glow_color}",
            f"general:glow_size = {self.hypr_config.glow_size}",
            f"general:glow_offset = {self.hypr_config.glow_offset}",
            f"general:glow_opacity = {self.hypr_config.glow_opacity}",
            f"general:glow_blur = {self.hypr_config.glow_blur}",
        ]
        
        return "\n".join(content)
    
    def _generate_plugins_config(self) -> str:
        """Generate plugins.conf with plugin-specific configurations."""
        content = [
            "# HyprRice Generated Plugins Configuration",
            "# This file contains plugin-specific configurations",
            "",
        ]
        
        # Hyprbars configuration
        if self.hypr_config.hyprbars_enabled:
            content.extend([
                "# Hyprbars Configuration",
                f"plugin:hyprbars:enabled = true",
                f"plugin:hyprbars:height = {self.hypr_config.hyprbars_height}",
                f"plugin:hyprbars:buttons_size = {self.hypr_config.hyprbars_buttons_size}",
                f"plugin:hyprbars:buttons_gap = {self.hypr_config.hyprbars_buttons_gap}",
                f"plugin:hyprbars:buttons_color = {self.hypr_config.hyprbars_buttons_color}",
                f"plugin:hyprbars:buttons_hover_color = {self.hypr_config.hyprbars_buttons_hover_color}",
                f"plugin:hyprbars:title_color = {self.hypr_config.hyprbars_title_color}",
                f"plugin:hyprbars:title_font = {self.hypr_config.hyprbars_title_font}",
                f"plugin:hyprbars:title_size = {self.hypr_config.hyprbars_title_size}",
                "",
            ])
        else:
            content.extend([
                "# Hyprbars Configuration (Disabled)",
                "plugin:hyprbars:enabled = false",
                "",
            ])
        
        # Hyprexpo configuration
        if self.hypr_config.hyprexpo_enabled:
            content.extend([
                "# Hyprexpo Configuration",
                f"plugin:hyprexpo:enabled = true",
                f"plugin:hyprexpo:workspace_method = {self.hypr_config.hyprexpo_workspace_method}",
                f"plugin:hyprexpo:workspace_gaps = {self.hypr_config.hyprexpo_workspace_gaps}",
                f"plugin:hyprexpo:workspace_rounding = {self.hypr_config.hyprexpo_workspace_rounding}",
                f"plugin:hyprexpo:workspace_shadow = {str(self.hypr_config.hyprexpo_workspace_shadow).lower()}",
                f"plugin:hyprexpo:workspace_shadow_color = {self.hypr_config.hyprexpo_workspace_shadow_color}",
                f"plugin:hyprexpo:workspace_shadow_size = {self.hypr_config.hyprexpo_workspace_shadow_size}",
                f"plugin:hyprexpo:workspace_shadow_offset = {self.hypr_config.hyprexpo_workspace_shadow_offset}",
                "",
            ])
        else:
            content.extend([
                "# Hyprexpo Configuration (Disabled)",
                "plugin:hyprexpo:enabled = false",
                "",
            ])
        
        # Blur shaders configuration
        if self.hypr_config.blur_shaders_enabled:
            content.extend([
                "# Blur Shaders Configuration",
                f"plugin:blur_shaders:enabled = true",
                f"plugin:blur_shaders:type = {self.hypr_config.blur_shader_type}",
                f"plugin:blur_shaders:passes = {self.hypr_config.blur_shader_passes}",
                f"plugin:blur_shaders:size = {self.hypr_config.blur_shader_size}",
                f"plugin:blur_shaders:noise = {self.hypr_config.blur_shader_noise}",
                f"plugin:blur_shaders:contrast = {self.hypr_config.blur_shader_contrast}",
                f"plugin:blur_shaders:brightness = {self.hypr_config.blur_shader_brightness}",
                f"plugin:blur_shaders:vibrancy = {self.hypr_config.blur_shader_vibrancy}",
                f"plugin:blur_shaders:vibrancy_darkness = {self.hypr_config.blur_shader_vibrancy_darkness}",
                "",
            ])
        else:
            content.extend([
                "# Blur Shaders Configuration (Disabled)",
                "plugin:blur_shaders:enabled = false",
                "",
            ])
        
        return "\n".join(content)
    
    def generate_palevioletred_theme(self) -> Dict[str, str]:
        """Generate a ready-to-drop PaleVioletRed 'soft neon' theme."""
        # Override config with PaleVioletRed theme colors
        original_config = self.hypr_config
        
        # Create temporary config with PaleVioletRed colors
        palevioletred_config = HyprlandConfig(
            border_color="#dda0dd",  # PaleVioletRed
            hyprbars_buttons_color="#dda0dd",
            hyprbars_buttons_hover_color="#ff69b4",  # HotPink
            hyprbars_title_color="#ffffff",
            glow_color="#dda0dd",
            hyprexpo_workspace_shadow_color="#dda0dd",
            hyprbars_enabled=True,
            hyprexpo_enabled=True,
            glow_enabled=True,
            blur_shaders_enabled=True,
            blur_shader_type="kawase",
            blur_shader_passes=3,
            blur_shader_size=4,
            blur_shader_vibrancy=0.2,
            blur_shader_vibrancy_darkness=0.1
        )
        
        # Temporarily replace config
        self.hypr_config = palevioletred_config
        
        try:
            # Generate theme
            theme_configs = self.generate_all_configs()
            
            # Add theme metadata
            theme_configs['theme_info'] = {
                'name': 'PaleVioletRed Soft Neon',
                'description': 'A soft neon theme with PaleVioletRed colors',
                'author': 'HyprRice Team',
                'version': '1.0.0',
                'tags': ['palevioletred', 'neon', 'soft', 'glow']
            }
            
            return theme_configs
            
        finally:
            # Restore original config
            self.hypr_config = original_config
    
    def apply_theme(self, theme_configs: Dict[str, str]) -> bool:
        """Apply a theme configuration."""
        try:
            for filename, content in theme_configs.items():
                if filename == 'theme_info':
                    continue
                    
                file_path = self.hypr_dir / filename
                with open(file_path, 'w') as f:
                    f.write(content)
                self.logger.info(f"Applied theme file: {filename}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply theme: {e}")
            return False
    
    def reload_hyprland(self) -> bool:
        """Reload Hyprland configuration."""
        try:
            import subprocess
            result = subprocess.run(['hyprctl', 'reload'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.logger.info("Hyprland configuration reloaded successfully")
                return True
            else:
                self.logger.error(f"Failed to reload Hyprland: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Error reloading Hyprland: {e}")
            return False
