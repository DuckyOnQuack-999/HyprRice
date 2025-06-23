# Theme Format Reference

Complete documentation of the HyprRice theme file format.

## Overview

HyprRice themes are YAML files with the `.hyprrice` extension. They define styles and configurations for all components of the Hyprland ecosystem.

## File Structure

```yaml
# Theme metadata
name: "My Theme"
author: "Your Name"
version: "1.0.0"
description: "A beautiful theme for Hyprland"
license: "MIT"
tags: ["dark", "minimal", "professional"]

# Component configurations
hyprland:
  # Hyprland-specific settings
  
waybar:
  # Waybar configuration
  
rofi:
  # Rofi theme settings
  
notifications:
  # Notification styling
  
clipboard:
  # Clipboard manager config
  
lockscreen:
  # Lock screen appearance
```

## Hyprland Configuration

```yaml
hyprland:
  # Animations
  animations:
    enabled: true
    bezier: "myBezier,0.05,0.9,0.1,1.05"
    animation:
      windows: "1, 7, myBezier"
      windowsOut: "1, 7, default"
      border: "1, 10, default"
      fade: "1, 7, default"
      workspaces: "1, 6, default"
  
  # Decoration
  decoration:
    blur:
      enabled: true
      size: 3
      passes: 1
      new_optimizations: true
    
    drop_shadow: true
    shadow_range: 4
    shadow_render_power: 3
    
    rounding: 10
    active_opacity: 1.0
    inactive_opacity: 0.95
  
  # Colors
  colors:
    foreground: "rgba(255, 255, 255, 1.0)"
    background: "rgba(30, 30, 30, 0.95)"
    accent: "rgba(100, 115, 245, 1.0)"
    
  # Window rules
  windowrule:
    - "float, ^(pavucontrol)$"
    - "center, ^(pavucontrol)$"
```

## Waybar Configuration

```yaml
waybar:
  # Bar configuration
  config:
    position: "top"
    height: 30
    modules-left: ["hyprland/workspaces"]
    modules-center: ["clock"]
    modules-right: ["network", "pulseaudio", "battery"]
  
  # Styling
  style: |
    * {
      border: none;
      border-radius: 0;
      font-family: "JetBrainsMono Nerd Font";
      font-size: 13px;
      min-height: 0;
    }
    
    window#waybar {
      background-color: rgba(43, 48, 59, 0.5);
      border-bottom: 3px solid rgba(100, 115, 245, 0.5);
      color: #ffffff;
    }
```

## Rofi Configuration

```yaml
rofi:
  # Theme configuration
  theme:
    window:
      background-color: "#2e3440"
      border: 1
      padding: 5
    
    mainbox:
      border: 0
      padding: 0
    
    inputbar:
      children: [prompt, entry]
      background-color: "#3b4252"
    
    prompt:
      padding: 6
      background-color: "#81a1c1"
    
    entry:
      padding: 6
      background-color: "#3b4252"
    
    listview:
      border: 0
      padding: 6
      columns: 1
```

## Notification Configuration

```yaml
notifications:
  # Dunst/Mako settings
  config:
    global:
      monitor: 0
      follow: "mouse"
      width: 300
      height: 300
      origin: "top-right"
      offset: "10x10"
      padding: 8
      horizontal_padding: 8
      
    urgency_low:
      background: "#2e3440"
      foreground: "#d8dee9"
      timeout: 10
      
    urgency_normal:
      background: "#3b4252"
      foreground: "#eceff4"
      timeout: 10
      
    urgency_critical:
      background: "#bf616a"
      foreground: "#eceff4"
      timeout: 0
```

## Clipboard Configuration

```yaml
clipboard:
  # Cliphist settings
  config:
    max_items: 100
    sync_selections: true
    use_primary: false
    
  # Styling
  style:
    background: "#2e3440"
    text: "#eceff4"
    selected: "#5e81ac"
```

## Lockscreen Configuration

```yaml
lockscreen:
  # Hyprlock/Swaylock settings
  background:
    source: "~/Pictures/wallpaper.jpg"
    blur: 5
    brightness: 0.8
    
  input:
    ring-color: "#5e81ac"
    inside-color: "#2e3440"
    text-color: "#eceff4"
    
  layout:
    clock: true
    indicator: true
```

## Theme Inheritance

Themes can inherit from other themes:

```yaml
inherit: "base_theme"
name: "Custom Theme"

# Override specific settings
hyprland:
  animations:
    enabled: false
```

## Variables and References

Use variables for consistent values:

```yaml
variables:
  colors:
    bg: "#2e3440"
    fg: "#eceff4"
    accent: "#5e81ac"

hyprland:
  colors:
    background: "${colors.bg}"
    foreground: "${colors.fg}"
    
waybar:
  style: |
    * {
      background-color: ${colors.bg};
      color: ${colors.fg};
    }
```

## Validation Rules

Themes must follow these rules:
1. Required fields: name, version
2. Valid component configurations
3. Proper YAML syntax
4. Valid color formats
5. Existing file references 