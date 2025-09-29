# CPU Management System

## Overview

The CPU Management System provides comprehensive control over CPU settings on Arch Linux systems with enhanced security, input validation, and audit logging. It implements functionality similar to the Arch-Linux-Toolbox with additional enterprise-grade features.

## Features

### Core Functionality
- **CPU Information Display**: Real-time CPU status, frequency, governor, and temperature
- **Governor Management**: Set and configure CPU scaling governors with validation
- **Frequency Control**: Manual CPU frequency adjustment with safety limits
- **Temperature Monitoring**: Real-time thermal monitoring with alerts
- **Stress Testing**: Comprehensive CPU stress testing with thermal tracking
- **Performance Monitoring**: Continuous performance metrics collection

### Security Features
- **Input Validation**: All user inputs validated against security patterns
- **Command Injection Prevention**: Comprehensive protection against malicious inputs
- **Privilege Checking**: Automatic sudo privilege validation
- **Audit Logging**: Complete audit trail for all operations
- **Path Traversal Protection**: Secure file and directory access

### Compliance Features
- **GDPR Compliance**: Data handling and audit trail encryption
- **ISO-27001**: Security management system compliance
- **Audit Trails**: Encrypted, tamper-evident logging

## Architecture

### Components

#### CPUManager Class
```python
from hyprrice.hardware_manager import CPUManager

cpu = CPUManager()
info = cpu.get_cpu_info()
```

**Methods:**
- `get_cpu_info()`: Retrieve comprehensive CPU information
- `set_cpu_governor(governor: str)`: Set CPU scaling governor
- `set_cpu_frequency(frequency: str)`: Set CPU frequency
- `run_stress_test(duration: int)`: Execute CPU stress test
- `_get_cpu_temperature()`: Get current CPU temperature

#### SecureCommandRunner Class
```python
from hyprrice.hardware_manager import SecureCommandRunner

runner = SecureCommandRunner()
result = runner.run_command(['cpupower', 'frequency-info'])
```

**Methods:**
- `run_command(command, require_sudo, timeout)`: Execute validated commands
- `check_sudo_privileges()`: Verify sudo access

### Input Validation

#### Supported Validation Types
- **cpu_governor**: CPU governor names (performance, powersave, etc.)
- **frequency**: CPU frequency values (kHz, min, max)
- **duration**: Stress test duration (1-3600 seconds)
- **command**: Shell command validation with injection protection

#### Example Usage
```python
from hyprrice.validation import validate_input

# Validate governor
governor = validate_input("performance", "cpu_governor", "set_governor")

# Validate frequency
freq = validate_input("2400000", "frequency", "set_frequency")

# Validate duration
duration = validate_input("300", "duration", "stress_test")
```

## Web Interface

### CPUManager Component

The React-based web interface provides a modern, accessible UI for CPU management.

#### Features
- **WCAG 2.1 Compliance**: Full accessibility support
- **Real-time Updates**: Live CPU information display
- **Input Validation**: Client-side validation with user feedback
- **Responsive Design**: Mobile and desktop optimized
- **Loading States**: Clear feedback during operations

#### Usage Example
```tsx
import CPUManager from '@/components/CPUManager';

export default function HardwarePage() {
  return <CPUManager />;
}
```

### Key Interface Elements

#### System Overview
- CPU model and specifications
- Current frequency and governor
- Temperature monitoring with visual indicators
- CPU usage with progress bars

#### Control Panel
- Operation selection dropdown
- Governor configuration with available options
- Frequency setting with range validation
- Stress test configuration with safety warnings

#### Results Display
- Formatted output display
- Error handling with user-friendly messages
- Stress test analysis with temperature tracking

## Installation

### Dependencies

#### System Requirements
```bash
# Required packages
sudo pacman -S cpupower stress-ng lm_sensors

# Optional packages
sudo pacman -S htop

# Python dependencies
pip install psutil
```

#### Python Requirements
```python
# requirements.txt additions
psutil>=5.9.0
```

### Setup

1. **Install hardware manager**:
```python
from hyprrice.hardware_manager import HardwareManager

hardware = HardwareManager()
hardware.install_missing_tools()
```

2. **Configure sensors**:
```bash
sudo sensors-detect --auto
```

3. **Set up logging**:
```python
import logging
from hyprrice.utils import setup_logging

setup_logging(level=logging.INFO)
```

## Configuration

### Validation Settings

Edit `src/hyprrice/validation.py` to customize validation patterns:

```python
# CPU governor validation
'cpu_governor': re.compile(r'^[a-z_]+$'),

# Frequency validation
'frequency': re.compile(r'^(\d+|min|max)$'),

# Duration validation (1 second to 1 hour)
'duration': re.compile(r'^\d+$'),
```

### Security Settings

Configure command injection protection:

```python
COMMAND_INJECTION_PATTERNS = [
    r'[;&|`$]',  # Command separators
    r'\.\./',    # Path traversal
    r'eval\s*\(',  # Code evaluation
    r'exec\s*\(',  # Code execution
]
```

### Performance Monitoring

Enable continuous performance monitoring:

```python
# Automatic performance logging
hardware.monitor_performance(duration=3600)  # 1 hour
```

## API Reference

### CPUManager Methods

#### get_cpu_info()
Returns comprehensive CPU information including:
- Model name and specifications
- Current frequency and governor
- Available governors
- Temperature readings
- Usage statistics
- Load averages

**Return Type**: `Dict[str, Any]`

#### set_cpu_governor(governor: str)
Sets the CPU scaling governor with validation.

**Parameters**:
- `governor`: Governor name (performance, powersave, ondemand, conservative, schedutil)

**Returns**: `bool` - Success status

**Validation**: 
- Pattern matching against known governors
- Security injection checks
- Sudo privilege verification

#### set_cpu_frequency(frequency: str)
Sets CPU frequency with safety validation.

**Parameters**:
- `frequency`: Frequency in kHz, or 'min'/'max'

**Returns**: `bool` - Success status

**Range Limits**:
- Minimum: 100MHz (100000 kHz)
- Maximum: 10GHz (10000000 kHz)

#### run_stress_test(duration: int)
Executes CPU stress test with thermal monitoring.

**Parameters**:
- `duration`: Test duration in seconds (1-3600)

**Returns**: `Dict[str, Any]` containing:
- Test duration
- Initial and final temperatures
- Temperature delta
- Success status
- Output logs

### Input Validation API

#### validate_input(value, validation_type, context, allow_empty)
Core validation function with audit logging.

**Parameters**:
- `value`: Input value to validate
- `validation_type`: Type of validation to perform
- `context`: Context for audit logging
- `allow_empty`: Whether empty values are allowed

**Returns**: Validated and sanitized input

**Raises**: `ValidationError` for invalid inputs

## Security Considerations

### Command Injection Prevention
All user inputs are validated against injection patterns:
- Command separators (`;&|`$`)
- Path traversal (`../`)
- Code evaluation (`eval`, `exec`)
- Dynamic imports (`__import__`)

### Privilege Management
- Automatic sudo privilege checking
- Secure command execution with timeout
- Audit logging for all privileged operations

### Data Protection
- Sensitive data logging controls
- Encrypted audit trails
- GDPR-compliant data handling

## Troubleshooting

### Common Issues

#### "cpupower not found"
```bash
# Install cpupower
sudo pacman -S cpupower

# Verify installation
which cpupower
```

#### "Permission denied"
```bash
# Check sudo privileges
sudo -v

# Add user to wheel group if needed
sudo usermod -a -G wheel $USER
```

#### "Temperature sensor not available"
```bash
# Install and configure sensors
sudo pacman -S lm_sensors
sudo sensors-detect --auto

# Load sensor modules
sudo modprobe coretemp
```

#### "Stress test failed"
```bash
# Install stress-ng
sudo pacman -S stress-ng

# Verify installation
stress-ng --version
```

### Performance Issues

#### High CPU usage during monitoring
Adjust monitoring frequency:
```python
# Reduce monitoring frequency
hardware.monitor_performance(duration=60)  # Shorter duration
```

#### Slow command execution
Check system load and adjust timeouts:
```python
# Increase timeout for slow systems
runner.run_command(command, timeout=60)
```

### Logging and Debugging

#### Enable debug logging
```python
import logging
logging.getLogger('hyprrice.hardware_manager').setLevel(logging.DEBUG)
```

#### View audit logs
```bash
# Performance logs
tail -f ~/.hyprrice/logs/performance.log

# Audit logs
tail -f ~/.hyprrice/logs/hyprrice.log
```

#### Clear old logs
```python
from hyprrice.utils import cleanup_old_backups
cleanup_old_backups('~/.hyprrice/logs', max_backups=50)
```

## Examples

### Basic CPU Information
```python
from hyprrice.hardware_manager import CPUManager

cpu = CPUManager()
info = cpu.get_cpu_info()

print(f"CPU: {info['model']}")
print(f"Cores: {info['cores']}")
print(f"Frequency: {info['frequency']['current']} MHz")
print(f"Governor: {info['governor']}")
print(f"Temperature: {info['temperature']}°C")
```

### Set Performance Governor
```python
# Set high-performance governor
success = cpu.set_cpu_governor("performance")
if success:
    print("Governor set to performance mode")
else:
    print("Failed to set governor")
```

### Run Stress Test
```python
# 5-minute stress test
results = cpu.run_stress_test(300)

if results['success']:
    print(f"Test Duration: {results['duration']}s")
    print(f"Temperature Delta: +{results['temperature_delta']}°C")
else:
    print(f"Test failed: {results.get('error', 'Unknown error')}")
```

### Monitor Performance
```python
from hyprrice.hardware_manager import HardwareManager

hardware = HardwareManager()

# Monitor for 10 minutes
stats = hardware.monitor_performance(600)
print(f"Average CPU: {stats['avg_cpu']:.1f}%")
print(f"Peak CPU: {stats['max_cpu']:.1f}%")
print(f"Average Memory: {stats['avg_memory']:.1f}%")
```

## Best Practices

### Security
1. Always validate user inputs
2. Use least-privilege principle
3. Monitor audit logs regularly
4. Keep dependencies updated

### Performance
1. Use appropriate test durations
2. Monitor system temperatures
3. Avoid concurrent stress tests
4. Clean up old logs periodically

### Reliability
1. Check dependencies before operations
2. Handle errors gracefully
3. Provide user feedback
4. Log all significant events

## Support

### Documentation
- [Hardware Management Overview](../README.md)
- [GPU Management](gpu_management.md)
- [Troubleshooting Guide](../howto/troubleshooting.md)

### Community
- GitHub Issues: Report bugs and feature requests
- Discussions: Community support and questions
- Wiki: Additional examples and use cases