# Quick Start Guide

Get started with HyprRice in minutes! This guide will walk you through installation and basic setup.

## Prerequisites

Ensure you have these dependencies installed:

```bash
# Arch Linux
sudo pacman -S hyprland waybar rofi dunst swww grim slurp cliphist hyprlock \
    python-pyqt5 python-yaml

# Ubuntu/Debian
sudo apt install hyprland waybar rofi dunst swww grim slurp cliphist hyprlock \
    python3-pyqt5 python3-yaml

# Fedora
sudo dnf install hyprland waybar rofi dunst swww grim slurp cliphist hyprlock \
    python3-qt5 python3-yaml
```

## Installation

```bash
# Install HyprRice
pip install hyprrice
```

## First Launch

1. Open a terminal and run:
   ```bash
   hyprrice
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

## Getting Help

- Check [Troubleshooting](../howto/troubleshooting.md)
- Review logs in `~/.local/share/hyprrice/`
- Join our community channels
- Report issues on GitHub 