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
from .gui import HyprRiceGUI
from .utils import setup_logging, check_dependencies

__all__ = [
    "Config",
    "HyprRiceGUI", 
    "setup_logging",
    "check_dependencies",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
] 