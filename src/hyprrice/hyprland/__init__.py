"""
Hyprland Integration Module

Provides managers for all aspects of Hyprland configuration including
animations, windows, displays, input, and workspaces.
"""

from .animations import AnimationManager
from .windows import WindowManager
from .display import DisplayManager
from .input import InputManager
from .workspaces import WorkspaceManager

__all__ = [
    "AnimationManager",
    "WindowManager", 
    "DisplayManager",
    "InputManager",
    "WorkspaceManager",
] 
