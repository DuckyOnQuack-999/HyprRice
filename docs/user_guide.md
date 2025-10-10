# HyprRice User Guide (v1.0.0)

## Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
- [Configuration Tabs](#configuration-tabs)
- [Advanced Features](#advanced-features)
- [New Features in v1.0](#new-features-in-v10)
- [Troubleshooting](#troubleshooting)
- [See Also](#see-also)

## Overview
HyprRice is a comprehensive ricing tool for the Hyprland Wayland compositor ecosystem. It provides a modern GUI, deep integration with Hyprland and related tools, theme management, plugin support, and robust configuration handling.

## Getting Started
- **Installation, Features, and Quick Start:** See the [README](../README.md) for the most up-to-date installation instructions, feature overview, and quick start guide.
- After installation, launch HyprRice and follow the on-screen setup wizard.
- For a fast onboarding, see the [Quick Start Tutorial](tutorials/quick_start.md).

## Configuration Tabs

### Hyprland Tab
- Animations, window management, input, display, performance

### Waybar Tab
- Layout, modules, colors, custom CSS

### Rofi Tab
- Theme selection, layout, colors, custom modes

### Notifications Tab
- Dunst/Mako config, position, timeout, rules

### Clipboard Tab
- Manager selection, history, sync, privacy

### Lockscreen Tab
- Hyprlock/Swaylock, backgrounds, effects, triggers

### Themes Tab
- Browse, preview, import/export, create, share themes
- For theme format details, see [Theme Format Reference](reference/theme_format.md)

### Settings Tab
- Backup/restore, import/export, undo/redo, audit log

### Plugins Tab
- Enable/disable plugins, configure settings, view events, install new plugins
- For plugin development, see [Plugin API Reference](reference/plugin_api.md)

## Advanced Features
- **Plugin System:** Extend HyprRice with Python plugins and event hooks. See [Plugin API Reference](reference/plugin_api.md) and [Plugin Development Tutorial](tutorials/plugin_development.md).
- **Theme Creation:** Create and share custom themes. See [Theme Format Reference](reference/theme_format.md) and [Theme Creation Tutorial](tutorials/theme_creation.md).
- **Import/Export:** Import/export themes and configs with validation and preview. All imports trigger backup and plugin hooks.
- **Changelog & Audit:** Export detailed changelogs and audit trails (Markdown, JSON, HTML).

## New Features in v1.0

### Configuration Editor
- **Access:** File → Configuration Editor
- **Features:** 
  - Dedicated text editor for manual configuration file editing
  - Syntax highlighting and validation
  - Save and save-as functionality
  - Unsaved changes detection
- **Use Cases:** Advanced users who prefer direct file editing, troubleshooting configuration issues

### Debug Mode
- **Access:** Tools → Debug Mode
- **Features:**
  - Comprehensive system analysis and testing
  - Dependency checking and validation
  - Configuration loading tests
  - Integration tests for all components
  - Detailed debug reports with recommendations
- **Use Cases:** Troubleshooting, system validation, performance analysis

### Enhanced Sourced Files Management
- **Access:** Hyprland Tab → Sourced Configuration Files
- **Features:**
  - Add, remove, and manage external configuration files
  - Template-based file creation
  - Configuration type selection (General, Window Rules, Keybindings, etc.)
  - Auto-creation of files with templates
- **Use Cases:** Organizing complex configurations, managing multiple config files

### Advanced Security Features
- **Plugin Sandboxing:** Enhanced security for plugin execution
- **Input Validation:** Comprehensive validation of user inputs
- **Path Restrictions:** Protection against path traversal attacks
- **Command Sanitization:** Safe execution of system commands

### Autoconfig System (New in v1.0)
- **Access:** Tools → Autoconfig Wizard, or CLI: `hyprrice autoconfig`
- **Features:**
  - Intelligent system profiling (CPU, memory, GPU, display analysis)
  - Four performance profiles: Performance, Visual, Battery, Minimal
  - Hardware-aware optimization based on system capabilities
  - Automatic backup creation with rollback capabilities
  - Real-time configuration preview and application
  - Interactive wizard with step-by-step guidance
- **Use Cases:** First-time setup, system optimization, performance tuning, battery saving
- **See Also:** [Autoconfig Guide](../AUTOCONFIG_GUIDE.md) for detailed usage instructions

### Package Options (New in v1.0)
- **Access:** Tools → Package Options
- **Features:**
  - Comprehensive package management options for all major distributions
  - Arch Linux: AUR, PKGBUILD, installation scripts
  - Fedora: RPM spec, COPR repository, installation scripts
  - Ubuntu/Debian: PPA, DEB package, installation scripts
  - Flatpak: Manifest file and installation instructions
  - Snap: snapcraft.yaml and installation instructions
  - Nix: Nix derivation and installation instructions
  - Docker: Dockerfile and container usage instructions
  - Homebrew: Formula and installation instructions for macOS
  - Copy to clipboard and save to file functionality
- **Use Cases:** Easy installation across different distributions, package development, deployment automation

### Import From Dotfiles (New in v1.0)
- **Access:** Tools → Import From Dotfiles
- **Features:**
  - Import configurations from popular Hyprland dotfiles repositories
  - Support for ML4W Dotfiles and end-4 dots-hyprland
  - Automatic detection and mapping of configurations
  - Preview and customization before import
  - Create themes from imported configurations
  - Backup existing configurations before import
  - Step-by-step wizard interface
- **Use Cases:** Quickly adopt proven configurations, learn from community setups, migrate from other dotfiles
- **Safety Notes:** 
  - Only imports from local directories (GitHub import coming soon)
  - Validates file paths and prevents directory traversal
  - Creates themes in user-writable directories only
  - Templates are examples only - customize as needed

## Troubleshooting
- For common issues, log locations, and solutions, see the [Troubleshooting Guide](howto/troubleshooting.md).

## See Also
- [README](../README.md)
- [Quick Start Tutorial](tutorials/quick_start.md)
- [Plugin Development Guide](plugins.md)
- [Security Guide](security.md)
- [API Reference](api.md)
- [Theme Format Reference](reference/theme_format.md)
- [Autoconfig Guide](../AUTOCONFIG_GUIDE.md)
- [Contributing Guide](development/contributing.md) 
