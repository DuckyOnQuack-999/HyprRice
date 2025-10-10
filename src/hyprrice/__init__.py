"""
HyprRice - Comprehensive Hyprland Ecosystem Ricing Tool

A modern, user-friendly GUI application for customizing the Hyprland Wayland compositor
and its associated tools including Waybar, Rofi, notifications, and more.
"""

__version__ = "1.0.0"
__author__ = "HyprRice Team"
__email__ = "hyprrice@example.com"
__description__ = "Comprehensive Hyprland Ecosystem Ricing Tool"

from .config import Config
from .main_gui import HyprRiceGUI
from .utils import setup_logging, check_dependencies
from .main import main as main_entry_point

# Create HyprRice as an alias to the main GUI for backward compatibility
HyprRice = HyprRiceGUI

__all__ = [
    "Config",
    "HyprRiceGUI",
    "HyprRice", 
    "setup_logging",
    "check_dependencies",
    "main_entry_point",
] 
