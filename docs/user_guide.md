# HyprRice User Guide (v1.0.0)

## Overview
HyprRice is a comprehensive ricing tool for the Hyprland Wayland compositor ecosystem. It provides a modern GUI, deep integration with Hyprland and related tools, theme management, plugin support, and robust configuration handling.

## Core Features
- **Modern GUI**: Intuitive PyQt5 interface with live preview
- **Deep Integration**: Configure Hyprland, Waybar, Rofi, notifications, clipboard, lockscreen
- **Theme System**: Switch, preview, import/export themes
- **Plugin System**: Extend functionality with Python plugins and event hooks
- **Safety**: Backup/restore, undo/redo, validation
- **Audit**: Full changelog and configuration history

## Getting Started

### Installation
```bash
# Install system dependencies (Arch Linux)
sudo pacman -S hyprland waybar rofi dunst swww grim slurp cliphist hyprlock python-pyqt5 python-yaml

# Install HyprRice
pip install hyprrice
```

### First Launch
1. Run `hyprrice` from your terminal
2. Choose a base theme (minimal, cyberpunk, pastel)
3. Configure basic settings
4. Use live preview to see changes

## Configuration Tabs

### Hyprland Tab
- **Animations**: Enable/disable, customize duration and style
- **Window Management**: Gaps, borders, opacity, blur
- **Input**: Mouse, keyboard, touchpad settings
- **Display**: Monitors, workspaces, scaling
- **Performance**: Rendering, VSync, frame timing

### Waybar Tab
- Layout and position
- Module selection and order
- Colors and transparency
- Custom CSS

### Rofi Tab
- Theme selection
- Layout and position
- Colors and transparency
- Custom modes

### Notifications Tab
- Dunst/Mako configuration
- Position and layout
- Timeout and actions
- Custom rules

### Clipboard Tab
- Manager selection (Cliphist/wl-clipboard)
- History size
- Sync settings
- Privacy options

### Lockscreen Tab
- Hyprlock/Swaylock settings
- Background and effects
- Timeout and triggers
- Custom scripts

### Themes Tab
- Browse and preview themes
- Import/export themes
- Create custom themes
- Share with community

### Settings Tab
- Backup and restore
- Import/export config
- Undo/redo changes
- View audit log
- Export changelog

### Plugins Tab
- Enable/disable plugins
- Configure plugin settings
- View plugin events
- Install new plugins

## Advanced Features

### Plugin Development
Plugins can now use advanced event hooks to extend functionality:

```python
from hyprrice.plugins import PluginBase

class MyPlugin(PluginBase):
    """Example plugin demonstrating event hooks"""
    
    def before_apply(self, context):
        """Called before applying any changes"""
        print(f"About to apply changes: {context}")
        
    def after_theme_change(self, context):
        """Called after a theme is changed"""
        theme_name = context.get('theme_name')
        print(f"Theme changed to: {theme_name}")
        
    def on_preview_update(self, context):
        """Called when preview window updates"""
        changes = context.get('changes')
        print(f"Preview updated with: {changes}")

def register(app):
    """Required: Register plugin with HyprRice"""
    plugin = MyPlugin()
    app.plugin_manager.plugin_instances.append(plugin)
    return plugin
```

Available hooks:
- `before_apply`, `after_apply`: Configuration changes
- `before_theme_change`, `after_theme_change`: Theme switching
- `before_import`, `after_import`: Config/theme import
- `on_preview_update`: Live preview updates

### Theme Creation
Create custom themes in `~/.config/hyprrice/themes/`:

```yaml
# mytheme.hyprrice
name: "My Custom Theme"
author: "Your Name"
version: "1.0"

hyprland:
  animations:
    enabled: true
    bezier: "myBezier,0.05,0.9,0.1,1.05"
    animation:
      windows: "1, 7, myBezier"
      border: "1, 10, default"
      
  decoration:
    blur:
      enabled: true
      size: 3
      passes: 1
      
waybar:
  style: |
    * {
      border: none;
      border-radius: 0;
      font-family: "JetBrainsMono Nerd Font";
      font-size: 13px;
      min-height: 0;
    }
    
rofi:
  theme:
    window:
      background-color: "#2e3440"
      border: 1
```

### Import/Export
- Import themes from files, URLs, or clipboard
- Export your config or themes to share
- All imports are validated and previewed
- Automatic backup before import

### Changelog & Audit
Export detailed changelogs and audit trails:
- Markdown format for documentation
- JSON format for automation
- HTML format for viewing
- Includes timestamps and context

## Troubleshooting

### Common Issues
1. **Preview not updating**
   - Check if compositor is running
   - Verify display permissions
   - Restart HyprRice

2. **Plugin not loading**
   - Check plugin file permissions
   - Verify Python dependencies
   - Check logs for errors

3. **Theme import fails**
   - Validate theme file format
   - Check for missing dependencies
   - Try importing sections separately

### Logs
- Main log: `~/.local/share/hyprrice/hyprrice.log`
- Debug log: `~/.local/share/hyprrice/debug.log`
- Plugin logs: `~/.local/share/hyprrice/plugins/*.log`

## Contributing
- Report issues on GitHub
- Submit pull requests
- Share themes and plugins
- Improve documentation

## See Also
- [README.md](../README.md)
- [CHANGELOG.md](../CHANGELOG.md)
- [PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md) 