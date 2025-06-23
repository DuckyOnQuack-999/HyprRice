# Troubleshooting Guide

Common issues and solutions when using HyprRice.

## Common Issues

### 1. Preview Not Updating

**Symptoms:**
- Live preview window not reflecting changes
- Preview appears frozen or blank

**Solutions:**
1. Check if Hyprland is running:
   ```bash
   ps aux | grep hyprland
   ```

2. Verify display permissions:
   ```bash
   ls -l /tmp/hypr
   ```

3. Restart HyprRice:
   ```bash
   killall hyprrice
   hyprrice
   ```

### 2. Plugin Loading Fails

**Symptoms:**
- Plugin doesn't appear in plugins tab
- Error in plugin loading

**Solutions:**
1. Check plugin file permissions:
   ```bash
   ls -l ~/.hyprrice/plugins/
   ```

2. Verify Python dependencies:
   ```bash
   pip list | grep required-package
   ```

3. Check plugin logs:
   ```bash
   cat ~/.local/share/hyprrice/plugins/plugin_name.log
   ```

### 3. Theme Import Fails

**Symptoms:**
- Import dialog shows error
- Theme not appearing in gallery

**Solutions:**
1. Validate theme file:
   ```bash
   hyprrice validate-theme path/to/theme.hyprrice
   ```

2. Check file format:
   ```bash
   file path/to/theme.hyprrice
   ```

3. Try importing sections separately:
   - Import only Hyprland config
   - Import only Waybar config
   - Merge manually if needed

### 4. Configuration Not Applying

**Symptoms:**
- Changes not taking effect
- System configuration unchanged

**Solutions:**
1. Check write permissions:
   ```bash
   ls -l ~/.config/hypr/
   ```

2. Verify config location:
   ```bash
   echo $XDG_CONFIG_HOME
   ```

3. Try manual apply:
   ```bash
   hyprrice apply --force
   ```

### 5. UI Issues

**Symptoms:**
- Widgets misaligned
- Text unreadable
- Controls not responding

**Solutions:**
1. Check Qt scaling:
   ```bash
   export QT_SCALE_FACTOR=1
   ```

2. Verify theme compatibility:
   ```bash
   hyprrice check-theme
   ```

3. Reset UI settings:
   ```bash
   rm ~/.config/hyprrice/ui.conf
   ```

## Log Files

### Main Logs
```bash
# Application log
~/.local/share/hyprrice/hyprrice.log

# Debug log
~/.local/share/hyprrice/debug.log

# Plugin logs
~/.local/share/hyprrice/plugins/*.log
```

### Reading Logs
```bash
# View last 50 lines
tail -n 50 ~/.local/share/hyprrice/hyprrice.log

# Follow log in real-time
tail -f ~/.local/share/hyprrice/hyprrice.log

# Search for errors
grep ERROR ~/.local/share/hyprrice/hyprrice.log
```

## Configuration Files

### Main Config
```bash
~/.config/hyprrice/config.yaml
```

### Component Configs
```bash
~/.config/hypr/hyprland.conf
~/.config/waybar/config
~/.config/rofi/config.rasi
~/.config/dunst/dunstrc
```

## Getting Help

1. **Documentation**
   - Check this troubleshooting guide
   - Review the [User Guide](../user_guide.md)
   - Search [Configuration Reference](../reference/configuration.md)

2. **Community**
   - GitHub Issues
   - Discord Server
   - Reddit Community

3. **Reporting Bugs**
   - Include log files
   - Describe steps to reproduce
   - List system information
   - Attach relevant configs

## Prevention

1. **Regular Backups**
   ```bash
   hyprrice backup
   ```

2. **Version Control**
   ```bash
   git init ~/.config/hyprrice
   ```

3. **Testing Changes**
   ```bash
   hyprrice apply --dry-run
   ```

4. **Monitoring Logs**
   ```bash
   hyprrice log-monitor
   ``` 