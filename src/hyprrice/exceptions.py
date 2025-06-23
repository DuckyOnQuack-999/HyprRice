"""
Custom exceptions for HyprRice
"""


class HyprRiceError(Exception):
    """Base exception for HyprRice."""
    pass


class ConfigError(HyprRiceError):
    """Configuration-related errors."""
    pass


class HyprlandError(HyprRiceError):
    """Hyprland-specific errors."""
    pass


class WaybarError(HyprRiceError):
    """Waybar-specific errors."""
    pass


class RofiError(HyprRiceError):
    """Rofi-specific errors."""
    pass


class NotificationError(HyprRiceError):
    """Notification daemon errors."""
    pass


class BackupError(HyprRiceError):
    """Backup and restore errors."""
    pass


class ThemeError(HyprRiceError):
    """Theme-related errors."""
    pass


class PluginError(HyprRiceError):
    """Plugin system errors."""
    pass


class ValidationError(HyprRiceError):
    """Validation errors."""
    pass


class DependencyError(HyprRiceError):
    """Missing dependency errors."""
    pass 