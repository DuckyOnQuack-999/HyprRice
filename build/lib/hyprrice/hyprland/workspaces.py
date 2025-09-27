"""
Workspace management for Hyprland
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from ..utils import hyprctl, run_command
from ..exceptions import HyprRiceError


class WorkspaceManager:
    """Manages Hyprland workspaces and workspace settings."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
    
    def get_workspace_config(self) -> Dict[str, Any]:
        """Get current workspace configuration from hyprctl."""
        try:
            config = {}
            
            # Get workspace-related settings
            settings = [
                'general:layout',
                'master:new_is_master',
                'master:new_on_top',
                'master:no_gaps_when_only',
                'master:orientation',
                'master:inherit_fullscreen',
                'dwindle:pseudotile',
                'dwindle:preserve_split',
                'dwindle:smart_split',
                'dwindle:smart_resizing',
                'dwindle:special_scale_factor',
                'misc:disable_hyprland_logo',
                'misc:disable_splash_rendering'
            ]
            
            for setting in settings:
                returncode, stdout, stderr = hyprctl(f'getoption {setting}')
                if returncode == 0 and stdout.strip():
                    lines = stdout.strip().split('\n')
                    for line in lines:
                        if 'option' in line.lower() and ':' in line:
                            value = line.split(':')[-1].strip()
                            config[setting.replace(':', '_')] = self._parse_value(value)
            
            # Get workspace information
            workspaces = self.get_workspaces()
            config['workspaces'] = workspaces
            
            # Get active workspace
            active_workspace = self.get_active_workspace()
            config['active_workspace'] = active_workspace
            
            return config
        except Exception as e:
            self.logger.error(f"Error getting workspace config: {e}")
            return {}
    
    def set_workspace_config(self, config: Dict[str, Any]) -> bool:
        """Set workspace configuration."""
        try:
            success = True
            
            # Map config keys to hyprctl keywords
            key_mapping = {
                'general_layout': 'general:layout',
                'master_new_is_master': 'master:new_is_master',
                'master_new_on_top': 'master:new_on_top',
                'master_no_gaps_when_only': 'master:no_gaps_when_only',
                'master_orientation': 'master:orientation',
                'master_inherit_fullscreen': 'master:inherit_fullscreen',
                'dwindle_pseudotile': 'dwindle:pseudotile',
                'dwindle_preserve_split': 'dwindle:preserve_split',
                'dwindle_smart_split': 'dwindle:smart_split',
                'dwindle_smart_resizing': 'dwindle:smart_resizing',
                'dwindle_special_scale_factor': 'dwindle:special_scale_factor',
                'misc_disable_hyprland_logo': 'misc:disable_hyprland_logo',
                'misc_disable_splash_rendering': 'misc:disable_splash_rendering'
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
            self.logger.error(f"Error setting workspace config: {e}")
            return False
    
    def get_workspaces(self) -> List[Dict[str, Any]]:
        """Get list of all workspaces."""
        try:
            returncode, stdout, stderr = hyprctl('workspaces -j')
            if returncode != 0:
                self.logger.error(f"Failed to get workspaces: {stderr}")
                return []
            
            workspaces = json.loads(stdout)
            return workspaces
        except Exception as e:
            self.logger.error(f"Error getting workspaces: {e}")
            return []
    
    def switch_to_workspace(self, workspace_id: int) -> bool:
        """Switch to a specific workspace."""
        try:
            returncode, stdout, stderr = hyprctl(f'dispatch workspace {workspace_id}')
            if returncode != 0:
                self.logger.error(f"Failed to switch to workspace {workspace_id}: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error switching to workspace: {e}")
            return False
    
    def move_to_workspace(self, workspace_id: int) -> bool:
        """Move active window to a specific workspace."""
        try:
            returncode, stdout, stderr = hyprctl(f'dispatch movetoworkspace {workspace_id}')
            if returncode != 0:
                self.logger.error(f"Failed to move window to workspace {workspace_id}: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error moving to workspace: {e}")
            return False
    
    def create_workspace(self, name: str) -> bool:
        """Create a new workspace with a name."""
        try:
            # In Hyprland, workspaces are created automatically when accessed
            # We can switch to a named workspace to create it
            returncode, stdout, stderr = hyprctl(f'dispatch workspace name:{name}')
            if returncode != 0:
                self.logger.error(f"Failed to create workspace {name}: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error creating workspace: {e}")
            return False
    
    def rename_workspace(self, workspace_id: int, new_name: str) -> bool:
        """Rename a workspace."""
        try:
            returncode, stdout, stderr = hyprctl(f'dispatch renameworkspace {workspace_id} {new_name}')
            if returncode != 0:
                self.logger.error(f"Failed to rename workspace: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error renaming workspace: {e}")
            return False
    
    def bind_workspace_to_monitor(self, workspace_id: int, monitor: str) -> bool:
        """Bind a workspace to a specific monitor."""
        try:
            returncode, stdout, stderr = hyprctl(f'dispatch moveworkspacetomonitor {workspace_id} {monitor}')
            if returncode != 0:
                self.logger.error(f"Failed to bind workspace to monitor: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error binding workspace to monitor: {e}")
            return False
    
    def get_active_workspace(self) -> Optional[Dict[str, Any]]:
        """Get the currently active workspace."""
        try:
            returncode, stdout, stderr = hyprctl('activeworkspace -j')
            if returncode != 0:
                self.logger.error(f"Failed to get active workspace: {stderr}")
                return None
            
            workspace = json.loads(stdout)
            return workspace
        except Exception as e:
            self.logger.error(f"Error getting active workspace: {e}")
            return None
    
    def switch_to_next_workspace(self) -> bool:
        """Switch to the next workspace."""
        try:
            returncode, stdout, stderr = hyprctl('dispatch workspace +1')
            if returncode != 0:
                self.logger.error(f"Failed to switch to next workspace: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error switching to next workspace: {e}")
            return False
    
    def switch_to_previous_workspace(self) -> bool:
        """Switch to the previous workspace."""
        try:
            returncode, stdout, stderr = hyprctl('dispatch workspace -1')
            if returncode != 0:
                self.logger.error(f"Failed to switch to previous workspace: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error switching to previous workspace: {e}")
            return False
    
    def toggle_special_workspace(self, name: str = "special") -> bool:
        """Toggle a special workspace (scratchpad)."""
        try:
            returncode, stdout, stderr = hyprctl(f'dispatch togglespecialworkspace {name}')
            if returncode != 0:
                self.logger.error(f"Failed to toggle special workspace: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error toggling special workspace: {e}")
            return False
    
    def move_to_special_workspace(self, name: str = "special") -> bool:
        """Move active window to special workspace."""
        try:
            returncode, stdout, stderr = hyprctl(f'dispatch movetoworkspace special:{name}')
            if returncode != 0:
                self.logger.error(f"Failed to move to special workspace: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error moving to special workspace: {e}")
            return False
    
    def set_layout(self, layout: str) -> bool:
        """Set workspace layout ('dwindle' or 'master')."""
        try:
            if layout not in ['dwindle', 'master']:
                self.logger.error(f"Invalid layout: {layout}")
                return False
            
            returncode, stdout, stderr = hyprctl(f'keyword general:layout {layout}')
            if returncode != 0:
                self.logger.error(f"Failed to set layout: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error setting layout: {e}")
            return False
    
    def toggle_pseudotile(self) -> bool:
        """Toggle pseudotile for the active window."""
        try:
            returncode, stdout, stderr = hyprctl('dispatch pseudo')
            if returncode != 0:
                self.logger.error(f"Failed to toggle pseudotile: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error toggling pseudotile: {e}")
            return False
    
    def cycle_next_window(self) -> bool:
        """Cycle to the next window in the workspace."""
        try:
            returncode, stdout, stderr = hyprctl('dispatch cyclenext')
            if returncode != 0:
                self.logger.error(f"Failed to cycle to next window: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error cycling to next window: {e}")
            return False
    
    def cycle_previous_window(self) -> bool:
        """Cycle to the previous window in the workspace."""
        try:
            returncode, stdout, stderr = hyprctl('dispatch cyclenext prev')
            if returncode != 0:
                self.logger.error(f"Failed to cycle to previous window: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error cycling to previous window: {e}")
            return False
    
    def swap_with_master(self) -> bool:
        """Swap the active window with the master window."""
        try:
            returncode, stdout, stderr = hyprctl('dispatch layoutmsg swapwithmaster')
            if returncode != 0:
                self.logger.error(f"Failed to swap with master: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error swapping with master: {e}")
            return False
    
    def focus_master(self) -> bool:
        """Focus the master window."""
        try:
            returncode, stdout, stderr = hyprctl('dispatch layoutmsg focusmaster')
            if returncode != 0:
                self.logger.error(f"Failed to focus master: {stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error focusing master: {e}")
            return False
    
    def get_workspace_windows(self, workspace_id: int) -> List[Dict[str, Any]]:
        """Get all windows in a specific workspace."""
        try:
            returncode, stdout, stderr = hyprctl('clients -j')
            if returncode != 0:
                self.logger.error(f"Failed to get clients: {stderr}")
                return []
            
            all_windows = json.loads(stdout)
            workspace_windows = [
                window for window in all_windows 
                if window.get('workspace', {}).get('id') == workspace_id
            ]
            
            return workspace_windows
        except Exception as e:
            self.logger.error(f"Error getting workspace windows: {e}")
            return []
    
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
