"""
Display and monitor management for Hyprland
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from ..utils import hyprctl, run_command, get_monitors
from ..exceptions import HyprRiceError


class DisplayManager:
    """Manages Hyprland display and monitor settings."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
    
    def get_display_config(self) -> Dict[str, Any]:
        """Get current display configuration from hyprctl."""
        try:
            config = {}
            
            # Get monitor information
            monitors = self.get_monitors()
            config['monitors'] = monitors
            
            # Get display-related settings
            settings = [
                'misc:vrr',
                'misc:no_direct_scanout',
                'decoration:drop_shadow',
                'decoration:shadow_range',
                'decoration:shadow_render_power',
                'general:layout'
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
            self.logger.error(f"Error getting display config: {e}")
            return {}
    
    def set_display_config(self, config: Dict[str, Any]) -> bool:
        """Set display configuration."""
        try:
            success = True
            
            # Map config keys to hyprctl keywords
            key_mapping = {
                'misc_vrr': 'misc:vrr',
                'misc_no_direct_scanout': 'misc:no_direct_scanout',
                'decoration_drop_shadow': 'decoration:drop_shadow',
                'decoration_shadow_range': 'decoration:shadow_range',
                'decoration_shadow_render_power': 'decoration:shadow_render_power',
                'general_layout': 'general:layout'
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
            self.logger.error(f"Error setting display config: {e}")
            return False
    
    def apply_display_config(self, config: Dict[str, Any]) -> bool:
        """Apply display configuration to Hyprland."""
        return self.set_display_config(config)
    
    def get_monitors(self) -> List[Dict[str, Any]]:
        """Get list of all monitors."""
        try:
            returncode, stdout, stderr = hyprctl('monitors -j')
            if returncode != 0:
                self.logger.error(f"Failed to get monitors: {stderr}")
                return []
            
            monitors = json.loads(stdout)
            return monitors
        except Exception as e:
            self.logger.error(f"Error getting monitors: {e}")
            return []
    
    def set_monitor_resolution(self, monitor_name: str, resolution: str) -> bool:
        """Set monitor resolution (e.g., '1920x1080@60')."""
        try:
            # Parse resolution string
            if '@' in resolution:
                res_part, refresh_part = resolution.split('@')
            else:
                res_part = resolution
                refresh_part = '60'
            
            # Validate resolution format
            if 'x' not in res_part:
                self.logger.error(f"Invalid resolution format: {resolution}")
                return False
            
            width, height = res_part.split('x')
            
            # Apply the monitor configuration
            monitor_config = f"{monitor_name},{width}x{height}@{refresh_part},auto,1"
            returncode, stdout, stderr = hyprctl(f'keyword monitor {monitor_config}')
            
            if returncode != 0:
                self.logger.error(f"Failed to set monitor resolution: {stderr}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error setting monitor resolution: {e}")
            return False
    
    def set_monitor_position(self, monitor_name: str, x: int, y: int) -> bool:
        """Set monitor position."""
        try:
            # Get current monitor info to preserve other settings
            monitors = self.get_monitors()
            target_monitor = None
            
            for monitor in monitors:
                if monitor.get('name') == monitor_name:
                    target_monitor = monitor
                    break
            
            if not target_monitor:
                self.logger.error(f"Monitor {monitor_name} not found")
                return False
            
            # Build monitor configuration string
            width = target_monitor.get('width', 1920)
            height = target_monitor.get('height', 1080)
            refresh = target_monitor.get('refreshRate', 60)
            scale = target_monitor.get('scale', 1.0)
            
            monitor_config = f"{monitor_name},{width}x{height}@{refresh},{x}x{y},{scale}"
            returncode, stdout, stderr = hyprctl(f'keyword monitor {monitor_config}')
            
            if returncode != 0:
                self.logger.error(f"Failed to set monitor position: {stderr}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error setting monitor position: {e}")
            return False
    
    def set_monitor_scale(self, monitor_name: str, scale: float) -> bool:
        """Set monitor scale factor."""
        try:
            scale = max(0.25, min(4.0, scale))  # Clamp scale between reasonable values
            
            # Get current monitor info to preserve other settings
            monitors = self.get_monitors()
            target_monitor = None
            
            for monitor in monitors:
                if monitor.get('name') == monitor_name:
                    target_monitor = monitor
                    break
            
            if not target_monitor:
                self.logger.error(f"Monitor {monitor_name} not found")
                return False
            
            # Build monitor configuration string
            width = target_monitor.get('width', 1920)
            height = target_monitor.get('height', 1080)
            refresh = target_monitor.get('refreshRate', 60)
            x = target_monitor.get('x', 0)
            y = target_monitor.get('y', 0)
            
            monitor_config = f"{monitor_name},{width}x{height}@{refresh},{x}x{y},{scale}"
            returncode, stdout, stderr = hyprctl(f'keyword monitor {monitor_config}')
            
            if returncode != 0:
                self.logger.error(f"Failed to set monitor scale: {stderr}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error setting monitor scale: {e}")
            return False
    
    def toggle_vrr(self, enabled: bool) -> bool:
        """Toggle Variable Refresh Rate (VRR/FreeSync/G-Sync)."""
        try:
            # VRR can be 0 (off), 1 (on), or 2 (fullscreen only)
            value = "1" if enabled else "0"
            returncode, stdout, stderr = hyprctl(f'keyword misc:vrr {value}')
            
            if returncode != 0:
                self.logger.error(f"Failed to toggle VRR: {stderr}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error toggling VRR: {e}")
            return False
    
    def toggle_tearing(self, enabled: bool) -> bool:
        """Toggle screen tearing allowance."""
        try:
            value = "true" if enabled else "false"
            returncode, stdout, stderr = hyprctl(f'keyword general:allow_tearing {value}')
            
            if returncode != 0:
                self.logger.error(f"Failed to toggle tearing: {stderr}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error toggling tearing: {e}")
            return False
    
    def set_max_render_time(self, time_ms: int) -> bool:
        """Set maximum render time in milliseconds."""
        try:
            time_ms = max(1, time_ms)  # Ensure positive value
            returncode, stdout, stderr = hyprctl(f'keyword decoration:max_render_time {time_ms}')
            
            if returncode != 0:
                self.logger.error(f"Failed to set max render time: {stderr}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error setting max render time: {e}")
            return False
    
    def mirror_displays(self, primary_monitor: str, secondary_monitor: str) -> bool:
        """Mirror one display to another."""
        try:
            # Get primary monitor info
            monitors = self.get_monitors()
            primary_info = None
            
            for monitor in monitors:
                if monitor.get('name') == primary_monitor:
                    primary_info = monitor
                    break
            
            if not primary_info:
                self.logger.error(f"Primary monitor {primary_monitor} not found")
                return False
            
            # Configure secondary monitor to mirror primary
            width = primary_info.get('width', 1920)
            height = primary_info.get('height', 1080)
            refresh = primary_info.get('refreshRate', 60)
            
            # Set secondary monitor to same position and resolution as primary
            monitor_config = f"{secondary_monitor},{width}x{height}@{refresh},0x0,1"
            returncode, stdout, stderr = hyprctl(f'keyword monitor {monitor_config}')
            
            if returncode != 0:
                self.logger.error(f"Failed to mirror displays: {stderr}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error mirroring displays: {e}")
            return False
    
    def extend_displays(self, primary_monitor: str, secondary_monitor: str, position: str = "right") -> bool:
        """Extend displays (position secondary monitor relative to primary)."""
        try:
            # Get primary monitor info
            monitors = self.get_monitors()
            primary_info = None
            secondary_info = None
            
            for monitor in monitors:
                if monitor.get('name') == primary_monitor:
                    primary_info = monitor
                elif monitor.get('name') == secondary_monitor:
                    secondary_info = monitor
            
            if not primary_info:
                self.logger.error(f"Primary monitor {primary_monitor} not found")
                return False
            
            if not secondary_info:
                self.logger.error(f"Secondary monitor {secondary_monitor} not found")
                return False
            
            # Calculate secondary monitor position based on primary
            primary_width = primary_info.get('width', 1920)
            primary_height = primary_info.get('height', 1080)
            primary_x = primary_info.get('x', 0)
            primary_y = primary_info.get('y', 0)
            
            secondary_width = secondary_info.get('width', 1920)
            secondary_height = secondary_info.get('height', 1080)
            secondary_refresh = secondary_info.get('refreshRate', 60)
            
            # Calculate position based on requested position
            if position == "right":
                sec_x = primary_x + primary_width
                sec_y = primary_y
            elif position == "left":
                sec_x = primary_x - secondary_width
                sec_y = primary_y
            elif position == "above":
                sec_x = primary_x
                sec_y = primary_y - secondary_height
            elif position == "below":
                sec_x = primary_x
                sec_y = primary_y + primary_height
            else:
                self.logger.error(f"Invalid position: {position}")
                return False
            
            # Apply secondary monitor configuration
            monitor_config = f"{secondary_monitor},{secondary_width}x{secondary_height}@{secondary_refresh},{sec_x}x{sec_y},1"
            returncode, stdout, stderr = hyprctl(f'keyword monitor {monitor_config}')
            
            if returncode != 0:
                self.logger.error(f"Failed to extend displays: {stderr}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error extending displays: {e}")
            return False
    
    def disable_monitor(self, monitor_name: str) -> bool:
        """Disable a monitor."""
        try:
            returncode, stdout, stderr = hyprctl(f'keyword monitor {monitor_name},disable')
            
            if returncode != 0:
                self.logger.error(f"Failed to disable monitor: {stderr}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error disabling monitor: {e}")
            return False
    
    def enable_monitor(self, monitor_name: str, resolution: str = "preferred", position: str = "auto") -> bool:
        """Enable a monitor with specified resolution and position."""
        try:
            if resolution == "preferred":
                resolution = "preferred"
            elif '@' not in resolution:
                resolution = f"{resolution}@60"
            
            monitor_config = f"{monitor_name},{resolution},{position},1"
            returncode, stdout, stderr = hyprctl(f'keyword monitor {monitor_config}')
            
            if returncode != 0:
                self.logger.error(f"Failed to enable monitor: {stderr}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error enabling monitor: {e}")
            return False
    
    def get_workspaces_per_monitor(self) -> Dict[str, List[int]]:
        """Get workspaces assigned to each monitor."""
        try:
            returncode, stdout, stderr = hyprctl('workspaces -j')
            if returncode != 0:
                self.logger.error(f"Failed to get workspaces: {stderr}")
                return {}
            
            workspaces = json.loads(stdout)
            monitor_workspaces = {}
            
            for workspace in workspaces:
                monitor = workspace.get('monitor', 'Unknown')
                workspace_id = workspace.get('id', 0)
                
                if monitor not in monitor_workspaces:
                    monitor_workspaces[monitor] = []
                
                monitor_workspaces[monitor].append(workspace_id)
            
            return monitor_workspaces
        except Exception as e:
            self.logger.error(f"Error getting workspaces per monitor: {e}")
            return {}
    
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
