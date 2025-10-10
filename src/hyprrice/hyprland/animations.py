"""
Animation management for Hyprland
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..utils import hyprctl, parse_hyprland_config, write_hyprland_config


class AnimationManager:
    """Manages Hyprland animations and effects."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path if config_path else str(Path.home() / ".config" / "hypr" / "hyprland.conf")
        self.logger = logging.getLogger(__name__)
        self.presets_dir = Path.home() / ".hyprrice" / "animation_presets"
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        
        # Default animation configurations
        self.default_animations = {
            "workspaces": {
                "enabled": True,
                "curve": "easeOutQuart",
                "speed": 0.5
            },
            "windows": {
                "enabled": True,
                "curve": "easeOutQuart", 
                "speed": 0.5
            },
            "fade": {
                "enabled": True,
                "curve": "easeOutQuart",
                "speed": 0.5
            },
            "border": {
                "enabled": True,
                "curve": "easeOutQuart",
                "speed": 0.5
            },
            "borderangle": {
                "enabled": True,
                "curve": "easeOutQuart",
                "speed": 0.5
            }
        }
    
    def get_animation_config(self) -> Dict[str, Any]:
        """Get current animation configuration from hyprctl."""
        try:
            returncode, stdout, stderr = hyprctl('getoption animations:enabled')
            if returncode != 0:
                self.logger.error(f"Failed to get animation status: {stderr}")
                return {}
            
            # Parse hyprctl output
            config = {}
            for line in stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Convert string values to appropriate types
                    if value.lower() in ['true', '1', 'yes']:
                        config[key] = True
                    elif value.lower() in ['false', '0', 'no']:
                        config[key] = False
                    elif value.replace('.', '').isdigit():
                        config[key] = float(value)
                    else:
                        config[key] = value
            
            return config
        except Exception as e:
            self.logger.error(f"Error getting animation config: {e}")
            return {}
    
    def set_animation_config(self, config: Dict[str, Any]) -> bool:
        """Set animation configuration."""
        try:
            success = True
            
            # Apply each animation setting
            for key, value in config.items():
                if key.startswith('animations:'):
                    returncode, stdout, stderr = hyprctl(f'keyword {key} {value}')
                    if returncode != 0:
                        self.logger.error(f"Failed to set {key}: {stderr}")
                        success = False
            
            return success
        except Exception as e:
            self.logger.error(f"Error setting animation config: {e}")
            return False
    
    def apply_animations(self, config: Dict[str, Any]) -> bool:
        """Apply animation configuration to Hyprland."""
        try:
            # Convert config to hyprctl commands
            commands = []
            
            # General animation settings
            if 'animations_enabled' in config:
                enabled = "1" if config['animations_enabled'] else "0"
                commands.append(f"animations:enabled {enabled}")
            
            if 'animation_duration' in config:
                duration = config['animation_duration']
                commands.append(f"animations:workspaces:curve easeOutQuart")
                commands.append(f"animations:workspaces:speed {duration}")
                commands.append(f"animations:windows:curve easeOutQuart")
                commands.append(f"animations:windows:speed {duration}")
                commands.append(f"animations:fade:curve easeOutQuart")
                commands.append(f"animations:fade:speed {duration}")
                commands.append(f"animations:border:curve easeOutQuart")
                commands.append(f"animations:border:speed {duration}")
                commands.append(f"animations:borderangle:curve easeOutQuart")
                commands.append(f"animations:borderangle:speed {duration}")
            
            if 'animation_curve' in config:
                curve = config['animation_curve']
                commands.append(f"animations:workspaces:curve {curve}")
                commands.append(f"animations:windows:curve {curve}")
                commands.append(f"animations:fade:curve {curve}")
                commands.append(f"animations:border:curve {curve}")
                commands.append(f"animations:borderangle:curve {curve}")
            
            # Apply commands
            for command in commands:
                returncode, stdout, stderr = hyprctl(f'keyword {command}')
                if returncode != 0:
                    self.logger.error(f"Failed to apply {command}: {stderr}")
                    return False
            
            # Update config file
            self._update_config_file(config)
            
            self.logger.info("Animation configuration applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying animations: {e}")
            return False
    
    def enable_animations(self) -> bool:
        """Enable all animations."""
        return self.set_animation_config({'animations:enabled': True})
    
    def disable_animations(self) -> bool:
        """Disable all animations."""
        return self.set_animation_config({'animations:enabled': False})
    
    def set_animation_duration(self, duration: float) -> bool:
        """Set animation duration for all animation types."""
        if not 0.1 <= duration <= 5.0:
            self.logger.error(f"Invalid animation duration: {duration}")
            return False
        
        config = {
            'animations:workspaces:speed': duration,
            'animations:windows:speed': duration,
            'animations:fade:speed': duration,
            'animations:border:speed': duration,
            'animations:borderangle:speed': duration
        }
        
        return self.set_animation_config(config)
    
    def set_animation_curve(self, curve: str) -> bool:
        """Set animation curve for all animation types."""
        valid_curves = [
            'linear', 'ease', 'easeIn', 'easeOut', 'easeInOut',
            'easeInQuart', 'easeOutQuart', 'easeInOutQuart',
            'easeInCubic', 'easeOutCubic', 'easeInOutCubic',
            'easeInExpo', 'easeOutExpo', 'easeInOutExpo'
        ]
        
        if curve not in valid_curves:
            self.logger.error(f"Invalid animation curve: {curve}")
            return False
        
        config = {
            'animations:workspaces:curve': curve,
            'animations:windows:curve': curve,
            'animations:fade:curve': curve,
            'animations:border:curve': curve,
            'animations:borderangle:curve': curve
        }
        
        return self.set_animation_config(config)
    
    def get_animation_status(self) -> Dict[str, Any]:
        """Get current animation status and settings."""
        try:
            status = {}
            
            # Get general animation status
            returncode, stdout, stderr = hyprctl('getoption animations:enabled')
            if returncode == 0:
                status['enabled'] = 'true' in stdout.lower()
            
            # Get specific animation settings
            animation_types = ['workspaces', 'windows', 'fade', 'border', 'borderangle']
            for anim_type in animation_types:
                # Get curve
                returncode, stdout, stderr = hyprctl(f'getoption animations:{anim_type}:curve')
                if returncode == 0:
                    status[f'{anim_type}_curve'] = stdout.strip()
                
                # Get speed
                returncode, stdout, stderr = hyprctl(f'getoption animations:{anim_type}:speed')
                if returncode == 0:
                    try:
                        status[f'{anim_type}_speed'] = float(stdout.strip())
                    except ValueError:
                        status[f'{anim_type}_speed'] = 0.5
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting animation status: {e}")
            return {}
    
    def create_animation_preset(self, name: str, config: Dict[str, Any]) -> bool:
        """Create a new animation preset."""
        try:
            preset_path = self.presets_dir / f"{name}.json"
            
            # Validate preset name
            if not name.replace('_', '').replace('-', '').isalnum():
                self.logger.error(f"Invalid preset name: {name}")
                return False
            
            # Save preset
            with open(preset_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Animation preset '{name}' created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating animation preset: {e}")
            return False
    
    def load_animation_preset(self, name: str) -> Dict[str, Any]:
        """Load an animation preset."""
        try:
            preset_path = self.presets_dir / f"{name}.json"
            
            if not preset_path.exists():
                self.logger.error(f"Preset '{name}' not found")
                return {}
            
            with open(preset_path, 'r') as f:
                config = json.load(f)
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading animation preset: {e}")
            return {}
    
    def list_animation_presets(self) -> List[str]:
        """List available animation presets."""
        try:
            presets = []
            for preset_file in self.presets_dir.glob("*.json"):
                presets.append(preset_file.stem)
            
            return sorted(presets)
            
        except Exception as e:
            self.logger.error(f"Error listing animation presets: {e}")
            return []
    
    def _update_config_file(self, config: Dict[str, Any]) -> None:
        """Update the Hyprland config file with animation settings."""
        try:
            sections = parse_hyprland_config(self.config_path)
            
            # Update animations section
            if 'animations' not in sections:
                sections['animations'] = []
            
            # Clear existing animation settings
            sections['animations'] = [line for line in sections['animations'] 
                                    if not any(key in line for key in ['enabled', 'curve', 'speed'])]
            
            # Add new animation settings
            if 'animations_enabled' in config:
                enabled = "1" if config['animations_enabled'] else "0"
                sections['animations'].append(f"enabled = {enabled}")
            
            if 'animation_duration' in config:
                duration = config['animation_duration']
                sections['animations'].extend([
                    f"workspaces:curve = easeOutQuart",
                    f"workspaces:speed = {duration}",
                    f"windows:curve = easeOutQuart", 
                    f"windows:speed = {duration}",
                    f"fade:curve = easeOutQuart",
                    f"fade:speed = {duration}",
                    f"border:curve = easeOutQuart",
                    f"border:speed = {duration}",
                    f"borderangle:curve = easeOutQuart",
                    f"borderangle:speed = {duration}"
                ])
            
            if 'animation_curve' in config:
                curve = config['animation_curve']
                sections['animations'].extend([
                    f"workspaces:curve = {curve}",
                    f"windows:curve = {curve}",
                    f"fade:curve = {curve}",
                    f"border:curve = {curve}",
                    f"borderangle:curve = {curve}"
                ])
            
            # Write updated config
            write_hyprland_config(self.config_path, sections)
            
        except Exception as e:
            self.logger.error(f"Error updating config file: {e}")
            raise 
