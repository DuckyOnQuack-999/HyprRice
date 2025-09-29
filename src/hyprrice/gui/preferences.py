"""
Preferences dialog for HyprRice
"""

from typing import Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLineEdit, QSpinBox, QCheckBox, QPushButton,
    QLabel, QComboBox, QGroupBox, QSlider, QFileDialog
)
from PyQt6.QtCore import Qt


class PreferencesDialog(QDialog):
    """Dialog for editing application preferences."""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.widgets = {}
        
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
        self.load_preferences()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Tab widget for different preference categories
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_general_tab()
        self.create_gui_tab()
        self.create_paths_tab()
        self.create_security_tab()
        self.create_advanced_tab()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_preferences)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """Create the general preferences tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Auto-save group
        autosave_group = QGroupBox("Auto-Save")
        autosave_layout = QFormLayout(autosave_group)
        
        self.widgets['auto_save'] = QCheckBox()
        autosave_layout.addRow("Enable Auto-Save:", self.widgets['auto_save'])
        
        self.widgets['auto_save_interval'] = QSpinBox()
        self.widgets['auto_save_interval'].setRange(30, 3600)
        self.widgets['auto_save_interval'].setSuffix(" seconds")
        autosave_layout.addRow("Auto-Save Interval:", self.widgets['auto_save_interval'])
        
        layout.addWidget(autosave_group)
        
        # Backup group
        backup_group = QGroupBox("Backups")
        backup_layout = QFormLayout(backup_group)
        
        self.widgets['auto_backup'] = QCheckBox()
        backup_layout.addRow("Auto Backup:", self.widgets['auto_backup'])
        
        self.widgets['max_backups'] = QSpinBox()
        self.widgets['max_backups'].setRange(1, 100)
        backup_layout.addRow("Max Backups:", self.widgets['max_backups'])
        
        layout.addWidget(backup_group)
        
        # Startup group
        startup_group = QGroupBox("Startup")
        startup_layout = QFormLayout(startup_group)
        
        self.widgets['check_deps_on_startup'] = QCheckBox()
        startup_layout.addRow("Check Dependencies on Startup:", self.widgets['check_deps_on_startup'])
        
        self.widgets['restore_window_state'] = QCheckBox()
        startup_layout.addRow("Restore Window State:", self.widgets['restore_window_state'])
        
        layout.addWidget(startup_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "General")
    
    def create_gui_tab(self):
        """Create the GUI preferences tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        self.widgets['theme'] = QComboBox()
        self.widgets['theme'].addItems(["auto", "dark", "light"])
        appearance_layout.addRow("Theme:", self.widgets['theme'])
        
        self.widgets['font_size'] = QSpinBox()
        self.widgets['font_size'].setRange(8, 20)
        appearance_layout.addRow("Font Size:", self.widgets['font_size'])
        
        layout.addWidget(appearance_group)
        
        # Window group
        window_group = QGroupBox("Window")
        window_layout = QFormLayout(window_group)
        
        self.widgets['window_width'] = QSpinBox()
        self.widgets['window_width'].setRange(800, 2000)
        window_layout.addRow("Window Width:", self.widgets['window_width'])
        
        self.widgets['window_height'] = QSpinBox()
        self.widgets['window_height'].setRange(600, 1500)
        window_layout.addRow("Window Height:", self.widgets['window_height'])
        
        # Wayland-safe rendering mode
        self.widgets['wayland_safe_mode'] = QCheckBox("Enable Wayland-safe rendering mode")
        self.widgets['wayland_safe_mode'].setToolTip("Improves compatibility with Wayland compositors")
        window_layout.addRow(self.widgets['wayland_safe_mode'])
        
        # Reset UI button
        self.reset_ui_button = QPushButton("Reset UI")
        self.reset_ui_button.setToolTip("Clear all styles and reset UI to default state")
        self.reset_ui_button.clicked.connect(self.reset_ui)
        window_layout.addRow("UI Reset:", self.reset_ui_button)
        
        self.widgets['remember_geometry'] = QCheckBox()
        window_layout.addRow("Remember Window Size:", self.widgets['remember_geometry'])
        
        layout.addWidget(window_group)
        
        # Preview group
        preview_group = QGroupBox("Preview")
        preview_layout = QFormLayout(preview_group)
        
        self.widgets['enable_live_preview'] = QCheckBox()
        preview_layout.addRow("Enable Live Preview:", self.widgets['enable_live_preview'])
        
        self.widgets['preview_update_delay'] = QSpinBox()
        self.widgets['preview_update_delay'].setRange(100, 2000)
        self.widgets['preview_update_delay'].setSuffix(" ms")
        preview_layout.addRow("Preview Update Delay:", self.widgets['preview_update_delay'])
        
        layout.addWidget(preview_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Interface")
    
    def create_paths_tab(self):
        """Create the paths preferences tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Config paths group
        config_group = QGroupBox("Configuration Paths")
        config_layout = QFormLayout(config_group)
        
        # Hyprland config path
        hyprland_layout = QHBoxLayout()
        self.widgets['hyprland_config_path'] = QLineEdit()
        hyprland_layout.addWidget(self.widgets['hyprland_config_path'])
        
        hyprland_browse = QPushButton("Browse...")
        hyprland_browse.clicked.connect(lambda: self.browse_file('hyprland_config_path'))
        hyprland_layout.addWidget(hyprland_browse)
        
        hyprland_widget = QWidget()
        hyprland_widget.setLayout(hyprland_layout)
        config_layout.addRow("Hyprland Config:", hyprland_widget)
        
        # Waybar config path
        waybar_layout = QHBoxLayout()
        self.widgets['waybar_config_path'] = QLineEdit()
        waybar_layout.addWidget(self.widgets['waybar_config_path'])
        
        waybar_browse = QPushButton("Browse...")
        waybar_browse.clicked.connect(lambda: self.browse_file('waybar_config_path'))
        waybar_layout.addWidget(waybar_browse)
        
        waybar_widget = QWidget()
        waybar_widget.setLayout(waybar_layout)
        config_layout.addRow("Waybar Config:", waybar_widget)
        
        layout.addWidget(config_group)
        
        # Data paths group
        data_group = QGroupBox("Data Paths")
        data_layout = QFormLayout(data_group)
        
        # Themes directory
        themes_layout = QHBoxLayout()
        self.widgets['themes_dir'] = QLineEdit()
        themes_layout.addWidget(self.widgets['themes_dir'])
        
        themes_browse = QPushButton("Browse...")
        themes_browse.clicked.connect(lambda: self.browse_directory('themes_dir'))
        themes_layout.addWidget(themes_browse)
        
        themes_widget = QWidget()
        themes_widget.setLayout(themes_layout)
        data_layout.addRow("Themes Directory:", themes_widget)
        
        # Backups directory
        backups_layout = QHBoxLayout()
        self.widgets['backups_dir'] = QLineEdit()
        backups_layout.addWidget(self.widgets['backups_dir'])
        
        backups_browse = QPushButton("Browse...")
        backups_browse.clicked.connect(lambda: self.browse_directory('backups_dir'))
        backups_layout.addWidget(backups_browse)
        
        backups_widget = QWidget()
        backups_widget.setLayout(backups_layout)
        data_layout.addRow("Backups Directory:", backups_widget)
        
        layout.addWidget(data_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Paths")
    
    def create_security_tab(self):
        """Create the security preferences tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Plugin Security group
        plugin_group = QGroupBox("Plugin Security")
        plugin_layout = QFormLayout(plugin_group)
        
        self.widgets['enable_plugin_sandbox'] = QCheckBox()
        plugin_layout.addRow("Enable Plugin Sandboxing:", self.widgets['enable_plugin_sandbox'])
        
        self.widgets['plugin_security_level'] = QComboBox()
        self.widgets['plugin_security_level'].addItems(["strict", "medium", "relaxed"])
        plugin_layout.addRow("Security Level:", self.widgets['plugin_security_level'])
        
        self.widgets['plugin_auto_load'] = QCheckBox()
        plugin_layout.addRow("Auto-load Plugins:", self.widgets['plugin_auto_load'])
        
        self.widgets['plugin_trust_policy'] = QComboBox()
        self.widgets['plugin_trust_policy'].addItems(["signed-only", "local-only", "all"])
        plugin_layout.addRow("Trust Policy:", self.widgets['plugin_trust_policy'])
        
        layout.addWidget(plugin_group)
        
        # Input Validation group
        validation_group = QGroupBox("Input Validation")
        validation_layout = QFormLayout(validation_group)
        
        self.widgets['strict_path_validation'] = QCheckBox()
        validation_layout.addRow("Strict Path Validation:", self.widgets['strict_path_validation'])
        
        self.widgets['sanitize_commands'] = QCheckBox()
        validation_layout.addRow("Sanitize Commands:", self.widgets['sanitize_commands'])
        
        self.widgets['validate_theme_data'] = QCheckBox()
        validation_layout.addRow("Validate Theme Data:", self.widgets['validate_theme_data'])
        
        layout.addWidget(validation_group)
        
        # File Security group
        file_group = QGroupBox("File Security")
        file_layout = QFormLayout(file_group)
        
        self.widgets['secure_file_operations'] = QCheckBox()
        file_layout.addRow("Secure File Operations:", self.widgets['secure_file_operations'])
        
        self.widgets['backup_encryption'] = QCheckBox()
        file_layout.addRow("Encrypt Backups:", self.widgets['backup_encryption'])
        
        self.widgets['config_access_logging'] = QCheckBox()
        file_layout.addRow("Log Configuration Access:", self.widgets['config_access_logging'])
        
        layout.addWidget(file_group)
        
        # Security Info
        info_label = QLabel(
            "Security settings help protect your system from malicious plugins and "
            "configuration files. Higher security levels provide better protection "
            "but may limit functionality."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Security")
    
    def create_advanced_tab(self):
        """Create the advanced preferences tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Logging group
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout(logging_group)
        
        self.widgets['log_level'] = QComboBox()
        self.widgets['log_level'].addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        logging_layout.addRow("Log Level:", self.widgets['log_level'])
        
        self.widgets['enable_file_logging'] = QCheckBox()
        logging_layout.addRow("Enable File Logging:", self.widgets['enable_file_logging'])
        
        layout.addWidget(logging_group)
        
        # Performance group
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout(performance_group)
        
        self.widgets['enable_animations'] = QCheckBox()
        performance_layout.addRow("Enable GUI Animations:", self.widgets['enable_animations'])
        
        self.widgets['worker_threads'] = QSpinBox()
        self.widgets['worker_threads'].setRange(1, 8)
        performance_layout.addRow("Worker Threads:", self.widgets['worker_threads'])
        
        layout.addWidget(performance_group)
        
        # Debug group
        debug_group = QGroupBox("Debug")
        debug_layout = QFormLayout(debug_group)
        
        self.widgets['debug_mode'] = QCheckBox()
        debug_layout.addRow("Debug Mode:", self.widgets['debug_mode'])
        
        self.widgets['verbose_output'] = QCheckBox()
        debug_layout.addRow("Verbose Output:", self.widgets['verbose_output'])
        
        layout.addWidget(debug_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Advanced")
    
    def load_preferences(self):
        """Load current preferences into widgets."""
        try:
            # General preferences
            if hasattr(self.config, 'gui'):
                gui_config = self.config.gui
                
                self.widgets['auto_save'].setChecked(getattr(gui_config, 'auto_save', True))
                self.widgets['auto_save_interval'].setValue(getattr(gui_config, 'auto_save_interval', 300))
                self.widgets['theme'].setCurrentText(getattr(gui_config, 'theme', 'auto'))
                self.widgets['font_size'].setValue(getattr(gui_config, 'font_size', 10))
                self.widgets['window_width'].setValue(getattr(gui_config, 'window_width', 1200))
                self.widgets['window_height'].setValue(getattr(gui_config, 'window_height', 800))
                self.widgets['remember_geometry'].setChecked(getattr(gui_config, 'remember_geometry', True))
                self.widgets['enable_live_preview'].setChecked(getattr(gui_config, 'enable_live_preview', True))
                self.widgets['preview_update_delay'].setValue(getattr(gui_config, 'preview_update_delay', 500))
                self.widgets['wayland_safe_mode'].setChecked(getattr(gui_config, 'wayland_safe_mode', True))
            
            # Paths
            if hasattr(self.config, 'paths'):
                paths_config = self.config.paths
                
                self.widgets['hyprland_config_path'].setText(getattr(paths_config, 'hyprland_config', ''))
                self.widgets['waybar_config_path'].setText(getattr(paths_config, 'waybar_config', ''))
                self.widgets['themes_dir'].setText(getattr(paths_config, 'themes_dir', ''))
                self.widgets['backups_dir'].setText(getattr(paths_config, 'backups_dir', ''))
            
            # Advanced
            if hasattr(self.config, 'general'):
                general_config = self.config.general
                
                self.widgets['auto_backup'].setChecked(getattr(general_config, 'auto_backup', True))
                self.widgets['max_backups'].setValue(getattr(general_config, 'max_backups', 10))
                self.widgets['check_deps_on_startup'].setChecked(getattr(general_config, 'check_deps_on_startup', True))
                self.widgets['restore_window_state'].setChecked(getattr(general_config, 'restore_window_state', True))
                self.widgets['log_level'].setCurrentText(getattr(general_config, 'log_level', 'INFO'))
                self.widgets['enable_file_logging'].setChecked(getattr(general_config, 'enable_file_logging', True))
                self.widgets['enable_animations'].setChecked(getattr(general_config, 'enable_animations', True))
                self.widgets['worker_threads'].setValue(getattr(general_config, 'worker_threads', 2))
                self.widgets['debug_mode'].setChecked(getattr(general_config, 'debug_mode', False))
                self.widgets['verbose_output'].setChecked(getattr(general_config, 'verbose_output', False))
            
            # Security preferences
            if hasattr(self.config, 'security'):
                security_config = self.config.security
                
                self.widgets['enable_plugin_sandbox'].setChecked(getattr(security_config, 'enable_plugin_sandbox', True))
                self.widgets['plugin_security_level'].setCurrentText(getattr(security_config, 'plugin_security_level', 'medium'))
                self.widgets['plugin_auto_load'].setChecked(getattr(security_config, 'plugin_auto_load', True))
                self.widgets['plugin_trust_policy'].setCurrentText(getattr(security_config, 'plugin_trust_policy', 'local-only'))
                self.widgets['strict_path_validation'].setChecked(getattr(security_config, 'strict_path_validation', True))
                self.widgets['sanitize_commands'].setChecked(getattr(security_config, 'sanitize_commands', True))
                self.widgets['validate_theme_data'].setChecked(getattr(security_config, 'validate_theme_data', True))
                self.widgets['secure_file_operations'].setChecked(getattr(security_config, 'secure_file_operations', True))
                self.widgets['backup_encryption'].setChecked(getattr(security_config, 'backup_encryption', False))
                self.widgets['config_access_logging'].setChecked(getattr(security_config, 'config_access_logging', False))
            else:
                # Set defaults if security config doesn't exist
                self.widgets['enable_plugin_sandbox'].setChecked(True)
                self.widgets['plugin_security_level'].setCurrentText('medium')
                self.widgets['plugin_auto_load'].setChecked(True)
                self.widgets['plugin_trust_policy'].setCurrentText('local-only')
                self.widgets['strict_path_validation'].setChecked(True)
                self.widgets['sanitize_commands'].setChecked(True)
                self.widgets['validate_theme_data'].setChecked(True)
                self.widgets['secure_file_operations'].setChecked(True)
                self.widgets['backup_encryption'].setChecked(False)
                self.widgets['config_access_logging'].setChecked(False)
                
        except Exception as e:
            print(f"Error loading preferences: {e}")
    
    def apply_preferences(self):
        """Apply current preferences to config."""
        try:
            # GUI preferences
            if hasattr(self.config, 'gui'):
                gui_config = self.config.gui
                
                gui_config.auto_save = self.widgets['auto_save'].isChecked()
                gui_config.auto_save_interval = self.widgets['auto_save_interval'].value()
                gui_config.theme = self.widgets['theme'].currentText()
                gui_config.font_size = self.widgets['font_size'].value()
                gui_config.window_width = self.widgets['window_width'].value()
                gui_config.window_height = self.widgets['window_height'].value()
                gui_config.remember_geometry = self.widgets['remember_geometry'].isChecked()
                gui_config.enable_live_preview = self.widgets['enable_live_preview'].isChecked()
                gui_config.preview_update_delay = self.widgets['preview_update_delay'].value()
                gui_config.wayland_safe_mode = self.widgets['wayland_safe_mode'].isChecked()
            
            # Paths
            if hasattr(self.config, 'paths'):
                paths_config = self.config.paths
                
                paths_config.hyprland_config = self.widgets['hyprland_config_path'].text()
                paths_config.waybar_config = self.widgets['waybar_config_path'].text()
                paths_config.themes_dir = self.widgets['themes_dir'].text()
                paths_config.backups_dir = self.widgets['backups_dir'].text()
            
            # General/Advanced
            if hasattr(self.config, 'general'):
                general_config = self.config.general
                
                general_config.auto_backup = self.widgets['auto_backup'].isChecked()
                general_config.max_backups = self.widgets['max_backups'].value()
                general_config.check_deps_on_startup = self.widgets['check_deps_on_startup'].isChecked()
                general_config.restore_window_state = self.widgets['restore_window_state'].isChecked()
                general_config.log_level = self.widgets['log_level'].currentText()
                general_config.enable_file_logging = self.widgets['enable_file_logging'].isChecked()
                general_config.enable_animations = self.widgets['enable_animations'].isChecked()
                general_config.worker_threads = self.widgets['worker_threads'].value()
                general_config.debug_mode = self.widgets['debug_mode'].isChecked()
                general_config.verbose_output = self.widgets['verbose_output'].isChecked()
            
            # Security preferences
            if not hasattr(self.config, 'security'):
                # Create security config if it doesn't exist
                from types import SimpleNamespace
                self.config.security = SimpleNamespace()
            
            security_config = self.config.security
            
            security_config.enable_plugin_sandbox = self.widgets['enable_plugin_sandbox'].isChecked()
            security_config.plugin_security_level = self.widgets['plugin_security_level'].currentText()
            security_config.plugin_auto_load = self.widgets['plugin_auto_load'].isChecked()
            security_config.plugin_trust_policy = self.widgets['plugin_trust_policy'].currentText()
            security_config.strict_path_validation = self.widgets['strict_path_validation'].isChecked()
            security_config.sanitize_commands = self.widgets['sanitize_commands'].isChecked()
            security_config.validate_theme_data = self.widgets['validate_theme_data'].isChecked()
            security_config.secure_file_operations = self.widgets['secure_file_operations'].isChecked()
            security_config.backup_encryption = self.widgets['backup_encryption'].isChecked()
            security_config.config_access_logging = self.widgets['config_access_logging'].isChecked()
            
            # Save config
            if hasattr(self.config, 'save'):
                self.config.save()
                
        except Exception as e:
            print(f"Error applying preferences: {e}")
    
    def browse_file(self, widget_key: str):
        """Browse for a file."""
        current_path = self.widgets[widget_key].text()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            current_path,
            "All Files (*)"
        )
        
        if file_path:
            self.widgets[widget_key].setText(file_path)
    
    def browse_directory(self, widget_key: str):
        """Browse for a directory."""
        current_path = self.widgets[widget_key].text()
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            current_path
        )
        
        if directory:
            self.widgets[widget_key].setText(directory)
    
    def reset_ui(self):
        """Reset UI to default state."""
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from ..utils import trace_ui_event
        
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Reset UI",
            "This will clear all custom styles and reset the UI to default state. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                app = QApplication.instance()
                if app:
                    # Clear all stylesheets
                    app.setUpdatesEnabled(False)
                    app.style().unpolish(app)
                    app.setStyleSheet("")
                    app.style().polish(app)
                    app.updateGeometry()
                    app.adjustSize()
                    app.setUpdatesEnabled(True)
                    app.repaint()
                    
                    trace_ui_event("ui_reset", "PreferencesDialog", "UI reset to default")
                    
                    QMessageBox.information(
                        self,
                        "UI Reset",
                        "UI has been reset to default state."
                    )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Reset Error",
                    f"Failed to reset UI: {str(e)}"
                )
    
    def accept(self):
        """Accept dialog and apply preferences."""
        self.apply_preferences()
        super().accept()
