# HyprRice User Guide (v1.0.0)

## Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
- [Configuration Tabs](#configuration-tabs)
- [Advanced Features](#advanced-features)
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

## Troubleshooting
- For common issues, log locations, and solutions, see the [Troubleshooting Guide](howto/troubleshooting.md).

## See Also
- [README](../README.md)
- [Quick Start Tutorial](tutorials/quick_start.md)
- [Plugin API Reference](reference/plugin_api.md)
- [Theme Format Reference](reference/theme_format.md)
- [Contributing Guide](development/contributing.md) 