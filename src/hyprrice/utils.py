"""
Utility functions for HyprRice
"""

import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Union
from datetime import datetime
import asyncio
import time
from functools import lru_cache

from .exceptions import DependencyError
from .security import sanitize_hyprctl_command

# Cache for hyprctl results with TTL
_hyprctl_cache = {}
_cache_ttl = {}
CACHE_DURATION = 5  # seconds

def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """Setup logging configuration."""
    if log_file is None:
        log_file = os.path.expanduser("~/.hyprrice/logs/hyprrice.log")
    
    # Create log directory
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def create_directories() -> None:
    """Create necessary directories for HyprRice."""
    directories = [
        "~/.hyprrice",
        "~/.hyprrice/backups",
        "~/.hyprrice/logs",
        "~/.hyprrice/themes",
        "~/.hyprrice/plugins",
        "~/.config/hyprrice",
    ]
    
    for directory in directories:
        Path(os.path.expanduser(directory)).mkdir(parents=True, exist_ok=True)


def check_dependencies() -> Dict[str, Any]:
    """Check if all required system dependencies are available."""
    logger = logging.getLogger(__name__)
    
    # Define dependencies with their paths and install commands
    dependencies = {
        'hyprland': {
            'paths': ['/usr/bin/hyprctl', '/usr/local/bin/hyprctl'],
            'install_command': 'sudo pacman -S hyprland  # Arch\nsudo apt install hyprland  # Ubuntu/Debian\nsudo dnf install hyprland  # Fedora',
            'required': True,
            'description': 'Hyprland Wayland compositor'
        },
        'waybar': {
            'paths': ['/usr/bin/waybar', '/usr/local/bin/waybar'],
            'install_command': 'sudo pacman -S waybar  # Arch\nsudo apt install waybar  # Ubuntu/Debian\nsudo dnf install waybar  # Fedora',
            'required': True,
            'description': 'Waybar status bar'
        },
        'rofi': {
            'paths': ['/usr/bin/rofi', '/usr/local/bin/rofi'],
            'install_command': 'sudo pacman -S rofi  # Arch\nsudo apt install rofi  # Ubuntu/Debian\nsudo dnf install rofi  # Fedora',
            'required': True,
            'description': 'Rofi application launcher'
        },
        'dunst': {
            'paths': ['/usr/bin/dunst', '/usr/local/bin/dunst'],
            'install_command': 'sudo pacman -S dunst  # Arch\nsudo apt install dunst  # Ubuntu/Debian\nsudo dnf install dunst  # Fedora',
            'required': False,
            'description': 'Dunst notification daemon'
        },
        'mako': {
            'paths': ['/usr/bin/mako', '/usr/local/bin/mako'],
            'install_command': 'sudo pacman -S mako  # Arch\nsudo apt install mako  # Ubuntu/Debian\nsudo dnf install mako  # Fedora',
            'required': False,
            'description': 'Mako notification daemon'
        },
        'grim': {
            'paths': ['/usr/bin/grim', '/usr/local/bin/grim'],
            'install_command': 'sudo pacman -S grim  # Arch\nsudo apt install grim  # Ubuntu/Debian\nsudo dnf install grim  # Fedora',
            'required': False,
            'description': 'Grim screenshot tool'
        },
        'slurp': {
            'paths': ['/usr/bin/slurp', '/usr/local/bin/slurp'],
            'install_command': 'sudo pacman -S slurp  # Arch\nsudo apt install slurp  # Ubuntu/Debian\nsudo dnf install slurp  # Fedora',
            'required': False,
            'description': 'Slurp area selection tool'
        },
        'cliphist': {
            'paths': ['/usr/bin/cliphist', '/usr/local/bin/cliphist'],
            'install_command': 'sudo pacman -S cliphist  # Arch\nsudo apt install cliphist  # Ubuntu/Debian',
            'required': False,
            'description': 'Cliphist clipboard manager'
        },
        'hyprlock': {
            'paths': ['/usr/bin/hyprlock', '/usr/local/bin/hyprlock'],
            'install_command': 'sudo pacman -S hyprlock  # Arch\nsudo apt install hyprlock  # Ubuntu/Debian',
            'required': False,
            'description': 'Hyprlock screen locker'
        },
        'swww': {
            'paths': ['/usr/bin/swww', '/usr/local/bin/swww'],
            'install_command': 'sudo pacman -S swww  # Arch\nsudo apt install swww  # Ubuntu/Debian',
            'required': False,
            'description': 'Swww wallpaper daemon'
        },
        'hyprpaper': {
            'paths': ['/usr/bin/hyprpaper', '/usr/local/bin/hyprpaper'],
            'install_command': 'sudo pacman -S hyprpaper  # Arch\nsudo apt install hyprpaper  # Ubuntu/Debian',
            'required': False,
            'description': 'Hyprpaper wallpaper utility'
        }
    }
    
    results = {}
    
    # Check each dependency
    for dep_name, dep_info in dependencies.items():
        available = False
        version = None
        path = None
        
        # Check if any of the paths exist
        for dep_path in dep_info['paths']:
            if Path(dep_path).exists():
                available = True
                path = dep_path
                break
        
        # Try to get version if available
        if available:
            try:
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                else:
                    # Try alternative version commands
                    for cmd in ['-v', '-V', 'version']:
                        result = subprocess.run([path, cmd], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            version = result.stdout.strip().split('\n')[0]
                            break
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                version = "Unknown"
        
        # Special check for Hyprland (check if running)
        if dep_name == 'hyprland' and available:
            try:
                result = subprocess.run(['hyprctl', 'version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                else:
                    available = False  # Hyprland not running
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                available = False
        
        results[dep_name] = {
            'available': available,
            'version': version,
            'path': path,
            'required': dep_info['required'],
            'description': dep_info['description'],
            'install_command': dep_info['install_command']
        }
        
        if available:
            logger.info(f"✓ {dep_name}: {version or 'Available'}")
        else:
            if dep_info['required']:
                logger.error(f"✗ {dep_name}: Not found (required)")
            else:
                logger.warning(f"✗ {dep_name}: Not found (optional)")
    
    # Check Python dependencies
    python_deps = {
        'PyQt6': 'PyQt6',
        'PyYAML': 'yaml',
        'psutil': 'psutil'
    }
    
    for dep_name, module_name in python_deps.items():
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'Unknown')
            results[f'python_{dep_name.lower()}'] = {
                'available': True,
                'version': version,
                'path': None,
                'required': True,
                'description': f'{dep_name} Python module',
                'install_command': f'pip install {dep_name}'
            }
            logger.info(f"✓ {dep_name}: {version}")
        except ImportError:
            results[f'python_{dep_name.lower()}'] = {
                'available': False,
                'version': None,
                'path': None,
                'required': True,
                'description': f'{dep_name} Python module',
                'install_command': f'pip install {dep_name}'
            }
            logger.error(f"✗ {dep_name}: Not found (required)")
    
    # Check system information
    try:
        import platform
        results['system'] = {
            'available': True,
            'version': f"{platform.system()} {platform.release()}",
            'path': None,
            'required': False,
            'description': 'Operating system',
            'install_command': 'N/A'
        }
    except Exception:
        results['system'] = {
            'available': False,
            'version': 'Unknown',
            'path': None,
            'required': False,
            'description': 'Operating system',
            'install_command': 'N/A'
        }
    
    # Check Wayland session
    wayland_session = os.environ.get('WAYLAND_DISPLAY') or os.environ.get('XDG_SESSION_TYPE') == 'wayland'
    results['wayland'] = {
        'available': wayland_session,
        'version': 'Wayland session detected' if wayland_session else 'X11 session',
        'path': None,
        'required': True,
        'description': 'Wayland session',
        'install_command': 'Use a Wayland-compatible display manager'
    }
    
    return results


def run_command(command: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
    """Run a system command and return the result."""
    try:
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", f"Command not found: {command[0]}"
    except Exception as e:
        return -1, "", str(e)


def hyprctl(command: str, json: bool = False, use_cache: bool = True) -> Tuple[int, str, str]:
    """
    Execute hyprctl command with caching support and security validation.
    
    Args:
        command: The hyprctl command to execute
        json: Whether to use JSON output
        use_cache: Whether to use caching for this command
        
    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    # Sanitize command for security
    try:
        command = sanitize_hyprctl_command(command)
    except Exception as e:
        logging.getLogger(__name__).error(f"Command validation failed: {e}")
        return -1, "", str(e)
    
    # Check cache first
    if use_cache and command in _hyprctl_cache:
        cache_time = _cache_ttl.get(command, 0)
        if time.time() - cache_time < CACHE_DURATION:
            return 0, _hyprctl_cache[command], ""
    
    try:
        args = ['hyprctl'] + (['-j'] if json else []) + command.split()
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=5  # 5 second timeout
        )
        
        if result.returncode == 0 and use_cache:
            # Cache successful results
            _hyprctl_cache[command] = result.stdout
            _cache_ttl[command] = time.time()
        
        return result.returncode, result.stdout, result.stderr
            
    except subprocess.TimeoutExpired:
        logging.getLogger(__name__).error(f"hyprctl command timed out: {command}")
        return -1, "", "Command timed out"
    except FileNotFoundError:
        logging.getLogger(__name__).error("hyprctl not found - is Hyprland running?")
        return -1, "", "hyprctl not found"
    except Exception as e:
        logging.getLogger(__name__).error(f"Error executing hyprctl: {e}")
        return -1, "", str(e)

async def hyprctl_async(command: str, json: bool = False, use_cache: bool = True) -> Tuple[int, str, str]:
    """
    Execute hyprctl command asynchronously with caching support and security validation.
    
    Args:
        command: The hyprctl command to execute
        json: Whether to use JSON output
        use_cache: Whether to use caching for this command
        
    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    # Sanitize command for security
    try:
        command = sanitize_hyprctl_command(command)
    except Exception as e:
        logging.getLogger(__name__).error(f"Command validation failed: {e}")
        return -1, "", str(e)
    
    # Check cache first
    if use_cache and command in _hyprctl_cache:
        cache_time = _cache_ttl.get(command, 0)
        if time.time() - cache_time < CACHE_DURATION:
            return 0, _hyprctl_cache[command], ""
    
    try:
        args = ['hyprctl'] + (['-j'] if json else []) + command.split()
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5.0)
        
        if process.returncode == 0 and use_cache:
            # Cache successful results
            _hyprctl_cache[command] = stdout.decode()
            _cache_ttl[command] = time.time()
        
        return process.returncode, stdout.decode(), stderr.decode()
            
    except asyncio.TimeoutError:
        logging.getLogger(__name__).error(f"hyprctl command timed out: {command}")
        return -1, "", "Command timed out"
    except FileNotFoundError:
        logging.getLogger(__name__).error("hyprctl not found - is Hyprland running?")
        return -1, "", "hyprctl not found"
    except Exception as e:
        logging.getLogger(__name__).error(f"Error executing hyprctl: {e}")
        return -1, "", str(e)

def clear_hyprctl_cache():
    """Clear the hyprctl cache."""
    global _hyprctl_cache, _cache_ttl
    _hyprctl_cache.clear()
    _cache_ttl.clear()

def get_monitors() -> List[Dict[str, str]]:
    """Get list of monitors from hyprctl."""
    returncode, stdout, stderr = hyprctl('monitors')
    
    if returncode != 0:
        return []
    
    monitors = []
    current_monitor = {}
    
    for line in stdout.split('\n'):
        line = line.strip()
        if not line:
            if current_monitor:
                monitors.append(current_monitor)
                current_monitor = {}
            continue
        
        if line.startswith('Monitor'):
            if current_monitor:
                monitors.append(current_monitor)
            current_monitor = {'name': line.split()[1]}
        elif ':' in line:
            key, value = line.split(':', 1)
            current_monitor[key.strip()] = value.strip()
    
    if current_monitor:
        monitors.append(current_monitor)
    
    return monitors


def get_workspaces() -> List[Dict[str, str]]:
    """Get list of workspaces from hyprctl."""
    returncode, stdout, stderr = hyprctl('workspaces')
    
    if returncode != 0:
        return []
    
    workspaces = []
    for line in stdout.split('\n'):
        line = line.strip()
        if line and not line.startswith('workspace'):
            parts = line.split()
            if len(parts) >= 2:
                workspaces.append({
                    'id': parts[0],
                    'name': parts[1],
                    'monitor': parts[2] if len(parts) > 2 else ''
                })
    
    return workspaces


def get_windows() -> List[Dict[str, str]]:
    """Get list of windows from hyprctl."""
    returncode, stdout, stderr = hyprctl('clients')
    
    if returncode != 0:
        return []
    
    windows = []
    current_window = {}
    
    for line in stdout.split('\n'):
        line = line.strip()
        if not line:
            if current_window:
                windows.append(current_window)
                current_window = {}
            continue
        
        if line.startswith('Window'):
            if current_window:
                windows.append(current_window)
            current_window = {'address': line.split()[1]}
        elif ':' in line:
            key, value = line.split(':', 1)
            current_window[key.strip()] = value.strip()
    
    if current_window:
        windows.append(current_window)
    
    return windows


def backup_file(file_path: str, backup_dir: str) -> str:
    """Create a backup of a file."""
    file_path = Path(file_path)
    backup_dir = Path(backup_dir)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Create backup directory if it doesn't exist
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"{timestamp}_{file_path.name}"
    backup_path = backup_dir / backup_name
    
    # Copy file
    shutil.copy2(file_path, backup_path)
    
    return str(backup_path)


def restore_file(backup_path: str, target_path: str) -> None:
    """Restore a file from backup."""
    backup_path = Path(backup_path)
    target_path = Path(target_path)
    
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    
    # Create target directory if it doesn't exist
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy backup to target
    shutil.copy2(backup_path, target_path)


def list_backups(backup_dir: str) -> List[Dict[str, str]]:
    """List available backups."""
    backup_dir = Path(backup_dir)
    
    if not backup_dir.exists():
        return []
    
    backups = []
    for backup_file in backup_dir.glob("*"):
        if backup_file.is_file():
            stat = backup_file.stat()
            backups.append({
                'filename': backup_file.name,
                'path': str(backup_file),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    
    # Sort by modification time (newest first)
    backups.sort(key=lambda x: x['modified'], reverse=True)
    
    return backups


def cleanup_old_backups(backup_dir: str, max_backups: int = 10) -> None:
    """Remove old backups, keeping only the most recent ones."""
    backups = list_backups(backup_dir)
    
    if len(backups) <= max_backups:
        return
    
    # Remove oldest backups
    for backup in backups[max_backups:]:
        try:
            Path(backup['path']).unlink()
        except Exception as e:
            logging.getLogger(__name__).warning(f"Failed to remove backup {backup['path']}: {e}")


def validate_color(color: str) -> bool:
    """Validate if a string is a valid color."""
    import re
    
    # Hex color patterns
    hex_patterns = [
        r'^#[0-9a-fA-F]{6}$',  # #RRGGBB
        r'^#[0-9a-fA-F]{8}$',  # #RRGGBBAA
        r'^#[0-9a-fA-F]{3}$',  # #RGB
        r'^#[0-9a-fA-F]{4}$',  # #RGBA
    ]
    
    # RGB/RGBA patterns
    rgb_patterns = [
        r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$',
        r'^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)$',
    ]
    
    # Check hex patterns
    for pattern in hex_patterns:
        if re.match(pattern, color):
            return True
    
    # Check RGB patterns
    for pattern in rgb_patterns:
        if re.match(pattern, color):
            return True
    
    return False

@lru_cache(maxsize=128)
def validate_color_cached(color: str) -> bool:
    """Cached version of color validation for better performance."""
    return validate_color(color)

def parse_hyprland_config(config_path: str) -> Dict[str, List[str]]:
    """Parse Hyprland configuration file with source directive support."""
    config_path = Path(config_path)
    
    if not config_path.exists():
        return {}
    
    sections = {}
    current_section = 'general'
    sections[current_section] = []
    sourced_files = []
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Check for source directives
                if line.startswith('source '):
                    # Handle both "source file.conf" and "source = file.conf"
                    if '=' in line:
                        source_file = line.split('=', 1)[1].strip().strip('"\'')
                    else:
                        source_file = line[7:].strip().strip('"\'')
                    if source_file:
                        sourced_files.append(source_file)
                    continue
                
                # Check for section headers
                if line.endswith('{'):
                    current_section = line[:-1].strip()
                    if current_section not in sections:
                        sections[current_section] = []
                    continue
                elif line == '}':
                    # End of section, continue with general
                    current_section = 'general'
                    continue
                
                # Add line to current section
                sections[current_section].append(line)
        
        # Store sourced files in a special section
        if sourced_files:
            sections['_sourced_files'] = sourced_files
    
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to parse config {config_path}: {e}")
        return {}
    
    return sections


def write_hyprland_config(config_path: str, sections: Dict[str, List[str]]) -> None:
    """Write Hyprland configuration file with source directive support."""
    config_path = Path(config_path)
    
    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            # Write sourced files first
            if '_sourced_files' in sections:
                for source_file in sections['_sourced_files']:
                    f.write(f"source = {source_file}\n")
                f.write("\n")
            
            # Write other sections
            for section_name, lines in sections.items():
                if section_name == '_sourced_files':
                    continue  # Already handled above
                    
                if section_name != 'general':
                    f.write(f"{section_name} {{\n")
                
                for line in lines:
                    f.write(f"    {line}\n")
                
                if section_name != 'general':
                    f.write("}\n")
                f.write("\n")
    
    except Exception as e:
        raise Exception(f"Failed to write config {config_path}: {e}")


def get_sourced_files_from_config(config_path: str) -> List[str]:
    """Extract sourced files from a Hyprland configuration."""
    sections = parse_hyprland_config(config_path)
    return sections.get('_sourced_files', [])


def create_sourced_file(file_path: str, content: str = None) -> bool:
    """Create a sourced configuration file with default content."""
    file_path = Path(file_path)
    
    # Create directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if content is None:
        # Generate default content based on filename
        if 'rules' in file_path.name.lower():
            content = """# Window rules
windowrule = float, ^(pavucontrol)$
windowrule = float, ^(blueman-manager)$
windowrule = float, ^(nm-connection-editor)$
windowrule = float, ^(chromium)$
windowrule = float, ^(thunar)$
windowrule = float, ^(org.kde.polkit-kde-authentication-agent-1)$

# Workspace rules
windowrulev2 = workspace 1, class:^(firefox)$
windowrulev2 = workspace 2, class:^(code)$
windowrulev2 = workspace 3, class:^(discord)$
windowrulev2 = workspace 4, class:^(spotify)$
"""
        elif 'workspace' in file_path.name.lower():
            content = """# Workspace configuration
workspace = 1, monitor:DP-1
workspace = 2, monitor:DP-1
workspace = 3, monitor:DP-1
workspace = 4, monitor:DP-1
workspace = 5, monitor:DP-1
workspace = 6, monitor:DP-2
workspace = 7, monitor:DP-2
workspace = 8, monitor:DP-2
workspace = 9, monitor:DP-2
workspace = 10, monitor:DP-2
"""
        elif 'exec' in file_path.name.lower():
            content = """# Autostart applications
exec-once = waybar
exec-once = dunst
exec-once = /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1
exec-once = hyprpaper
exec-once = wl-paste --type text --watch cliphist store
exec-once = wl-paste --type image --watch cliphist store
"""
        else:
            content = f"# {file_path.name}\n# Add your configuration here\n"
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to create sourced file {file_path}: {e}")
        return False


def validate_sourced_file(file_path: str) -> bool:
    """Validate that a sourced file exists and is readable."""
    try:
        file_path = Path(file_path)
        return file_path.exists() and file_path.is_file() and file_path.stat().st_size > 0
    except Exception:
        return False


def get_system_info() -> Dict[str, str]:
    """Get system information."""
    info = {}
    
    # OS information
    try:
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    info[f"os_{key.lower()}"] = value.strip('"')
    except:
        info['os_name'] = 'Unknown'
    
    # Desktop environment
    info['desktop'] = os.environ.get('XDG_CURRENT_DESKTOP', 'Unknown')
    info['wayland_display'] = os.environ.get('WAYLAND_DISPLAY', 'Not set')
    
    # Python version
    info['python_version'] = sys.version
    
    return info 

def batch_hyprctl(commands: list, use_cache: bool = True) -> Dict[str, Optional[str]]:
    """
    Execute multiple hyprctl commands efficiently.
    
    Args:
        commands: List of hyprctl commands to execute
        use_cache: Whether to use caching
        
    Returns:
        Dictionary mapping commands to their outputs
    """
    results = {}
    
    # Check cache for all commands first
    uncached_commands = []
    for command in commands:
        if use_cache and command in _hyprctl_cache:
            cache_time = _cache_ttl.get(command, 0)
            if time.time() - cache_time < CACHE_DURATION:
                results[command] = _hyprctl_cache[command]
                continue
        uncached_commands.append(command)
    
    # Execute uncached commands
    for command in uncached_commands:
        returncode, stdout, stderr = hyprctl(command, use_cache=use_cache)
        results[command] = stdout if returncode == 0 else None
    
    return results

async def batch_hyprctl_async(commands: list, use_cache: bool = True) -> Dict[str, Optional[str]]:
    """
    Execute multiple hyprctl commands asynchronously.
    
    Args:
        commands: List of hyprctl commands to execute
        use_cache: Whether to use caching
        
    Returns:
        Dictionary mapping commands to their outputs
    """
    results = {}
    
    # Check cache for all commands first
    uncached_commands = []
    for command in commands:
        if use_cache and command in _hyprctl_cache:
            cache_time = _cache_ttl.get(command, 0)
            if time.time() - cache_time < CACHE_DURATION:
                results[command] = _hyprctl_cache[command]
                continue
        uncached_commands.append(command)
    
    # Execute uncached commands concurrently
    tasks = [hyprctl_async(command, use_cache=use_cache) for command in uncached_commands]
    if tasks:
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for command, result in zip(uncached_commands, task_results):
            if isinstance(result, Exception):
                logging.getLogger(__name__).error(f"Error in batch command {command}: {result}")
                results[command] = None
            else:
                returncode, stdout, stderr = result
                results[command] = stdout if returncode == 0 else None
    
    return results 
