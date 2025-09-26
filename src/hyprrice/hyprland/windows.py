"""
Window management for Hyprland
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from ..utils import hyprctl, hyprctl_async, batch_hyprctl, batch_hyprctl_async, run_command
from ..exceptions import HyprRiceError


class WindowManager:
    """Manages Hyprland windows and window rules."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
    
    def get_window_config(self) -> Dict[str, Any]:
        """Get current window configuration from hyprctl with caching."""
        try:
            config = {}
            
            # Use batch command for efficiency
            commands = [
                'getoption general:gaps_in',
                'getoption general:gaps_out',
                'getoption general:border_size',
                'getoption general:col.active_border',
                'getoption general:col.inactive_border',
                'getoption decoration:blur:enabled',
                'getoption decoration:blur:size',
                'getoption decoration:rounding',
                'getoption animations:enabled'
            ]
            
            results = batch_hyprctl(commands)
            
            # Parse results
            for command, result in results.items():
                if result:
                    try:
                        data = json.loads(result)
                        option_name = command.replace('getoption ', '')
                        config_key = option_name.replace(':', '_').replace('.', '_')
                        
                        if 'option' in data and 'set' in data['option']:
                            config[config_key] = data['option']['set']
                        else:
                            # Fallback values
                            if 'gaps_in' in option_name:
                                config[config_key] = 5
                            elif 'gaps_out' in option_name:
                                config[config_key] = 10
                            elif 'border_size' in option_name:
                                config[config_key] = 2
                            elif 'col_active_border' in config_key:
                                config[config_key] = '#5e81ac'
                            elif 'blur_enabled' in config_key:
                                config[config_key] = True
                            elif 'blur_size' in config_key:
                                config[config_key] = 8
                            elif 'rounding' in option_name:
                                config[config_key] = 8
                            elif 'animations_enabled' in config_key:
                                config[config_key] = True
                    except (json.JSONDecodeError, KeyError) as e:
                        self.logger.warning(f"Failed to parse {command}: {e}")
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error getting window config: {e}")
            return {}
    
    async def get_window_config_async(self) -> Dict[str, Any]:
        """Get current window configuration asynchronously."""
        try:
            config = {}
            
            # Use batch command for efficiency
            commands = [
                'getoption general:gaps_in',
                'getoption general:gaps_out', 
                'getoption general:border_size',
                'getoption general:col.active_border',
                'getoption general:col.inactive_border',
                'getoption decoration:blur:enabled',
                'getoption decoration:blur:size',
                'getoption decoration:rounding',
                'getoption animations:enabled'
            ]
            
            results = await batch_hyprctl_async(commands)
            
            # Parse results
            for command, result in results.items():
                if result:
                    try:
                        data = json.loads(result)
                        option_name = command.replace('getoption ', '')
                        config_key = option_name.replace(':', '_').replace('.', '_')
                        
                        if 'option' in data and 'set' in data['option']:
                            config[config_key] = data['option']['set']
                    except (json.JSONDecodeError, KeyError) as e:
                        self.logger.warning(f"Failed to parse {command}: {e}")
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error getting window config async: {e}")
            return {}
    
    def set_window_config(self, config: Dict[str, Any]) -> bool:
        """Set window configuration."""
        try:
            success = True
            
            # Map config keys to hyprctl keywords
            key_mapping = {
                'general_gaps_in': 'general:gaps_in',
                'general_gaps_out': 'general:gaps_out',
                'general_border_size': 'general:border_size',
                'general_col_active_border': 'general:col.active_border',
                'general_col_inactive_border': 'general:col.inactive_border',
                'decoration_blur_enabled': 'decoration:blur:enabled',
                'decoration_blur_size': 'decoration:blur:size',
                'decoration_blur_passes': 'decoration:blur:passes',
                'decoration_rounding': 'decoration:rounding'
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
            self.logger.error(f"Error setting window config: {e}")
            return False
    
    def apply_window_config(self, config: Dict[str, Any]) -> bool:
        """Apply window configuration to Hyprland."""
        return self.set_window_config(config)
    
    def set_window_opacity(self, opacity: float) -> bool:
        """Set global window opacity."""
        try:
            opacity = max(0.0, min(1.0, opacity))  # Clamp between 0 and 1
            returncode, stdout, stderr = hyprctl(f'keyword decoration:active_opacity {opacity}')
            if returncode != 0:
                self.logger.error(f"Failed to set window opacity: {stderr}")
                return False
            
            returncode, stdout, stderr = hyprctl(f'keyword decoration:inactive_opacity {opacity * 0.9}')
            if returncode != 0:
                self.logger.error(f"Failed to set inactive window opacity: {stderr}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error setting window opacity: {e}")
            return False
    
    def set_border_size(self, size: int) -> bool:
        """Set window border size."""
        try:
            size = max(0, size)  # Ensure non-negative
            returncode, stdout, stderr = hyprctl(f'keyword general:border_size {size}')
            if returncode != 0:
                self.logger.error(f"Failed to set border size: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error setting border size: {e}")
            return False
    
    def set_border_color(self, color: str) -> bool:
        """Set window border color."""
        try:
            # Ensure color starts with 0x or rgb()
            if not (color.startswith('0x') or color.startswith('rgb')):
                color = f'0x{color.lstrip("#")}'
            
            returncode, stdout, stderr = hyprctl(f'keyword general:col.active_border {color}')
            if returncode != 0:
                self.logger.error(f"Failed to set active border color: {stderr}")
                return False
            
            # Set inactive border to a dimmer version
            returncode, stdout, stderr = hyprctl(f'keyword general:col.inactive_border {color}aa')
            if returncode != 0:
                self.logger.error(f"Failed to set inactive border color: {stderr}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error setting border color: {e}")
            return False
    
    def set_gaps(self, gaps_in: int, gaps_out: int) -> bool:
        """Set window gaps."""
        try:
            gaps_in = max(0, gaps_in)
            gaps_out = max(0, gaps_out)
            
            returncode, stdout, stderr = hyprctl(f'keyword general:gaps_in {gaps_in}')
            if returncode != 0:
                self.logger.error(f"Failed to set inner gaps: {stderr}")
                return False
            
            returncode, stdout, stderr = hyprctl(f'keyword general:gaps_out {gaps_out}')
            if returncode != 0:
                self.logger.error(f"Failed to set outer gaps: {stderr}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error setting gaps: {e}")
            return False
    
    def toggle_smart_gaps(self, enabled: bool) -> bool:
        """Toggle smart gaps feature."""
        try:
            value = "1" if enabled else "0"
            returncode, stdout, stderr = hyprctl(f'keyword general:no_gaps_when_only {value}')
            if returncode != 0:
                self.logger.error(f"Failed to toggle smart gaps: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error toggling smart gaps: {e}")
            return False
    
    def toggle_blur(self, enabled: bool) -> bool:
        """Toggle window blur effect."""
        try:
            value = "true" if enabled else "false"
            returncode, stdout, stderr = hyprctl(f'keyword decoration:blur:enabled {value}')
            if returncode != 0:
                self.logger.error(f"Failed to toggle blur: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error toggling blur: {e}")
            return False
    
    def set_blur_size(self, size: int) -> bool:
        """Set blur size."""
        try:
            size = max(1, size)  # Ensure positive
            returncode, stdout, stderr = hyprctl(f'keyword decoration:blur:size {size}')
            if returncode != 0:
                self.logger.error(f"Failed to set blur size: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error setting blur size: {e}")
            return False
    
    def get_window_list(self) -> List[Dict[str, Any]]:
        """Get list of current windows with caching."""
        try:
            result = hyprctl('clients')
            if result:
                windows = json.loads(result)
                return windows if isinstance(windows, list) else []
            return []
        except Exception as e:
            self.logger.error(f"Error getting window list: {e}")
            return []
    
    async def get_window_list_async(self) -> List[Dict[str, Any]]:
        """Get list of current windows asynchronously."""
        try:
            result = await hyprctl_async('clients')
            if result:
                windows = json.loads(result)
                return windows if isinstance(windows, list) else []
            return []
        except Exception as e:
            self.logger.error(f"Error getting window list async: {e}")
            return []
    
    def focus_window(self, window_address: str) -> bool:
        """Focus a specific window."""
        try:
            returncode, stdout, stderr = hyprctl(f'dispatch focuswindow address:{window_address}')
            if returncode != 0:
                self.logger.error(f"Failed to focus window: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error focusing window: {e}")
            return False
    
    def close_window(self, window_address: str) -> bool:
        """Close a specific window."""
        try:
            returncode, stdout, stderr = hyprctl(f'dispatch closewindow address:{window_address}')
            if returncode != 0:
                self.logger.error(f"Failed to close window: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error closing window: {e}")
            return False
    
    def toggle_floating(self, window_address: str) -> bool:
        """Toggle floating state of a window."""
        try:
            returncode, stdout, stderr = hyprctl(f'dispatch togglefloating address:{window_address}')
            if returncode != 0:
                self.logger.error(f"Failed to toggle floating: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error toggling floating: {e}")
            return False
    
    def set_window_opacity_rule(self, window_class: str, opacity: float) -> bool:
        """Set opacity rule for specific window class."""
        try:
            opacity = max(0.0, min(1.0, opacity))
            returncode, stdout, stderr = hyprctl(f'keyword windowrulev2 opacity {opacity},class:{window_class}')
            if returncode != 0:
                self.logger.error(f"Failed to set opacity rule: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error setting opacity rule: {e}")
            return False
    
    def get_window_rules(self) -> List[Dict[str, Any]]:
        """Get current window rules."""
        try:
            # Hyprctl doesn't have a direct way to get window rules
            # We'll need to parse the config file for this
            # For now, return empty list
            return []
        except Exception as e:
            self.logger.error(f"Error getting window rules: {e}")
            return []
    
    def add_window_rule(self, rule: str, window_criteria: str) -> bool:
        """Add a window rule."""
        try:
            returncode, stdout, stderr = hyprctl(f'keyword windowrulev2 {rule},{window_criteria}')
            if returncode != 0:
                self.logger.error(f"Failed to add window rule: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error adding window rule: {e}")
            return False
    
    def remove_window_rule(self, rule_id: str) -> bool:
        """Remove a window rule."""
        # This would require config file manipulation
        # For now, just log that it's not implemented
        self.logger.warning("Window rule removal not yet implemented")
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
