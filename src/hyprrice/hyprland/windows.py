import logging
import os
from typing import Dict, List, Any, Optional

class WindowManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
    
    def get_window_config(self):
        """Get current window configuration from hyprland.conf"""
        try:
            from ..utils import parse_hyprland_config
            sections = parse_hyprland_config(self.config_path)
            return {
                'general': sections.get('general', []),
                'decoration': sections.get('decoration', []),
                'windowrule': sections.get('windowrule', []),
                'windowrulev2': sections.get('windowrulev2', [])
            }
        except Exception as e:
            self.logger.error(f"Failed to get window config: {e}")
            return {}
    
    def set_window_config(self, config):
        """Set window configuration in hyprland.conf"""
        try:
            from ..utils import parse_hyprland_config, write_hyprland_config
            sections = parse_hyprland_config(self.config_path)
            
            # Update general section
            general_config = []
            if 'gaps_in' in config:
                general_config.append(f"gaps_in = {config['gaps_in']}")
            if 'gaps_out' in config:
                general_config.append(f"gaps_out = {config['gaps_out']}")
            if 'border_size' in config:
                general_config.append(f"border_size = {config['border_size']}")
            if 'smart_gaps' in config:
                general_config.append(f"no_gaps_when_only = {config['smart_gaps']}")
            if 'smart_borders' in config:
                general_config.append(f"no_border_on_floating = {config['smart_borders']}")
            
            sections['general'] = general_config
            
            # Update decoration section
            decoration_config = []
            if 'window_opacity' in config:
                decoration_config.append(f"active_opacity = {config['window_opacity']}")
                decoration_config.append(f"inactive_opacity = {max(0.8, config['window_opacity'] - 0.1)}")
            if 'border_color' in config:
                decoration_config.append(f"col.active_border = {config['border_color']}")
                decoration_config.append(f"col.inactive_border = {config['border_color']}55")
            if 'blur_enabled' in config:
                decoration_config.append(f"blur.enabled = {str(config['blur_enabled']).lower()}")
            if 'blur_size' in config:
                decoration_config.append(f"blur.size = {config['blur_size']}")
            if 'blur_passes' in config:
                decoration_config.append(f"blur.passes = {config['blur_passes']}")
            
            # Add drop shadow settings
            decoration_config.extend([
                "drop_shadow = yes",
                "shadow_range = 4",
                "shadow_render_power = 3",
                "col.shadow = rgba(1a1a1aee)"
            ])
            
            sections['decoration'] = decoration_config
            
            write_hyprland_config(self.config_path, sections)
            self._reload_hyprland_config()
            
        except Exception as e:
            self.logger.error(f"Failed to set window config: {e}")
            raise
    
    def apply_window_config(self, config):
        """Apply window configuration to running Hyprland instance"""
        try:
            from ..utils import run_command
            
            # Apply general settings
            if 'gaps_in' in config:
                run_command(['hyprctl', 'keyword', 'general:gaps_in', str(config['gaps_in'])])
            if 'gaps_out' in config:
                run_command(['hyprctl', 'keyword', 'general:gaps_out', str(config['gaps_out'])])
            if 'border_size' in config:
                run_command(['hyprctl', 'keyword', 'general:border_size', str(config['border_size'])])
                
            # Apply decoration settings
            if 'window_opacity' in config:
                run_command(['hyprctl', 'keyword', 'decoration:active_opacity', str(config['window_opacity'])])
                run_command(['hyprctl', 'keyword', 'decoration:inactive_opacity', str(max(0.8, config['window_opacity'] - 0.1))])
            if 'border_color' in config:
                run_command(['hyprctl', 'keyword', 'decoration:col.active_border', config['border_color']])
                run_command(['hyprctl', 'keyword', 'decoration:col.inactive_border', config['border_color'] + '55'])
            if 'blur_enabled' in config:
                run_command(['hyprctl', 'keyword', 'decoration:blur:enabled', str(config['blur_enabled']).lower()])
            if 'blur_size' in config:
                run_command(['hyprctl', 'keyword', 'decoration:blur:size', str(config['blur_size'])])
            if 'blur_passes' in config:
                run_command(['hyprctl', 'keyword', 'decoration:blur:passes', str(config['blur_passes'])])
            
            self.logger.info("Window configuration applied successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to apply window config: {e}")
            raise
    
    def set_window_opacity(self, opacity: float):
        """Set global window opacity"""
        try:
            from ..utils import run_command
            run_command(['hyprctl', 'keyword', 'decoration:active_opacity', str(opacity)])
            run_command(['hyprctl', 'keyword', 'decoration:inactive_opacity', str(max(0.8, opacity - 0.1))])
        except Exception as e:
            self.logger.error(f"Failed to set window opacity: {e}")
            raise
    
    def set_border_size(self, size: int):
        """Set window border size"""
        try:
            from ..utils import run_command
            run_command(['hyprctl', 'keyword', 'general:border_size', str(size)])
        except Exception as e:
            self.logger.error(f"Failed to set border size: {e}")
            raise
    
    def set_border_color(self, color: str):
        """Set window border color"""
        try:
            from ..utils import run_command
            run_command(['hyprctl', 'keyword', 'decoration:col.active_border', color])
            run_command(['hyprctl', 'keyword', 'decoration:col.inactive_border', color + '55'])
        except Exception as e:
            self.logger.error(f"Failed to set border color: {e}")
            raise
    
    def set_gaps(self, gaps_in: int, gaps_out: int):
        """Set window gaps"""
        try:
            from ..utils import run_command
            run_command(['hyprctl', 'keyword', 'general:gaps_in', str(gaps_in)])
            run_command(['hyprctl', 'keyword', 'general:gaps_out', str(gaps_out)])
        except Exception as e:
            self.logger.error(f"Failed to set gaps: {e}")
            raise
    
    def toggle_smart_gaps(self, enabled: bool):
        """Toggle smart gaps (no gaps when only one window)"""
        try:
            from ..utils import run_command
            run_command(['hyprctl', 'keyword', 'general:no_gaps_when_only', str(enabled).lower()])
        except Exception as e:
            self.logger.error(f"Failed to toggle smart gaps: {e}")
            raise
    
    def toggle_blur(self, enabled: bool):
        """Toggle window blur effect"""
        try:
            from ..utils import run_command
            run_command(['hyprctl', 'keyword', 'decoration:blur:enabled', str(enabled).lower()])
        except Exception as e:
            self.logger.error(f"Failed to toggle blur: {e}")
            raise
    
    def set_blur_size(self, size: int):
        """Set blur effect size"""
        try:
            from ..utils import run_command
            run_command(['hyprctl', 'keyword', 'decoration:blur:size', str(size)])
        except Exception as e:
            self.logger.error(f"Failed to set blur size: {e}")
            raise
    
    def get_window_list(self) -> List[Dict[str, Any]]:
        """Get list of all windows"""
        try:
            from ..utils import get_windows
            return get_windows()
        except Exception as e:
            self.logger.error(f"Failed to get window list: {e}")
            return []
    
    def focus_window(self, window_address: str):
        """Focus a specific window by address"""
        try:
            from ..utils import run_command
            run_command(['hyprctl', 'dispatch', 'focuswindow', f'address:{window_address}'])
        except Exception as e:
            self.logger.error(f"Failed to focus window: {e}")
            raise
    
    def close_window(self, window_address: str):
        """Close a specific window by address"""
        try:
            from ..utils import run_command
            run_command(['hyprctl', 'dispatch', 'closewindow', f'address:{window_address}'])
        except Exception as e:
            self.logger.error(f"Failed to close window: {e}")
            raise
    
    def toggle_floating(self, window_address: Optional[str] = None):
        """Toggle floating state of a window"""
        try:
            from ..utils import run_command
            if window_address:
                run_command(['hyprctl', 'dispatch', 'togglefloating', f'address:{window_address}'])
            else:
                run_command(['hyprctl', 'dispatch', 'togglefloating'])
        except Exception as e:
            self.logger.error(f"Failed to toggle floating: {e}")
            raise
    
    def set_window_opacity_rule(self, window_class: str, opacity: float):
        """Set opacity rule for specific window class"""
        try:
            from ..utils import run_command, parse_hyprland_config, write_hyprland_config
            
            # Add window rule to config
            sections = parse_hyprland_config(self.config_path)
            if 'windowrulev2' not in sections:
                sections['windowrulev2'] = []
            
            rule = f"opacity {opacity} {opacity}, class:^({window_class})$"
            sections['windowrulev2'].append(rule)
            
            write_hyprland_config(self.config_path, sections)
            
            # Apply immediately
            run_command(['hyprctl', 'keyword', 'windowrulev2', rule])
            
        except Exception as e:
            self.logger.error(f"Failed to set window opacity rule: {e}")
            raise
    
    def get_window_rules(self) -> List[str]:
        """Get all current window rules"""
        try:
            from ..utils import parse_hyprland_config
            sections = parse_hyprland_config(self.config_path)
            rules = []
            rules.extend(sections.get('windowrule', []))
            rules.extend(sections.get('windowrulev2', []))
            return rules
        except Exception as e:
            self.logger.error(f"Failed to get window rules: {e}")
            return []
    
    def add_window_rule(self, rule: str, window_criteria: str, version: int = 2):
        """Add a new window rule"""
        try:
            from ..utils import run_command, parse_hyprland_config, write_hyprland_config
            
            sections = parse_hyprland_config(self.config_path)
            
            if version == 2:
                rule_key = 'windowrulev2'
                full_rule = f"{rule}, {window_criteria}"
            else:
                rule_key = 'windowrule'
                full_rule = f"{rule}, {window_criteria}"
            
            if rule_key not in sections:
                sections[rule_key] = []
            
            sections[rule_key].append(full_rule)
            write_hyprland_config(self.config_path, sections)
            
            # Apply immediately
            run_command(['hyprctl', 'keyword', rule_key, full_rule])
            
        except Exception as e:
            self.logger.error(f"Failed to add window rule: {e}")
            raise
    
    def remove_window_rule(self, rule_pattern: str):
        """Remove window rules matching pattern"""
        try:
            from ..utils import parse_hyprland_config, write_hyprland_config
            
            sections = parse_hyprland_config(self.config_path)
            
            # Remove from windowrule
            if 'windowrule' in sections:
                sections['windowrule'] = [rule for rule in sections['windowrule'] if rule_pattern not in rule]
            
            # Remove from windowrulev2
            if 'windowrulev2' in sections:
                sections['windowrulev2'] = [rule for rule in sections['windowrulev2'] if rule_pattern not in rule]
            
            write_hyprland_config(self.config_path, sections)
            self._reload_hyprland_config()
            
        except Exception as e:
            self.logger.error(f"Failed to remove window rule: {e}")
            raise
    
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently active window"""
        try:
            from ..utils import run_command
            returncode, stdout, stderr = run_command(['hyprctl', 'activewindow', '-j'])
            
            if returncode == 0:
                import json
                return json.loads(stdout)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get active window: {e}")
            return None
    
    def _reload_hyprland_config(self):
        """Reload Hyprland configuration"""
        try:
            from ..utils import run_command
            run_command(['hyprctl', 'reload'])
        except Exception as e:
            self.logger.warning(f"Failed to reload Hyprland config: {e}") 