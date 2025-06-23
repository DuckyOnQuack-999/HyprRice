# Plugin API Reference

Complete documentation of the HyprRice plugin system.

## Overview

The HyprRice plugin system allows extending functionality through Python plugins. Plugins can:
- Register for event hooks
- Add new UI elements
- Modify configurations
- Interact with the preview system
- Add custom validation

## Plugin Base Class

```python
from hyprrice.plugins import PluginBase

class MyPlugin(PluginBase):
    """Example plugin implementation"""
    pass
```

## Event Hooks

### Configuration Events
```python
def before_apply(self, context: Dict[str, Any]):
    """Called before applying configuration changes"""
    # context contains:
    # - 'changes': Dict of changes
    # - 'component': Component being changed
    # - 'user': User making changes
    pass

def after_apply(self, context: Dict[str, Any]):
    """Called after applying configuration changes"""
    # context contains:
    # - 'result': Success/failure
    # - 'changes': Applied changes
    # - 'errors': Any errors
    pass
```

### Theme Events
```python
def before_theme_change(self, context: Dict[str, Any]):
    """Called before changing themes"""
    # context contains:
    # - 'old_theme': Current theme
    # - 'new_theme': Theme being applied
    # - 'components': Affected components
    pass

def after_theme_change(self, context: Dict[str, Any]):
    """Called after changing themes"""
    # context contains:
    # - 'theme': Applied theme
    # - 'result': Success/failure
    # - 'changes': Applied changes
    pass
```

### Import/Export Events
```python
def before_import(self, context: Dict[str, Any]):
    """Called before importing config/theme"""
    # context contains:
    # - 'source': Import source
    # - 'format': Import format
    # - 'content': Data being imported
    pass

def after_import(self, context: Dict[str, Any]):
    """Called after importing config/theme"""
    # context contains:
    # - 'result': Success/failure
    # - 'changes': Applied changes
    # - 'errors': Any validation errors
    pass
```

### Preview Events
```python
def on_preview_update(self, context: Dict[str, Any]):
    """Called when preview window updates"""
    # context contains:
    # - 'changes': Preview changes
    # - 'component': Updated component
    # - 'preview_window': Preview window instance
    pass
```

## Plugin Registration

```python
def register(app):
    """Required: Register plugin with HyprRice"""
    plugin = MyPlugin()
    # Optional: Setup plugin
    plugin.setup()
    # Required: Add to plugin manager
    app.plugin_manager.plugin_instances.append(plugin)
    return plugin
```

## UI Integration

### Adding Tabs
```python
from PyQt5.QtWidgets import QWidget, QVBoxLayout

class MyPluginTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        # Add your UI elements
```

### Adding Menu Items
```python
def add_menu_items(self, menu_bar):
    menu = menu_bar.addMenu('My Plugin')
    action = menu.addAction('Do Something')
    action.triggered.connect(self.on_action)
```

## Configuration Access

```python
def modify_config(self, config):
    """Access and modify configuration"""
    # Read config
    value = config.get('section', 'key')
    # Modify config
    config.set('section', 'key', new_value)
    # Save changes
    config.save()
```

## Preview Integration

```python
def update_preview(self, preview_window):
    """Interact with preview system"""
    # Update preview
    preview_window.update()
    # Add overlay
    preview_window.add_overlay('my_plugin', widget)
    # Remove overlay
    preview_window.remove_overlay('my_plugin')
```

## Best Practices

1. **Error Handling**
   ```python
   try:
       # Your code
   except Exception as e:
       self.logger.error(f"Plugin error: {e}")
       return False
   ```

2. **Resource Cleanup**
   ```python
   def cleanup(self):
       """Called when plugin is disabled"""
       # Clean up resources
       pass
   ```

3. **Validation**
   ```python
   def validate_changes(self, changes):
       """Validate before applying"""
       if invalid_condition:
           raise ValueError("Invalid change")
   ```

## Example Plugin

```python
from hyprrice.plugins import PluginBase
from PyQt5.QtWidgets import QWidget, QPushButton

class ExamplePlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "Example Plugin"
        self.version = "1.0.0"
        self.description = "An example plugin"
        
    def register(self, app):
        # Create UI
        self.tab = QWidget()
        button = QPushButton("Click Me", self.tab)
        button.clicked.connect(self.on_click)
        
        # Register events
        self.before_apply = self.on_before_apply
        self.after_theme_change = self.on_theme_change
        
    def on_click(self):
        """Handle button click"""
        pass
        
    def on_before_apply(self, context):
        """Handle pre-apply event"""
        pass
        
    def on_theme_change(self, context):
        """Handle theme change event"""
        pass
        
def register(app):
    plugin = ExamplePlugin()
    app.plugin_manager.plugin_instances.append(plugin)
    return plugin
``` 