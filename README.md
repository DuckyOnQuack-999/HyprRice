# HyprRice - Comprehensive Hyprland Ecosystem Ricing Tool

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Wayland](https://img.shields.io/badge/Wayland-Compatible-brightgreen.svg)](https://wayland.freedesktop.org/)
[![CI](https://github.com/DuckyOnQuack-999/HyprRice/actions/workflows/python-ci.yml/badge.svg)](https://github.com/DuckyOnQuack-999/HyprRice/actions/workflows/python-ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hyprrice.svg)](https://pypi.org/project/hyprrice/)
[![Downloads](https://pepy.tech/badge/hyprrice)](https://pepy.tech/project/hyprrice)

HyprRice is an advanced, all-encompassing ricing tool for the Hyprland Wayland compositor ecosystem. It provides a seamless, user-friendly GUI to customize every aspect of Hyprland and its associated tools, including animations, Waybar, Rofi, window opacities, notifications, clipboard managers, and more.

## 📚 Documentation
- [Documentation Home](docs/README.md)
- [User Guide](docs/user_guide.md)
- [Troubleshooting](docs/howto/troubleshooting.md)
- [Quick Start](docs/tutorials/quick_start.md)
- [API Reference](docs/api.md)
- [Plugin Development](docs/plugins.md)
- [Security Guide](docs/security.md)

## 🌟 Features

### 🎨 **Comprehensive Customization**
- **Hyprland Core**: Animations, window management, workspaces, input, display settings
- **Waybar**: Layout, styling, modules, and interactivity
- **Rofi**: Appearance, modes, themes, and behavior
- **Notifications**: Dunst/Mako integration with styling and behavior
- **Clipboard Manager**: Cliphist/wl-clipboard integration with GUI
- **Lockscreen**: Hyprlock/Swaylock customization
- **Ecosystem Tools**: Terminal, file manager, screenshot tools, audio

### 🎯 **User Experience**
- Modern, responsive PyQt5 GUI optimized for Wayland
- Live preview system for animations and color schemes
- Theme system with gallery and import/export capabilities
- Auto-backup and rollback functionality
- Beginner-friendly presets and advanced customization options

### 🔧 **Technical Excellence**
- Modular, extensible architecture with plugin support
- Robust error handling and validation
- Configuration parsing and syntax validation
- Performance optimized for low resource usage
- Full Wayland compatibility

### 🆕 **What's New in v1.0.0**
- **Fixed Installation & Runtime Issues**: Resolved entry points, hyprctl API, and GUI startup problems
- **Modern Python Packaging**: Updated to use `pyproject.toml` with SPDX license format, no setuptools warnings
- **Enhanced CLI**: Improved `hyprrice doctor`, `hyprrice migrate`, and `hyprrice gui` commands
- **Advanced Plugin System**: Event-based hooks (before/after apply, theme change, import, preview, etc.)
- **Modern UI**: Polished interface with tooltips, help overlays, and improved feedback
- **Configuration Migration**: Automatic migration from older config formats with backup
- **Import/Export**: Validation, preview, and backup integration
- **Security Features**: Input validation, path restrictions, and command sanitization
- **Performance Monitoring**: Built-in performance tracking and optimization
- **Comprehensive Testing**: 298+ tests covering all major functionality

## 📦 Installation

### Install from the AUR (Arch Linux)
HyprRice is available on the AUR as `hyprrice`:
```sh
yay -S hyprrice
```
Or use your favorite AUR helper.

### Prerequisites (Manual Install)

Ensure you have the following system dependencies installed:

```bash
# Arch Linux / Manjaro
sudo pacman -S hyprland waybar rofi dunst swww grim slurp cliphist hyprlock \
    python-pyqt5 python-pillow python-yaml python-gobject

# Ubuntu / Debian
sudo apt install hyprland waybar rofi dunst swww grim slurp cliphist hyprlock \
    python3-pyqt5 python3-pil python3-yaml python3-gi

# Fedora
sudo dnf install hyprland waybar rofi dunst swww grim slurp cliphist hyprlock \
    python3-qt5 python3-pillow python3-pyyaml python3-gobject
```

### Install HyprRice (Manual)

#### Option 1: From Source (Recommended)
```bash
git clone https://github.com/DuckyOnQuack-999/HyprRice.git
cd HyprRice

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt -r requirements-test.txt
```

#### Option 2: Using pip
```bash
pip install hyprrice
```

#### Option 3: Using setup.py (Legacy)
```bash
# Clone the repository
git clone https://github.com/DuckyOnQuack-999/HyprRice.git
cd HyprRice

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install using setup.py
python setup.py install

# Or install in development mode
python setup.py develop

# Note: setup.py is maintained for compatibility but pyproject.toml is preferred
```

#### Option 4: Verify Installation
```bash
# Check system status and dependencies
hyprrice doctor

# Launch GUI
hyprrice gui

# List available plugins
hyprrice plugins list

# Migrate configuration (if needed)
hyprrice migrate
```

## 🚀 Quick Start

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Run HyprRice:**
   ```sh
   # Launch GUI
   hyprrice gui
   
   # Or check system status first
   hyprrice doctor
   ```

See the [Quick Start Guide](docs/tutorials/quick_start.md) or the [User Guide](docs/user_guide.md) for detailed instructions.

## 🎨 Usage Examples

### Basic Animation Setup
```python
# HyprRice automatically generates this hyprland.conf
animations {
    enabled = true
    animation = windows, 1, 7, myBezier
    animation = border, 1, 10, default
    animation = fade, 1, 7, default
    animation = workspaces, 1, 6, default
}
```

### Waybar Configuration
```css
/* Generated by HyprRice */
* {
    border: none;
    border-radius: 0;
    font-family: "JetBrainsMono Nerd Font", "Font Awesome 5 Free";
    font-size: 13px;
    min-height: 0;
}

window#waybar {
    background-color: rgba(43, 48, 59, 0.5);
    border-bottom: 3px solid rgba(100, 115, 245, 0.5);
    color: #ffffff;
    transition-property: background-color;
    transition-duration: .5s;
}
```

### Rofi Theme
```css
/* Generated by HyprRice */
* {
    bg: #2e3440;
    bg-alt: #3b4252;
    fg: #eceff4;
    fg-alt: #d8dee9;
    border: 0;
    margin: 0;
    padding: 0;
    highlight: bold, #5e81ac;
    urgent: #bf616a;
}

window {
    width: 40%;
    location: center;
    anchor: center;
    y-offset: -50px;
    x-offset: 0px;
}
```

## 📁 Project Structure

```
HyprRice/
├── src/hyprrice/          # Main source code
│   ├── cli.py             # Command-line interface
│   ├── main.py            # Legacy entry point
│   ├── main_gui.py        # Main GUI application
│   ├── config.py          # Configuration management
│   ├── utils.py           # Utility functions
│   ├── migration.py       # Configuration migration
│   ├── backup.py          # Backup system
│   ├── history.py         # History management
│   ├── plugins.py         # Plugin system
│   ├── security.py        # Security features
│   ├── performance.py     # Performance monitoring
│   ├── hyprland/          # Hyprland-specific modules
│   │   ├── animations.py  # Animation configuration
│   │   ├── display.py     # Display settings
│   │   ├── input.py       # Input configuration
│   │   ├── windows.py     # Window management
│   │   └── workspaces.py  # Workspace settings
│   └── gui/               # GUI components
│       ├── tabs.py        # Tab implementations
│       ├── theme_manager.py # Theme management
│       ├── preview.py     # Live preview
│       ├── preferences.py # Preferences dialog
│       ├── backup_manager.py # Backup management
│       └── plugin_manager.py # Plugin management
├── plugins/               # Built-in plugins
│   ├── terminal_theming.py
│   └── notification_theming.py
├── themes/                # Pre-installed themes
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── requirements-dev.txt   # Development dependencies
├── requirements-test.txt  # Testing dependencies
├── pyproject.toml        # Modern Python packaging (primary)
└── setup.py              # Legacy setup (minimal, for compatibility)
```

### 📦 Packaging
- **Primary**: `pyproject.toml` - Modern Python packaging with SPDX license format
- **Legacy**: `setup.py` - Minimal compatibility layer
- **Dependencies**: Managed through `pyproject.toml` with optional extras
- **No Warnings**: All setuptools deprecation warnings resolved

#### Running setup.py Commands
```bash
# Install the package
python setup.py install

# Install in development mode (editable)
python setup.py develop

# Build distribution packages
python setup.py sdist bdist_wheel

# Clean build artifacts
python setup.py clean --all

# Show package information
python setup.py --help-commands

# Note: While setup.py works, pip install -e . is recommended for development
```

## 🎯 Key Features in Detail

### Animation System
- **Global Toggle**: Enable/disable all animations
- **Animation Types**: slide, fade, popin, shrink, zoom
- **Duration Control**: 0.1s to 5.0s with fine-grained control
- **Easing Curves**: linear, ease-in-out, cubic-bezier
- **Per-Window Rules**: Custom animations for specific applications

### Window Management
- **Opacity Control**: Global and per-application (0.0-1.0)
- **Border Customization**: Size, color, gradient, corner radius
- **Effects**: Shadows, blur, dim with customizable parameters
- **Gaps**: Inner/outer gaps with smart gap support
- **Floating Rules**: Size, position, opacity for floating windows

### Theme System
- **Pre-installed Themes**: minimal, cyberpunk, pastel, nord, dracula
- **Custom Themes**: Create and save your own themes
- **Import/Export**: Share themes with the community
- **Live Preview**: See changes before applying

### Plugin System
- **Extensible Architecture**: Add custom animations, Waybar modules
- **API**: Third-party tool integration
- **Community Contributions**: Share plugins via GitHub
- **Plugin Development**: Place your plugin `.py` files in `~/.hyprrice/plugins/`
- **Plugin Registration**: Each plugin must define a `register(app)` function
- **Example Plugin**:
  ```python
  def register(app):
      print("Plugin loaded! You can add tabs, controls, or logic here.")
  ```
- **Plugin Capabilities**: Plugins can add tabs, controls, or logic to the main app

## 🔧 Configuration

### HyprRice Configuration
```yaml
# ~/.config/hyprrice/config.yaml
general:
  auto_backup: true
  backup_retention: 10
  live_preview: true
  theme: dark

paths:
  hyprland_config: ~/.config/hypr/hyprland.conf
  waybar_config: ~/.config/waybar/
  rofi_config: ~/.config/rofi/
  backup_dir: ~/.hyprrice/backups/
  log_dir: ~/.hyprrice/logs/
```

### Backup and Rollback
HyprRice automatically creates timestamped backups before applying changes:
```bash
~/.hyprrice/backups/
├── 2024-01-15_14-30-25_hyprland.conf
├── 2024-01-15_14-30-25_waybar_config
└── 2024-01-15_14-30-25_rofi_config
```

### Backup, Restore, Undo, Redo
- Use the Settings tab to backup or restore your config, or to undo/redo changes
- All changes are logged in the audit log for traceability
- Export/import and CI/CD-ready output (coming soon)

## 🧪 Testing

Run the complete test suite:
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test categories
pytest tests/test_cli.py
pytest tests/test_gui.py
pytest tests/test_hyprland_integration.py
pytest tests/test_plugin_system.py

# Run with coverage
pytest --cov=src/hyprrice

# Run tests in parallel
pytest -n auto
```

**Test Coverage**: 298+ tests covering:
- CLI functionality and commands
- GUI components and interactions
- Hyprland integration and configuration
- Plugin system and security
- Backup and migration systems
- Configuration management
- Error handling and validation

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/HyprRice.git
   cd HyprRice
   ```

2. **Set up development environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   pip install -r requirements-dev.txt -r requirements-test.txt
   ```

3. **Run tests to ensure everything works:**
   ```bash
   pytest
   ```

### Making Changes
1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Make your changes and add tests
3. Run tests (`pytest`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### What We're Looking For
- **Bug fixes**: Help us improve stability
- **New features**: Enhance the user experience
- **Plugin development**: Extend functionality
- **Documentation**: Improve guides and examples
- **Testing**: Increase test coverage
- **AUR PKGBUILD**: Package management improvements

### Code Style
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings for new functions
- Include tests for new functionality

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Hyprland](https://github.com/hyprwm/Hyprland) - The amazing Wayland compositor
- [Waybar](https://github.com/Alexays/Waybar) - Highly customizable Wayland bar
- [Rofi](https://github.com/davatorium/rofi) - Window switcher and launcher
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework

## 📞 Support & Troubleshooting

### Getting Help
- **GitHub Issues**: [Report bugs and request features](https://github.com/DuckyOnQuack-999/HyprRice/issues)
- **Documentation**: Check the [docs](docs/) folder for detailed guides
- **Troubleshooting**: See [troubleshooting guide](docs/howto/troubleshooting.md)

### Common Issues & Solutions

#### Installation Problems
```bash
# Check system dependencies
hyprrice doctor

# Verify Python version (3.10+ required)
python --version

# Reinstall in development mode (clean installation)
pip install -e . --force-reinstall

# If you see setuptools warnings, they should be resolved in v1.0.0+
# The project now uses modern pyproject.toml packaging
```

#### Runtime Issues
```bash
# Check if Hyprland is running
hyprctl version

# Verify configuration
hyprrice migrate

# Reset to defaults (creates backup)
rm ~/.config/hyprrice/config.yaml
hyprrice gui
```

#### GUI Issues
- Ensure you're running on Wayland: `echo $WAYLAND_DISPLAY`
- Check PyQt5 installation: `python -c "import PyQt5; print('OK')"`
- Try running with debug mode: `hyprrice gui --debug`

### Performance Tips
- Use `hyprrice doctor` to identify missing dependencies
- Enable performance monitoring in preferences
- Use the backup system before major changes
- Keep your configuration files organized

---

**Made with ❤️ for the Hyprland community** 
