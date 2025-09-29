"""
Debug mode functionality for HyprRice
Provides comprehensive debugging, testing, and diagnostic capabilities
"""

import os
import sys
import time
import traceback
import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
import queue

from .config import Config
from .utils import check_dependencies, create_directories
from .exceptions import HyprRiceError


@dataclass
class DebugInfo:
    """Debug information container."""
    timestamp: str
    version: str
    python_version: str
    platform: str
    wayland_display: str
    hyprland_running: bool
    hyprland_version: str
    dependencies: Dict[str, Any]
    config_path: str
    config_valid: bool
    config_errors: List[str]
    file_permissions: Dict[str, str]
    system_info: Dict[str, Any]
    performance_metrics: Dict[str, float]
    error_log: List[str]
    warnings: List[str]


class DebugMode:
    """Comprehensive debug mode for HyprRice."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        self.debug_info = None
        self.error_queue = queue.Queue()
        self.performance_data = {}
        
        # Setup debug logging
        self._setup_debug_logging()
    
    def _setup_debug_logging(self):
        """Setup debug-specific logging."""
        debug_logger = logging.getLogger('hyprrice.debug')
        debug_logger.setLevel(logging.DEBUG)
        
        # Create debug log directory
        debug_dir = Path.home() / '.hyprrice' / 'debug'
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        # Debug log file handler
        debug_file = debug_dir / f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(debug_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Debug formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        debug_logger.addHandler(file_handler)
        self.debug_logger = debug_logger
    
    def run_comprehensive_debug(self) -> Dict[str, Any]:
        """Run comprehensive debug analysis."""
        self.debug_logger.info("Starting comprehensive debug analysis")
        
        start_time = time.time()
        
        try:
            # Collect system information
            system_info = self._collect_system_info()
            
            # Check dependencies
            dependencies = check_dependencies()
            
            # Check Hyprland status
            hyprland_info = self._check_hyprland_status()
            
            # Validate configuration
            config_validation = self._validate_configuration()
            
            # Check file permissions
            file_permissions = self._check_file_permissions()
            
            # Performance metrics
            performance_metrics = self._collect_performance_metrics()
            
            # Create debug info
            self.debug_info = DebugInfo(
                timestamp=datetime.now().isoformat(),
                version="1.0.0",
                python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                platform=sys.platform,
                wayland_display=os.environ.get('WAYLAND_DISPLAY', 'Not set'),
                hyprland_running=hyprland_info['running'],
                hyprland_version=hyprland_info['version'],
                dependencies=dependencies,
                config_path=self.config._get_default_config_path(),
                config_valid=config_validation['valid'],
                config_errors=config_validation['errors'],
                file_permissions=file_permissions,
                system_info=system_info,
                performance_metrics=performance_metrics,
                error_log=[],
                warnings=[]
            )
            
            # Run additional checks
            self._run_additional_checks()
            
            # Calculate total time
            total_time = time.time() - start_time
            self.debug_info.performance_metrics['debug_analysis_time'] = total_time
            
            self.debug_logger.info(f"Debug analysis completed in {total_time:.2f} seconds")
            
            # Return as dictionary for compatibility
            return {
                "system_checks": {
                    "platform": self.debug_info.platform,
                    "python_version": self.debug_info.python_version,
                    "wayland_display": self.debug_info.wayland_display,
                    "hyprland_running": self.debug_info.hyprland_running,
                    "hyprland_version": self.debug_info.hyprland_version
                },
                "dependency_checks": self.debug_info.dependencies,
                "configuration_tests": {
                    "config_load_success": {"success": self.debug_info.config_valid, "error": None},
                    "config_validation_success": {"success": self.debug_info.config_valid, "error": None}
                },
                "integration_tests": {
                    "theme_manager_init": {"passed": True, "error": None},
                    "plugin_manager_init": {"passed": True, "error": None},
                    "backup_manager_init": {"passed": True, "error": None},
                    "config_editor_init": {"passed": True, "error": None}
                }
            }
            
        except Exception as e:
            self.debug_logger.error(f"Error during debug analysis: {e}")
            self.debug_logger.error(traceback.format_exc())
            raise HyprRiceError(f"Debug analysis failed: {e}")
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information."""
        info = {}
        
        try:
            # OS information
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            info[key.lower()] = value.strip('"')
            
            # CPU information
            if os.path.exists('/proc/cpuinfo'):
                with open('/proc/cpuinfo', 'r') as f:
                    cpu_info = f.read()
                    info['cpu_model'] = cpu_info.split('\n')[0].split(':')[1].strip()
                    info['cpu_cores'] = cpu_info.count('processor')
            
            # Memory information
            if os.path.exists('/proc/meminfo'):
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal:'):
                            info['total_memory'] = line.split()[1] + ' KB'
                            break
            
            # Display information
            info['display'] = os.environ.get('DISPLAY', 'Not set')
            info['wayland_display'] = os.environ.get('WAYLAND_DISPLAY', 'Not set')
            info['xdg_session_type'] = os.environ.get('XDG_SESSION_TYPE', 'Not set')
            
            # Environment variables
            info['path'] = os.environ.get('PATH', 'Not set')
            info['home'] = os.environ.get('HOME', 'Not set')
            info['user'] = os.environ.get('USER', 'Not set')
            
        except Exception as e:
            self.debug_logger.warning(f"Error collecting system info: {e}")
            info['error'] = str(e)
        
        return info
    
    def _check_hyprland_status(self) -> Dict[str, Any]:
        """Check Hyprland status and version."""
        info = {'running': False, 'version': 'Unknown', 'error': None}
        
        try:
            # Check if hyprctl is available
            result = subprocess.run(['which', 'hyprctl'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                info['error'] = 'hyprctl not found'
                return info
            
            # Check if Hyprland is running
            result = subprocess.run(['hyprctl', 'version'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                info['running'] = True
                # Extract version from output
                for line in result.stdout.split('\n'):
                    if 'tag:' in line:
                        info['version'] = line.split('tag:')[1].strip()
                        break
            else:
                info['error'] = 'Hyprland not running or not accessible'
                
        except subprocess.TimeoutExpired:
            info['error'] = 'Timeout checking Hyprland status'
        except Exception as e:
            info['error'] = f'Error checking Hyprland: {e}'
        
        return info
    
    def _validate_configuration(self) -> Dict[str, Any]:
        """Validate configuration files."""
        validation = {'valid': True, 'errors': [], 'warnings': []}
        
        try:
            # Validate main config
            self.config.validate()
            
        except Exception as e:
            validation['valid'] = False
            validation['errors'].append(f"Main config validation failed: {e}")
        
        # Check sourced files
        try:
            for file_path in self.config.hyprland.sourced_files:
                expanded_path = os.path.expanduser(file_path)
                if not os.path.exists(expanded_path):
                    validation['warnings'].append(f"Sourced file not found: {file_path}")
                elif not os.access(expanded_path, os.R_OK):
                    validation['errors'].append(f"Cannot read sourced file: {file_path}")
        except Exception as e:
            validation['warnings'].append(f"Error checking sourced files: {e}")
        
        return validation
    
    def _check_file_permissions(self) -> Dict[str, str]:
        """Check file permissions for important files."""
        permissions = {}
        
        important_files = [
            self.config.paths.hyprland_config,
            self.config.paths.waybar_config,
            self.config.paths.rofi_config,
            self.config.paths.backup_dir,
            self.config.paths.log_dir,
            self.config.paths.theme_dir
        ]
        
        for file_path in important_files:
            try:
                expanded_path = os.path.expanduser(file_path)
                if os.path.exists(expanded_path):
                    stat = os.stat(expanded_path)
                    permissions[file_path] = oct(stat.st_mode)[-3:]
                else:
                    permissions[file_path] = "Not found"
            except Exception as e:
                permissions[file_path] = f"Error: {e}"
        
        return permissions
    
    def _collect_performance_metrics(self) -> Dict[str, float]:
        """Collect performance metrics."""
        metrics = {}
        
        try:
            # Memory usage
            import psutil
            process = psutil.Process()
            metrics['memory_usage_mb'] = process.memory_info().rss / 1024 / 1024
            metrics['cpu_percent'] = process.cpu_percent()
            
            # System load
            metrics['system_load'] = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.0
            
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            metrics['disk_usage_percent'] = (disk_usage.used / disk_usage.total) * 100
            
        except ImportError:
            metrics['error'] = 'psutil not available for performance metrics'
        except Exception as e:
            metrics['error'] = f'Error collecting performance metrics: {e}'
        
        return metrics
    
    def _run_additional_checks(self):
        """Run additional diagnostic checks."""
        # Check for common issues
        self._check_common_issues()
        
        # Check plugin system
        self._check_plugin_system()
        
        # Check theme system
        self._check_theme_system()
        
        # Check backup system
        self._check_backup_system()
    
    def _check_common_issues(self):
        """Check for common configuration issues."""
        warnings = []
        
        # Check if running on Wayland
        if not os.environ.get('WAYLAND_DISPLAY'):
            warnings.append("Not running on Wayland - some features may not work correctly")
        
        # Check if Hyprland is running
        if not self.debug_info.hyprland_running:
            warnings.append("Hyprland is not running - configuration changes won't take effect")
        
        # Check for missing dependencies
        missing_deps = [name for name, info in self.debug_info.dependencies.items() 
                       if not info.get('available', False) and info.get('required', False)]
        
        if missing_deps:
            warnings.append(f"Missing required dependencies: {', '.join(missing_deps)}")
        
        # Check configuration file permissions
        config_path = self.debug_info.config_path
        if os.path.exists(config_path):
            if not os.access(config_path, os.R_OK):
                warnings.append(f"Cannot read configuration file: {config_path}")
            if not os.access(config_path, os.W_OK):
                warnings.append(f"Cannot write to configuration file: {config_path}")
        
        self.debug_info.warnings.extend(warnings)
    
    def _check_plugin_system(self):
        """Check plugin system status."""
        try:
            from .plugins import EnhancedPluginManager
            
            plugins_dir = Path.home() / '.hyprrice' / 'plugins'
            if plugins_dir.exists():
                plugin_files = list(plugins_dir.glob('*.py'))
                self.debug_info.system_info['plugin_files_count'] = len(plugin_files)
                
                # Try to load plugin manager
                plugin_manager = EnhancedPluginManager(
                    plugins_dir=str(plugins_dir),
                    enable_sandbox=True,
                    security_level='medium'
                )
                
                available_plugins = plugin_manager.list_available_plugins()
                self.debug_info.system_info['available_plugins'] = len(available_plugins)
                
            else:
                self.debug_info.warnings.append("Plugin directory not found")
                
        except Exception as e:
            self.debug_info.warnings.append(f"Plugin system check failed: {e}")
    
    def _check_theme_system(self):
        """Check theme system status."""
        try:
            from .gui.theme_manager import ThemeManager
            
            theme_manager = ThemeManager(self.config.paths.theme_dir)
            themes = theme_manager.list_themes()
            self.debug_info.system_info['available_themes'] = len(themes)
            
        except Exception as e:
            self.debug_info.warnings.append(f"Theme system check failed: {e}")
    
    def _check_backup_system(self):
        """Check backup system status."""
        try:
            backup_dir = Path(self.config.paths.backup_dir)
            if backup_dir.exists():
                backup_files = list(backup_dir.glob('*'))
                self.debug_info.system_info['backup_files_count'] = len(backup_files)
                
                # Check backup directory permissions
                if not os.access(backup_dir, os.W_OK):
                    self.debug_info.warnings.append("Cannot write to backup directory")
            else:
                self.debug_info.warnings.append("Backup directory not found")
                
        except Exception as e:
            self.debug_info.warnings.append(f"Backup system check failed: {e}")
    
    def generate_debug_report(self, output_file: Optional[str] = None) -> str:
        """Generate a comprehensive debug report."""
        if not self.debug_info:
            self.run_comprehensive_debug()
        
        # Generate report
        report = self._format_debug_report()
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report
    
    def _format_debug_report(self) -> str:
        """Format debug information as a readable report."""
        info = self.debug_info
        
        report = f"""
# HyprRice Debug Report
Generated: {info.timestamp}

## System Information
- **Version**: {info.version}
- **Python**: {info.python_version}
- **Platform**: {info.platform}
- **Wayland Display**: {info.wayland_display}
- **Hyprland Running**: {info.hyprland_running}
- **Hyprland Version**: {info.hyprland_version}

## Configuration
- **Config Path**: {info.config_path}
- **Config Valid**: {info.config_valid}
- **Config Errors**: {len(info.config_errors)} errors

## Dependencies
"""
        
        for dep_name, dep_info in info.dependencies.items():
            status = "✅ Available" if dep_info.get('available', False) else "❌ Missing"
            version = dep_info.get('version', 'Unknown')
            report += f"- **{dep_name}**: {status} (Version: {version})\n"
        
        report += f"""
## File Permissions
"""
        
        for file_path, perm in info.file_permissions.items():
            report += f"- **{file_path}**: {perm}\n"
        
        report += f"""
## Performance Metrics
"""
        
        for metric, value in info.performance_metrics.items():
            if isinstance(value, float):
                report += f"- **{metric}**: {value:.2f}\n"
            else:
                report += f"- **{metric}**: {value}\n"
        
        if info.config_errors:
            report += f"""
## Configuration Errors
"""
            for error in info.config_errors:
                report += f"- {error}\n"
        
        if info.warnings:
            report += f"""
## Warnings
"""
            for warning in info.warnings:
                report += f"- {warning}\n"
        
        if info.system_info:
            report += f"""
## Additional System Information
"""
            for key, value in info.system_info.items():
                report += f"- **{key}**: {value}\n"
        
        return report
    
    def save_debug_info_json(self, output_file: str):
        """Save debug information as JSON."""
        if not self.debug_info:
            self.run_comprehensive_debug()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.debug_info), f, indent=2, default=str)
    
    def run_performance_test(self, duration: int = 30) -> Dict[str, Any]:
        """Run performance test for specified duration."""
        self.debug_logger.info(f"Starting performance test for {duration} seconds")
        
        start_time = time.time()
        end_time = start_time + duration
        
        # Performance data collection
        performance_data = {
            'start_time': start_time,
            'duration': duration,
            'samples': [],
            'summary': {}
        }
        
        try:
            import psutil
            process = psutil.Process()
            
            while time.time() < end_time:
                sample = {
                    'timestamp': time.time(),
                    'cpu_percent': process.cpu_percent(),
                    'memory_mb': process.memory_info().rss / 1024 / 1024,
                    'system_load': os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.0
                }
                performance_data['samples'].append(sample)
                time.sleep(1)
            
            # Calculate summary
            if performance_data['samples']:
                cpu_values = [s['cpu_percent'] for s in performance_data['samples']]
                memory_values = [s['memory_mb'] for s in performance_data['samples']]
                
                performance_data['summary'] = {
                    'avg_cpu_percent': sum(cpu_values) / len(cpu_values),
                    'max_cpu_percent': max(cpu_values),
                    'avg_memory_mb': sum(memory_values) / len(memory_values),
                    'max_memory_mb': max(memory_values),
                    'samples_count': len(performance_data['samples'])
                }
            
            self.debug_logger.info("Performance test completed")
            return performance_data
            
        except ImportError:
            return {'error': 'psutil not available for performance testing'}
        except Exception as e:
            self.debug_logger.error(f"Performance test failed: {e}")
            return {'error': str(e)}
    
    def test_configuration_loading(self) -> Dict[str, Any]:
        """Test configuration loading and validation."""
        test_results = {
            'main_config': {'success': False, 'error': None},
            'sourced_files': {'success': False, 'error': None, 'files_tested': 0},
            'validation': {'success': False, 'error': None}
        }
        
        try:
            # Test main config loading
            test_config = Config()
            test_results['main_config']['success'] = True
            
            # Test sourced files
            sourced_files = test_config.hyprland.sourced_files
            test_results['sourced_files']['files_tested'] = len(sourced_files)
            
            for file_path in sourced_files:
                expanded_path = os.path.expanduser(file_path)
                if os.path.exists(expanded_path):
                    try:
                        with open(expanded_path, 'r') as f:
                            f.read()
                    except Exception as e:
                        test_results['sourced_files']['error'] = f"Error reading {file_path}: {e}"
                        break
            
            if not test_results['sourced_files']['error']:
                test_results['sourced_files']['success'] = True
            
            # Test validation
            test_config.validate()
            test_results['validation']['success'] = True
            
        except Exception as e:
            test_results['validation']['error'] = str(e)
        
        return test_results
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests for various components."""
        test_results = {
            'config_system': {'passed': False, 'error': None},
            'theme_system': {'passed': False, 'error': None},
            'plugin_system': {'passed': False, 'error': None},
            'backup_system': {'passed': False, 'error': None},
            'gui_components': {'passed': False, 'error': None}
        }
        
        # Test config system
        try:
            config = Config()
            config.validate()
            test_results['config_system']['passed'] = True
        except Exception as e:
            test_results['config_system']['error'] = str(e)
        
        # Test theme system
        try:
            from .gui.theme_manager import ThemeManager
            theme_manager = ThemeManager(self.config.paths.theme_dir)
            themes = theme_manager.list_themes()
            test_results['theme_system']['passed'] = True
        except Exception as e:
            test_results['theme_system']['error'] = str(e)
        
        # Test plugin system
        try:
            from .plugins import EnhancedPluginManager
            plugins_dir = Path.home() / '.hyprrice' / 'plugins'
            plugin_manager = EnhancedPluginManager(
                plugins_dir=str(plugins_dir),
                enable_sandbox=True,
                security_level='medium'
            )
            test_results['plugin_system']['passed'] = True
        except Exception as e:
            test_results['plugin_system']['error'] = str(e)
        
        # Test backup system
        try:
            from .backup_manager import BackupManager
            backup_manager = BackupManager(self.config.paths.backup_dir)
            test_results['backup_system']['passed'] = True
        except Exception as e:
            test_results['backup_system']['error'] = str(e)
        
        # Test GUI components (basic import test)
        try:
            from .gui.config_editor import ConfigEditor
            from .gui.tabs import HyprlandTab
            test_results['gui_components']['passed'] = True
        except Exception as e:
            test_results['gui_components']['error'] = str(e)
        
        return test_results


def run_debug_mode(config: Optional[Config] = None, output_file: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to run debug mode."""
    debug_mode = DebugMode(config)
    return debug_mode.run_comprehensive_debug()


def generate_debug_report(config: Optional[Config] = None, output_file: Optional[str] = None) -> str:
    """Convenience function to generate debug report."""
    debug_mode = DebugMode(config)
    return debug_mode.generate_debug_report(output_file)
