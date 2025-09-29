# Quick Start Guide

Get started with HyprRice in minutes! This guide will walk you through installation and basic setup.

## Prerequisites

Ensure you have these dependencies installed:

```bash
# Arch Linux
sudo pacman -S hyprland waybar rofi dunst swww grim slurp cliphist hyprlock \
    python-pyqt6 python-yaml qt6-wayland

# Ubuntu/Debian
sudo apt install hyprland waybar rofi dunst swww grim slurp cliphist hyprlock \
    python3-pyqt6 python3-yaml qt6-wayland

# Fedora
sudo dnf install hyprland waybar rofi dunst swww grim slurp cliphist hyprlock \
    python3-qt6 python3-yaml qt6-qtwayland
```

## Installation

```bash
# Install HyprRice
pip install hyprrice
```

## First Launch

1. Open a terminal and run:
   ```bash
   hyprrice gui
   ```

2. Choose a base theme:
   - Minimal: Clean, simple design
   - Cyberpunk: Neon, high-contrast
   - Pastel: Soft, muted colors

3. Configure basic settings:
   - Display resolution
   - Input devices
   - Basic animations

4. Use live preview to see changes in real-time

5. **New in v1.0**: Access the Configuration Editor from the File menu for manual editing
6. **New in v1.0**: Use Debug Mode from the Tools menu for system analysis

## Next Steps

- Explore the tabs to customize different components
- Try importing and customizing themes
- Check out the [User Guide](../user_guide.md) for detailed information
- Join the community to share themes and plugins

## Common Operations

### Save Your Theme
1. Go to Themes tab
2. Click "Save As"
3. Enter a name and description
4. Click Save

### Apply Changes
1. Make your adjustments
2. Click "Preview" to test
3. Click "Apply" to save changes
4. Use "Rollback" if needed

### Import/Export
1. Go to Settings tab
2. Use Import/Export buttons
3. Choose format (YAML/JSON)
4. Select destination

### Manual Configuration Editing (New in v1.0)
1. Go to File → Configuration Editor
2. Select the configuration file to edit
3. Make your changes in the text editor
4. Save the file

### Debug Mode (New in v1.0)
1. Go to Tools → Debug Mode
2. Run comprehensive system analysis
3. Review the debug report
4. Save the report for troubleshooting

### Package Options (New in v1.0)
1. Go to Tools → Package Options
2. Select your distribution (Arch, Fedora, Ubuntu, etc.)
3. Choose package type (AUR, RPM, PPA, etc.)
4. Copy installation script or save to file

### Import From Dotfiles (New in v1.0)
1. Go to Tools → Import From Dotfiles
2. Select source (ML4W, end-4, or custom repository)
3. Review detected configurations
4. Map configurations to HyprRice themes
5. Import and apply the configurations

**Note:** Currently supports local directories only. GitHub import coming soon. Templates are examples - customize as needed.

## Getting Help

- Check [Troubleshooting](../howto/troubleshooting.md)
- Review logs in `~/.local/share/hyprrice/`
- Join our community channels
- Report issues on GitHub 
