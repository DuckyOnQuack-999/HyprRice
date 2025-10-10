"""
GUI components for HyprRice
"""

from .tabs import (
    HyprlandTab,
    WaybarTab,
    RofiTab,
    NotificationsTab,
    ClipboardTab,
    LockscreenTab,
    ThemesTab,
    SettingsTab,
    PluginsTab
)
from .preview import PreviewWindow
from .theme_manager import ThemeManager
from .modern_navigation import ModernSidebar, ModernContentArea
from .modern_theme import ModernTheme
from .theme_editor import ThemeEditorDialog
from .preferences import PreferencesDialog
from .backup_manager import BackupSelectionDialog
from .plugin_manager import PluginManagerDialog
from .import_wizard import ImportWizard
from .package_options import PackageOptionsDialog
from .backup_tab import BackupTab
from .plugin_tabs import (
    HyprbarsTab,
    HyprexpoTab,
    GlowTab,
    BlurShadersTab,
    PluginsTab
)

__all__ = [
    'HyprlandTab',
    'WaybarTab', 
    'RofiTab',
    'NotificationsTab',
    'ClipboardTab',
    'LockscreenTab',
    'ThemesTab',
    'SettingsTab',
    'PluginsTab',
    'HyprbarsTab',
    'HyprexpoTab',
    'GlowTab',
    'BlurShadersTab',
    'PreviewWindow',
    'ThemeManager',
    'ModernSidebar',
    'ModernContentArea',
    'ModernTheme',
    'ThemeEditorDialog',
    'PreferencesDialog',
    'BackupSelectionDialog',
    'PluginManagerDialog',
    'ImportWizard',
    'PackageOptionsDialog',
    'BackupTab',
] 
