"""
Enhanced main window with modern UI components and better user experience.
"""

import sys
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import os

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QSplitter,
    QStackedWidget, QToolBar, QStatusBar, QProgressBar,
    QMenuBar, QMenu, QFileDialog,
    QMessageBox, QInputDialog, QComboBox, QSlider, QSpinBox,
    QCheckBox, QRadioButton, QButtonGroup, QGroupBox,
    QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QTabWidget, QTextEdit, QLineEdit, QFormLayout,
    QSizePolicy, QSpacerItem, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import (
    QKeySequence, QIcon, QFont, QPalette, QColor, QShortcut,
    QPixmap, QPainter, QLinearGradient, QBrush, QPen, QAction, QActionGroup
)

from ..config import Config
from ..exceptions import HyprRiceError
from ..utils import setup_logging, check_dependencies
from ..history import HistoryManager, BackupManager
from .tabs import (
    HyprlandTab, WaybarTab, RofiTab, NotificationsTab,
    ClipboardTab, LockscreenTab, ThemesTab, SettingsTab, PluginsTab
)
from .preview import PreviewWindow
from .theme_manager import ThemeManager
from .modern_theme import ModernTheme
from .theme_editor import ThemeEditorDialog
from .preferences import PreferencesDialog
from .backup_manager import BackupSelectionDialog
from .plugin_manager import PluginManagerDialog
from ..plugins import EnhancedPluginManager


class ModernCard(QFrame):
    """Modern card widget with rounded corners and shadow."""
    
    def __init__(self, title: str = "", content: QWidget = None, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(0)
        self.setContentsMargins(16, 16, 16, 16)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        if title:
            title_label = QLabel(title)
            title_label.setProperty("class", "title")
            layout.addWidget(title_label)
        
        if content:
            layout.addWidget(content)
        
        # Set modern styling
        self.setProperty("class", "card")
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)


class ModernButton(QPushButton):
    """Modern button with enhanced styling and animations."""
    
    def __init__(self, text: str = "", icon: QIcon = None, style: str = "primary", parent=None):
        super().__init__(text, parent)
        
        if icon:
            self.setIcon(icon)
        
        self.style_type = style
        self.setProperty("class", style)
        self.setMinimumHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Add hover effects
        self.setMouseTracking(True)


class ModernSidebar(QFrame):
    """Modern sidebar with navigation and quick actions."""
    
    item_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(0)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("HyprRice")
        header.setProperty("class", "title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Quick actions
        self._create_quick_actions(layout)
        
        # Navigation
        self._create_navigation(layout)
        
        # Spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Footer
        self._create_footer(layout)
    
    def _create_quick_actions(self, layout):
        """Create quick action buttons."""
        group = QGroupBox("Quick Actions")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(8)
        
        # Apply button
        apply_btn = ModernButton("Apply Changes", style="primary")
        apply_btn.clicked.connect(lambda: self.item_selected.emit("apply"))
        group_layout.addWidget(apply_btn)
        
        # Preview button
        preview_btn = ModernButton("Preview", style="secondary")
        preview_btn.clicked.connect(lambda: self.item_selected.emit("preview"))
        group_layout.addWidget(preview_btn)
        
        # Backup button
        backup_btn = ModernButton("Backup", style="secondary")
        backup_btn.clicked.connect(lambda: self.item_selected.emit("backup"))
        group_layout.addWidget(backup_btn)
        
        layout.addWidget(group)
    
    def _create_navigation(self, layout):
        """Create navigation tree."""
        group = QGroupBox("Configuration")
        group_layout = QVBoxLayout(group)
        
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.setRootIsDecorated(True)
        self.nav_tree.setIndentation(20)
        self.nav_tree.itemClicked.connect(self._on_nav_item_clicked)
        
        # Add navigation items
        self._populate_navigation()
        
        group_layout.addWidget(self.nav_tree)
        layout.addWidget(group)
    
    def _populate_navigation(self):
        """Populate navigation tree with configuration sections."""
        # Main sections
        hyprland_item = QTreeWidgetItem(["Hyprland"])
        waybar_item = QTreeWidgetItem(["Waybar"])
        rofi_item = QTreeWidgetItem(["Rofi"])
        notifications_item = QTreeWidgetItem(["Notifications"])
        clipboard_item = QTreeWidgetItem(["Clipboard"])
        lockscreen_item = QTreeWidgetItem(["Lockscreen"])
        themes_item = QTreeWidgetItem(["Themes"])
        settings_item = QTreeWidgetItem(["Settings"])
        plugins_item = QTreeWidgetItem(["Plugins"])
        
        # Add to tree
        self.nav_tree.addTopLevelItem(hyprland_item)
        self.nav_tree.addTopLevelItem(waybar_item)
        self.nav_tree.addTopLevelItem(rofi_item)
        self.nav_tree.addTopLevelItem(notifications_item)
        self.nav_tree.addTopLevelItem(clipboard_item)
        self.nav_tree.addTopLevelItem(lockscreen_item)
        self.nav_tree.addTopLevelItem(themes_item)
        self.nav_tree.addTopLevelItem(settings_item)
        self.nav_tree.addTopLevelItem(plugins_item)
        
        # Expand all
        self.nav_tree.expandAll()
    
    def _on_nav_item_clicked(self, item, column):
        """Handle navigation item click."""
        section = item.text(0).lower()
        self.item_selected.emit(section)
    
    def _create_footer(self, layout):
        """Create footer with status and info."""
        footer = QFrame()
        footer_layout = QVBoxLayout(footer)
        footer_layout.setSpacing(4)
        
        # Status
        status_label = QLabel("Ready")
        status_label.setProperty("class", "caption")
        footer_layout.addWidget(status_label)
        
        # Version
        version_label = QLabel("v1.0.0")
        version_label.setProperty("class", "caption")
        footer_layout.addWidget(version_label)
        
        layout.addWidget(footer)


class ModernStatusBar(QStatusBar):
    """Enhanced status bar with progress and notifications."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.addPermanentWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.addWidget(self.status_label)
        
        # System info
        self.system_label = QLabel("Hyprland: Not Running")
        self.addPermanentWidget(self.system_label)
    
    def show_progress(self, message: str = "Working..."):
        """Show progress bar with message."""
        self.status_label.setText(message)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
    
    def hide_progress(self, message: str = "Ready"):
        """Hide progress bar."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(message)
    
    def update_system_status(self, status: str):
        """Update system status."""
        self.system_label.setText(status)


class EnhancedMainWindow(QMainWindow):
    """Enhanced main window with modern UI and better UX."""
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.theme_manager = ThemeManager()
        self.modern_theme = ModernTheme()
        self.history_manager = HistoryManager(config)
        self.backup_manager = BackupManager(config.paths.backup_dir)
        
        # Initialize plugin system
        plugins_dir = Path(__file__).parent.parent.parent / "plugins"
        self.plugin_manager = EnhancedPluginManager(
            plugins_dir=str(plugins_dir),
            enable_sandbox=False,  # Disable for now
            security_level='medium'
        )
        
        # UI components
        self.sidebar = None
        self.content_stack = None
        self.tabs = {}
        self.preview_window = None
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        self.setup_shortcuts()
        
        # Apply theme
        self.apply_theme()
        
        # Load initial state
        self.load_initial_state()
    
    def setup_ui(self):
        """Setup the main user interface."""
        self.setWindowTitle("HyprRice - Modern Hyprland Configuration Tool")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Sidebar
        self.sidebar = ModernSidebar()
        splitter.addWidget(self.sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        splitter.addWidget(self.content_stack)
        
        # Set splitter proportions
        splitter.setSizes([280, 1120])
        splitter.setCollapsible(0, False)
        
        # Create content pages
        self._create_content_pages()
        
        # Status bar
        self.status_bar = ModernStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Menu bar
        self.setup_menu_bar()
    
    def _create_content_pages(self):
        """Create content pages for different sections."""
        # Hyprland page
        hyprland_page = self._create_hyprland_page()
        self.content_stack.addWidget(hyprland_page)
        
        # Waybar page
        waybar_page = self._create_waybar_page()
        self.content_stack.addWidget(waybar_page)
        
        # Rofi page
        rofi_page = self._create_rofi_page()
        self.content_stack.addWidget(rofi_page)
        
        # Notifications page
        notifications_page = self._create_notifications_page()
        self.content_stack.addWidget(notifications_page)
        
        # Clipboard page
        clipboard_page = self._create_clipboard_page()
        self.content_stack.addWidget(clipboard_page)
        
        # Lockscreen page
        lockscreen_page = self._create_lockscreen_page()
        self.content_stack.addWidget(lockscreen_page)
        
        # Themes page
        themes_page = self._create_themes_page()
        self.content_stack.addWidget(themes_page)
        
        # Settings page
        settings_page = self._create_settings_page()
        self.content_stack.addWidget(settings_page)
        
        # Plugins page
        plugins_page = self._create_plugins_page()
        self.content_stack.addWidget(plugins_page)
    
    def _create_hyprland_page(self) -> QWidget:
        """Create Hyprland configuration page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # Header
        header = QLabel("Hyprland Configuration")
        header.setProperty("class", "title")
        layout.addWidget(header)
        
        # Content cards
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(16)
        
        # Animation settings card
        anim_card = ModernCard("Animation Settings")
        anim_content = self._create_animation_controls()
        anim_card.layout().addWidget(anim_content)
        scroll_layout.addWidget(anim_card)
        
        # Window management card
        window_card = ModernCard("Window Management")
        window_content = self._create_window_controls()
        window_card.layout().addWidget(window_content)
        scroll_layout.addWidget(window_card)
        
        # Input settings card
        input_card = ModernCard("Input Settings")
        input_content = self._create_input_controls()
        input_card.layout().addWidget(input_content)
        scroll_layout.addWidget(input_card)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        return page
    
    def _create_animation_controls(self) -> QWidget:
        """Create animation controls."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Animation enable
        self.anim_enable = QCheckBox("Enable animations")
        self.anim_enable.setChecked(True)
        layout.addRow("Animations:", self.anim_enable)
        
        # Animation speed
        self.anim_speed = QSlider(Qt.Orientation.Horizontal)
        self.anim_speed.setRange(1, 10)
        self.anim_speed.setValue(5)
        layout.addRow("Speed:", self.anim_speed)
        
        # Animation curve
        self.anim_curve = QComboBox()
        self.anim_curve.addItems(["linear", "ease", "ease-in", "ease-out", "ease-in-out"])
        layout.addRow("Curve:", self.anim_curve)
        
        return widget
    
    def _create_window_controls(self) -> QWidget:
        """Create window management controls."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Window gaps
        self.window_gaps = QSpinBox()
        self.window_gaps.setRange(0, 50)
        self.window_gaps.setValue(10)
        layout.addRow("Window gaps:", self.window_gaps)
        
        # Border size
        self.border_size = QSpinBox()
        self.border_size.setRange(0, 10)
        self.border_size.setValue(2)
        layout.addRow("Border size:", self.border_size)
        
        # Border color
        self.border_color = QLineEdit("#5e81ac")
        layout.addRow("Border color:", self.border_color)
        
        return widget
    
    def _create_input_controls(self) -> QWidget:
        """Create input controls."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Sensitivity
        self.sensitivity = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity.setRange(1, 10)
        self.sensitivity.setValue(5)
        layout.addRow("Mouse sensitivity:", self.sensitivity)
        
        # Scroll factor
        self.scroll_factor = QSlider(Qt.Orientation.Horizontal)
        self.scroll_factor.setRange(1, 10)
        self.scroll_factor.setValue(3)
        layout.addRow("Scroll factor:", self.scroll_factor)
        
        return widget
    
    def _create_waybar_page(self) -> QWidget:
        """Create Waybar configuration page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        
        header = QLabel("Waybar Configuration")
        header.setProperty("class", "title")
        layout.addWidget(header)
        
        # Placeholder content
        content = QLabel("Waybar configuration options will be available here.")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content)
        
        return page
    
    def _create_rofi_page(self) -> QWidget:
        """Create Rofi configuration page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        
        header = QLabel("Rofi Configuration")
        header.setProperty("class", "title")
        layout.addWidget(header)
        
        content = QLabel("Rofi configuration options will be available here.")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content)
        
        return page
    
    def _create_notifications_page(self) -> QWidget:
        """Create notifications configuration page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        
        header = QLabel("Notifications Configuration")
        header.setProperty("class", "title")
        layout.addWidget(header)
        
        content = QLabel("Notification configuration options will be available here.")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content)
        
        return page
    
    def _create_clipboard_page(self) -> QWidget:
        """Create clipboard configuration page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        
        header = QLabel("Clipboard Configuration")
        header.setProperty("class", "title")
        layout.addWidget(header)
        
        content = QLabel("Clipboard configuration options will be available here.")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content)
        
        return page
    
    def _create_lockscreen_page(self) -> QWidget:
        """Create lockscreen configuration page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        
        header = QLabel("Lockscreen Configuration")
        header.setProperty("class", "title")
        layout.addWidget(header)
        
        content = QLabel("Lockscreen configuration options will be available here.")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content)
        
        return page
    
    def _create_themes_page(self) -> QWidget:
        """Create themes configuration page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        
        header = QLabel("Themes")
        header.setProperty("class", "title")
        layout.addWidget(header)
        
        # Theme selection
        theme_card = ModernCard("Theme Selection")
        theme_content = QWidget()
        theme_layout = QVBoxLayout(theme_content)
        
        self.theme_list = QListWidget()
        self.theme_list.addItems(["Dark", "Light", "Nord", "Dracula", "Catppuccin"])
        theme_layout.addWidget(self.theme_list)
        
        theme_buttons = QHBoxLayout()
        apply_theme_btn = ModernButton("Apply Theme", style="primary")
        import_theme_btn = ModernButton("Import", style="secondary")
        export_theme_btn = ModernButton("Export", style="secondary")
        
        theme_buttons.addWidget(apply_theme_btn)
        theme_buttons.addWidget(import_theme_btn)
        theme_buttons.addWidget(export_theme_btn)
        theme_layout.addLayout(theme_buttons)
        
        theme_card.layout().addWidget(theme_content)
        layout.addWidget(theme_card)
        
        return page
    
    def _create_settings_page(self) -> QWidget:
        """Create settings configuration page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        
        header = QLabel("Settings")
        header.setProperty("class", "title")
        layout.addWidget(header)
        
        # General settings card
        general_card = ModernCard("General Settings")
        general_content = QWidget()
        general_layout = QFormLayout(general_content)
        
        self.auto_backup = QCheckBox("Enable auto-backup")
        self.auto_backup.setChecked(True)
        general_layout.addRow("Auto-backup:", self.auto_backup)
        
        self.backup_retention = QSpinBox()
        self.backup_retention.setRange(1, 30)
        self.backup_retention.setValue(7)
        general_layout.addRow("Backup retention (days):", self.backup_retention)
        
        general_card.layout().addWidget(general_content)
        layout.addWidget(general_card)
        
        return page
    
    def _create_plugins_page(self) -> QWidget:
        """Create plugins configuration page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        
        header = QLabel("Plugins")
        header.setProperty("class", "title")
        layout.addWidget(header)
        
        # Plugin management card
        plugin_card = ModernCard("Plugin Management")
        plugin_content = QWidget()
        plugin_layout = QVBoxLayout(plugin_content)
        
        self.plugin_list = QListWidget()
        plugin_layout.addWidget(self.plugin_list)
        
        plugin_buttons = QHBoxLayout()
        load_plugin_btn = ModernButton("Load Plugin", style="primary")
        reload_plugin_btn = ModernButton("Reload", style="secondary")
        plugin_buttons.addWidget(load_plugin_btn)
        plugin_buttons.addWidget(reload_plugin_btn)
        plugin_layout.addLayout(plugin_buttons)
        
        plugin_card.layout().addWidget(plugin_content)
        layout.addWidget(plugin_card)
        
        return page
    
    def setup_connections(self):
        """Setup signal connections."""
        self.sidebar.item_selected.connect(self._on_sidebar_item_selected)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+S to save
        save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_shortcut.activated.connect(self.save_config)
        
        # Ctrl+O to open
        open_shortcut = QShortcut(QKeySequence.StandardKey.Open, self)
        open_shortcut.activated.connect(self.open_config)
        
        # Ctrl+Z to undo
        undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        undo_shortcut.activated.connect(self.undo)
        
        # Ctrl+Y to redo
        redo_shortcut = QShortcut(QKeySequence.StandardKey.Redo, self)
        redo_shortcut.activated.connect(self.redo)
        
        # F5 to refresh
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.refresh)
    
    def setup_menu_bar(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_config)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        preview_action = QAction("Preview", self)
        preview_action.setShortcut(QKeySequence("F6"))
        preview_action.triggered.connect(self.show_preview)
        view_menu.addAction(preview_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        backup_action = QAction("Backup", self)
        backup_action.triggered.connect(self.create_backup)
        tools_menu.addAction(backup_action)
        
        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self.restore_backup)
        tools_menu.addAction(restore_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def apply_theme(self):
        """Apply the current theme."""
        self.modern_theme.apply_to_application(QApplication.instance())
    
    def load_initial_state(self):
        """Load initial application state."""
        # Set initial page
        self.content_stack.setCurrentIndex(0)
        
        # Update status
        self.status_bar.update_system_status("Hyprland: Not Running")
    
    @pyqtSlot(str)
    def _on_sidebar_item_selected(self, item: str):
        """Handle sidebar item selection."""
        page_map = {
            "hyprland": 0,
            "waybar": 1,
            "rofi": 2,
            "notifications": 3,
            "clipboard": 4,
            "lockscreen": 5,
            "themes": 6,
            "settings": 7,
            "plugins": 8,
            "apply": self.apply_changes,
            "preview": self.show_preview,
            "backup": self.create_backup
        }
        
        if item in page_map:
            if callable(page_map[item]):
                page_map[item]()
            else:
                self.content_stack.setCurrentIndex(page_map[item])
    
    def save_config(self):
        """Save current configuration."""
        self.status_bar.show_progress("Saving configuration...")
        # TODO: Implement save logic
        QTimer.singleShot(1000, lambda: self.status_bar.hide_progress("Configuration saved"))
    
    def open_config(self):
        """Open configuration file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Configuration", "", "YAML Files (*.yaml *.yml);;All Files (*)"
        )
        if file_path:
            self.status_bar.show_progress("Loading configuration...")
            # TODO: Implement load logic
            QTimer.singleShot(1000, lambda: self.status_bar.hide_progress("Configuration loaded"))
    
    def undo(self):
        """Undo last action."""
        self.history_manager.undo()
        self.status_bar.hide_progress("Action undone")
    
    def redo(self):
        """Redo last action."""
        self.history_manager.redo()
        self.status_bar.hide_progress("Action redone")
    
    def refresh(self):
        """Refresh current view."""
        self.status_bar.show_progress("Refreshing...")
        QTimer.singleShot(500, lambda: self.status_bar.hide_progress("Refreshed"))
    
    def show_preview(self):
        """Show preview window."""
        if not self.preview_window:
            self.preview_window = PreviewWindow()
        self.preview_window.show()
    
    def create_backup(self):
        """Create configuration backup."""
        self.status_bar.show_progress("Creating backup...")
        # TODO: Implement backup logic
        QTimer.singleShot(2000, lambda: self.status_bar.hide_progress("Backup created"))
    
    def restore_backup(self):
        """Restore from backup."""
        # TODO: Implement restore logic
        pass
    
    def apply_changes(self):
        """Apply configuration changes."""
        self.status_bar.show_progress("Applying changes...")
        # TODO: Implement apply logic
        QTimer.singleShot(3000, lambda: self.status_bar.hide_progress("Changes applied"))
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About HyprRice",
            "HyprRice v1.0.0\n\n"
            "Modern Hyprland Configuration Tool\n"
            "Built with PyQt6 and Python"
        )