"""
GUI components for HyprRice
"""

# Import GUI components only when needed to avoid QApplication issues
def get_gui_components():
    """Get GUI components when needed."""
    from .tabs import (
        HyprlandTab, WaybarTab, RofiTab, NotificationsTab,
        ClipboardTab, LockscreenTab, ThemesTab, SettingsTab, PluginsTab
    )
    from .preview import PreviewWindow
    from .theme_manager import ThemeManager
    return {
        'HyprlandTab': HyprlandTab,
        'WaybarTab': WaybarTab,
        'RofiTab': RofiTab,
        'NotificationsTab': NotificationsTab,
        'ClipboardTab': ClipboardTab,
        'LockscreenTab': LockscreenTab,
        'ThemesTab': ThemesTab,
        'SettingsTab': SettingsTab,
        'PluginsTab': PluginsTab,
        'PreviewWindow': PreviewWindow,
        'ThemeManager': ThemeManager,
    }

__all__ = [
    'get_gui_components',
] 
