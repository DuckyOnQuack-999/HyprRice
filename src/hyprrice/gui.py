"""
Main GUI application for HyprRice
"""

import sys
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import os

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QMenuBar, QStatusBar, QMessageBox, QApplication, QSplitter,
    QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor

from .config import Config
from .exceptions import HyprRiceError
from .utils import setup_logging, check_dependencies
from .gui.tabs import (
    HyprlandTab, WaybarTab, RofiTab, NotificationsTab,
    ClipboardTab, LockscreenTab, ThemesTab, SettingsTab, PluginsTab
)
from .gui.preview import PreviewWindow
from .gui.theme_manager import ThemeManager
from .plugins import PluginManager


class HyprRiceGUI(QMainWindow):
    """Main application window for HyprRice."""
    
    # Signals
    config_changed = pyqtSignal()
    theme_applied = pyqtSignal(str)
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.theme_manager = ThemeManager(themes_dir=os.path.join(os.path.dirname(__file__), '../../themes'))
        self.plugin_manager = PluginManager(plugins_dir=os.path.expanduser('~/.hyprrice/plugins'))
        self.preview_window: Optional[PreviewWindow] = None
        
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.apply_theme()
        
        # Auto-save timer
        if self.config.gui.auto_save:
            self.auto_save_timer = QTimer()
            self.auto_save_timer.timeout.connect(self.auto_save)
            self.auto_save_timer.start(self.config.gui.auto_save_interval * 1000)
    
    def setup_ui(self):
        """Setup the main user interface."""
        self.setWindowTitle("HyprRice - Hyprland Configuration Tool")
        self.setGeometry(100, 100, self.config.gui.window_width, self.config.gui.window_height)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for sidebar and main content
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Sidebar
        self.setup_sidebar(splitter)
        
        # Main content area
        self.setup_main_content(splitter)
        
        # Set splitter proportions
        splitter.setSizes([200, 800])
    
    def setup_sidebar(self, parent):
        """Setup the sidebar with navigation."""
        sidebar = QFrame()
        sidebar.setFrameStyle(QFrame.StyledPanel)
        sidebar.setMaximumWidth(250)
        sidebar.setMinimumWidth(150)
        
        layout = QVBoxLayout(sidebar)
        
        # Title
        title = QLabel("HyprRice")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Navigation tree
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.itemClicked.connect(self.on_nav_item_clicked)
        layout.addWidget(self.nav_tree)
        
        # Setup navigation items
        self.setup_navigation()
        
        parent.addWidget(sidebar)
    
    def setup_navigation(self):
        """Setup navigation tree items."""
        # Main categories
        hyprland_item = QTreeWidgetItem(self.nav_tree, ["Hyprland"])
        hyprland_item.setIcon(0, QIcon(":/icons/hyprland.png"))
        
        waybar_item = QTreeWidgetItem(self.nav_tree, ["Waybar"])
        waybar_item.setIcon(0, QIcon(":/icons/waybar.png"))
        
        rofi_item = QTreeWidgetItem(self.nav_tree, ["Rofi"])
        rofi_item.setIcon(0, QIcon(":/icons/rofi.png"))
        
        notifications_item = QTreeWidgetItem(self.nav_tree, ["Notifications"])
        notifications_item.setIcon(0, QIcon(":/icons/notifications.png"))
        
        clipboard_item = QTreeWidgetItem(self.nav_tree, ["Clipboard"])
        clipboard_item.setIcon(0, QIcon(":/icons/clipboard.png"))
        
        lockscreen_item = QTreeWidgetItem(self.nav_tree, ["Lockscreen"])
        lockscreen_item.setIcon(0, QIcon(":/icons/lockscreen.png"))
        
        themes_item = QTreeWidgetItem(self.nav_tree, ["Themes"])
        themes_item.setIcon(0, QIcon(":/icons/themes.png"))
        
        settings_item = QTreeWidgetItem(self.nav_tree, ["Settings"])
        settings_item.setIcon(0, QIcon(":/icons/settings.png"))
        
        plugins_item = QTreeWidgetItem(self.nav_tree, ["Plugins"])
        plugins_item.setIcon(0, QIcon(":/icons/plugins.png"))
        
        self.nav_tree.expandAll()
    
    def setup_main_content(self, parent):
        """Setup the main content area with tabs."""
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(False)
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_tabs()
        
        # Add a button to show the preview window
        preview_btn = QPushButton("Show Live Preview")
        preview_btn.setToolTip("Open a live preview of your current theme and settings.")
        preview_btn.clicked.connect(self.show_preview)
        layout.addWidget(preview_btn)
        
        parent.addWidget(content_widget)
    
    def create_tabs(self):
        """Create all application tabs."""
        # Hyprland tab
        self.hyprland_tab = HyprlandTab(self.config, self.preview_window)
        self.tab_widget.addTab(self.hyprland_tab, "Hyprland")
        
        # Waybar tab
        self.waybar_tab = WaybarTab(self.config, self.preview_window)
        self.tab_widget.addTab(self.waybar_tab, "Waybar")
        
        # Rofi tab
        self.rofi_tab = RofiTab(self.config, self.preview_window)
        self.tab_widget.addTab(self.rofi_tab, "Rofi")
        
        # Notifications tab
        self.notifications_tab = NotificationsTab(self.config, self.preview_window)
        self.tab_widget.addTab(self.notifications_tab, "Notifications")
        
        # Clipboard tab
        self.clipboard_tab = ClipboardTab(self.config, self.preview_window)
        self.tab_widget.addTab(self.clipboard_tab, "Clipboard")
        
        # Lockscreen tab
        self.lockscreen_tab = LockscreenTab(self.config, self.preview_window)
        self.tab_widget.addTab(self.lockscreen_tab, "Lockscreen")
        
        # Themes tab
        self.themes_tab = ThemesTab(self.config, self.theme_manager, self.preview_window)
        self.tab_widget.addTab(self.themes_tab, "Themes")
        
        # Settings tab
        self.settings_tab = SettingsTab(self.config, self.preview_window)
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        # Plugins tab
        self.plugins_tab = PluginsTab(self.config, self.plugin_manager, self)
        self.tab_widget.addTab(self.plugins_tab, "Plugins")
        
        # Connect signals
        for tab in [self.hyprland_tab, self.waybar_tab, self.rofi_tab,
                   self.notifications_tab, self.clipboard_tab, self.lockscreen_tab]:
            tab.config_changed.connect(self.on_config_changed)
        
        # Add tooltips to tabs
        self.tab_widget.setTabToolTip(0, "Configure Hyprland core settings.")
        self.tab_widget.setTabToolTip(1, "Configure Waybar settings.")
        self.tab_widget.setTabToolTip(2, "Configure Rofi settings.")
        self.tab_widget.setTabToolTip(3, "Configure notification daemon settings.")
        self.tab_widget.setTabToolTip(4, "Configure clipboard manager settings.")
        self.tab_widget.setTabToolTip(5, "Configure lockscreen settings.")
        self.tab_widget.setTabToolTip(6, "Manage and preview themes.")
        self.tab_widget.setTabToolTip(7, "General settings, backup, restore, undo, redo.")
        self.tab_widget.setTabToolTip(8, "Manage and load plugins.")
    
    def setup_menu(self):
        """Setup the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = file_menu.addAction("&New Theme")
        new_action.triggered.connect(self.new_theme)
        
        open_action = file_menu.addAction("&Open Theme")
        open_action.triggered.connect(self.open_theme)
        
        save_action = file_menu.addAction("&Save Theme")
        save_action.triggered.connect(self.save_theme)
        
        file_menu.addSeparator()
        
        export_action = file_menu.addAction("&Export Configuration")
        export_action.triggered.connect(self.export_config)
        
        import_action = file_menu.addAction("&Import Configuration")
        import_action.triggered.connect(self.import_config)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("E&xit")
        exit_action.triggered.connect(self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = edit_menu.addAction("&Undo")
        undo_action.triggered.connect(self.undo)
        
        redo_action = edit_menu.addAction("&Redo")
        redo_action.triggered.connect(self.redo)
        
        edit_menu.addSeparator()
        
        preferences_action = edit_menu.addAction("&Preferences")
        preferences_action.triggered.connect(self.show_preferences)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        preview_action = view_menu.addAction("&Preview")
        preview_action.triggered.connect(self.show_preview)
        
        view_menu.addSeparator()
        
        theme_menu = view_menu.addMenu("&Theme")
        dark_action = theme_menu.addAction("&Dark")
        dark_action.triggered.connect(lambda: self.set_theme("dark"))
        light_action = theme_menu.addAction("&Light")
        light_action.triggered.connect(lambda: self.set_theme("light"))
        auto_action = theme_menu.addAction("&Auto")
        auto_action.triggered.connect(lambda: self.set_theme("auto"))
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        backup_action = tools_menu.addAction("&Backup")
        backup_action.triggered.connect(self.backup_config)
        
        restore_action = tools_menu.addAction("&Restore")
        restore_action.triggered.connect(self.restore_config)
        
        tools_menu.addSeparator()
        
        check_deps_action = tools_menu.addAction("Check &Dependencies")
        check_deps_action.triggered.connect(self.check_dependencies)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.show_about)
        
        help_action = help_menu.addAction("&Help")
        help_action.triggered.connect(self.show_help)
    
    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def apply_theme(self):
        """Apply the current theme to the application."""
        theme = self.config.gui.theme
        
        if theme == "auto":
            # Auto-detect theme based on system
            theme = self.detect_system_theme()
        
        self.theme_manager.apply_theme(self, theme)
    
    def detect_system_theme(self) -> str:
        """Detect system theme preference."""
        # This is a simplified implementation
        # In a real application, you'd check various system settings
        return "dark"  # Default to dark theme
    
    def on_nav_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle navigation item clicks."""
        item_text = item.text(0)
        
        # Map navigation items to tabs
        tab_mapping = {
            "Hyprland": 0,
            "Waybar": 1,
            "Rofi": 2,
            "Notifications": 3,
            "Clipboard": 4,
            "Lockscreen": 5,
            "Themes": 6,
            "Settings": 7,
            "Plugins": 8,
        }
        
        if item_text in tab_mapping:
            self.tab_widget.setCurrentIndex(tab_mapping[item_text])
    
    def on_config_changed(self):
        """Handle configuration changes."""
        self.config_changed.emit()
        self.status_label.setText("Configuration modified")
        
        # Auto-save if enabled
        if self.config.gui.auto_save:
            self.auto_save()
    
    def auto_save(self):
        """Auto-save configuration."""
        try:
            self.config.save()
            self.logger.debug("Configuration auto-saved")
        except Exception as e:
            self.logger.error(f"Auto-save failed: {e}")
    
    def new_theme(self):
        """Create a new theme."""
        # Implementation for creating new theme
        pass
    
    def open_theme(self):
        """Open an existing theme."""
        # Implementation for opening theme
        pass
    
    def save_theme(self):
        """Save current theme."""
        # Implementation for saving theme
        pass
    
    def export_config(self):
        """Export current configuration."""
        # Implementation for exporting configuration
        pass
    
    def import_config(self):
        """Import configuration."""
        # Implementation for importing configuration
        pass
    
    def undo(self):
        """Undo last action."""
        # Implementation for undo functionality
        pass
    
    def redo(self):
        """Redo last action."""
        # Implementation for redo functionality
        pass
    
    def show_preferences(self):
        """Show preferences dialog."""
        # Implementation for preferences dialog
        pass
    
    def show_preview(self):
        """Show preview window."""
        if not self.preview_window:
            self.preview_window = PreviewWindow(self.config)
        
        self.preview_window.show()
        self.preview_window.raise_()
    
    def set_theme(self, theme: str):
        """Set application theme."""
        self.config.gui.theme = theme
        self.apply_theme()
    
    def backup_config(self):
        """Backup current configuration."""
        # Implementation for backup functionality
        pass
    
    def restore_config(self):
        """Restore configuration from backup."""
        # Implementation for restore functionality
        pass
    
    def check_dependencies(self):
        """Check system dependencies."""
        deps_ok = check_dependencies()
        
        if deps_ok:
            QMessageBox.information(self, "Dependencies", "All required dependencies are available.")
        else:
            QMessageBox.warning(self, "Dependencies", "Some dependencies are missing. Check the logs for details.")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About HyprRice",
            "HyprRice - Comprehensive Hyprland Ecosystem Ricing Tool\n\n"
            "Version: 1.0.0\n"
            "A modern GUI for customizing Hyprland and its ecosystem."
        )
    
    def show_help(self):
        """Show help dialog."""
        # Implementation for help dialog
        pass
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Save configuration before closing
        try:
            self.config.save()
            self.logger.info("Configuration saved on exit")
        except Exception as e:
            self.logger.error(f"Failed to save configuration on exit: {e}")
        
        event.accept() 

    def set_status(self, message):
        self.status_bar.showMessage(message, 5000) 