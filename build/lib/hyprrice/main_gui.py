"""
Main GUI application for HyprRice
"""

import sys
import logging
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
import os

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QMenuBar, QStatusBar, QMessageBox, QApplication, QSplitter,
    QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QFrame, QProgressBar,
    QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QKeySequence, QIcon, QFont, QPalette, QColor, QShortcut

from .config import Config
from .exceptions import HyprRiceError
from .utils import setup_logging, check_dependencies
from .history import HistoryManager, BackupManager
from .gui.tabs import (
    HyprlandTab, WaybarTab, RofiTab, NotificationsTab,
    ClipboardTab, LockscreenTab, ThemesTab, SettingsTab, PluginsTab
)
from .gui.preview import PreviewWindow
from .gui.theme_manager import ThemeManager
from .gui.modern_theme import ModernTheme
from .gui.theme_editor import ThemeEditorDialog
from .gui.preferences import PreferencesDialog
from .gui.backup_manager import BackupSelectionDialog
from .gui.plugin_manager import PluginManagerDialog
from .plugins import EnhancedPluginManager
from .performance import performance_monitor, profile

import yaml
import json
from pathlib import Path


class BackgroundWorker(QThread):
    """Background worker for long-running operations."""
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, operation, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            if asyncio.iscoroutinefunction(self.operation):
                # Handle async operations
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.operation(*self.args, **self.kwargs))
                loop.close()
            else:
                result = self.operation(*self.args, **self.kwargs)
            
            self.finished.emit(result if isinstance(result, dict) else {'result': result})
        except Exception as e:
            self.error.emit(str(e))


class HyprRiceGUI(QMainWindow):
    """Enhanced main GUI for HyprRice with keyboard shortcuts and performance improvements."""
    
    config_changed = pyqtSignal()
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.theme_manager = ThemeManager(themes_dir=os.path.join(os.path.dirname(__file__), '../../themes'))
        self.modern_theme = ModernTheme()
        
        # Initialize enhanced plugin system with security settings
        plugins_dir = Path(__file__).parent.parent.parent / "plugins"
        
        # Get security settings from config
        enable_sandbox = False  # Default to False for file-based plugins
        security_level = 'medium'
        
        if hasattr(config, 'security'):
            enable_sandbox = getattr(config.security, 'enable_plugin_sandbox', False)
            security_level = getattr(config.security, 'plugin_security_level', 'medium')
        
        self.plugin_manager = EnhancedPluginManager(
            plugins_dir=str(plugins_dir),
            enable_sandbox=enable_sandbox,
            security_level=security_level
        )
        
        self.history_manager = HistoryManager(config)
        self.backup_manager = BackupManager(config.paths.backup_dir)
        self.preview_window: Optional[PreviewWindow] = None
        
        # Background workers
        self.workers = []
        
        # Setup global error boundary
        self.setup_global_error_handler()
        
        self.setup_ui()
        self.setup_menu()
        self.setup_shortcuts()
        self.setup_status_bar()
        
        # Check first-run and migration (after UI is set up)
        self.check_startup_requirements()
        
        self.apply_theme()
        
        # Load default plugins after UI setup
        self.load_default_plugins()
        
        # Apply modern theme with ultra-modern styling
        self.modern_theme.set_accent_color("#6366f1")  # Modern indigo accent
        self.modern_theme.set_theme("dark")  # Force dark theme for sleek look
        self.modern_theme.apply_to_application(QApplication.instance())
        
        # Start performance monitoring (if enabled)
        from .performance import _auto_monitoring_enabled
        if _auto_monitoring_enabled:
            performance_monitor.start_monitoring()
        
        # Auto-save timer
        if self.config.gui.auto_save:
            self.auto_save_timer = QTimer()
            self.auto_save_timer.timeout.connect(self.auto_save)
            self.auto_save_timer.start(self.config.gui.auto_save_interval * 1000)
    
    def setup_global_error_handler(self):
        """Setup global error handler for uncaught exceptions."""
        import sys
        import traceback
        
        def handle_exception(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions with user-friendly dialog."""
            if issubclass(exc_type, KeyboardInterrupt):
                # Allow keyboard interrupt to work normally
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            # Log the error
            self.logger.critical(
                "Uncaught exception", 
                exc_info=(exc_type, exc_value, exc_traceback)
            )
            
            # Show user-friendly error dialog
            error_msg = f"An unexpected error occurred:\n\n{exc_value}"
            if getattr(self.config.gui, 'debug_mode', False):
                error_msg += f"\n\nTechnical details:\n{traceback.format_exception(exc_type, exc_value, exc_traceback)}"
            
            QMessageBox.critical(
                self,
                "HyprRice Error",
                error_msg
            )
        
        sys.excepthook = handle_exception
    
    def check_startup_requirements(self):
        """Check first-run status and migration requirements."""
        try:
            # Check if this is first run
            first_run_marker = Path.home() / '.hyprrice' / '.first_run'
            is_first_run = not first_run_marker.exists()
            
            if is_first_run:
                self.handle_first_run()
                # Create first run marker
                first_run_marker.parent.mkdir(parents=True, exist_ok=True)
                first_run_marker.touch()
            
            # Check if migration is needed
            from .migration import check_migration_needed
            if check_migration_needed():
                self.prompt_migration()
                
        except Exception as e:
            self.logger.warning(f"Error checking startup requirements: {e}")
    
    def handle_first_run(self):
        """Handle first run setup."""
        try:
            # Create necessary directories
            directories = [
                Path.home() / '.hyprrice' / 'themes',
                Path.home() / '.hyprrice' / 'plugins',
                Path.home() / '.hyprrice' / 'backups',
                Path.home() / '.hyprrice' / 'logs',
                Path.home() / '.config' / 'hyprrice',
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
            
            # Show welcome message
            QMessageBox.information(
                self,
                "Welcome to HyprRice!",
                "Welcome to HyprRice! This appears to be your first time running the application.\n\n"
                "HyprRice has created the necessary directories and is ready to use.\n\n"
                "You can start by:\n"
                "• Exploring the theme gallery\n"
                "• Configuring your Hyprland settings\n"
                "• Installing plugins from the plugin manager\n\n"
                "For help, press F1 or check the documentation."
            )
            
        except Exception as e:
            self.logger.error(f"Error during first run setup: {e}")
    
    def prompt_migration(self):
        """Prompt user about configuration migration."""
        try:
            from .migration import migrate_config
            
            reply = QMessageBox.question(
                self,
                "Configuration Migration",
                "Your configuration format is outdated and needs to be migrated.\n\n"
                "This will:\n"
                "• Update your configuration to the latest format\n"
                "• Create a backup of your current configuration\n"
                "• Preserve all your existing settings\n\n"
                "Would you like to migrate now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Run migration in background
                def migration_operation():
                    return migrate_config(create_backup=True)
                
                worker = self.run_background_operation(migration_operation)
                worker.finished.connect(self.on_migration_completed)
                worker.error.connect(self.on_migration_error)
            else:
                self.logger.info("User declined configuration migration")
                
        except Exception as e:
            self.logger.error(f"Error prompting migration: {e}")
    
    def on_migration_completed(self, result):
        """Handle successful migration."""
        try:
            if result.get('success', False):
                QMessageBox.information(
                    self,
                    "Migration Complete",
                    "Configuration migration completed successfully!\n\n"
                    f"Backup created at: {result.get('backup_path', 'Unknown')}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Migration Failed",
                    f"Configuration migration failed:\n\n{result.get('error', 'Unknown error')}"
                )
        except Exception as e:
            self.logger.error(f"Error handling migration completion: {e}")
    
    def on_migration_error(self, error_msg):
        """Handle migration error."""
        QMessageBox.critical(
            self,
            "Migration Error",
            f"An error occurred during migration:\n\n{error_msg}"
        )
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts for better accessibility."""
        shortcuts = [
            # File operations
            (QKeySequence.StandardKey.New, self.new_theme),
            (QKeySequence.StandardKey.Open, self.open_theme),
            (QKeySequence.StandardKey.Save, self.save_theme),
            (QKeySequence("Ctrl+E"), self.export_config),
            (QKeySequence("Ctrl+I"), self.import_config),
            (QKeySequence.StandardKey.Quit, self.close),
            
            # Edit operations
            (QKeySequence.StandardKey.Undo, self.undo),
            (QKeySequence.StandardKey.Redo, self.redo),
            (QKeySequence.StandardKey.Preferences, self.show_preferences),
            
            # View operations
            (QKeySequence("F5"), self.refresh_all_tabs),
            (QKeySequence("Ctrl+P"), self.show_preview),
            (QKeySequence("F11"), self.toggle_fullscreen),
            
            # Tools
            (QKeySequence("Ctrl+B"), self.backup_config),
            (QKeySequence("Ctrl+R"), self.restore_config),
            (QKeySequence("F1"), self.show_help),
            
            # Navigation
            (QKeySequence("Ctrl+1"), lambda: self.tab_widget.setCurrentIndex(0)),
            (QKeySequence("Ctrl+2"), lambda: self.tab_widget.setCurrentIndex(1)),
            (QKeySequence("Ctrl+3"), lambda: self.tab_widget.setCurrentIndex(2)),
            (QKeySequence("Ctrl+4"), lambda: self.tab_widget.setCurrentIndex(3)),
            (QKeySequence("Ctrl+5"), lambda: self.tab_widget.setCurrentIndex(4)),
            (QKeySequence("Ctrl+6"), lambda: self.tab_widget.setCurrentIndex(5)),
            (QKeySequence("Ctrl+7"), lambda: self.tab_widget.setCurrentIndex(6)),
            (QKeySequence("Ctrl+8"), lambda: self.tab_widget.setCurrentIndex(7)),
        ]
        
        for shortcut_key, action in shortcuts:
            try:
                shortcut = QShortcut(shortcut_key, self)
                shortcut.activated.connect(action)
                
                # Add tooltip showing the shortcut
                if hasattr(action, '__self__') and hasattr(action.__self__, 'setToolTip'):
                    current_tooltip = action.__self__.toolTip()
                    shortcut_text = str(shortcut_key)
                    if current_tooltip:
                        action.__self__.setToolTip(f"{current_tooltip} ({shortcut_text})")
                    else:
                        action.__self__.setToolTip(f"Shortcut: {shortcut_text}")
                        
            except Exception as e:
                self.logger.warning(f"Failed to setup shortcut {shortcut_key}: {e}")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def run_background_operation(self, operation, *args, **kwargs):
        """Run an operation in the background with progress indication."""
        worker = BackgroundWorker(operation, *args, **kwargs)
        worker.finished.connect(self.on_background_finished)
        worker.error.connect(self.on_background_error)
        worker.progress.connect(self.on_background_progress)
        
        self.workers.append(worker)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        worker.start()
        return worker
    
    @pyqtSlot(dict)
    def on_background_finished(self, result):
        """Handle background operation completion."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Operation completed successfully")
        
        # Clean up worker
        sender = self.sender()
        if sender in self.workers:
            self.workers.remove(sender)
            sender.deleteLater()
    
    @pyqtSlot(str)
    def on_background_error(self, error_message):
        """Handle background operation error."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Operation failed: {error_message}")
        
        # Show error dialog
        QMessageBox.critical(self, "Operation Failed", f"An error occurred:\n\n{error_message}")
        
        # Clean up worker
        sender = self.sender()
        if sender in self.workers:
            self.workers.remove(sender)
            sender.deleteLater()
    
    @pyqtSlot(int)
    def on_background_progress(self, value):
        """Handle background operation progress."""
        if self.progress_bar.maximum() > 0:
            self.progress_bar.setValue(value)
    
    def show_error_dialog(self, title: str, message: str, details: str = ""):
        """Show enhanced error dialog with details."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if details:
            msg_box.setDetailedText(details)
        
        # Add helpful buttons
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Help)
        
        # Connect help button
        if msg_box.clickedButton(msg_box.button(QMessageBox.StandardButton.Help)):
            self.show_help()
        
        msg_box.exec()
    
    def show_success_notification(self, message: str, timeout: int = 3000):
        """Show success notification in status bar."""
        self.status_label.setText(f"✅ {message}")
        QTimer.singleShot(timeout, lambda: self.status_label.setText("Ready"))
    
    def show_warning_notification(self, message: str, timeout: int = 5000):
        """Show warning notification in status bar."""
        self.status_label.setText(f"⚠️ {message}")
        QTimer.singleShot(timeout, lambda: self.status_label.setText("Ready"))
    
    def apply_to_hyprland_async(self):
        """Apply configuration to Hyprland asynchronously."""
        def apply_operation():
            # This would contain the actual application logic
            # For now, just simulate the operation
            import time
            time.sleep(2)  # Simulate work
            return {"success": True, "message": "Configuration applied successfully"}
        
        self.run_background_operation(apply_operation)
        self.status_label.setText("Applying configuration to Hyprland...")
    
    def enhanced_error_handling(self, operation):
        """Decorator for enhanced error handling."""
        def wrapper(*args, **kwargs):
            try:
                return operation(*args, **kwargs)
            except FileNotFoundError as e:
                self.show_error_dialog(
                    "File Not Found",
                    f"The requested file could not be found.",
                    f"Details: {str(e)}\n\nPlease check that the file exists and you have permission to access it."
                )
            except PermissionError as e:
                self.show_error_dialog(
                    "Permission Denied",
                    f"Permission denied while accessing file or resource.",
                    f"Details: {str(e)}\n\nPlease check file permissions or run with appropriate privileges."
                )
            except json.JSONDecodeError as e:
                self.show_error_dialog(
                    "Invalid JSON",
                    f"The file contains invalid JSON data.",
                    f"Details: {str(e)}\n\nPlease check the file format and try again."
                )
            except yaml.YAMLError as e:
                self.show_error_dialog(
                    "Invalid YAML",
                    f"The file contains invalid YAML data.",
                    f"Details: {str(e)}\n\nPlease check the file format and try again."
                )
            except Exception as e:
                self.show_error_dialog(
                    "Unexpected Error",
                    f"An unexpected error occurred.",
                    f"Details: {str(e)}\n\nPlease report this issue if it persists."
                )
                self.logger.exception(f"Unexpected error in {operation.__name__}")
        
        return wrapper

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
        splitter = QSplitter(Qt.Orientation.Horizontal)
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
        sidebar.setFrameStyle(QFrame.Shape.StyledPanel)
        sidebar.setMaximumWidth(250)
        sidebar.setMinimumWidth(150)
        
        layout = QVBoxLayout(sidebar)
        
        # Title
        title = QLabel("HyprRice")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        
        # Plugin Menu (NEW)
        plugin_menu = menubar.addMenu('&Plugins')
        
        plugin_manager_action = plugin_menu.addAction('Plugin &Manager')
        plugin_manager_action.triggered.connect(self.show_plugin_manager)
        
        plugin_menu.addSeparator()
        
        load_plugins_action = plugin_menu.addAction('&Load Default Plugins')
        load_plugins_action.triggered.connect(self.load_default_plugins)
        
        reload_plugins_action = plugin_menu.addAction('&Reload All Plugins')
        reload_plugins_action.triggered.connect(self.reload_all_plugins)
        
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
        
        # Apply modern theme
        self.modern_theme.set_theme(theme)
        self.modern_theme.apply_to_application(QApplication.instance())
        
        # Apply legacy theme manager if needed
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
    
    def show_help(self):
        """Show help dialog."""
        pass  # Placeholder - will be implemented later
    
    # ===== THEME MENU ACTIONS =====
    
    def new_theme(self):
        """Create a new theme from template."""
        try:
            # Create new theme template
            template = self.theme_manager.create_theme_template()
            
            # Show theme editor dialog
            dialog = ThemeEditorDialog(template, self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                theme_data = dialog.get_theme_data()
                
                # Validate theme
                errors = self.theme_manager.get_theme_validation_errors(theme_data)
                if errors:
                    error_msg = "Theme validation failed:\n" + "\n".join(errors)
                    QMessageBox.warning(self, "Invalid Theme", error_msg)
                    return
                
                # Save theme
                theme_name = theme_data['name'].lower().replace(' ', '_')
                theme_file = self.theme_manager.themes_dir / f"{theme_name}.hyprrice"
                
                with open(theme_file, 'w', encoding='utf-8') as f:
                    yaml.dump(theme_data, f, default_flow_style=False, indent=2)
                
                self.status_label.setText(f"Created theme: {theme_data['name']}")
                self.logger.info(f"Created new theme: {theme_name}")
                
                # Refresh themes in GUI
                if hasattr(self.themes_tab, 'refresh_themes'):
                    self.themes_tab.refresh_themes()
                    
        except Exception as e:
            self.logger.error(f"Error creating new theme: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create theme: {str(e)}")
    
    def open_theme(self):
        """Open and load an existing theme file."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Theme",
                str(self.theme_manager.themes_dir),
                "HyprRice Themes (*.hyprrice);;YAML Files (*.yaml *.yml);;JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                # Import the theme
                if self.theme_manager.import_theme(file_path):
                    # Get theme name from file
                    theme_name = Path(file_path).stem
                    
                    # Apply the theme
                    if self.theme_manager.apply_theme(theme_name, self.config):
                        self.status_label.setText(f"Loaded theme: {theme_name}")
                        self.logger.info(f"Loaded theme: {theme_name}")
                        
                        # Refresh GUI
                        self.refresh_all_tabs()
                        
                        # Update preview
                        if self.preview_window:
                            self.preview_window.update_preview()
                    else:
                        QMessageBox.warning(self, "Warning", f"Theme loaded but failed to apply: {theme_name}")
                else:
                    QMessageBox.critical(self, "Error", f"Failed to import theme from: {file_path}")
                    
        except Exception as e:
            self.logger.error(f"Error opening theme: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open theme: {str(e)}")
    
    def save_theme(self):
        """Save current configuration as a theme."""
        try:
            # Get save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Theme",
                str(self.theme_manager.themes_dir / "custom_theme.hyprrice"),
                "HyprRice Themes (*.hyprrice);;YAML Files (*.yaml);;JSON Files (*.json)"
            )
            
            if file_path:
                # Export current config as theme
                if self.theme_manager.export_theme(self.config, file_path):
                    theme_name = Path(file_path).stem
                    self.status_label.setText(f"Saved theme: {theme_name}")
                    self.logger.info(f"Saved theme: {theme_name}")
                    
                    # Refresh themes in GUI
                    if hasattr(self.themes_tab, 'refresh_themes'):
                        self.themes_tab.refresh_themes()
                else:
                    QMessageBox.critical(self, "Error", "Failed to save theme")
                    
        except Exception as e:
            self.logger.error(f"Error saving theme: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save theme: {str(e)}")
    
    # ===== CONFIGURATION MENU ACTIONS =====
    
    def export_config(self):
        """Export current configuration to file."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Configuration",
                "hyprrice_config.yaml",
                "YAML Files (*.yaml *.yml);;JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                # Convert config to dictionary
                config_dict = self.config.to_dict()
                
                # Save based on file extension
                if file_path.lower().endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(config_dict, f, indent=2)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                
                self.status_label.setText(f"Exported configuration to: {Path(file_path).name}")
                self.logger.info(f"Exported configuration to: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export configuration: {str(e)}")
    
    def import_config(self):
        """Import configuration from file."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Configuration",
                "",
                "YAML Files (*.yaml *.yml);;JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                # Confirm import
                reply = QMessageBox.question(
                    self,
                    "Import Configuration",
                    "This will replace your current configuration. Continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Create backup first
                    self.backup_config()
                    
                    # Load config data
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if file_path.lower().endswith('.json'):
                            config_data = json.load(f)
                        else:
                            config_data = yaml.safe_load(f)
                    
                    # Update config
                    self.config.from_dict(config_data)
                    
                    # Refresh all tabs
                    self.refresh_all_tabs()
                    
                    # Update preview
                    if self.preview_window:
                        self.preview_window.update_preview()
                    
                    self.status_label.setText(f"Imported configuration from: {Path(file_path).name}")
                    self.logger.info(f"Imported configuration from: {file_path}")
                    
        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
            QMessageBox.critical(self, "Error", f"Failed to import configuration: {str(e)}")
    
    # ===== EDIT MENU ACTIONS =====
    
    def undo(self):
        """Undo the last operation."""
        try:
            if hasattr(self, 'history_manager'):
                if self.history_manager.can_undo():
                    command = self.history_manager.undo()
                    if command:
                        self.status_label.setText(f"Undone: {command.description}")
                        self.logger.info(f"Undone command: {command}")
                        
                        # Refresh GUI
                        self.refresh_all_tabs()
                        
                        # Update preview
                        if self.preview_window:
                            self.preview_window.update_preview()
                    else:
                        self.status_label.setText("Nothing to undo")
                else:
                    self.status_label.setText("Nothing to undo")
            else:
                self.status_label.setText("Undo not available")
                
        except Exception as e:
            self.logger.error(f"Error during undo: {e}")
            QMessageBox.critical(self, "Error", f"Failed to undo: {str(e)}")
    
    def redo(self):
        """Redo the last undone operation."""
        try:
            if hasattr(self, 'history_manager'):
                if self.history_manager.can_redo():
                    command = self.history_manager.redo()
                    if command:
                        self.status_label.setText(f"Redone: {command.description}")
                        self.logger.info(f"Redone command: {command}")
                        
                        # Refresh GUI
                        self.refresh_all_tabs()
                        
                        # Update preview
                        if self.preview_window:
                            self.preview_window.update_preview()
                    else:
                        self.status_label.setText("Nothing to redo")
                else:
                    self.status_label.setText("Nothing to redo")
            else:
                self.status_label.setText("Redo not available")
                
        except Exception as e:
            self.logger.error(f"Error during redo: {e}")
            QMessageBox.critical(self, "Error", f"Failed to redo: {str(e)}")
    
    def show_preferences(self):
        """Show preferences dialog."""
        try:
            dialog = PreferencesDialog(self.config, self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                # Check if security settings changed
                old_sandbox = getattr(self.config.security, 'enable_plugin_sandbox', True) if hasattr(self.config, 'security') else True
                old_level = getattr(self.config.security, 'plugin_security_level', 'medium') if hasattr(self.config, 'security') else 'medium'
                
                # Apply preferences
                self.apply_theme()
                self.refresh_all_tabs()
                
                # Check if security settings changed
                new_sandbox = getattr(self.config.security, 'enable_plugin_sandbox', True) if hasattr(self.config, 'security') else True
                new_level = getattr(self.config.security, 'plugin_security_level', 'medium') if hasattr(self.config, 'security') else 'medium'
                
                if old_sandbox != new_sandbox or old_level != new_level:
                    # Security settings changed, reload plugin manager
                    self.reload_plugin_manager_with_security_settings()
                
                self.status_label.setText("Preferences updated")
                
        except Exception as e:
            self.logger.error(f"Error showing preferences: {e}")
            QMessageBox.critical(self, "Error", f"Failed to show preferences: {str(e)}")
    
    # ===== BACKUP/RESTORE ACTIONS =====
    
    def backup_config(self):
        """Create a backup of current configuration."""
        try:
            backup_file = self.backup_manager.create_backup(self.config)
            if backup_file:
                self.status_label.setText(f"Backup created: {backup_file.name}")
                self.logger.info(f"Created backup: {backup_file}")
            else:
                QMessageBox.warning(self, "Warning", "Failed to create backup")
                
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create backup: {str(e)}")
    
    def restore_config(self):
        """Restore configuration from backup."""
        try:
            # Get list of available backups
            backups = self.backup_manager.list_backups()
            if not backups:
                QMessageBox.information(self, "No Backups", "No backups available to restore")
                return
            
            # Show backup selection dialog
            dialog = BackupSelectionDialog(backups, self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                selected_backup = dialog.get_selected_backup()
                if selected_backup:
                    # Confirm restore
                    reply = QMessageBox.question(
                        self,
                        "Restore Backup",
                        f"Restore from backup '{selected_backup.name}'?\nThis will replace your current configuration.",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # Restore backup
                        if self.backup_manager.restore_backup(selected_backup, self.config):
                            self.status_label.setText(f"Restored from: {selected_backup.name}")
                            self.logger.info(f"Restored from backup: {selected_backup}")
                            
                            # Refresh GUI
                            self.refresh_all_tabs()
                            
                            # Update preview
                            if self.preview_window:
                                self.preview_window.update_preview()
                        else:
                            QMessageBox.critical(self, "Error", "Failed to restore backup")
                            
        except Exception as e:
            self.logger.error(f"Error restoring backup: {e}")
            QMessageBox.critical(self, "Error", f"Failed to restore backup: {str(e)}")
    
    def check_dependencies(self):
        """Check system dependencies."""
        try:
            self.status_label.setText("Checking dependencies...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Run dependency check
            missing_deps = check_dependencies()
            
            self.progress_bar.setVisible(False)
            
            if missing_deps:
                deps_text = "\n".join(f"• {dep}" for dep in missing_deps)
                QMessageBox.warning(
                    self,
                    "Missing Dependencies",
                    f"The following dependencies are missing:\n\n{deps_text}\n\nPlease install them for full functionality."
                )
                self.status_label.setText(f"Missing {len(missing_deps)} dependencies")
            else:
                QMessageBox.information(
                    self,
                    "Dependencies OK",
                    "All required dependencies are installed!"
                )
                self.status_label.setText("All dependencies OK")
                
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.logger.error(f"Error checking dependencies: {e}")
            QMessageBox.critical(self, "Error", f"Failed to check dependencies: {str(e)}")
    
    # ===== UTILITY METHODS =====
    
    @profile("refresh_all_tabs")
    def refresh_all_tabs(self):
        """Refresh all tabs to reflect current configuration."""
        try:
            # Refresh each tab
            tabs = [
                self.hyprland_tab, self.waybar_tab, self.rofi_tab,
                self.notifications_tab, self.clipboard_tab, self.lockscreen_tab,
                self.themes_tab, self.settings_tab
            ]
            
            for tab in tabs:
                if hasattr(tab, 'refresh'):
                    tab.refresh()
                elif hasattr(tab, 'update_from_config'):
                    tab.update_from_config()
                    
        except Exception as e:
            self.logger.error(f"Error refreshing tabs: {e}")
    
    def auto_save(self):
        """Auto-save current configuration."""
        try:
            # Create auto-save backup
            backup_file = self.backup_manager.create_auto_backup(self.config)
            if backup_file:
                self.logger.info(f"Auto-saved configuration: {backup_file}")
            
        except Exception as e:
            self.logger.error(f"Error during auto-save: {e}")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About HyprRice",
            "HyprRice - Comprehensive Hyprland Ecosystem Ricing Tool\n\n"
            "Version: 1.0.0\n"
            "A modern GUI for customizing Hyprland and its ecosystem."
        )
    
    def show_preview(self):
        """Show preview window."""
        if not self.preview_window:
            self.preview_window = PreviewWindow(self.config)
        
        self.preview_window.show()
        self.preview_window.raise_()
        self.preview_window.update_preview()
    
    def set_theme(self, theme: str):
        """Set application theme."""
        self.config.gui.theme = theme
        self.apply_theme()
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Stop performance monitoring
        performance_monitor.stop_monitoring()
        
        # Save configuration before closing
        try:
            self.config.save()
            self.logger.info("Configuration saved on exit")
        except Exception as e:
            self.logger.error(f"Failed to save configuration on exit: {e}")
        
        event.accept() 

    def set_status(self, message):
        self.status_bar.showMessage(message, 5000) 

    @profile("load_default_plugins")
    def load_default_plugins(self):
        """Load default plugins automatically."""
        try:
            # List of default plugins to load
            default_plugins = ['terminal_theming', 'notification_theming']
            
            loaded_count = 0
            for plugin_name in default_plugins:
                try:
                    if self.plugin_manager.load_plugin(plugin_name, self):
                        loaded_count += 1
                        self.logger.info(f"Loaded default plugin: {plugin_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to load default plugin {plugin_name}: {e}")
            
            if loaded_count > 0:
                self.show_success_notification(f"Loaded {loaded_count} plugins")
                
        except Exception as e:
            self.logger.error(f"Error loading default plugins: {e}")
    
    def reload_all_plugins(self):
        """Reload all currently loaded plugins."""
        try:
            loaded_plugins = self.plugin_manager.list_loaded_plugins()
            reloaded_count = 0
            
            for plugin_name in loaded_plugins:
                try:
                    if self.plugin_manager.reload_plugin(plugin_name, self):
                        reloaded_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to reload plugin {plugin_name}: {e}")
            
            if reloaded_count > 0:
                self.show_success_notification(f"Reloaded {reloaded_count} plugins")
            else:
                self.show_warning_notification("No plugins to reload")
                
        except Exception as e:
            self.logger.error(f"Error reloading plugins: {e}")
            self.show_error_dialog("Plugin Error", f"Failed to reload plugins: {e}")
    
    def reload_plugin_manager_with_security_settings(self):
        """Reload plugin manager with updated security settings."""
        try:
            # Get current security settings
            enable_sandbox = True
            security_level = 'medium'
            
            if hasattr(self.config, 'security'):
                enable_sandbox = getattr(self.config.security, 'enable_plugin_sandbox', True)
                security_level = getattr(self.config.security, 'plugin_security_level', 'medium')
            
            # Get list of currently loaded plugins
            loaded_plugins = self.plugin_manager.list_loaded_plugins()
            
            # Create new plugin manager with updated settings
            plugins_dir = Path(__file__).parent.parent.parent / "plugins"
            self.plugin_manager = EnhancedPluginManager(
                plugins_dir=str(plugins_dir),
                enable_sandbox=enable_sandbox,
                security_level=security_level
            )
            
            # Reload previously loaded plugins
            reloaded_count = 0
            for plugin_name in loaded_plugins:
                try:
                    if self.plugin_manager.load_plugin(plugin_name, self):
                        reloaded_count += 1
                except Exception as e:
                    self.logger.warning(f"Failed to reload plugin {plugin_name} with new security settings: {e}")
            
            if reloaded_count > 0:
                self.show_success_notification(f"Reloaded {reloaded_count} plugins with updated security settings")
            else:
                self.show_warning_notification("No plugins were reloaded")
                
        except Exception as e:
            self.logger.error(f"Error reloading plugin manager: {e}")
            self.show_error_dialog("Plugin Manager Error", f"Failed to reload plugin manager: {e}")
    
    def show_plugin_manager(self):
        """Show the plugin manager dialog."""
        try:
            dialog = PluginManagerDialog(self.plugin_manager, self)
            dialog.plugin_status_changed.connect(self.on_plugin_status_changed)
            dialog.exec_()
        except Exception as e:
            self.logger.error(f"Error showing plugin manager: {e}")
            self.show_error_dialog("Plugin Manager Error", f"Failed to open plugin manager: {e}")
    
    def on_plugin_status_changed(self, plugin_name: str, action: str):
        """Handle plugin status changes."""
        self.logger.info(f"Plugin {plugin_name} {action}")
        
        # Emit plugin events to other plugins
        context = {
            'plugin_name': plugin_name,
            'action': action,
            'app': self
        }
        
        if action == 'loaded':
            self.plugin_manager.emit_event('on_plugin_loaded', context)
        elif action == 'unloaded':
            self.plugin_manager.emit_event('on_plugin_unloaded', context)
        elif action == 'configured':
            self.plugin_manager.emit_event('on_plugin_configured', context)
    
    def emit_theme_change_event(self, theme_data: Dict[str, Any]):
        """Emit theme change event to plugins."""
        context = {
            'colors': theme_data.get('colors', {}),
            'theme_data': theme_data,
            'app': self
        }
        
        self.plugin_manager.emit_event('before_theme_change', context)
        # ... apply theme ...
        self.plugin_manager.emit_event('after_theme_change', context)
    
    def emit_apply_event(self, config_data: Dict[str, Any]):
        """Emit configuration apply event to plugins."""
        context = {
            'config': config_data,
            'colors': self.config.colors.__dict__ if hasattr(self.config, 'colors') else {},
            'app': self
        }
        
        self.plugin_manager.emit_event('before_apply', context)
        # ... apply configuration ...
        self.plugin_manager.emit_event('after_apply', context) 
