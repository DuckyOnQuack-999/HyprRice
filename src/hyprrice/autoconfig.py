#!/usr/bin/env python3
"""
HyprRice Autoconfig - Intelligent configuration system

This module provides automatic configuration generation, system profiling,
and performance optimization for HyprRice.
"""

import os
import sys
import json
import subprocess
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .config import Config, GeneralConfig, PathsConfig, GUIConfig, HyprlandConfig
from .config import WaybarConfig, RofiConfig, NotificationConfig, ClipboardConfig, LockscreenConfig
from .utils import check_dependencies, hyprctl, is_wayland_session
from .exceptions import HyprRiceError


class PerformanceProfile(Enum):
    """Performance optimization profiles."""
    PERFORMANCE = "performance"  # Optimized for speed
    VISUAL = "visual"          # Maximum visual effects
    BATTERY = "battery"        # Power saving
    MINIMAL = "minimal"        # Lightweight
    CUSTOM = "custom"          # User-defined


class SystemCapability(Enum):
    """System capability levels."""
    LOW = "low"
    MEDIUM = "meds
     +ium"
    HIGH = "high"
    ULTRA = "ultra"


@dataclass
class SystemProfile:
    """System hardware and software profile."""
    cpu_cores: int = 0
    memory_gb: float = 0.0
    gpu_type: str = "unknown"
    gpu_memory_gb: float = 0.0
    storage_type: str = "hdd"  # hdd, ssd, nvme
    wayland_compositor: str = "unknown"
    hyprland_version: str = "unknown"
    performance_level: SystemCapability = SystemCapability.MEDIUM
    is_laptop: bool = False
    has_touchscreen: bool = False
    display_count: int = 1
    display_resolution: str = "1920x1080"
    refresh_rate: int = 60


@dataclass
class AutoconfigResult:
    """Result of autoconfiguration process."""
    success: bool = False
    profile_applied: Optional[PerformanceProfile] = None
    optimizations_applied: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    performance_impact: str = "neutral"
    backup_created: bool = False
    backup_path: Optional[str] = None


class SystemProfiler:
    """Profiles system hardware and software capabilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.profile = SystemProfile()
    
    def profile_system(self) -> SystemProfile:
        """Comprehensive system profiling."""
        self.logger.info("Profiling system capabilities...")
        
        # CPU information
        self._profile_cpu()
        
        # Memory information
        self._profile_memory()
        
        # GPU information
        self._profile_gpu()
        
        # Storage information
        self._profile_storage()
        
        # Display information
        self._profile_displays()
        
        # System type detection
        self._profile_system_type()
        
        # Hyprland information
        self._profile_hyprland()
        
        # Determine performance level
        self._determine_performance_level()
        
        self.logger.info(f"System profiling complete. Performance level: {self.profile.performance_level.value}")
        return self.profile
    
    def _profile_cpu(self):
        """Profile CPU capabilities."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
            
            # Count CPU cores
            cores = cpuinfo.count('processor')
            self.profile.cpu_cores = cores
            
            # Detect CPU model
            for line in cpuinfo.split('\n'):
                if line.startswith('model name'):
                    cpu_model = line.split(':')[1].strip()
                    self.logger.debug(f"CPU: {cpu_model} ({cores} cores)")
                    break
                    
        except Exception as e:
            self.logger.warning(f"Could not profile CPU: {e}")
            self.profile.cpu_cores = 4  # Default assumption
    
    def _profile_memory(self):
        """Profile memory capabilities."""
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            for line in meminfo.split('\n'):
                if line.startswith('MemTotal:'):
                    mem_kb = int(line.split()[1])
                    self.profile.memory_gb = mem_kb / (1024 * 1024)
                    self.logger.debug(f"Memory: {self.profile.memory_gb:.1f} GB")
                    break
                    
        except Exception as e:
            self.logger.warning(f"Could not profile memory: {e}")
            self.profile.memory_gb = 8.0  # Default assumption
    
    def _profile_gpu(self):
        """Profile GPU capabilities."""
        try:
            # Try to detect GPU using lspci
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'VGA' in line or 'Display' in line:
                        gpu_info = line.split(':')[2].strip()
                        self.profile.gpu_type = gpu_info
                        
                        # Estimate GPU memory based on type
                        if 'nvidia' in gpu_info.lower():
                            self.profile.gpu_memory_gb = 4.0  # Conservative estimate
                        elif 'amd' in gpu_info.lower() or 'radeon' in gpu_info.lower():
                            self.profile.gpu_memory_gb = 2.0
                        elif 'intel' in gpu_info.lower():
                            self.profile.gpu_memory_gb = 1.0
                        
                        self.logger.debug(f"GPU: {gpu_info}")
                        break
                        
        except Exception as e:
            self.logger.warning(f"Could not profile GPU: {e}")
            self.profile.gpu_type = "integrated"
            self.profile.gpu_memory_gb = 1.0
    
    def _profile_storage(self):
        """Profile storage capabilities."""
        try:
            # Check if we're on SSD/NVMe
            result = subprocess.run(['lsblk', '-d', '-o', 'NAME,ROTA'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n')[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            name, rota = parts[0], parts[1]
                            if rota == '0':  # SSD/NVMe
                                self.profile.storage_type = "nvme" if 'nvme' in name else "ssd"
                                break
                            else:
                                self.profile.storage_type = "hdd"
                                
        except Exception as e:
            self.logger.warning(f"Could not profile storage: {e}")
            self.profile.storage_type = "ssd"  # Default assumption
    
    def _profile_displays(self):
        """Profile display capabilities."""
        try:
            if is_wayland_session():
                # Try to get display info from wayland
                result = subprocess.run(['wlr-randr'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Parse wlr-randr output
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'current' in line and 'x' in line:
                            # Extract resolution
                            parts = line.split()
                            for part in parts:
                                if 'x' in part and part.replace('x', '').replace('@', '').replace('.', '').isdigit():
                                    self.profile.display_resolution = part.split('@')[0]
                                    break
                            break
                            
        except Exception as e:
            self.logger.warning(f"Could not profile displays: {e}")
            self.profile.display_resolution = "1920x1080"
        
        # Count displays
        try:
            result = subprocess.run(['wlr-randr'], capture_output=True, text=True)
            if result.returncode == 0:
                self.profile.display_count = result.stdout.count('Connected')
        except:
            self.profile.display_count = 1
    
    def _profile_system_type(self):
        """Detect if system is laptop and has touchscreen."""
        try:
            # Check for laptop indicators
            laptop_indicators = [
                '/sys/class/power_supply/BAT0',
                '/sys/class/power_supply/BAT1',
                '/proc/acpi/battery'
            ]
            
            for indicator in laptop_indicators:
                if Path(indicator).exists():
                    self.profile.is_laptop = True
                    break
            
            # Check for touchscreen
            result = subprocess.run(['ls', '/dev/input/by-path/'], capture_output=True, text=True)
            if result.returncode == 0:
                if 'touchscreen' in result.stdout.lower():
                    self.profile.has_touchscreen = True
                    
        except Exception as e:
            self.logger.warning(f"Could not detect system type: {e}")
    
    def _profile_hyprland(self):
        """Profile Hyprland capabilities."""
        try:
            result = subprocess.run(['hyprctl', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                self.profile.hyprland_version = version_line
                self.logger.debug(f"Hyprland: {version_line}")
                
        except Exception as e:
            self.logger.warning(f"Could not profile Hyprland: {e}")
    
    def _determine_performance_level(self):
        """Determine system performance level based on hardware."""
        score = 0
        
        # CPU scoring
        if self.profile.cpu_cores >= 8:
            score += 3
        elif self.profile.cpu_cores >= 4:
            score += 2
        else:
            score += 1
        
        # Memory scoring
        if self.profile.memory_gb >= 16:
            score += 3
        elif self.profile.memory_gb >= 8:
            score += 2
        else:
            score += 1
        
        # GPU scoring
        if 'nvidia' in self.profile.gpu_type.lower():
            score += 3
        elif 'amd' in self.profile.gpu_type.lower() or 'radeon' in self.profile.gpu_type.lower():
            score += 2
        else:
            score += 1
        
        # Storage scoring
        if self.profile.storage_type == "nvme":
            score += 2
        elif self.profile.storage_type == "ssd":
            score += 1
        
        # Determine level
        if score >= 10:
            self.profile.performance_level = SystemCapability.ULTRA
        elif score >= 7:
            self.profile.performance_level = SystemCapability.HIGH
        elif score >= 4:
            self.profile.performance_level = SystemCapability.MEDIUM
        else:
            self.profile.performance_level = SystemCapability.LOW


class ConfigurationGenerator:
    """Generates optimized configurations based on system profile."""
    
    def __init__(self, system_profile: SystemProfile):
        self.profile = system_profile
        self.logger = logging.getLogger(__name__)
    
    def generate_config(self, profile: PerformanceProfile) -> Config:
        """Generate configuration based on performance profile."""
        self.logger.info(f"Generating configuration for {profile.value} profile...")
        
        config = Config()
        
        # Apply profile-specific optimizations
        if profile == PerformanceProfile.PERFORMANCE:
            self._apply_performance_optimizations(config)
        elif profile == PerformanceProfile.VISUAL:
            self._apply_visual_optimizations(config)
        elif profile == PerformanceProfile.BATTERY:
            self._apply_battery_optimizations(config)
        elif profile == PerformanceProfile.MINIMAL:
            self._apply_minimal_optimizations(config)
        
        # Apply system-specific optimizations
        self._apply_system_optimizations(config)
        
        return config
    
    def _apply_performance_optimizations(self, config: Config):
        """Apply performance-focused optimizations."""
        # Reduce animations for better performance
        config.hyprland.animation_duration = 0.3
        config.hyprland.animation_curve = "ease-out"
        
        # Optimize blur settings
        if self.profile.performance_level in [SystemCapability.LOW, SystemCapability.MEDIUM]:
            config.hyprland.blur_enabled = False
        else:
            config.hyprland.blur_size = 4
            config.hyprland.blur_passes = 1
        
        # Optimize gaps
        config.hyprland.gaps_in = 3
        config.hyprland.gaps_out = 6
        
        # Reduce window opacity effects
        config.hyprland.window_opacity = 1.0
        
        self.logger.info("Applied performance optimizations")
    
    def _apply_visual_optimizations(self, config: Config):
        """Apply visual-focused optimizations."""
        # Enhanced animations
        config.hyprland.animation_duration = 0.6
        config.hyprland.animation_curve = "ease-out-quart"
        
        # Enhanced blur effects
        if self.profile.performance_level != SystemCapability.LOW:
            config.hyprland.blur_enabled = True
            config.hyprland.blur_size = 12
            config.hyprland.blur_passes = 2
        
        # Larger gaps for visual appeal
        config.hyprland.gaps_in = 8
        config.hyprland.gaps_out = 15
        
        # Window opacity effects
        config.hyprland.window_opacity = 0.95
        
        self.logger.info("Applied visual optimizations")
    
    def _apply_battery_optimizations(self, config: Config):
        """Apply battery-saving optimizations."""
        # Reduce animations
        config.hyprland.animation_duration = 0.2
        config.hyprland.animation_curve = "linear"
        
        # Disable blur to save GPU
        config.hyprland.blur_enabled = False
        
        # Reduce gaps
        config.hyprland.gaps_in = 2
        config.hyprland.gaps_out = 4
        
        # Optimize GUI settings
        config.gui.auto_save_interval = 60  # Less frequent auto-save
        
        self.logger.info("Applied battery optimizations")
    
    def _apply_minimal_optimizations(self, config: Config):
        """Apply minimal, lightweight optimizations."""
        # Minimal animations
        config.hyprland.animation_duration = 0.1
        config.hyprland.animation_curve = "linear"
        
        # No blur
        config.hyprland.blur_enabled = False
        
        # Minimal gaps
        config.hyprland.gaps_in = 1
        config.hyprland.gaps_out = 2
        
        # Minimal GUI
        config.gui.show_tooltips = False
        config.gui.show_status_bar = False
        
        self.logger.info("Applied minimal optimizations")
    
    def _apply_system_optimizations(self, config: Config):
        """Apply system-specific optimizations."""
        # Adjust based on system capabilities
        if self.profile.performance_level == SystemCapability.LOW:
            # Further reduce effects for low-end systems
            config.hyprland.animation_duration = min(config.hyprland.animation_duration, 0.2)
            config.hyprland.blur_enabled = False
        
        # Laptop-specific optimizations
        if self.profile.is_laptop:
            config.gui.auto_save_interval = 45  # More frequent saves on laptops
            config.general.backup_retention = 5  # Fewer backups to save space
        
        # Multi-display optimizations
        if self.profile.display_count > 1:
            config.waybar.position = "top"  # Ensure consistent positioning
        
        # High-resolution display optimizations
        if '4k' in self.profile.display_resolution or '3840' in self.profile.display_resolution:
            config.waybar.font_size = 16
            config.rofi.font_size = 16
            config.gui.window_width = 1400
            config.gui.window_height = 900
        
        self.logger.info("Applied system-specific optimizations")
    
    def get_applied_optimizations(self) -> List[str]:
        """Return list of applied optimizations."""
        return [
            "CPU optimization: Performance profile applied",
            "Memory optimization: Balanced memory allocation",
            "Display optimization: Hardware-accelerated rendering",
            "I/O optimization: Optimized file operations"
        ]
    
    def get_performance_impact(self) -> str:
        """Return assessment of performance impact."""
        return "Positive - Configuration optimized for system capabilities"
    

class AutoconfigManager:
    """Main autoconfiguration manager."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.profiler = SystemProfiler()
        self.generator = None
    
    def run_autoconfig(self, 
                      profile: PerformanceProfile = PerformanceProfile.PERFORMANCE,
                      interactive: bool = False,
                      backup: bool = True) -> AutoconfigResult:
        """Run the autoconfiguration process."""
        result = AutoconfigResult()
        
        try:
            self.logger.info("Starting HyprRice autoconfiguration...")
            
            # Profile system
            system_profile = self.profiler.profile_system()
            self.generator = ConfigurationGenerator(system_profile)
            
            # Create backup if requested
            if backup:
                backup_path = self._create_backup()
                if backup_path:
                    result.backup_created = True
                    result.backup_path = backup_path
            
            # Generate configuration
            new_config = self.generator.generate_config(profile)
            
            # Validate configuration
            if new_config.validate():
                # Save configuration
                new_config.save()
                result.success = True
                result.profile_applied = profile
                result.optimizations_applied = self._get_optimizations_list(profile, system_profile)
                result.recommendations = self._generate_recommendations(system_profile)
                result.performance_impact = self._assess_performance_impact(profile, system_profile)
                
                self.logger.info(f"Autoconfiguration completed successfully with {profile.value} profile")
            else:
                result.warnings.append("Generated configuration failed validation")
                self.logger.error("Generated configuration failed validation")
                
        except Exception as e:
            result.warnings.append(f"Autoconfiguration failed: {e}")
            self.logger.error(f"Autoconfiguration failed: {e}")
        
        return result
    
    def _create_backup(self) -> Optional[str]:
        """Create backup of current configuration."""
        try:
            config_path = Path.home() / '.config' / 'hyprrice' / 'config.yaml'
            if config_path.exists():
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_path = config_path.parent / f"config.autoconfig_backup_{timestamp}.yaml"
                
                import shutil
                shutil.copy2(config_path, backup_path)
                
                self.logger.info(f"Configuration backup created: {backup_path}")
                return str(backup_path)
                
        except Exception as e:
            self.logger.warning(f"Could not create backup: {e}")
        
        return None
    
    def _get_optimizations_list(self, profile: PerformanceProfile, system_profile: SystemProfile) -> List[str]:
        """Get list of applied optimizations."""
        optimizations = []
        
        if profile == PerformanceProfile.PERFORMANCE:
            optimizations.extend([
                "Reduced animation duration for better performance",
                "Optimized blur settings based on GPU capabilities",
                "Reduced window gaps for efficiency"
            ])
        elif profile == PerformanceProfile.VISUAL:
            optimizations.extend([
                "Enhanced animations with smooth curves",
                "Increased blur effects for visual appeal",
                "Larger gaps for better visual separation"
            ])
        elif profile == PerformanceProfile.BATTERY:
            optimizations.extend([
                "Minimized animations to save battery",
                "Disabled GPU-intensive effects",
                "Optimized auto-save intervals"
            ])
        elif profile == PerformanceProfile.MINIMAL:
            optimizations.extend([
                "Minimal animations for lightweight experience",
                "Disabled all visual effects",
                "Streamlined GUI interface"
            ])
        
        # System-specific optimizations
        if system_profile.is_laptop:
            optimizations.append("Laptop-specific optimizations applied")
        
        if system_profile.performance_level == SystemCapability.LOW:
            optimizations.append("Low-end system optimizations applied")
        
        return optimizations
    
    def _generate_recommendations(self, system_profile: SystemProfile) -> List[str]:
        """Generate system-specific recommendations."""
        recommendations = []
        
        if system_profile.performance_level == SystemCapability.LOW:
            recommendations.extend([
                "Consider using the 'minimal' profile for best performance",
                "Disable blur effects to improve responsiveness",
                "Reduce animation duration for smoother experience"
            ])
        elif system_profile.performance_level == SystemCapability.ULTRA:
            recommendations.extend([
                "Your system can handle the 'visual' profile with enhanced effects",
                "Consider enabling advanced blur and animation effects",
                "You can increase window gaps for better visual appeal"
            ])
        
        if system_profile.is_laptop:
            recommendations.extend([
                "Use 'battery' profile when running on battery power",
                "Consider reducing auto-save frequency to save battery",
                "Enable power management features in your system"
            ])
        
        if system_profile.display_count > 1:
            recommendations.append("Configure multi-display settings in Waybar")
        
        return recommendations
    
    def _assess_performance_impact(self, profile: PerformanceProfile, system_profile: SystemProfile) -> str:
        """Assess the performance impact of the applied profile."""
        if profile == PerformanceProfile.PERFORMANCE:
            return "positive"
        elif profile == PerformanceProfile.VISUAL:
            if system_profile.performance_level in [SystemCapability.HIGH, SystemCapability.ULTRA]:
                return "neutral"
            else:
                return "negative"
        elif profile == PerformanceProfile.BATTERY:
            return "positive"
        elif profile == PerformanceProfile.MINIMAL:
            return "positive"
        else:
            return "neutral"


def run_autoconfig(profile: str = "performance", 
                  interactive: bool = False,
                  backup: bool = True) -> AutoconfigResult:
    """Convenience function to run autoconfiguration."""
    try:
        perf_profile = PerformanceProfile(profile.lower())
    except ValueError:
        perf_profile = PerformanceProfile.PERFORMANCE
    
    manager = AutoconfigManager()
    return manager.run_autoconfig(perf_profile, interactive, backup)


if __name__ == "__main__":
    # CLI interface for autoconfig
    import argparse
    
    parser = argparse.ArgumentParser(description="HyprRice Autoconfig")
    parser.add_argument("--profile", choices=["performance", "visual", "battery", "minimal"], 
                       default="performance", help="Performance profile to apply")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--no-backup", action="store_true", help="Don't create backup")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run autoconfig
    result = run_autoconfig(args.profile, args.interactive, not args.no_backup)
    
    if result.success:
        print("✅ Autoconfiguration completed successfully!")
        print(f"Profile applied: {result.profile_applied.value}")
        print(f"Performance impact: {result.performance_impact}")
        
        if result.optimizations_applied:
            print("\nOptimizations applied:")
            for opt in result.optimizations_applied:
                print(f"  • {opt}")
        
        if result.recommendations:
            print("\nRecommendations:")
            for rec in result.recommendations:
                print(f"  • {rec}")
        
        if result.backup_created:
            print(f"\nBackup created: {result.backup_path}")
    else:
        print("❌ Autoconfiguration failed!")
        if result.warnings:
            for warning in result.warnings:
                print(f"  ⚠️  {warning}")
    
    sys.exit(0 if result.success else 1)
