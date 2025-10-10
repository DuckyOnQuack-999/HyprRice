# HyprRice Plugin Development Guide

## Overview

HyprRice's plugin system allows you to extend functionality with custom themes, additional configuration options, and integrated tools. This guide covers plugin development, architecture, and best practices.

## Plugin System Architecture

### Core Components

#### `hyprrice.plugins.PluginBase`
Base class that all plugins must inherit from.

#### `hyprrice.plugins.PluginManager`
Manages plugin lifecycle, loading, unloading, and event dispatching.

#### `hyprrice.plugin_sandbox.PluginSandbox`
Provides secure execution environment with resource limits and import restrictions.

## Plugin Lifecycle

### 1. Discovery
- Plugins are discovered in `~/.hyprrice/plugins/`
- Valid plugins must be Python files with `.py` extension
- Must contain a `register(app)` function or inherit from `PluginBase`

### 2. Loading
- Plugins are loaded during application startup
- Security validation occurs during load
- Resource limits are applied immediately

### 3. Registration
- `register(app)` is called with the main application instance
- Plugins can add tabs, controls, or modify behavior
- Event handlers can be registered

### 4. Event Dispatching
- Plugins receive events throughout application lifecycle
- Events include configuration changes, theme switches, preview updates
- Event handlers run in sandboxed environment

### 5. Unloading
- Cleanup resources and event handlers
- Revert any UI modifications
- Clear cached data

## Creating Your First Plugin

### Basic Plugin Structure

```python
from hyprrice.plugins import PluginBase
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class MyPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.metadata = {
            "name": "My Awesome Plugin",
            "version": "1.0.0",
            "description": "Demonstrates basic plugin functionality",
            "author": "Your Name",
            "dependencies": []
        }
    
    def register(self, app):
        """Called when plugin is loaded."""
        self.main_app = app
        self.setup_ui()
        self.register_events()
    
    def setup_ui(self):
        """Add UI elements to the main application."""
        # Add a custom tab
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Hello from MyPlugin!"))
        tab.setLayout(layout)
        
        # Add tab to main interface
        self.main_app.add_custom_tab("My Plugin", tab)
    
    def register_events(self):
        """Register event handlers."""
        self.main_app.register_event_handler(
            "config_apply", 
            self.on_config_apply
        )
    
    def on_config_apply(self, config):
        """Handle configuration changes."""
        print(f"Configuration applied: {config}")
    
    def unregister(self):
        """Called when plugin is unloaded."""
        # Cleanup code here
        pass
```

### Plugin Metadata

All plugins should define metadata:

```python
self.metadata = {
    "name": "Plugin Name",           # Display name
    "version": "1.0.0",              # Semantic version
    "description": "What this plugin does",
    "author": "Plugin Author",
    "dependencies": [                # Other plugins required
        "plugin_name >= 1.0.0"
    ],
    "compatibility": {               # HyprRice version requirements
        "min_version": "1.0.0",
        "max_version": "2.0.0"
    },
    "settings_schema": {             # Configuration schema
        "type": "object",
        "properties": {
            "enabled": {
                "type": "boolean",
                "default": True
            }
        }
    }
}
```

## Event System

### Available Events

```python
from hyprrice.plugins import PluginEvent

# Core application events
BEFORE_APPLY = "before_apply"         # Before applying configuration
AFTER_APPLY = "after_apply"           # After applying configuration
CONFIG_LOAD = "config_load"           # When configuration is loaded
CONFIG_SAVE = "config_save"           # When configuration is saved

# Theme events
THEME_CHANGE = "theme_change"         # When theme changes
THEME_APPLY = "theme_apply"           # When theme is applied
THEME_IMPORT = "theme_import"        # When theme is imported

# Preview events
PREVIEW_UPDATE = "preview_update"     # When preview updates
PREVIEW_RESET = "preview_reset"       # When preview is reset

# Plugin events
PLUGIN_ENABLE = "plugin_enable"       # When plugin is enabled
PLUGIN_DISABLE = "plugin_disable"     # When plugin is disabled
```

### Event Handler Registration

```python
def register_events(self):
    """Register event handlers with the application."""
    
    # Register for multiple events
    events = [
        "before_apply",
        "after_apply", 
        "theme_change",
        "preview_update"
    ]
    
    for event in events:
        self.main_app.register_event_handler(
            event, 
            getattr(self, f"on_{event}")
        )

def on_before_apply(self, data):
    """Handle before apply event."""
    print(f"About to apply configuration: {data}")

def on_after_apply(self, data):
    """Handle after apply event."""
    print(f"Configuration applied successfully: {data}")
```

## Adding Custom Tabs

### Creating Configuration Tabs

```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QSlider, QSpinBox, QCheckBox
)

class CustomConfigTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Custom Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Settings
        enabled_layout = QHBoxLayout()
        enabled_layout.addWidget(QLabel("Enabled:"))
        self.enabled_checkbox = QCheckBox()
        enabled_layout.addWidget(self.enabled_checkbox)
        enabled_layout.addStretch()
        layout.addLayout(enabled_layout)
        
        # Value slider
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("Value:"))
        self.value_slider = QSlider()
        self.value_slider.setRange(0, 100)
        value_layout.addWidget(self.value_slider)
        self.value_spinbox = QSpinBox()
        self.value_spinbox.setRange(0, 100)
        value_layout.addWidget(self.value_spinbox)
        layout.addLayout(value_layout)
        
        # Connect signals
        self.value_slider.valueChanged.connect(
            self.value_spinbox.setValue
        )
        self.value_spinbox.valueChanged.connect(
            self.value_slider.setValue
        )
        
        layout.addStretch()
        self.setLayout(layout)

class MyPlugin(PluginBase):
    def setup_ui(self):
        """Add custom tab to main interface."""
        tab = CustomConfigTab()
        self.main_app.add_custom_tab("Custom Config", tab)
```

## Configuration Integration

### Reading Configuration

```python
def read_config(self):
    """Read current configuration."""
    config = self.main_app.config
    
    # Access different sections
    general = config.general
    hyprland = config.hyprland
    custom_settings = config.custom_settings  # Plugin settings
    
    return {
        "general": general,
        "hyprland": hyprland,
        "custom": custom_settings
    }
```

### Writing Configuration

```python
def update_config(self, changes):
    """Update configuration with plugin changes."""
    config = self.main_app.config
    
    # Update plugin-specific settings
    if "custom_settings" not in config.__dict__:
        config.custom_settings = {}
    
    config.custom_settings.update(changes)
    
    # Mark as modified
    config.mark_modified()
    
    # Trigger config save event
    self.main_app.trigger_event("config_save", config.custom_settings)
```

## Theme Integration

### Creating Custom Themes

```python
def create_custom_theme(self):
    """Create a custom theme configuration."""
    theme_config = {
        "name": "My Custom Theme",
        "description": "Theme created by my plugin",
        "author": "Plugin Author",
        "version": "1.0.0",
        "colors": {
            "background": "#2e3440",
            "foreground": "#eceff4",
            "accent": "#5e81ac"
        },
        "hyprland": {
            "gaps_in": 5,
            "gaps_out": 10,
            "border_size": 2,
            "window_opacity": 0.95
        },
        "waybar": {
            "background_color": "rgba(46, 52, 64, 0.8)",
            "border_bottom": "3px solid rgba(94, 129, 172, 0.5)"
        }
    }
    
    return theme_config

def apply_custom_theme(self, theme_config):
    """Apply custom theme through HyprRice."""
    self.main_app.theme_manager.import_theme(theme_config)
    self.main_app.theme_manager.apply_theme(theme_config["name"])
```

## Security Considerations

### Sandbox Environment

Plugins execute in a sandboxed environment with restrictions:

```python
# Restricted imports (blocked in sandbox)
import subprocess      # Blocked
import os.system       # Blocked  
import ctypes          # Blocked
import urllib.request  # Blocked

# Allowed imports
import json            # Allowed
import datetime        # Allowed
import math            # Allowed
import PyQt6.QtCore    # Allowed
```

### Resource Limits

```python
# Sandbox limits
MAX_MEMORY = 100 * 1024 * 1024  # 100MB
MAX_CPU_TIME = 30  # 30 seconds
MAX_FILE_DESCRIPTORS = 50
```

### Best Practices

1. **Input Validation**: Always validate inputs from configuration
2. **Error Handling**: Wrap risky operations in try-catch blocks
3. **Resource Cleanup**: Clean up resources in `unregister()`
4. **No File Operations**: Avoid direct file system access
5. **Safe APIs**: Use HyprRice APIs instead of direct system calls

## Testing Plugins

### Unit Testing

```python
import pytest
from hyprrice.pluggins import PluginManager
from unittest.mock import MagicMock

def test_plugin_loading():
    """Test plugin loading and registration."""
    manager = PluginManager()
    mock_app = MagicMock()
    
    # Load plugin
    plugin = MyPlugin()
    plugin.register(mock_app)
    
    # Verify registration
    assert plugin.main_app == mock_app
    assert plugin.metadata["name"] == "My Awesome Plugin"

def test_event_handling():
    """Test event handler registration."""
    plugin = MyPlugin()
    plugin.register(mock_app)
    
    # Simulate event
    plugin.on_config_apply({"test": "value"})
    
    # Verify behavior
    # Add assertions specific to your plugin
```

### Integration Testing

```python
def test_plugin_integration():
    """Test plugin integration with HyprRice."""
    from hyprrice.main_gui import MainGUI
    
    app = MainGUI()
    app.setup_ui()
    
    # Load plugin
    plugin_path = "tests/test_plugins/my_plugin.py"
    success = app.plugin_manager.load_plugin(plugin_path)
    
    assert success == True
    assert "MyPlugin" in app.get_loaded_plugins()
```

## Distribution

### Packaging Plugins

Plugin structure for distribution:

```
my-plugin/
├── __init__.py
├── plugin.py
├── resources/
│   ├── icons/
│   └── themes/
├── requirements.txt
├── README.md
└── LICENSE
```

### Installation Methods

1. **Manual Installation**: Copy to `~/.hyprrice/plugins/`
2. **Package Manager**: Distribute via pip/conda
3. **Git Repository**: Clone into plugins directory
4. **HyprRice Marketplace**: (Future feature)

## Advanced Features

### External Tool Integration

```python
def integrate_external_tool(self):
    """Integrate with external Hyprland tools."""
    
    # Get tool status via hyprctl
    result = self.main_app.hyprland_client.hyprctl("monitors")
    
    if result.returncode == 0:
        monitors = json.loads(result.stdout)
        self.process_monitor_data(monitors)
    
def process_monitor_data(self, monitors):
    """Process monitor information from hyprctl."""
    for monitor in monitors:
        name = monitor.get("name")
        resolution = monitor.get("resolution")
        # Process monitor data
```

### Real-time Updates

```python
from PyQt6.QtCore import QTimer

def setup_realtime_updates(self):
    """Set up real-time configuration updates."""
    self.update_timer = QTimer()
    self.update_timer.timeout.connect(self.update_config)
    self.update_timer.start(1000)  # Update every second

def update_config(self):
    """Update configuration based on current state."""
    # Get current Hyprland state
    current_config = self.get_current_hyprland_state()
    
    # Update plugin settings
    self.sync_with_hyprland(current_config)
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Check sandbox restrictions
2. **Memory Issues**: Monitor resource usage
3. **UI Conflicts**: Ensure proper cleanup
4. **Event Handlers**: Verify registration

### Debugging

```python
import logging

logger = logging.getLogger(f"hyprrice.plugin.{self.metadata['name']}")

def debug_method(self, data):
    """Debug method with proper logging."""
    logger.debug(f"Processing data: {data}")
    
    try:
        # Risk operation
        result = self.process_data(data)
        logger.info(f"Operation successful: {result}")
        
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise
```

### Plugin Validation

```python
def validate_plugin(plugin_path):
    """Validate plugin before loading."""
    
    # Check required metadata
    if not hasattr(plugin, 'metadata'):
        raise ValueError("Plugin missing metadata")
    
    # Check required methods
    if not hasattr(plugin, 'register'):
        raise ValueError("Plugin missing register method")
    
    # Validate dependencies
    check_dependencies(plugin.metadata.get('dependencies', []))
    
    return True
```

## Examples

### Theme Plugin Example

See `src/hyprrice/plugins_builtin/notification_theming.py` for a complete theme plugin example.

### Configuration Plugin Example

See `src/hyprrice/plugins_builtin/terminal_theming.py` for a configuration plugin example.

## Resources

- [Plugin API Reference](api.md)
- [Security Guidelines](security.md)
- [Theme Format Documentation](reference/theme_format.md)
- [HyprRice GitHub Repository](https://github.com/DuckyOnQuack-999/HyprRice)

