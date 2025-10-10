# HyprRice API Reference

## Overview

This document provides comprehensive API documentation for HyprRice, covering all major modules, classes, and functions available for development and integration.

## Core Modules

### Configuration Management

#### `hyprrice.config.Config`

Base configuration class for HyprRice settings.

```python
class Config:
    def __init__(self, config_path: Optional[str] = None)
    def load(self) -> bool
    def save(self) -> bool
    def backup(self) -> bool
    def restore(self, backup_path: str) -> bool
    def validate(self) -> List[str]
```

**Attributes:**
- `general`: General application settings
- `paths`: File and directory paths
- `hyprland`: Hyprland-specific configuration
- `gui`: GUI-related settings

#### `hyprrice.config.HyprlandConfig`

Hyprland-specific configuration management.

```python
class HyprlandConfig:
    def get_animations_config(self) -> Dict[str, Any]
    def set_window_rules(self, rules: List[Dict[str, Any]]) -> None
    def update_general_settings(self, settings: Dict[str, Any]) -> None
```

### GUI Components

#### `hyprrice.main_gui.MainGUI`

Main PyQt6 application window.

```python
class MainGUI(QMainWindow):
    def __init__(self)
    def setup_ui(self) -> None
    def load_configuration(self) -> None
    def save_configuration(self) -> None
    def show_preview(self) -> None
```

#### Preview System

#### `hyprrice.gui.preview.PreviewWindow`

Live preview window for configuration changes.

```python
class PreviewWindow(QDialog):
    def __init__(self, parent=None)
    def update_preview(self) -> None
    def apply_changes(self) -> None
    def reset_preview(self) -> None
```

#### `hyprrice.gui.preview.InteractivePreviewWidget`

Real-time visual preview widget.

```python
class InteractivePreviewWidget(QWidget):
    def paintEvent(self, event: QPaintEvent) -> None
    def set_gap(self, gap: int) -> None
    def set_border_size(self, size: int) -> None
    def set_border_color(self, color: str) -> None
```

### Security Modules

#### `hyprrice.security.InputValidator`

Input validation and sanitization.

```python
class InputValidator:
    @staticmethod
    def validate_path(path: str) -> bool
    @staticmethod
    def validate_color(color: str) -> bool
    @staticmethod
    def sanitize_command(cmd: str) -> str
    @staticmethod
    def validate_file_size(file_path: str, max_size: int) -> bool
```

#### `hyprrice.security.PluginSandbox`

Secure plugin execution environment.

```python
class PluginSandbox:
    def __init__(self, security_level: str = "medium")
    def execute_plugin(self, plugin_code: str) -> Any
    def set_resource_limits(self, memory: int, cpu_time: int) -> None
    def is_allowed_import(self, module_name: str) -> bool
```

### Performance Monitoring

#### `hyprrice.performance.PerformanceMonitor`

System performance tracking and optimization.

```python
class PerformanceMonitor:
    def __init__(self)
    def start_monitoring(self) -> None
    def stop_monitoring(self) -> None
    def get_metrics(self) -> Dict[str, float]
    def optimize_worker(self) -> None
```

### Backup System

#### `hyprrice.backup.BackupManager`

Configuration backup and restore management.

```python
class BackupManager:
    def __init__(self, backup_dir: str)
    def create_backup(self, config_type: str = ...) -> bool
    def restore_backup(self, backup_name: str) -> bool
    def list_backups(self) -> List[str]
    def cleanup_backups(self, retention_days: int) -> None
```

#### `hyprrice.backup.HistoryManager`

Change history tracking and undo/redo functionality.

```python
class HistoryManager:
    def add_entry(self, action: str, config_snapshot: Dict, metadata: Dict) -> None
    def undo(self) -> bool
    def redo(self) -> bool
    def can_undo(self) -> bool
    def can_redo(self) -> bool
```

### Plugin System

#### `hyprrice.plugins.PluginBase`

Base class for HyprRice plugins.

```python
class PluginBase(QObject):
    def __init__(self)
    def register(self, app: 'MainGUI') -> None
    def unregister(self) -> None
    def get_metadata(self) -> Dict[str, Any]
    def on_config_apply(self, config: Dict[str, Any]) -> None
```

#### `hyprrice.plugins.PluginManager`

Plugin lifecycle management and event dispatch.

```python
class PluginManager:
    def __init__(self)
    def load_plugin(self, plugin_path: str) -> bool
    def unload_plugin(self, plugin_name: str) -> bool
    def dispatch_event(self, event_type: str, data: Dict) -> None
    def get_loaded_plugins(self) -> List[str]
```

### Hyprland Integration

#### `hyprrice.hyprland.HyprlandClient`

Interface to Hyprland via hyprctl.

```python
class HyprlandClient:
    @staticmethod
    def hyprctl(command: str) -> subprocess.CompletedProcess
    @staticmethod
    def hyprctl_async(command: str) -> asyncio.Future
    @staticmethod
    def reload_config() -> bool
    @staticmethod
    def get_monitors() -> List[Dict[str, Any]]
```

### Autoconfig System

#### `hyprrice.autoconfig.SystemProfiler`

Hardware profiling and performance assessment.

```python
class SystemProfiler:
    def profile_system(self) -> Dict[str, Any]
    def get_cpu_info(self) -> Dict[str, Any]
    def get_memory_info(self) -> Dict[str, Any]
    def get_gpu_info(self) -> Dict[str, Any]
    def assess_performance_level(self) -> str
```

#### `hyprrice.autoconfig.ConfigurationGenerator`

Smart configuration generation based on system capabilities.

```python
class ConfigurationGenerator:
    def __init__(self, profiler: SystemProfiler)
    def generate_config(self, profile: PerformanceProfile) -> Dict[str, Any]
    def optimize_for_performance(self, config: Dict[str, Any]) -> Dict[str, Any]
    def optimize_for_battery(self, config: Dict[str, Any]) -> Dict[str, Any]
```

### CLI Interface

#### `hyprrice.cli.HyprRiceCLI`

Command-line interface and argument parsing.

```python
class HyprRiceCLI:
    def __init__(self)
    def setup_subcommands(self) -> None
    def doctor_command(self, args: Namespace) -> None
    def autoconfig_command(self, args: Namespace) -> None
    def plugins_command(self, args: Namespace) -> None
```

## Data Structures

### Configuration Schema

```python
@dataclass
class GeneralConfig:
    auto_backup: bool = True
    backup_retention: int = 10
    live_preview: bool = True
    theme: str = "auto"

@dataclass
class PathsConfig:
    hyprland_config: str = "~/.config/hypr/"
    waybar_config: str = "~/.config/waybar/"
    backup_dir: str = "~/.hyprrice/backups/"
    log_dir: str = "~/.hyprrice/logs/"

@dataclass
class HyprlandConfig:
    gaps_in: int = 3
    gaps_out: int = 6
    border_size: int = 2
    window_opacity: float = 1.0
    enable_blur: bool = True
```

### Performance Profiles

```python
class PerformanceProfile(Enum):
    PERFORMANCE = "performance"
    VISUAL = "visual"
    BATTERY = "battery"
    MINIMAL = "minimal"
```

### Event Types

```python
class PluginEvent(Enum):
    BEFORE_APPLY = "before_apply"
    AFTER_APPLY = "after_apply"
    THEME_CHANGE = "theme_change"
    CONFIG_LOAD = "config_load"
    PREVIEW_UPDATE = "preview_update"
```

## Usage Examples

### Basic Configuration Management

```python
from hyprrice.config import Config

# Load configuration
config = Config()
config.load()

# Modify settings
config.general.auto_backup = True
config.hyprland.gaps_in = 5

# Save changes
config.save()
```

### Creating a Custom Plugin

```python
from hyprrice.plugins import PluginBase

class CustomPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.metadata = {
            "name": "Custom Theme Plugin",
            "version": "1.0.0",
            "description": "Adds custom theme support"
        }
    
    def register(self, app):
        # Add custom tab or functionality
        self.main_app = app
        self.setup_ui()
    
    def on_config_apply(self, config):
        # Handle configuration changes
        self.apply_custom_config(config)
```

### Using Performance Monitoring

```python
from hyprrice.performance import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.start_monitoring()

# Your code here...

metrics = monitor.get_metrics()
print(f"CPU Usage: {metrics['cpu_percent']}%")
print(f"Memory Usage: {metrics['memory_mb']} MB")

monitor.stop_monitoring()
```

### Backup Management

```python
from hyprrice.backup import BackupManager

manager = BackupManager("~/.hyprrice/backups/")

# Create backup
success = manager.create_backup("manual_backup")

if success:
    print("Backup created successfully")
    
# List available backups
backups = manager.list_backups()
for backup in backups:
    print(f"Backup: {backup}")
```

## Error Handling

Most HyprRice functions raise specific exceptions for error handling:

- `hyprrice.exceptions.ConfigurationError`: Configuration loading/saving issues
- `hyprrice.exceptions.SecurityError`: Security validation failures
- `hyprrice.exceptions.PluginError`: Plugin loading/execution errors
- `hyprrice.exceptions.HyprlandError`: Hyprland communication failures

## Development Guidelines

### Adding New Features

1. Follow the existing architectural patterns
2. Add comprehensive type hints
3. Include error handling and logging
4. Write unit tests for new functionality
5. Update documentation

### Plugin Development

1. Inherit from `PluginBase`
2. Implement required methods (`register`, `get_metadata`)
3. Handle events appropriately
4. Follow security guidelines
5. Test in sandboxed environment

### Performance Considerations

1. Use async operations for I/O
2. Cache frequently accessed data
3. Implement resource cleanup
4. Monitor memory usage
5. Profile performance-critical code

## Version History

- **v1.0.0**: Initial stable API release
- **v1.1.0**: Enhanced autoconfig and preview system (current development)

