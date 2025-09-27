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
from .utils import setup_logging, check_dependencies

# Import GUI components conditionally to avoid PyQt6 dependency issues
try:
    from .main_gui import HyprRiceGUI
    # Create HyprRice as an alias to the main GUI for backward compatibility
    HyprRice = HyprRiceGUI
    GUI_AVAILABLE = True
except ImportError:
    HyprRiceGUI = None
    HyprRice = None
    GUI_AVAILABLE = False

__all__ = [
    "Config",
    "setup_logging",
    "check_dependencies",
]

if GUI_AVAILABLE:
    __all__.extend(["HyprRiceGUI", "HyprRice"]) 
