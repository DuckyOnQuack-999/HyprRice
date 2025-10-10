# HyprRice Autoconfig Guide

## Overview

HyprRice Autoconfig is an intelligent configuration system that automatically optimizes your HyprRice setup based on your system's hardware capabilities and your preferred performance profile.

## Features

### 🔍 **System Profiling**
- **Hardware Detection**: CPU cores, memory, GPU type and capabilities
- **Performance Assessment**: Automatic system performance level detection
- **Display Analysis**: Multi-monitor support, resolution detection
- **System Type**: Laptop vs desktop, touchscreen detection
- **Storage Type**: SSD/NVMe vs HDD detection

### ⚡ **Performance Profiles**

#### Performance Profile
- Optimized for speed and responsiveness
- Reduced animation durations
- Optimized blur settings based on GPU
- Efficient window gaps
- Best for: Gaming, productivity, general use

#### Visual Profile
- Maximum visual effects and animations
- Enhanced blur effects
- Smooth animation curves
- Larger gaps for visual appeal
- Best for: Showcasing, aesthetic-focused setups

#### Battery Profile
- Power-saving optimizations
- Minimized animations
- Disabled GPU-intensive effects
- Optimized auto-save intervals
- Best for: Laptops, mobile devices

#### Minimal Profile
- Lightweight, clean experience
- Minimal animations
- No visual effects
- Streamlined interface
- Best for: Low-end systems, resource-constrained environments

### 🛠️ **Intelligent Optimizations**

#### System-Specific
- **Low-end Systems**: Further reduced effects, disabled blur
- **Laptops**: More frequent auto-saves, reduced backup retention
- **Multi-display**: Consistent positioning, optimized layouts
- **High-resolution**: Adjusted font sizes, larger GUI windows

#### Hardware-Aware
- **GPU Capabilities**: Blur settings based on GPU performance
- **Memory**: Animation complexity based on available RAM
- **Storage**: Backup frequency based on storage type
- **CPU**: Animation duration based on CPU cores

## Usage

### Command Line Interface

```bash
# Basic autoconfig with performance profile
hyprrice autoconfig

# Apply specific profile
hyprrice autoconfig --profile visual
hyprrice autoconfig --profile battery
hyprrice autoconfig --profile minimal

# Interactive mode
hyprrice autoconfig --interactive

# Skip backup creation
hyprrice autoconfig --no-backup

# JSON output for scripting
hyprrice autoconfig --json
```

### Programmatic Usage

```python
from hyprrice.autoconfig import run_autoconfig, PerformanceProfile

# Run autoconfig
result = run_autoconfig(
    profile="performance",
    interactive=False,
    backup=True
)

if result.success:
    print(f"Applied {result.profile_applied.value} profile")
    print(f"Performance impact: {result.performance_impact}")
    
    for optimization in result.optimizations_applied:
        print(f"• {optimization}")
```

## System Requirements

### Minimum Requirements
- **CPU**: 2+ cores
- **Memory**: 4GB RAM
- **GPU**: Integrated graphics
- **Storage**: Any type

### Recommended Requirements
- **CPU**: 4+ cores
- **Memory**: 8GB+ RAM
- **GPU**: Dedicated graphics card
- **Storage**: SSD or NVMe

### Optimal Requirements
- **CPU**: 8+ cores
- **Memory**: 16GB+ RAM
- **GPU**: High-end dedicated graphics
- **Storage**: NVMe SSD

## Configuration Profiles

### Performance Profile Settings
```yaml
hyprland:
  animation_duration: 0.3
  animation_curve: "ease-out"
  blur_enabled: true  # Based on GPU
  blur_size: 4
  gaps_in: 3
  gaps_out: 6
  window_opacity: 1.0
```

### Visual Profile Settings
```yaml
hyprland:
  animation_duration: 0.6
  animation_curve: "ease-out-quart"
  blur_enabled: true
  blur_size: 12
  blur_passes: 2
  gaps_in: 8
  gaps_out: 15
  window_opacity: 0.95
```

### Battery Profile Settings
```yaml
hyprland:
  animation_duration: 0.2
  animation_curve: "linear"
  blur_enabled: false
  gaps_in: 2
  gaps_out: 4

gui:
  auto_save_interval: 60
```

### Minimal Profile Settings
```yaml
hyprland:
  animation_duration: 0.1
  animation_curve: "linear"
  blur_enabled: false
  gaps_in: 1
  gaps_out: 2

gui:
  show_tooltips: false
  show_status_bar: false
```

## Advanced Features

### System Profiling Details

#### CPU Profiling
- Core count detection
- CPU model identification
- Performance scoring

#### Memory Profiling
- Total RAM detection
- Memory-based optimizations
- Performance impact assessment

#### GPU Profiling
- GPU type detection (NVIDIA, AMD, Intel)
- GPU memory estimation
- Blur capability assessment

#### Display Profiling
- Resolution detection
- Multi-monitor support
- Refresh rate analysis

#### Storage Profiling
- SSD/NVMe vs HDD detection
- Backup frequency optimization
- Performance impact

### Performance Level Detection

#### Scoring System
- **CPU**: 1-3 points based on core count
- **Memory**: 1-3 points based on RAM
- **GPU**: 1-3 points based on type
- **Storage**: 1-2 points based on type

#### Performance Levels
- **Ultra**: 10+ points (High-end systems)
- **High**: 7-9 points (Gaming systems)
- **Medium**: 4-6 points (Standard systems)
- **Low**: 1-3 points (Budget systems)

### Backup and Recovery

#### Automatic Backups
- Timestamped backup creation
- Configurable backup retention
- Rollback capabilities

#### Backup Naming
```
config.autoconfig_backup_YYYYMMDD_HHMMSS.yaml
```

#### Recovery Process
```bash
# Restore from backup
cp ~/.config/hyprrice/config.autoconfig_backup_20250930_231924.yaml \
   ~/.config/hyprrice/config.yaml
```

## Troubleshooting

### Common Issues

#### Autoconfig Fails
```bash
# Check system dependencies
hyprrice doctor

# Run with verbose output
hyprrice autoconfig --verbose

# Check logs
tail -f ~/.hyprrice/logs/hyprrice.log
```

#### Performance Issues
```bash
# Apply minimal profile
hyprrice autoconfig --profile minimal

# Check system resources
hyprctl monitors
free -h
```

#### Configuration Conflicts
```bash
# Restore from backup
hyprrice autoconfig --no-backup

# Manual configuration
hyprrice gui
```

### Debug Mode

```bash
# Enable debug logging
export HYPRRICE_DEBUG=1
hyprrice autoconfig

# Check system profile
python -c "from hyprrice.autoconfig import SystemProfiler; p = SystemProfiler(); print(p.profile_system())"
```

## Integration

### GUI Integration
- Autoconfig wizard in main GUI
- System analysis dashboard
- Performance monitoring
- Profile switching interface

### CLI Integration
- Doctor command integration
- Migration system integration
- Plugin system integration
- Backup system integration

### API Integration
```python
from hyprrice.autoconfig import AutoconfigManager, PerformanceProfile

# Create manager
manager = AutoconfigManager()

# Run autoconfig
result = manager.run_autoconfig(
    profile=PerformanceProfile.VISUAL,
    interactive=False,
    backup=True
)

# Access results
print(f"Success: {result.success}")
print(f"Profile: {result.profile_applied}")
print(f"Optimizations: {result.optimizations_applied}")
```

## Best Practices

### Profile Selection
- **Performance**: General use, gaming, productivity
- **Visual**: Showcasing, aesthetic setups
- **Battery**: Laptops, mobile devices
- **Minimal**: Low-end systems, resource constraints

### System Optimization
- Run autoconfig after hardware changes
- Use appropriate profile for your use case
- Monitor performance impact
- Create backups before major changes

### Maintenance
- Regular system profiling
- Profile updates based on usage
- Performance monitoring
- Configuration validation

## Examples

### Basic Setup
```bash
# First-time setup
hyprrice autoconfig --profile performance

# Check results
hyprrice doctor
```

### Laptop Optimization
```bash
# Battery-optimized setup
hyprrice autoconfig --profile battery

# Performance setup when plugged in
hyprrice autoconfig --profile performance
```

### Gaming Setup
```bash
# Performance-optimized for gaming
hyprrice autoconfig --profile performance

# Visual setup for streaming
hyprrice autoconfig --profile visual
```

### Low-end System
```bash
# Minimal setup for old hardware
hyprrice autoconfig --profile minimal

# Check system capabilities
hyprrice autoconfig --json | jq '.recommendations'
```

## Contributing

### Adding New Profiles
1. Define profile in `PerformanceProfile` enum
2. Implement optimization logic in `ConfigurationGenerator`
3. Add profile-specific settings
4. Update documentation

### Enhancing System Profiling
1. Add new profiling methods to `SystemProfiler`
2. Update performance scoring
3. Add hardware-specific optimizations
4. Test with various hardware configurations

### Improving Optimizations
1. Analyze performance impact
2. Add new optimization strategies
3. Implement hardware-specific tweaks
4. Validate with real-world testing

## License

This autoconfig system is part of HyprRice and follows the same MIT license.
