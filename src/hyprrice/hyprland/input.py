"""
Input device management for Hyprland
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from ..utils import hyprctl, run_command
from ..exceptions import HyprRiceError


class InputManager:
    """Manages Hyprland input devices and settings."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
    
    def get_input_config(self) -> Dict[str, Any]:
        """Get current input configuration from hyprctl."""
        try:
            config = {}
            
            # Get input-related settings
            settings = [
                'input:kb_layout',
                'input:kb_variant',
                'input:kb_model',
                'input:kb_options',
                'input:kb_rules',
                'input:repeat_rate',
                'input:repeat_delay',
                'input:sensitivity',
                'input:accel_profile',
                'input:force_no_accel',
                'input:left_handed',
                'input:scroll_method',
                'input:natural_scroll',
                'input:follow_mouse',
                'input:mouse_refocus',
                'input:touchpad:natural_scroll',
                'input:touchpad:tap-to-click',
                'input:touchpad:tap-and-drag',
                'input:touchpad:drag_lock',
                'input:touchpad:disable_while_typing'
            ]
            
            for setting in settings:
                returncode, stdout, stderr = hyprctl(f'getoption {setting}')
                if returncode == 0 and stdout.strip():
                    lines = stdout.strip().split('\n')
                    for line in lines:
                        if 'option' in line.lower() and ':' in line:
                            value = line.split(':')[-1].strip()
                            config[setting.replace(':', '_')] = self._parse_value(value)
            
            return config
        except Exception as e:
            self.logger.error(f"Error getting input config: {e}")
            return {}
    
    def set_input_config(self, config: Dict[str, Any]) -> bool:
        """Set input configuration."""
        try:
            success = True
            
            # Map config keys to hyprctl keywords
            key_mapping = {
                'input_kb_layout': 'input:kb_layout',
                'input_kb_variant': 'input:kb_variant',
                'input_kb_model': 'input:kb_model',
                'input_kb_options': 'input:kb_options',
                'input_kb_rules': 'input:kb_rules',
                'input_repeat_rate': 'input:repeat_rate',
                'input_repeat_delay': 'input:repeat_delay',
                'input_sensitivity': 'input:sensitivity',
                'input_accel_profile': 'input:accel_profile',
                'input_force_no_accel': 'input:force_no_accel',
                'input_left_handed': 'input:left_handed',
                'input_scroll_method': 'input:scroll_method',
                'input_natural_scroll': 'input:natural_scroll',
                'input_follow_mouse': 'input:follow_mouse',
                'input_mouse_refocus': 'input:mouse_refocus',
                'input_touchpad_natural_scroll': 'input:touchpad:natural_scroll',
                'input_touchpad_tap_to_click': 'input:touchpad:tap-to-click',
                'input_touchpad_tap_and_drag': 'input:touchpad:tap-and-drag',
                'input_touchpad_drag_lock': 'input:touchpad:drag_lock',
                'input_touchpad_disable_while_typing': 'input:touchpad:disable_while_typing'
            }
            
            for config_key, value in config.items():
                if config_key in key_mapping:
                    hypr_key = key_mapping[config_key]
                    returncode, stdout, stderr = hyprctl(f'keyword {hypr_key} {value}')
                    if returncode != 0:
                        self.logger.error(f"Failed to set {hypr_key}: {stderr}")
                        success = False
            
            return success
        except Exception as e:
            self.logger.error(f"Error setting input config: {e}")
            return False
    
    def apply_input_config(self, config: Dict[str, Any]) -> bool:
        """Apply input configuration to Hyprland."""
        return self.set_input_config(config)
    
    def set_keyboard_repeat_rate(self, rate: int) -> bool:
        """Set keyboard repeat rate (repeats per second)."""
        try:
            rate = max(1, min(50, rate))  # Clamp between reasonable values
            returncode, stdout, stderr = hyprctl(f'keyword input:repeat_rate {rate}')
            if returncode != 0:
                self.logger.error(f"Failed to set repeat rate: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error setting keyboard repeat rate: {e}")
            return False
    
    def set_keyboard_repeat_delay(self, delay: int) -> bool:
        """Set keyboard repeat delay in milliseconds."""
        try:
            delay = max(100, min(2000, delay))  # Clamp between reasonable values
            returncode, stdout, stderr = hyprctl(f'keyword input:repeat_delay {delay}')
            if returncode != 0:
                self.logger.error(f"Failed to set repeat delay: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error setting keyboard repeat delay: {e}")
            return False
    
    def set_mouse_sensitivity(self, sensitivity: float) -> bool:
        """Set mouse sensitivity (-1.0 to 1.0)."""
        try:
            sensitivity = max(-1.0, min(1.0, sensitivity))
            returncode, stdout, stderr = hyprctl(f'keyword input:sensitivity {sensitivity}')
            if returncode != 0:
                self.logger.error(f"Failed to set mouse sensitivity: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error setting mouse sensitivity: {e}")
            return False
    
    def set_mouse_accel_profile(self, profile: str) -> bool:
        """Set mouse acceleration profile ('flat' or 'adaptive')."""
        try:
            if profile not in ['flat', 'adaptive']:
                self.logger.error(f"Invalid acceleration profile: {profile}")
                return False
        
            returncode, stdout, stderr = hyprctl(f'keyword input:accel_profile {profile}')
            if returncode != 0:
                self.logger.error(f"Failed to set acceleration profile: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error setting mouse acceleration profile: {e}")
            return False
    
    def toggle_touchpad_natural_scroll(self, enabled: bool) -> bool:
        """Toggle touchpad natural scroll."""
        try:
            value = "true" if enabled else "false"
            returncode, stdout, stderr = hyprctl(f'keyword input:touchpad:natural_scroll {value}')
            if returncode != 0:
                self.logger.error(f"Failed to toggle touchpad natural scroll: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error toggling touchpad natural scroll: {e}")
            return False
    
    def toggle_touchpad_tap_to_click(self, enabled: bool) -> bool:
        """Toggle touchpad tap-to-click."""
        try:
            value = "true" if enabled else "false"
            returncode, stdout, stderr = hyprctl(f'keyword input:touchpad:tap-to-click {value}')
            if returncode != 0:
                self.logger.error(f"Failed to toggle tap-to-click: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error toggling touchpad tap-to-click: {e}")
            return False
    
    def get_input_devices(self) -> List[Dict[str, Any]]:
        """Get list of input devices."""
        try:
            returncode, stdout, stderr = hyprctl('devices -j')
            if returncode != 0:
                self.logger.error(f"Failed to get input devices: {stderr}")
                return []
            
            devices = json.loads(stdout)
            return devices
        except Exception as e:
            self.logger.error(f"Error getting input devices: {e}")
            return []
    
    def set_keyboard_layout(self, layout: str, variant: str = "") -> bool:
        """Set keyboard layout and variant."""
        try:
            returncode, stdout, stderr = hyprctl(f'keyword input:kb_layout {layout}')
            if returncode != 0:
                self.logger.error(f"Failed to set keyboard layout: {stderr}")
                return False
            
            if variant:
                returncode, stdout, stderr = hyprctl(f'keyword input:kb_variant {variant}')
                if returncode != 0:
                    self.logger.error(f"Failed to set keyboard variant: {stderr}")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error setting keyboard layout: {e}")
            return False
    
    def set_keyboard_options(self, options: str) -> bool:
        """Set keyboard options (e.g., 'grp:alt_shift_toggle')."""
        try:
            returncode, stdout, stderr = hyprctl(f'keyword input:kb_options {options}')
            if returncode != 0:
                self.logger.error(f"Failed to set keyboard options: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error setting keyboard options: {e}")
            return False
    
    def toggle_left_handed_mouse(self, enabled: bool) -> bool:
        """Toggle left-handed mouse mode."""
        try:
            value = "true" if enabled else "false"
            returncode, stdout, stderr = hyprctl(f'keyword input:left_handed {value}')
            if returncode != 0:
                self.logger.error(f"Failed to toggle left-handed mouse: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error toggling left-handed mouse: {e}")
            return False
    
    def set_scroll_method(self, method: str) -> bool:
        """Set scroll method ('2fg', 'edge', 'on_button_down', 'no_scroll')."""
        try:
            valid_methods = ['2fg', 'edge', 'on_button_down', 'no_scroll']
            if method not in valid_methods:
                self.logger.error(f"Invalid scroll method: {method}")
                return False
            
            returncode, stdout, stderr = hyprctl(f'keyword input:scroll_method {method}')
            if returncode != 0:
                self.logger.error(f"Failed to set scroll method: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error setting scroll method: {e}")
            return False
    
    def toggle_mouse_natural_scroll(self, enabled: bool) -> bool:
        """Toggle mouse natural scroll."""
        try:
            value = "true" if enabled else "false"
            returncode, stdout, stderr = hyprctl(f'keyword input:natural_scroll {value}')
            if returncode != 0:
                self.logger.error(f"Failed to toggle mouse natural scroll: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error toggling mouse natural scroll: {e}")
            return False
    
    def set_follow_mouse_mode(self, mode: int) -> bool:
        """Set follow mouse mode (0=disabled, 1=loose, 2=strict, 3=always focused)."""
        try:
            if mode not in [0, 1, 2, 3]:
                self.logger.error(f"Invalid follow mouse mode: {mode}")
                return False
            
            returncode, stdout, stderr = hyprctl(f'keyword input:follow_mouse {mode}')
            if returncode != 0:
                self.logger.error(f"Failed to set follow mouse mode: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error setting follow mouse mode: {e}")
            return False
    
    def toggle_mouse_refocus(self, enabled: bool) -> bool:
        """Toggle mouse refocus on window close."""
        try:
            value = "true" if enabled else "false"
            returncode, stdout, stderr = hyprctl(f'keyword input:mouse_refocus {value}')
            if returncode != 0:
                self.logger.error(f"Failed to toggle mouse refocus: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error toggling mouse refocus: {e}")
            return False
    
    def toggle_touchpad_tap_and_drag(self, enabled: bool) -> bool:
        """Toggle touchpad tap-and-drag."""
        try:
            value = "true" if enabled else "false"
            returncode, stdout, stderr = hyprctl(f'keyword input:touchpad:tap-and-drag {value}')
            if returncode != 0:
                self.logger.error(f"Failed to toggle tap-and-drag: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error toggling touchpad tap-and-drag: {e}")
            return False
    
    def toggle_touchpad_drag_lock(self, enabled: bool) -> bool:
        """Toggle touchpad drag lock."""
        try:
            value = "true" if enabled else "false"
            returncode, stdout, stderr = hyprctl(f'keyword input:touchpad:drag_lock {value}')
            if returncode != 0:
                self.logger.error(f"Failed to toggle drag lock: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error toggling touchpad drag lock: {e}")
            return False
    
    def toggle_disable_while_typing(self, enabled: bool) -> bool:
        """Toggle disable touchpad while typing."""
        try:
            value = "true" if enabled else "false"
            returncode, stdout, stderr = hyprctl(f'keyword input:touchpad:disable_while_typing {value}')
            if returncode != 0:
                self.logger.error(f"Failed to toggle disable while typing: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error toggling disable while typing: {e}")
            return False
    
    def force_no_acceleration(self, enabled: bool) -> bool:
        """Force disable mouse acceleration."""
        try:
            value = "true" if enabled else "false"
            returncode, stdout, stderr = hyprctl(f'keyword input:force_no_accel {value}')
            if returncode != 0:
                self.logger.error(f"Failed to set force no acceleration: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error setting force no acceleration: {e}")
            return False
    
    def get_keyboard_layouts(self) -> List[str]:
        """Get available keyboard layouts."""
        # This is a static list of common layouts
        # In a real implementation, you might parse from /usr/share/X11/xkb/rules/base.lst
        return [
            'us', 'us(dvorak)', 'us(colemak)',
            'gb', 'de', 'fr', 'es', 'it', 'pt',
            'ru', 'pl', 'cz', 'hu', 'ro',
            'dk', 'no', 'se', 'fi',
            'jp', 'kr', 'cn',
            'ar', 'il', 'tr',
            'in', 'th', 'vn'
        ]
    
    def reload_input_config(self) -> bool:
        """Reload input configuration from config file."""
        try:
            returncode, stdout, stderr = hyprctl('reload')
            if returncode != 0:
                self.logger.error(f"Failed to reload config: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error reloading input config: {e}")
            return False
    
    def _parse_value(self, value: str) -> Any:
        """Parse a string value to appropriate type."""
        value = value.strip()
        
        # Boolean values
        if value.lower() in ['true', '1', 'yes', 'on']:
            return True
        elif value.lower() in ['false', '0', 'no', 'off']:
            return False
        
        # Numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # String value
        return value 
