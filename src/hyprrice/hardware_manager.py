"""
Hardware Management System for HyprRice
Implements comprehensive CPU, GPU, storage, and memory management with security and audit features
"""

import os
import sys
import time
import psutil
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass

from .validation import validate_input, sanitize_command
from .exceptions import HyprRiceError, ValidationError


@dataclass
class HardwareInfo:
    """Data class for hardware information."""
    cpu_model: str
    cpu_cores: int
    cpu_frequency: float
    gpu_model: str
    memory_total: int
    memory_available: int
    storage_devices: List[Dict[str, Any]]


class SecureCommandRunner:
    """Secure command execution with validation and audit logging."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audit_log = logging.getLogger(f"{__name__}.audit")
        self.performance_log = logging.getLogger(f"{__name__}.performance")
    
    def check_sudo_privileges(self) -> bool:
        """Check if current user has sudo privileges."""
        try:
            result = subprocess.run(['sudo', '-n', 'true'], 
                                  capture_output=True, timeout=5)
            has_sudo = result.returncode == 0
            self.audit_log.info(f"Sudo privilege check: {'passed' if has_sudo else 'failed'}")
            return has_sudo
        except Exception as e:
            self.audit_log.error(f"Sudo privilege check failed: {e}")
            return False
    
    def run_command(self, command: List[str], require_sudo: bool = False, 
                   timeout: int = 30, capture_output: bool = True) -> Tuple[int, str, str]:
        """
        Execute system commands with security validation and performance monitoring.
        
        Args:
            command: Command to execute (pre-validated list)
            require_sudo: Whether sudo is required
            timeout: Command timeout in seconds
            capture_output: Whether to capture output
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        start_time = datetime.now()
        
        try:
            # Validate command components
            validated_command = []
            for cmd_part in command:
                validated_part = validate_input(cmd_part, "command", f"command_execution_{cmd_part}")
                validated_command.extend(validated_part if isinstance(validated_part, list) else [validated_part])
            
            # Add sudo if required
            if require_sudo:
                if not self.check_sudo_privileges():
                    raise HyprRiceError("Sudo privileges required but not available")
                validated_command = ['sudo'] + validated_command
            
            # Log command execution attempt
            self.audit_log.info(f"Executing command: {' '.join(validated_command)}")
            
            # Execute command
            result = subprocess.run(
                validated_command,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                check=False
            )
            
            # Log performance metrics
            duration = (datetime.now() - start_time).total_seconds()
            self.performance_log.info(f"Command execution: duration={duration:.3f}s, "
                                    f"return_code={result.returncode}")
            
            # Log success/failure
            if result.returncode == 0:
                self.audit_log.info(f"Command succeeded: {' '.join(validated_command)}")
            else:
                self.audit_log.warning(f"Command failed: {' '.join(validated_command)}, "
                                     f"return_code={result.returncode}")
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            self.audit_log.error(f"Command timeout: {' '.join(command)}")
            return -1, "", "Command timed out"
        except ValidationError as e:
            self.audit_log.error(f"Command validation failed: {e}")
            return -1, "", f"Validation error: {e}"
        except Exception as e:
            self.audit_log.error(f"Command execution error: {e}")
            return -1, "", str(e)


class CPUManager:
    """Comprehensive CPU management with security and performance monitoring."""
    
    def __init__(self):
        self.runner = SecureCommandRunner()
        self.logger = logging.getLogger(__name__)
        self.audit_log = logging.getLogger(f"{__name__}.audit")
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get comprehensive CPU information."""
        try:
            info = {
                'model': self._get_cpu_model(),
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'frequency': self._get_cpu_frequency(),
                'governor': self._get_cpu_governor(),
                'available_governors': self._get_available_governors(),
                'temperature': self._get_cpu_temperature(),
                'usage': psutil.cpu_percent(interval=1),
                'load_average': os.getloadavg()
            }
            
            self.audit_log.info("CPU information retrieved successfully")
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get CPU info: {e}")
            raise HyprRiceError(f"CPU information retrieval failed: {e}")
    
    def set_cpu_governor(self, governor: str) -> bool:
        """Set CPU governor with validation and audit logging."""
        try:
            # Validate governor name
            validated_governor = validate_input(governor, "cpu_governor", "set_cpu_governor")
            
            # Check if cpupower is available
            if not self._check_cpupower():
                raise HyprRiceError("cpupower not available")
            
            # Set governor
            returncode, stdout, stderr = self.runner.run_command(
                ['cpupower', 'frequency-set', '-g', validated_governor],
                require_sudo=True
            )
            
            if returncode == 0:
                self.audit_log.info(f"CPU governor changed to: {validated_governor}")
                return True
            else:
                self.logger.error(f"Failed to set governor: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Governor setting failed: {e}")
            return False
    
    def set_cpu_frequency(self, frequency: str) -> bool:
        """Set CPU frequency with validation."""
        try:
            # Validate frequency
            validated_freq = validate_input(frequency, "frequency", "set_cpu_frequency")
            
            if not self._check_cpupower():
                raise HyprRiceError("cpupower not available")
            
            # Set frequency
            freq_arg = f"{validated_freq}kHz" if validated_freq.isdigit() else validated_freq
            returncode, stdout, stderr = self.runner.run_command(
                ['cpupower', 'frequency-set', '-f', freq_arg],
                require_sudo=True
            )
            
            if returncode == 0:
                self.audit_log.info(f"CPU frequency set to: {freq_arg}")
                return True
            else:
                self.logger.error(f"Failed to set frequency: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Frequency setting failed: {e}")
            return False
    
    def run_stress_test(self, duration: int = 60) -> Dict[str, Any]:
        """Run CPU stress test with monitoring."""
        try:
            # Validate duration
            validated_duration = validate_input(duration, "duration", "cpu_stress_test")
            
            if not self._check_stress_ng():
                raise HyprRiceError("stress-ng not available")
            
            self.audit_log.info(f"Starting CPU stress test for {validated_duration}s")
            
            # Start monitoring
            start_time = time.time()
            initial_temp = self._get_cpu_temperature()
            
            # Run stress test
            returncode, stdout, stderr = self.runner.run_command(
                ['stress-ng', '--cpu', str(psutil.cpu_count()), 
                 '--timeout', f"{validated_duration}s"],
                timeout=validated_duration + 30
            )
            
            # Collect results
            end_time = time.time()
            final_temp = self._get_cpu_temperature()
            
            results = {
                'duration': end_time - start_time,
                'initial_temperature': initial_temp,
                'final_temperature': final_temp,
                'temperature_delta': final_temp - initial_temp if initial_temp and final_temp else None,
                'success': returncode == 0,
                'output': stdout if returncode == 0 else stderr
            }
            
            self.audit_log.info(f"Stress test completed: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Stress test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_cpu_model(self) -> str:
        """Get CPU model name."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('model name'):
                        return line.split(':', 1)[1].strip()
            return "Unknown"
        except:
            return "Unknown"
    
    def _get_cpu_frequency(self) -> Dict[str, float]:
        """Get current CPU frequency information."""
        try:
            freq_info = psutil.cpu_freq()
            return {
                'current': freq_info.current,
                'min': freq_info.min,
                'max': freq_info.max
            }
        except:
            return {'current': 0, 'min': 0, 'max': 0}
    
    def _get_cpu_governor(self) -> str:
        """Get current CPU governor."""
        try:
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor', 'r') as f:
                return f.read().strip()
        except:
            return "unknown"
    
    def _get_available_governors(self) -> List[str]:
        """Get list of available CPU governors."""
        try:
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors', 'r') as f:
                return f.read().strip().split()
        except:
            return []
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature using sensors."""
        try:
            returncode, stdout, stderr = self.runner.run_command(
                ['sensors'], timeout=10
            )
            
            if returncode == 0:
                for line in stdout.split('\n'):
                    if 'Core 0' in line and '°C' in line:
                        temp_str = line.split('°C')[0].split('+')[-1]
                        return float(temp_str)
            return None
        except:
            return None
    
    def _check_cpupower(self) -> bool:
        """Check if cpupower is available."""
        returncode, _, _ = self.runner.run_command(['which', 'cpupower'])
        return returncode == 0
    
    def _check_stress_ng(self) -> bool:
        """Check if stress-ng is available."""
        returncode, _, _ = self.runner.run_command(['which', 'stress-ng'])
        return returncode == 0


class GPUManager:
    """Comprehensive GPU management."""
    
    def __init__(self):
        self.runner = SecureCommandRunner()
        self.logger = logging.getLogger(__name__)
        self.audit_log = logging.getLogger(f"{__name__}.audit")
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get comprehensive GPU information."""
        try:
            info = {
                'nvidia': self._get_nvidia_info(),
                'amd': self._get_amd_info(),
                'intel': self._get_intel_info(),
                'general': self._get_general_gpu_info()
            }
            
            self.audit_log.info("GPU information retrieved successfully")
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get GPU info: {e}")
            raise HyprRiceError(f"GPU information retrieval failed: {e}")
    
    def _get_nvidia_info(self) -> Optional[Dict[str, Any]]:
        """Get NVIDIA GPU information."""
        try:
            returncode, stdout, stderr = self.runner.run_command(
                ['nvidia-smi', '--query-gpu=name,memory.total,memory.used,temperature.gpu,power.draw',
                 '--format=csv,noheader,nounits']
            )
            
            if returncode == 0:
                lines = stdout.strip().split('\n')
                gpus = []
                for line in lines:
                    if line.strip():
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 5:
                            gpus.append({
                                'name': parts[0],
                                'memory_total': int(parts[1]),
                                'memory_used': int(parts[2]),
                                'temperature': int(parts[3]),
                                'power_draw': float(parts[4])
                            })
                return {'available': True, 'gpus': gpus}
            
        except:
            pass
        
        return {'available': False, 'gpus': []}
    
    def _get_amd_info(self) -> Dict[str, Any]:
        """Get AMD GPU information."""
        try:
            # Check for ROCm
            returncode, stdout, stderr = self.runner.run_command(['rocm-smi'])
            
            if returncode == 0:
                return {'available': True, 'info': stdout}
            
        except:
            pass
        
        return {'available': False, 'info': ''}
    
    def _get_intel_info(self) -> Dict[str, Any]:
        """Get Intel GPU information."""
        try:
            # Check for Intel GPU tools
            returncode, stdout, stderr = self.runner.run_command(['intel_gpu_top', '-l'])
            
            if returncode == 0:
                return {'available': True, 'info': stdout}
            
        except:
            pass
        
        return {'available': False, 'info': ''}
    
    def _get_general_gpu_info(self) -> Dict[str, Any]:
        """Get general GPU information from lspci."""
        try:
            returncode, stdout, stderr = self.runner.run_command(
                ['lspci', '-nn'], timeout=10
            )
            
            if returncode == 0:
                gpu_lines = [line for line in stdout.split('\n') 
                           if 'VGA' in line or 'Display' in line or '3D' in line]
                return {'devices': gpu_lines}
            
        except:
            pass
        
        return {'devices': []}


class HardwareManager:
    """Main hardware management interface."""
    
    def __init__(self):
        self.cpu_manager = CPUManager()
        self.gpu_manager = GPUManager()
        self.logger = logging.getLogger(__name__)
        self.audit_log = logging.getLogger(f"{__name__}.audit")
        
        # Initialize performance monitoring
        self.performance_log = logging.getLogger(f"{__name__}.performance")
        self._start_performance_monitoring()
    
    def get_system_overview(self) -> HardwareInfo:
        """Get comprehensive system hardware overview."""
        try:
            cpu_info = self.cpu_manager.get_cpu_info()
            gpu_info = self.gpu_manager.get_gpu_info()
            memory_info = psutil.virtual_memory()
            
            # Get storage information
            storage_devices = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    storage_devices.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free
                    })
                except:
                    pass
            
            # Extract primary GPU
            gpu_model = "Unknown"
            if gpu_info['nvidia']['available'] and gpu_info['nvidia']['gpus']:
                gpu_model = gpu_info['nvidia']['gpus'][0]['name']
            elif gpu_info['general']['devices']:
                gpu_model = gpu_info['general']['devices'][0]
            
            overview = HardwareInfo(
                cpu_model=cpu_info['model'],
                cpu_cores=cpu_info['cores'],
                cpu_frequency=cpu_info['frequency']['current'],
                gpu_model=gpu_model,
                memory_total=memory_info.total,
                memory_available=memory_info.available,
                storage_devices=storage_devices
            )
            
            self.audit_log.info("System overview generated successfully")
            return overview
            
        except Exception as e:
            self.logger.error(f"Failed to get system overview: {e}")
            raise HyprRiceError(f"System overview failed: {e}")
    
    def monitor_performance(self, duration: int = 60) -> Dict[str, Any]:
        """Monitor system performance for specified duration."""
        try:
            validated_duration = validate_input(duration, "duration", "performance_monitoring")
            
            self.audit_log.info(f"Starting performance monitoring for {validated_duration}s")
            
            start_time = time.time()
            samples = []
            
            while time.time() - start_time < validated_duration:
                sample = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                    'load_avg': os.getloadavg()
                }
                samples.append(sample)
                time.sleep(1)
            
            # Calculate statistics
            stats = {
                'duration': validated_duration,
                'samples': len(samples),
                'avg_cpu': sum(s['cpu_percent'] for s in samples) / len(samples),
                'max_cpu': max(s['cpu_percent'] for s in samples),
                'avg_memory': sum(s['memory_percent'] for s in samples) / len(samples),
                'max_memory': max(s['memory_percent'] for s in samples),
                'samples': samples
            }
            
            self.performance_log.info(f"Performance monitoring completed: {stats}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Performance monitoring failed: {e}")
            return {'error': str(e)}
    
    def _start_performance_monitoring(self):
        """Initialize background performance monitoring."""
        # Set up performance logging format
        perf_formatter = logging.Formatter(
            '%(asctime)s - PERF - %(message)s'
        )
        
        # Create performance log handler
        perf_log_path = Path.home() / '.hyprrice' / 'logs' / 'performance.log'
        perf_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        perf_handler = logging.FileHandler(perf_log_path)
        perf_handler.setFormatter(perf_formatter)
        self.performance_log.addHandler(perf_handler)
        self.performance_log.setLevel(logging.INFO)
    
    def install_missing_tools(self) -> Dict[str, bool]:
        """Install missing hardware management tools."""
        tools = {
            'cpupower': ['sudo', 'pacman', '-S', '--noconfirm', 'cpupower'],
            'stress-ng': ['sudo', 'pacman', '-S', '--noconfirm', 'stress-ng'],
            'lm_sensors': ['sudo', 'pacman', '-S', '--noconfirm', 'lm_sensors'],
            'htop': ['sudo', 'pacman', '-S', '--noconfirm', 'htop'],
        }
        
        results = {}
        runner = SecureCommandRunner()
        
        for tool, install_cmd in tools.items():
            try:
                # Check if tool exists
                check_code, _, _ = runner.run_command(['which', tool])
                
                if check_code != 0:
                    self.audit_log.info(f"Installing missing tool: {tool}")
                    install_code, stdout, stderr = runner.run_command(install_cmd, require_sudo=True, timeout=300)
                    results[tool] = install_code == 0
                    
                    if install_code == 0:
                        self.audit_log.info(f"Successfully installed: {tool}")
                    else:
                        self.logger.error(f"Failed to install {tool}: {stderr}")
                else:
                    results[tool] = True  # Already installed
                    
            except Exception as e:
                self.logger.error(f"Installation check failed for {tool}: {e}")
                results[tool] = False
        
        return results