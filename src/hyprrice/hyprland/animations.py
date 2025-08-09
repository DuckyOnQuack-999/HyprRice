import logging
import os
from typing import Dict, Any

class AnimationManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
    
    def get_animation_config(self):
        """Get current animation configuration from hyprland.conf"""
        try:
            from ..utils import parse_hyprland_config
            sections = parse_hyprland_config(self.config_path)
            return sections.get('animations', [])
        except Exception as e:
            self.logger.error(f"Failed to get animation config: {e}")
            return []

    def set_animation_config(self, config):
        """Set animation configuration in hyprland.conf"""
        try:
            from ..utils import parse_hyprland_config, write_hyprland_config
            sections = parse_hyprland_config(self.config_path)
            
            # Build animation configuration
            anim_config = []
            if config.get('animations_enabled', True):
                anim_config.append("enabled = yes")
                
                # Add bezier curves
                anim_config.append("bezier = myBezier, 0.05, 0.9, 0.1, 1.05")
                anim_config.append("bezier = smoothOut, 0.36, 0, 0.66, -0.56")
                anim_config.append("bezier = smoothIn, 0.25, 1, 0.5, 1")
                
                # Add animation definitions
                duration = config.get('animation_duration', 0.5)
                curve = config.get('animation_curve', 'ease-out')
                
                # Map curve names to bezier curves
                curve_map = {
                    'ease-out': 'smoothOut',
                    'ease-in': 'smoothIn', 
                    'ease-in-out': 'myBezier',
                    'linear': 'default'
                }
                
                bezier_curve = curve_map.get(curve, 'default')
                
                animations = [
                    f"animation = windows, 1, {int(duration*10)}, {bezier_curve}",
                    f"animation = windowsOut, 1, {int(duration*7)}, default, popin 80%",
                    f"animation = border, 1, {int(duration*10)}, default",
                    f"animation = borderangle, 1, {int(duration*8)}, default",
                    f"animation = fade, 1, {int(duration*7)}, default",
                    f"animation = workspaces, 1, {int(duration*6)}, default",
                    f"animation = specialWorkspace, 1, {int(duration*6)}, default, slidevert",
                ]
                anim_config.extend(animations)
            else:
                anim_config.append("enabled = no")
            
            sections['animations'] = anim_config
            write_hyprland_config(self.config_path, sections)
            
            # Apply via hyprctl
            self._reload_hyprland_config()
            
        except Exception as e:
            self.logger.error(f"Failed to set animation config: {e}")
            raise

    def apply_animations(self, config):
        """Apply animation configuration to running Hyprland instance"""
        try:
            from ..utils import run_command
            
            if config.get('animations_enabled', True):
                # Enable animations
                run_command(['hyprctl', 'keyword', 'animations:enabled', 'true'])
                
                # Set animation duration and curve
                duration = config.get('animation_duration', 0.5)
                curve = config.get('animation_curve', 'ease-out')
                
                # Map curve names to bezier curves
                curve_map = {
                    'ease-out': 'smoothOut',
                    'ease-in': 'smoothIn',
                    'ease-in-out': 'myBezier', 
                    'linear': 'default'
                }
                
                bezier_curve = curve_map.get(curve, 'default')
                
                # Define bezier curves
                bezier_curves = [
                    'animations:bezier = myBezier, 0.05, 0.9, 0.1, 1.05',
                    'animations:bezier = smoothOut, 0.36, 0, 0.66, -0.56',
                    'animations:bezier = smoothIn, 0.25, 1, 0.5, 1'
                ]
                
                for bezier in bezier_curves:
                    run_command(['hyprctl', 'keyword', bezier])
                
                # Apply individual animation settings
                animations = {
                    'windows': f"1,{int(duration*10)},{bezier_curve}",
                    'windowsOut': f"1,{int(duration*7)},default,popin 80%",
                    'border': f"1,{int(duration*10)},default",
                    'borderangle': f"1,{int(duration*8)},default",
                    'fade': f"1,{int(duration*7)},default",
                    'workspaces': f"1,{int(duration*6)},default",
                    'specialWorkspace': f"1,{int(duration*6)},default,slidevert"
                }
                
                for anim_type, anim_config in animations.items():
                    run_command(['hyprctl', 'keyword', f'animation', f'{anim_type},{anim_config}'])
            else:
                # Disable animations
                run_command(['hyprctl', 'keyword', 'animations:enabled', 'false'])
                
            self.logger.info("Animation configuration applied successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to apply animations: {e}")
            raise
    
    def get_available_curves(self):
        """Get list of available animation curves."""
        return ['linear', 'ease-in', 'ease-out', 'ease-in-out']
    
    def get_animation_presets(self):
        """Get predefined animation presets."""
        return {
            'fast': {'duration': 0.2, 'curve': 'ease-out'},
            'normal': {'duration': 0.5, 'curve': 'ease-out'},
            'slow': {'duration': 1.0, 'curve': 'ease-in-out'},
            'bouncy': {'duration': 0.8, 'curve': 'ease-in-out'},
            'smooth': {'duration': 0.6, 'curve': 'ease-out'}
        }
    
    def apply_preset(self, preset_name: str):
        """Apply a predefined animation preset."""
        presets = self.get_animation_presets()
        if preset_name in presets:
            preset = presets[preset_name]
            config = {
                'animations_enabled': True,
                'animation_duration': preset['duration'],
                'animation_curve': preset['curve']
            }
            self.apply_animations(config)
        else:
            raise ValueError(f"Unknown preset: {preset_name}")
    
    def _reload_hyprland_config(self):
        """Reload Hyprland configuration"""
        try:
            from ..utils import run_command
            run_command(['hyprctl', 'reload'])
        except Exception as e:
            self.logger.warning(f"Failed to reload Hyprland config: {e}")
    
    def test_animation(self, animation_type: str = 'windows'):
        """Test a specific animation by triggering a demonstration."""
        try:
            from ..utils import run_command
            
            if animation_type == 'windows':
                # Open and close a test window
                run_command(['hyprctl', 'dispatch', 'exec', 'sleep 0.1 && exit'])
            elif animation_type == 'workspaces':
                # Switch workspaces
                run_command(['hyprctl', 'dispatch', 'workspace', '1'])
                run_command(['hyprctl', 'dispatch', 'workspace', '2'])
                run_command(['hyprctl', 'dispatch', 'workspace', '1'])
            elif animation_type == 'fade':
                # Toggle a window's floating state
                run_command(['hyprctl', 'dispatch', 'togglefloating'])
                
        except Exception as e:
            self.logger.error(f"Failed to test animation: {e}")
            raise 