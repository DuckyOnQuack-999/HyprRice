"""
Input management for Hyprland configuration
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from ..utils import hyprctl, run_command, parse_hyprland_config, write_hyprland_config
from ..exceptions import HyprlandError


class InputManager:
    """Manages Hyprland input device configuration."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        self._input_config = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load current input configuration from Hyprland config."""
        try:
            if self.config_path.exists():
                sections = parse_hyprland_config(str(self.config_path))
                self._input_config = sections.get('input', {})
            else:
                self.logger.warning(f"Config file not found: {self.config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load input config: {e}")
            raise HyprlandError(f"Could not load input configuration: {e}")
    
    def get_input_config(self) -> Dict[str, Any]:
        """Get current input configuration."""
        return {
            'kb_layout': self._get_config_value('kb_layout', 'us'),
            'kb_variant': self._get_config_value('kb_variant', ''),
            'kb_model': self._get_config_value('kb_model', ''),
            'kb_options': self._get_config_value('kb_options', ''),
            'kb_rules': self._get_config_value('kb_rules', ''),
            'repeat_rate': self._get_config_value('repeat_rate', 25),
            'repeat_delay': self._get_config_value('repeat_delay', 600),
            'numlock_by_default': self._get_config_value('numlock_by_default', False),
            'sensitivity': self._get_config_value('sensitivity', 0.0),
            'accel_profile': self._get_config_value('accel_profile', 'adaptive'),
            'force_no_accel': self._get_config_value('force_no_accel', False),
            'left_handed': self._get_config_value('left_handed', False),
            'scroll_method': self._get_config_value('scroll_method', '2fg'),
            'natural_scroll': self._get_config_value('natural_scroll', False),
            'follow_mouse': self._get_config_value('follow_mouse', 1),
            'float_switch_override_focus': self._get_config_value('float_switch_override_focus', True),
            'touchpad': {
                'natural_scroll': self._get_config_value('touchpad:natural_scroll', True),
                'disable_while_typing': self._get_config_value('touchpad:disable_while_typing', True),
                'clickfinger_behavior': self._get_config_value('touchpad:clickfinger_behavior', False),
                'tap_to_click': self._get_config_value('touchpad:tap_to_click', True),
                'tap_and_drag': self._get_config_value('touchpad:tap_and_drag', True),
                'scroll_factor': self._get_config_value('touchpad:scroll_factor', 1.0),
                'middle_button_emulation': self._get_config_value('touchpad:middle_button_emulation', False),
            }
        }
    
    def _get_config_value(self, key: str, default: Any) -> Any:
        """Get configuration value with default fallback."""
        for line in self._input_config:
            if line.strip().startswith(key):
                try:
                    value_part = line.split('=', 1)[1].strip()
                    # Handle boolean values
                    if isinstance(default, bool):
                        return value_part.lower() in ('true', 'yes', '1', 'on')
                    # Handle numeric values
                    elif isinstance(default, (int, float)):
                        return type(default)(value_part)
                    # Handle string values
                    else:
                        return value_part
                except (IndexError, ValueError) as e:
                    self.logger.warning(f"Failed to parse config value for {key}: {e}")
        return default
    
    def set_input_config(self, config: Dict[str, Any]) -> None:
        """Set input configuration."""
        try:
            # Validate configuration
            self._validate_config(config)
            
            # Build new input configuration
            new_input_lines = []
            
            # Keyboard configuration
            if 'kb_layout' in config:
                new_input_lines.append(f"kb_layout = {config['kb_layout']}")
            if 'kb_variant' in config and config['kb_variant']:
                new_input_lines.append(f"kb_variant = {config['kb_variant']}")
            if 'kb_model' in config and config['kb_model']:
                new_input_lines.append(f"kb_model = {config['kb_model']}")
            if 'kb_options' in config and config['kb_options']:
                new_input_lines.append(f"kb_options = {config['kb_options']}")
            if 'kb_rules' in config and config['kb_rules']:
                new_input_lines.append(f"kb_rules = {config['kb_rules']}")
            
            # Repeat settings
            if 'repeat_rate' in config:
                new_input_lines.append(f"repeat_rate = {config['repeat_rate']}")
            if 'repeat_delay' in config:
                new_input_lines.append(f"repeat_delay = {config['repeat_delay']}")
            if 'numlock_by_default' in config:
                new_input_lines.append(f"numlock_by_default = {config['numlock_by_default']}")
            
            # Mouse configuration
            if 'sensitivity' in config:
                new_input_lines.append(f"sensitivity = {config['sensitivity']}")
            if 'accel_profile' in config:
                new_input_lines.append(f"accel_profile = {config['accel_profile']}")
            if 'force_no_accel' in config:
                new_input_lines.append(f"force_no_accel = {config['force_no_accel']}")
            if 'left_handed' in config:
                new_input_lines.append(f"left_handed = {config['left_handed']}")
            if 'scroll_method' in config:
                new_input_lines.append(f"scroll_method = {config['scroll_method']}")
            if 'natural_scroll' in config:
                new_input_lines.append(f"natural_scroll = {config['natural_scroll']}")
            if 'follow_mouse' in config:
                new_input_lines.append(f"follow_mouse = {config['follow_mouse']}")
            if 'float_switch_override_focus' in config:
                new_input_lines.append(f"float_switch_override_focus = {config['float_switch_override_focus']}")
            
            # Touchpad configuration
            if 'touchpad' in config and isinstance(config['touchpad'], dict):
                touchpad = config['touchpad']
                for key, value in touchpad.items():
                    new_input_lines.append(f"touchpad:{key} = {value}")
            
            # Update internal config
            self._input_config = new_input_lines
            
            self.logger.info("Input configuration updated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to set input config: {e}")
            raise HyprlandError(f"Could not set input configuration: {e}")
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate input configuration values."""
        # Validate repeat rate
        if 'repeat_rate' in config:
            rate = config['repeat_rate']
            if not isinstance(rate, (int, float)) or not (0 <= rate <= 100):
                raise ValueError("repeat_rate must be between 0 and 100")
        
        # Validate repeat delay
        if 'repeat_delay' in config:
            delay = config['repeat_delay']
            if not isinstance(delay, (int, float)) or not (0 <= delay <= 2000):
                raise ValueError("repeat_delay must be between 0 and 2000")
        
        # Validate sensitivity
        if 'sensitivity' in config:
            sens = config['sensitivity']
            if not isinstance(sens, (int, float)) or not (-1.0 <= sens <= 1.0):
                raise ValueError("sensitivity must be between -1.0 and 1.0")
        
        # Validate accel profile
        if 'accel_profile' in config:
            profile = config['accel_profile']
            if profile not in ['adaptive', 'flat']:
                raise ValueError("accel_profile must be 'adaptive' or 'flat'")
        
        # Validate scroll method
        if 'scroll_method' in config:
            method = config['scroll_method']
            if method not in ['2fg', 'edge', 'on_button_down', 'no_scroll']:
                raise ValueError("scroll_method must be '2fg', 'edge', 'on_button_down', or 'no_scroll'")
        
        # Validate follow_mouse
        if 'follow_mouse' in config:
            follow = config['follow_mouse']
            if not isinstance(follow, int) or not (0 <= follow <= 3):
                raise ValueError("follow_mouse must be between 0 and 3")
    
    def apply_input_config(self, config: Dict[str, Any]) -> bool:
        """Apply input configuration to the system."""
        try:
            # Set the configuration
            self.set_input_config(config)
            
            # Write to config file
            self._write_to_config_file()
            
            # Reload Hyprland configuration
            returncode, stdout, stderr = hyprctl('reload')
            if returncode != 0:
                self.logger.error(f"Failed to reload Hyprland: {stderr}")
                return False
            
            self.logger.info("Input configuration applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply input config: {e}")
            return False
    
    def _write_to_config_file(self) -> None:
        """Write input configuration to Hyprland config file."""
        try:
            # Load existing config
            if self.config_path.exists():
                sections = parse_hyprland_config(str(self.config_path))
            else:
                sections = {}
            
            # Update input section
            sections['input'] = self._input_config
            
            # Write back to file
            write_hyprland_config(str(self.config_path), sections)
            
        except Exception as e:
            self.logger.error(f"Failed to write config file: {e}")
            raise HyprlandError(f"Could not write configuration: {e}")
    
    def set_keyboard_repeat_rate(self, rate: int) -> bool:
        """Set keyboard repeat rate."""
        try:
            if not (0 <= rate <= 100):
                raise ValueError("Rate must be between 0 and 100")
            
            config = self.get_input_config()
            config['repeat_rate'] = rate
            return self.apply_input_config(config)
            
        except Exception as e:
            self.logger.error(f"Failed to set repeat rate: {e}")
            return False
    
    def set_keyboard_repeat_delay(self, delay: int) -> bool:
        """Set keyboard repeat delay."""
        try:
            if not (0 <= delay <= 2000):
                raise ValueError("Delay must be between 0 and 2000")
            
            config = self.get_input_config()
            config['repeat_delay'] = delay
            return self.apply_input_config(config)
            
        except Exception as e:
            self.logger.error(f"Failed to set repeat delay: {e}")
            return False
    
    def set_mouse_sensitivity(self, sensitivity: float) -> bool:
        """Set mouse sensitivity."""
        try:
            if not (-1.0 <= sensitivity <= 1.0):
                raise ValueError("Sensitivity must be between -1.0 and 1.0")
            
            config = self.get_input_config()
            config['sensitivity'] = sensitivity
            return self.apply_input_config(config)
            
        except Exception as e:
            self.logger.error(f"Failed to set mouse sensitivity: {e}")
            return False
    
    def set_mouse_accel_profile(self, profile: str) -> bool:
        """Set mouse acceleration profile."""
        try:
            if profile not in ['adaptive', 'flat']:
                raise ValueError("Profile must be 'adaptive' or 'flat'")
            
            config = self.get_input_config()
            config['accel_profile'] = profile
            return self.apply_input_config(config)
            
        except Exception as e:
            self.logger.error(f"Failed to set accel profile: {e}")
            return False
    
    def toggle_touchpad_natural_scroll(self, enabled: bool) -> bool:
        """Toggle touchpad natural scroll."""
        try:
            config = self.get_input_config()
            if 'touchpad' not in config:
                config['touchpad'] = {}
            config['touchpad']['natural_scroll'] = enabled
            return self.apply_input_config(config)
            
        except Exception as e:
            self.logger.error(f"Failed to toggle natural scroll: {e}")
            return False
    
    def toggle_touchpad_tap_to_click(self, enabled: bool) -> bool:
        """Toggle touchpad tap to click."""
        try:
            config = self.get_input_config()
            if 'touchpad' not in config:
                config['touchpad'] = {}
            config['touchpad']['tap_to_click'] = enabled
            return self.apply_input_config(config)
            
        except Exception as e:
            self.logger.error(f"Failed to toggle tap to click: {e}")
            return False
    
    def get_input_devices(self) -> List[Dict[str, str]]:
        """Get list of input devices."""
        try:
            returncode, stdout, stderr = hyprctl('devices')
            
            if returncode != 0:
                self.logger.error(f"Failed to get devices: {stderr}")
                return []
            
            devices = []
            current_device = {}
            device_type = None
            
            for line in stdout.split('\n'):
                line = line.strip()
                if not line:
                    if current_device and device_type:
                        current_device['type'] = device_type
                        devices.append(current_device)
                        current_device = {}
                    continue
                
                # Check for device type headers
                if line in ['Keyboards:', 'Mice:', 'Tablets:', 'Touch Devices:', 'Switches:']:
                    device_type = line.rstrip(':').lower()
                    continue
                
                # Parse device information
                if ':' in line and device_type:
                    if line.startswith('\t'):
                        # Device property
                        key, value = line.strip().split(':', 1)
                        current_device[key.strip()] = value.strip()
                    else:
                        # New device
                        if current_device:
                            current_device['type'] = device_type
                            devices.append(current_device)
                        current_device = {'name': line}
            
            # Add last device
            if current_device and device_type:
                current_device['type'] = device_type
                devices.append(current_device)
            
            return devices
            
        except Exception as e:
            self.logger.error(f"Failed to get input devices: {e}")
            return []
    
    def get_keyboard_layouts(self) -> List[str]:
        """Get available keyboard layouts."""
        # Common keyboard layouts
        return [
            'us', 'us(intl)', 'us(dvorak)', 'us(colemak)',
            'gb', 'de', 'fr', 'es', 'it', 'pt', 'br',
            'ru', 'ua', 'pl', 'cz', 'sk', 'hu', 'ro',
            'fi', 'se', 'no', 'dk', 'nl', 'be',
            'ch', 'at', 'ca', 'ca(fr)', 'mx',
            'jp', 'kr', 'cn', 'tw', 'hk',
            'in', 'ar', 'tr', 'gr', 'il'
        ]
    
    def reset_to_defaults(self) -> bool:
        """Reset input configuration to defaults."""
        try:
            default_config = {
                'kb_layout': 'us',
                'repeat_rate': 25,
                'repeat_delay': 600,
                'numlock_by_default': False,
                'sensitivity': 0.0,
                'accel_profile': 'adaptive',
                'force_no_accel': False,
                'left_handed': False,
                'scroll_method': '2fg',
                'natural_scroll': False,
                'follow_mouse': 1,
                'float_switch_override_focus': True,
                'touchpad': {
                    'natural_scroll': True,
                    'disable_while_typing': True,
                    'tap_to_click': True,
                    'tap_and_drag': True,
                    'scroll_factor': 1.0,
                    'middle_button_emulation': False,
                }
            }
            
            return self.apply_input_config(default_config)
            
        except Exception as e:
            self.logger.error(f"Failed to reset to defaults: {e}")
            return False 