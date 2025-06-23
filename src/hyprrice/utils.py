"""
Utility functions for HyprRice
"""

import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from .exceptions import DependencyError


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


def check_dependencies() -> bool:
    """Check if all required system dependencies are available."""
    logger = logging.getLogger(__name__)
    
    required_deps = {
        'hyprctl': '/usr/bin/hyprctl',
        'waybar': '/usr/bin/waybar',
        'rofi': '/usr/bin/rofi',
        'dunst': '/usr/bin/dunst',
        'grim': '/usr/bin/grim',
        'slurp': '/usr/bin/slurp',
    }
    
    optional_deps = {
        'mako': '/usr/bin/mako',
        'cliphist': '/usr/bin/cliphist',
        'hyprlock': '/usr/bin/hyprlock',
        'swww': '/usr/bin/swww',
        'hyprpaper': '/usr/bin/hyprpaper',
    }
    
    missing_required = []
    missing_optional = []
    
    # Check required dependencies
    for dep_name, dep_path in required_deps.items():
        if not Path(dep_path).exists():
            missing_required.append(dep_name)
            logger.error(f"Required dependency '{dep_name}' not found at {dep_path}")
    
    # Check optional dependencies
    for dep_name, dep_path in optional_deps.items():
        if not Path(dep_path).exists():
            missing_optional.append(dep_name)
            logger.warning(f"Optional dependency '{dep_name}' not found at {dep_path}")
    
    if missing_required:
        logger.error(f"Missing required dependencies: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        logger.warning(f"Missing optional dependencies: {', '.join(missing_optional)}")
    
    logger.info("All required dependencies are available")
    return True


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


def hyprctl(command: str) -> Tuple[int, str, str]:
    """Run hyprctl command."""
    return run_command(['hyprctl', command])


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


def parse_hyprland_config(config_path: str) -> Dict[str, List[str]]:
    """Parse Hyprland configuration file."""
    config_path = Path(config_path)
    
    if not config_path.exists():
        return {}
    
    sections = {}
    current_section = 'general'
    sections[current_section] = []
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Check for section headers
                if line.startswith('{') and line.endswith('}'):
                    current_section = line[1:-1].strip()
                    if current_section not in sections:
                        sections[current_section] = []
                    continue
                
                # Add line to current section
                sections[current_section].append(line)
    
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to parse config {config_path}: {e}")
        return {}
    
    return sections


def write_hyprland_config(config_path: str, sections: Dict[str, List[str]]) -> None:
    """Write Hyprland configuration file."""
    config_path = Path(config_path)
    
    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            for section_name, lines in sections.items():
                if section_name != 'general':
                    f.write(f"{section_name} {{\n")
                
                for line in lines:
                    f.write(f"    {line}\n")
                
                if section_name != 'general':
                    f.write("}\n")
                f.write("\n")
    
    except Exception as e:
        raise Exception(f"Failed to write config {config_path}: {e}")


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