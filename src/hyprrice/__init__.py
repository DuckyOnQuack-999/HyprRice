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

# Import HyprRiceGUI only when needed to avoid QApplication issues
def get_hyprrice_gui():
    """Get HyprRiceGUI class when needed."""
    from .main_gui import HyprRiceGUI
    return HyprRiceGUI

# Create HyprRice as an alias to the main GUI for backward compatibility
HyprRice = get_hyprrice_gui

# Lazy import for HyprRiceGUI to avoid QApplication issues
def __getattr__(name):
    if name == 'HyprRiceGUI':
        from .main_gui import HyprRiceGUI
        return HyprRiceGUI
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "Config",
    "get_hyprrice_gui",
    "HyprRice", 
    "setup_logging",
    "check_dependencies",
] 
