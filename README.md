# HyprRice - Comprehensive Hyprland Configuration Tool

A modern, feature-rich GUI application for customizing and managing your Hyprland desktop environment and its ecosystem.

## 🚀 Quick Start

```bash
# Install HyprRice
pip install hyprrice

# Launch the GUI
hyprrice gui

# Check system status
hyprrice doctor

# Auto-fix common issues
hyprrice doctor --fix
```

## ✨ What's New

- **Full Pipeline Analysis**: Comprehensive code quality, security, and performance improvements
- **Modern Python Packaging**: Updated to use `pyproject.toml` with SPDX license format, no setuptools warnings
- **Enhanced CLI**: Improved `hyprrice doctor --fix` with auto-repair capabilities
- **Architecture Improvements**: Abstract base classes for better code organization
- **Performance Optimizations**: Expanded caching system with automatic cache clearing
- **Security Hardening**: Input validation, path restrictions, and command sanitization
- **Comprehensive Testing**: 300+ tests covering all major functionality

## 🔧 Full Pipeline Improvements

The latest release includes a comprehensive full pipeline analysis and improvements:

### Code Quality & Architecture
- **Abstract Base Classes**: `Command` and `PluginBase` now use ABC for better type safety
- **Exception Handling**: Replaced broad `except Exception` with specific exception types
- **Code Organization**: Improved module structure and separation of concerns

### Performance & Caching
- **Enhanced Caching**: Expanded `hyprctl` caching with automatic cache clearing on state changes
- **LRU Cache**: Added `@lru_cache` decorators for frequently called functions
- **Cache Management**: Automatic cache invalidation when applying configurations

### Security & Validation
- **Input Sanitization**: All `hyprctl` commands are validated and sanitized
- **Path Validation**: File operations use `InputValidator.validate_path`
- **YAML Safety**: All YAML operations use `safe_load`/`safe_dump`
- **Subprocess Security**: No `shell=True`, proper timeouts, and error handling

### CLI & User Experience
- **Auto-Fix**: `hyprrice doctor --fix` automatically creates missing configs and directories
- **Better Error Messages**: Clear, actionable error messages with troubleshooting hints
- **Idempotent Operations**: Commands can be run multiple times safely

### Testing & Quality Assurance
- **Comprehensive Test Suite**: 300+ tests covering all major functionality
- **CLI Testing**: Extensive tests for auto-fix functionality and error handling
- **Integration Tests**: End-to-end testing of the complete workflow

## Backlog


## 📚 Documentation

- [ ] [Documentation Home](docs/README.md)
- [ ] [User Guide](docs/user_guide.md)
- [ ] [Troubleshooting](docs/howto/troubleshooting.md)
- [ ] [Quick Start](docs/tutorials/quick_start.md)
- [ ] [API Reference](docs/api.md)
- [ ] [Plugin Development](docs/plugins.md)
- [ ] [Security Guide](docs/security.md)

## 🌟 Features

- [ ] **Hyprland Core**: Animations, window management, workspaces, input, display settings
- [ ] **Waybar**: Layout, styling, modules, and interactivity
- [ ] **Rofi**: Appearance, modes, themes, and behavior
- [ ] **Notifications**: Dunst/Mako integration with styling and behavior
- [ ] **Clipboard Manager**: Cliphist/wl-clipboard integration with GUI
- [ ] **Lockscreen**: Hyprlock/Swaylock customization
- [ ] **Ecosystem Tools**: Terminal, file manager, screenshot tools, audio
- [ ] Modern, responsive PyQt5 GUI optimized for Wayland
- [ ] Live preview system for animations and color schemes
- [ ] Theme system with gallery and import/export capabilities
- [ ] Auto-backup and rollback functionality
- [ ] Beginner-friendly presets and advanced customization options
- [ ] Modular, extensible architecture with plugin support
- [ ] Robust error handling and validation
- [ ] Configuration parsing and syntax validation
- [ ] Performance optimized for low resource usage
- [ ] Full Wayland compatibility
- [ ] **Fixed Installation & Runtime Issues**: Resolved entry points, hyprctl API, and GUI startup problems
- [ ] **Modern Python Packaging**: Updated to use `pyproject.toml` with SPDX license format, no setuptools warnings
- [ ] **Enhanced CLI**: Improved `hyprrice doctor`, `hyprrice migrate`, and `hyprrice gui` commands
- [ ] **Advanced Plugin System**: Event-based hooks (before/after apply, theme change, import, preview, etc.)
- [ ] **Modern UI**: Polished interface with tooltips, help overlays, and improved feedback
- [ ] **Configuration Migration**: Automatic migration from older config formats with backup
- [ ] **Import/Export**: Validation, preview, and backup integration
- [ ] **Security Features**: Input validation, path restrictions, and command sanitization
- [ ] **Performance Monitoring**: Built-in performance tracking and optimization
- [ ] **Comprehensive Testing**: 298+ tests covering all major functionality

## 📁 Project Structure

- [ ] **Primary**: `pyproject.toml` - Modern Python packaging with SPDX license format
- [ ] **Legacy**: `setup.py` - Minimal compatibility layer
- [ ] **Dependencies**: Managed through `pyproject.toml` with optional extras
- [ ] **No Warnings**: All setuptools deprecation warnings resolved

## 🎯 Key Features in Detail

- [ ] **Global Toggle**: Enable/disable all animations
- [ ] **Animation Types**: slide, fade, popin, shrink, zoom
- [ ] **Duration Control**: 0.1s to 5.0s with fine-grained control
- [ ] **Easing Curves**: linear, ease-in-out, cubic-bezier
- [ ] **Per-Window Rules**: Custom animations for specific applications
- [ ] **Opacity Control**: Global and per-application (0.0-1.0)
- [ ] **Border Customization**: Size, color, gradient, corner radius
- [ ] **Effects**: Shadows, blur, dim with customizable parameters
- [ ] **Gaps**: Inner/outer gaps with smart gap support
- [ ] **Floating Rules**: Size, position, opacity for floating windows
- [ ] **Pre-installed Themes**: minimal, cyberpunk, pastel, nord, dracula
- [ ] **Custom Themes**: Create and save your own themes
- [ ] **Import/Export**: Share themes with the community
- [ ] **Live Preview**: See changes before applying
- [ ] **Extensible Architecture**: Add custom animations, Waybar modules
- [ ] **API**: Third-party tool integration
- [ ] **Community Contributions**: Share plugins via GitHub
- [ ] **Plugin Development**: Place your plugin `.py` files in `~/.hyprrice/plugins/`
- [ ] **Plugin Registration**: Each plugin must define a `register(app)` function
- [ ] **Example Plugin**:
- [ ] **Plugin Capabilities**: Plugins can add tabs, controls, or logic to the main app

## 🔧 Configuration

- [ ] Use the Settings tab to backup or restore your config, or to undo/redo changes
- [ ] All changes are logged in the audit log for traceability
- [ ] Export/import and CI/CD-ready output (coming soon)

## 🧪 Testing

- [ ] CLI functionality and commands
- [ ] GUI components and interactions
- [ ] Hyprland integration and configuration
- [ ] Plugin system and security
- [ ] Backup and migration systems
- [ ] Configuration management
- [ ] Error handling and validation

## 🤝 Contributing

- [ ] **Bug fixes**: Help us improve stability
- [ ] **New features**: Enhance the user experience
- [ ] **Plugin development**: Extend functionality
- [ ] **Documentation**: Improve guides and examples
- [ ] **Testing**: Increase test coverage
- [ ] **AUR PKGBUILD**: Package management improvements
- [ ] Follow PEP 8 for Python code
- [ ] Use type hints where appropriate
- [ ] Add docstrings for new functions
- [ ] Include tests for new functionality

## 🙏 Acknowledgments

- [ ] [Hyprland](https://github.com/hyprwm/Hyprland) - The amazing Wayland compositor
- [ ] [Waybar](https://github.com/Alexays/Waybar) - Highly customizable Wayland bar
- [ ] [Rofi](https://github.com/davatorium/rofi) - Window switcher and launcher
- [ ] [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework

## 📞 Support & Troubleshooting

### Common Issues & Solutions

#### Configuration Issues
```bash
# Check system status
hyprrice doctor

# Auto-fix common issues
hyprrice doctor --fix

# Manual configuration migration
hyprrice migrate --backup
```

#### Missing Dependencies
```bash
# Check what's missing
hyprrice check

# Install missing packages (Arch Linux)
sudo pacman -S hyprland waybar rofi dunst grim slurp

# Install missing packages (Ubuntu/Debian)
sudo apt install hyprland waybar rofi dunst grim slurp
```

#### GUI Issues
```bash
# Check PyQt5 installation
python -c "import PyQt5; print('OK')"

# Run with debug mode
hyprrice gui --debug

# Check Wayland session
echo $WAYLAND_DISPLAY
```

#### Plugin Issues
```bash
# List available plugins
hyprrice plugins list

# Load a specific plugin
hyprrice plugins load <plugin_name>

# Reload all plugins
hyprrice plugins reload
```

### Getting Help

- **GitHub Issues**: [Report bugs and request features](https://github.com/DuckyOnQuack-999/HyprRice/issues)
- **Documentation**: Check the [docs](docs/) folder for detailed guides
- **Troubleshooting**: See [troubleshooting guide](docs/howto/troubleshooting.md)

### Best Practices

- Use the backup system before major changes
- Keep your configuration files organized
- Enable performance monitoring in preferences
- Run `hyprrice doctor --fix` after system updates
- Check the logs in `~/.hyprrice/logs/` for detailed error information
