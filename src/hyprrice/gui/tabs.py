from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QCheckBox, QDoubleSpinBox, QComboBox, QSpinBox, QLineEdit, QPushButton, QColorDialog, QHBoxLayout, QMessageBox, QFileDialog
from PyQt5.QtCore import pyqtSignal
from ..hyprland.animations import AnimationManager
from ..hyprland.windows import WindowManager
from ..utils import backup_file, restore_file, parse_hyprland_config, write_hyprland_config
from ..plugins import PluginManager
import os
import copy
import json

# Each tab emits config_changed when its config is modified

class HyprlandTab(QWidget):
    def __init__(self, config, preview_window=None):
        super().__init__()
        self.config = config
        self.preview_window = preview_window
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)

        # Animations
        self.animations_enabled = QCheckBox()
        self.animations_enabled.setChecked(self.config.hyprland.animations_enabled)
        self.animations_enabled.toggled.connect(self._on_change)
        form.addRow("Enable Animations", self.animations_enabled)

        self.animation_duration = QDoubleSpinBox()
        self.animation_duration.setRange(0.1, 5.0)
        self.animation_duration.setValue(self.config.hyprland.animation_duration)
        self.animation_duration.setSingleStep(0.1)
        self.animation_duration.valueChanged.connect(self._on_change)
        form.addRow("Animation Duration (s)", self.animation_duration)

        self.animation_curve = QComboBox()
        self.animation_curve.addItems(["linear", "ease-out", "ease-in", "ease-in-out"])
        self.animation_curve.setCurrentText(self.config.hyprland.animation_curve)
        self.animation_curve.currentTextChanged.connect(self._on_change)
        form.addRow("Animation Curve", self.animation_curve)

        # Window Management
        self.window_opacity = QDoubleSpinBox()
        self.window_opacity.setRange(0.0, 1.0)
        self.window_opacity.setValue(self.config.hyprland.window_opacity)
        self.window_opacity.setSingleStep(0.05)
        self.window_opacity.valueChanged.connect(self._on_change)
        form.addRow("Window Opacity", self.window_opacity)

        self.border_size = QSpinBox()
        self.border_size.setRange(0, 20)
        self.border_size.setValue(self.config.hyprland.border_size)
        self.border_size.valueChanged.connect(self._on_change)
        form.addRow("Border Size", self.border_size)

        # Border Color
        color_layout = QHBoxLayout()
        self.border_color = QLineEdit(self.config.hyprland.border_color)
        self.border_color.textChanged.connect(self._on_change)
        color_layout.addWidget(self.border_color)
        color_btn = QPushButton("Pick Color")
        color_btn.clicked.connect(self._pick_border_color)
        color_layout.addWidget(color_btn)
        form.addRow("Border Color", color_layout)

        self.gaps_in = QSpinBox()
        self.gaps_in.setRange(0, 50)
        self.gaps_in.setValue(self.config.hyprland.gaps_in)
        self.gaps_in.valueChanged.connect(self._on_change)
        form.addRow("Inner Gaps", self.gaps_in)

        self.gaps_out = QSpinBox()
        self.gaps_out.setRange(0, 50)
        self.gaps_out.setValue(self.config.hyprland.gaps_out)
        self.gaps_out.valueChanged.connect(self._on_change)
        form.addRow("Outer Gaps", self.gaps_out)

        self.blur_enabled = QCheckBox()
        self.blur_enabled.setChecked(self.config.hyprland.blur_enabled)
        self.blur_enabled.toggled.connect(self._on_change)
        form.addRow("Enable Blur", self.blur_enabled)

        # Save button (for demonstration)
        save_btn = QPushButton("Save Hyprland Settings")
        save_btn.clicked.connect(self._save_to_config)
        layout.addWidget(save_btn)
        # Add Apply and Rollback buttons
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply to System")
        apply_btn.clicked.connect(self._apply_to_system)
        rollback_btn = QPushButton("Rollback")
        rollback_btn.clicked.connect(self._rollback_config)
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(rollback_btn)
        layout.addLayout(btn_layout)

    def _pick_border_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.border_color.setText(color.name())
            self._on_change()

    def _on_change(self):
        if self.preview_window:
            self.preview_window.update_preview()

    def _save_to_config(self):
        self.config.hyprland.animations_enabled = self.animations_enabled.isChecked()
        self.config.hyprland.animation_duration = self.animation_duration.value()
        self.config.hyprland.animation_curve = self.animation_curve.currentText()
        self.config.hyprland.window_opacity = self.window_opacity.value()
        self.config.hyprland.border_size = self.border_size.value()
        self.config.hyprland.border_color = self.border_color.text()
        self.config.hyprland.gaps_in = self.gaps_in.value()
        self.config.hyprland.gaps_out = self.gaps_out.value()
        self.config.hyprland.blur_enabled = self.blur_enabled.isChecked()
        self.config.save()
        if self.preview_window:
            self.preview_window.update_preview()

    def _apply_to_system(self):
        try:
            config_path = self.config.paths.hyprland_config
            backup_dir = self.config.paths.backup_dir
            # Backup current config
            backup_file(config_path, backup_dir)
            # Apply settings using managers (stub calls for now)
            anim_mgr = AnimationManager(config_path)
            win_mgr = WindowManager(config_path)
            anim_mgr.apply_animations(self.config.hyprland.__dict__)
            win_mgr.apply_window_config(self.config.hyprland.__dict__)
            # Write config to file (mock: just write current config as a section)
            sections = parse_hyprland_config(config_path)
            # For demo, update general section with some values
            sections['general'] = [
                f"animations_enabled={self.config.hyprland.animations_enabled}",
                f"animation_duration={self.config.hyprland.animation_duration}",
                f"animation_curve={self.config.hyprland.animation_curve}",
                f"window_opacity={self.config.hyprland.window_opacity}",
                f"border_size={self.config.hyprland.border_size}",
                f"border_color={self.config.hyprland.border_color}",
                f"gaps_in={self.config.hyprland.gaps_in}",
                f"gaps_out={self.config.hyprland.gaps_out}",
                f"blur_enabled={self.config.hyprland.blur_enabled}",
            ]
            write_hyprland_config(config_path, sections)
            QMessageBox.information(self, "Apply Success", "Hyprland config applied and backed up.")
        except Exception as e:
            QMessageBox.critical(self, "Apply Failed", f"Failed to apply config: {e}")

    def _rollback_config(self):
        try:
            config_path = self.config.paths.hyprland_config
            backup_dir = self.config.paths.backup_dir
            # Find latest backup
            backups = os.listdir(backup_dir)
            backups = [b for b in backups if b.endswith(os.path.basename(config_path))]
            if not backups:
                QMessageBox.warning(self, "No Backups", "No backups found to rollback.")
                return
            latest_backup = sorted(backups)[-1]
            restore_file(os.path.join(backup_dir, latest_backup), config_path)
            QMessageBox.information(self, "Rollback Success", "Hyprland config restored from backup.")
        except Exception as e:
            QMessageBox.critical(self, "Rollback Failed", f"Failed to rollback config: {e}")

class WaybarTab(QWidget):
    def __init__(self, config, preview_window=None):
        super().__init__()
        self.config = config
        self.preview_window = preview_window
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        self.position = QComboBox()
        self.position.addItems(["top", "bottom", "left", "right"])
        self.position.setCurrentText(self.config.waybar.position)
        self.position.currentTextChanged.connect(self._on_change)
        form.addRow("Position", self.position)
        self.height = QSpinBox()
        self.height.setRange(10, 100)
        self.height.setValue(self.config.waybar.height)
        self.height.valueChanged.connect(self._on_change)
        form.addRow("Height", self.height)
        self.background_color = QLineEdit(self.config.waybar.background_color)
        self.background_color.textChanged.connect(self._on_change)
        form.addRow("Background Color", self.background_color)
        self.text_color = QLineEdit(self.config.waybar.text_color)
        self.text_color.textChanged.connect(self._on_change)
        form.addRow("Text Color", self.text_color)
        self.font_family = QLineEdit(self.config.waybar.font_family)
        self.font_family.textChanged.connect(self._on_change)
        form.addRow("Font Family", self.font_family)
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 32)
        self.font_size.setValue(self.config.waybar.font_size)
        self.font_size.valueChanged.connect(self._on_change)
        form.addRow("Font Size", self.font_size)
        self.modules = QLineEdit(", ".join(self.config.waybar.modules))
        self.modules.textChanged.connect(self._on_change)
        form.addRow("Modules (comma separated)", self.modules)
        save_btn = QPushButton("Save Waybar Settings")
        save_btn.clicked.connect(self._save_to_config)
        layout.addWidget(save_btn)
    def _on_change(self):
        if self.preview_window:
            self.preview_window.update_preview()
    def _save_to_config(self):
        self.config.waybar.position = self.position.currentText()
        self.config.waybar.height = self.height.value()
        self.config.waybar.background_color = self.background_color.text()
        self.config.waybar.text_color = self.text_color.text()
        self.config.waybar.font_family = self.font_family.text()
        self.config.waybar.font_size = self.font_size.value()
        self.config.waybar.modules = [m.strip() for m in self.modules.text().split(",") if m.strip()]
        self.config.save()
        if self.preview_window:
            self.preview_window.update_preview()

class RofiTab(QWidget):
    def __init__(self, config, preview_window=None):
        super().__init__()
        self.config = config
        self.preview_window = preview_window
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        self.theme = QLineEdit(self.config.rofi.theme)
        self.theme.textChanged.connect(self._on_change)
        form.addRow("Theme", self.theme)
        self.width = QSpinBox()
        self.width.setRange(10, 100)
        self.width.setValue(self.config.rofi.width)
        self.width.valueChanged.connect(self._on_change)
        form.addRow("Width (%)", self.width)
        self.location = QComboBox()
        self.location.addItems(["center", "top", "bottom", "left", "right"])
        self.location.setCurrentText(self.config.rofi.location)
        self.location.currentTextChanged.connect(self._on_change)
        form.addRow("Location", self.location)
        self.background_color = QLineEdit(self.config.rofi.background_color)
        self.background_color.textChanged.connect(self._on_change)
        form.addRow("Background Color", self.background_color)
        self.text_color = QLineEdit(self.config.rofi.text_color)
        self.text_color.textChanged.connect(self._on_change)
        form.addRow("Text Color", self.text_color)
        self.border_color = QLineEdit(self.config.rofi.border_color)
        self.border_color.textChanged.connect(self._on_change)
        form.addRow("Border Color", self.border_color)
        self.font_family = QLineEdit(self.config.rofi.font_family)
        self.font_family.textChanged.connect(self._on_change)
        form.addRow("Font Family", self.font_family)
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 32)
        self.font_size.setValue(self.config.rofi.font_size)
        self.font_size.valueChanged.connect(self._on_change)
        form.addRow("Font Size", self.font_size)
        save_btn = QPushButton("Save Rofi Settings")
        save_btn.clicked.connect(self._save_to_config)
        layout.addWidget(save_btn)
    def _on_change(self):
        if self.preview_window:
            self.preview_window.update_preview()
    def _save_to_config(self):
        self.config.rofi.theme = self.theme.text()
        self.config.rofi.width = self.width.value()
        self.config.rofi.location = self.location.currentText()
        self.config.rofi.background_color = self.background_color.text()
        self.config.rofi.text_color = self.text_color.text()
        self.config.rofi.border_color = self.border_color.text()
        self.config.rofi.font_family = self.font_family.text()
        self.config.rofi.font_size = self.font_size.value()
        self.config.save()
        if self.preview_window:
            self.preview_window.update_preview()

class NotificationsTab(QWidget):
    def __init__(self, config, preview_window=None):
        super().__init__()
        self.config = config
        self.preview_window = preview_window
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        self.daemon = QComboBox()
        self.daemon.addItems(["dunst", "mako"])
        self.daemon.setCurrentText(self.config.notifications.daemon)
        self.daemon.currentTextChanged.connect(self._on_change)
        form.addRow("Daemon", self.daemon)
        self.position = QLineEdit(self.config.notifications.position)
        self.position.textChanged.connect(self._on_change)
        form.addRow("Position", self.position)
        self.timeout = QSpinBox()
        self.timeout.setRange(100, 30000)
        self.timeout.setValue(self.config.notifications.timeout)
        self.timeout.valueChanged.connect(self._on_change)
        form.addRow("Timeout (ms)", self.timeout)
        self.background_color = QLineEdit(self.config.notifications.background_color)
        self.background_color.textChanged.connect(self._on_change)
        form.addRow("Background Color", self.background_color)
        self.text_color = QLineEdit(self.config.notifications.text_color)
        self.text_color.textChanged.connect(self._on_change)
        form.addRow("Text Color", self.text_color)
        self.border_color = QLineEdit(self.config.notifications.border_color)
        self.border_color.textChanged.connect(self._on_change)
        form.addRow("Border Color", self.border_color)
        self.font_family = QLineEdit(self.config.notifications.font_family)
        self.font_family.textChanged.connect(self._on_change)
        form.addRow("Font Family", self.font_family)
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 32)
        self.font_size.setValue(self.config.notifications.font_size)
        self.font_size.valueChanged.connect(self._on_change)
        form.addRow("Font Size", self.font_size)
        save_btn = QPushButton("Save Notification Settings")
        save_btn.clicked.connect(self._save_to_config)
        layout.addWidget(save_btn)
    def _on_change(self):
        if self.preview_window:
            self.preview_window.update_preview()
    def _save_to_config(self):
        self.config.notifications.daemon = self.daemon.currentText()
        self.config.notifications.position = self.position.text()
        self.config.notifications.timeout = self.timeout.value()
        self.config.notifications.background_color = self.background_color.text()
        self.config.notifications.text_color = self.text_color.text()
        self.config.notifications.border_color = self.border_color.text()
        self.config.notifications.font_family = self.font_family.text()
        self.config.notifications.font_size = self.font_size.value()
        self.config.save()
        if self.preview_window:
            self.preview_window.update_preview()

class ClipboardTab(QWidget):
    config_changed = pyqtSignal()
    
    def __init__(self, config, preview_window=None):
        super().__init__()
        self.config = config
        self.preview_window = preview_window
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        
        # Manager selection
        self.manager = QComboBox()
        self.manager.addItems(["cliphist", "wl-clipboard", "clipman"])
        self.manager.setCurrentText(self.config.clipboard.manager)
        self.manager.currentTextChanged.connect(self._on_change)
        form.addRow("Manager", self.manager)
        
        # History size
        self.history_size = QSpinBox()
        self.history_size.setRange(10, 10000)
        self.history_size.setValue(self.config.clipboard.history_size)
        self.history_size.valueChanged.connect(self._on_change)
        form.addRow("History Size", self.history_size)
        
        # Max item size
        self.max_item_size = QSpinBox()
        self.max_item_size.setRange(64, 8192)
        self.max_item_size.setSuffix(" KB")
        self.max_item_size.setValue(self.config.clipboard.max_item_size)
        self.max_item_size.valueChanged.connect(self._on_change)
        form.addRow("Max Item Size", self.max_item_size)
        
        # Enable images
        self.enable_images = QCheckBox()
        self.enable_images.setChecked(self.config.clipboard.enable_images)
        self.enable_images.toggled.connect(self._on_change)
        form.addRow("Enable Images", self.enable_images)
        
        # Primary selection
        self.enable_primary = QCheckBox()
        self.enable_primary.setChecked(self.config.clipboard.enable_primary_selection)
        self.enable_primary.toggled.connect(self._on_change)
        form.addRow("Primary Selection", self.enable_primary)
        
        # Exclude patterns
        self.exclude_patterns = QLineEdit(", ".join(self.config.clipboard.exclude_patterns))
        self.exclude_patterns.textChanged.connect(self._on_change)
        form.addRow("Exclude Patterns", self.exclude_patterns)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Clipboard Settings")
        save_btn.clicked.connect(self._save_to_config)
        apply_btn = QPushButton("Apply to System")
        apply_btn.clicked.connect(self._apply_to_system)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)
        
    def _on_change(self):
        self.config_changed.emit()
        if self.preview_window:
            self.preview_window.update_preview()
            
    def _save_to_config(self):
        self.config.clipboard.manager = self.manager.currentText()
        self.config.clipboard.history_size = self.history_size.value()
        self.config.clipboard.max_item_size = self.max_item_size.value()
        self.config.clipboard.enable_images = self.enable_images.isChecked()
        self.config.clipboard.enable_primary_selection = self.enable_primary.isChecked()
        self.config.clipboard.exclude_patterns = [
            p.strip() for p in self.exclude_patterns.text().split(",") if p.strip()
        ]
        self.config.save()
        if self.preview_window:
            self.preview_window.update_preview()
            
    def _apply_to_system(self):
        try:
            # Apply clipboard manager configuration
            manager = self.config.clipboard.manager
            
            if manager == "cliphist":
                self._apply_cliphist_config()
            elif manager == "wl-clipboard":
                self._apply_wl_clipboard_config()
            elif manager == "clipman":
                self._apply_clipman_config()
                
            QMessageBox.information(self, "Apply Success", f"{manager} configuration applied.")
        except Exception as e:
            QMessageBox.critical(self, "Apply Failed", f"Failed to apply clipboard config: {e}")
    
    def _apply_cliphist_config(self):
        """Apply cliphist-specific configuration."""
        from ..utils import run_command
        
        # Set history size via environment variable
        os.environ['CLIPHIST_MAX_ITEMS'] = str(self.config.clipboard.history_size)
        
        # Start cliphist daemon if not running
        returncode, _, _ = run_command(['pgrep', '-f', 'cliphist'])
        if returncode != 0:
            run_command(['cliphist', 'daemon'], capture_output=False)
    
    def _apply_wl_clipboard_config(self):
        """Apply wl-clipboard configuration."""
        # wl-clipboard doesn't have persistent daemon, just ensure it's available
        from ..utils import run_command
        run_command(['which', 'wl-copy'])  # Check if available
    
    def _apply_clipman_config(self):
        """Apply clipman configuration."""
        from ..utils import run_command
        
        # Start clipman daemon if not running
        returncode, _, _ = run_command(['pgrep', '-f', 'clipman'])
        if returncode != 0:
            run_command(['clipman', 'store', '--daemon'], capture_output=False)

class LockscreenTab(QWidget):
    config_changed = pyqtSignal()
    
    def __init__(self, config, preview_window=None):
        super().__init__()
        self.config = config
        self.preview_window = preview_window
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        
        # Locker selection
        self.locker = QComboBox()
        self.locker.addItems(["hyprlock", "swaylock"])
        self.locker.setCurrentText(self.config.lockscreen.locker)
        self.locker.currentTextChanged.connect(self._on_change)
        form.addRow("Locker", self.locker)
        
        # Background type
        self.background_type = QComboBox()
        self.background_type.addItems(["image", "color", "blur"])
        self.background_type.setCurrentText(self.config.lockscreen.background_type)
        self.background_type.currentTextChanged.connect(self._on_background_type_changed)
        form.addRow("Background Type", self.background_type)
        
        # Background path (for image type)
        bg_layout = QHBoxLayout()
        self.background_path = QLineEdit(self.config.lockscreen.background_path)
        self.background_path.textChanged.connect(self._on_change)
        bg_layout.addWidget(self.background_path)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_background)
        bg_layout.addWidget(browse_btn)
        form.addRow("Background Image", bg_layout)
        
        # Background color
        color_layout = QHBoxLayout()
        self.background_color = QLineEdit(self.config.lockscreen.background_color)
        self.background_color.textChanged.connect(self._on_change)
        color_layout.addWidget(self.background_color)
        color_btn = QPushButton("Pick Color")
        color_btn.clicked.connect(self._pick_background_color)
        color_layout.addWidget(color_btn)
        form.addRow("Background Color", color_layout)
        
        # Timeout
        self.timeout = QSpinBox()
        self.timeout.setRange(30, 3600)
        self.timeout.setSuffix(" seconds")
        self.timeout.setValue(self.config.lockscreen.timeout)
        self.timeout.valueChanged.connect(self._on_change)
        form.addRow("Lock Timeout", self.timeout)
        
        # Grace period
        self.grace_period = QSpinBox()
        self.grace_period.setRange(0, 60)
        self.grace_period.setSuffix(" seconds")
        self.grace_period.setValue(self.config.lockscreen.grace_period)
        self.grace_period.valueChanged.connect(self._on_change)
        form.addRow("Grace Period", self.grace_period)
        
        # Show failed attempts
        self.show_failed = QCheckBox()
        self.show_failed.setChecked(self.config.lockscreen.show_failed_attempts)
        self.show_failed.toggled.connect(self._on_change)
        form.addRow("Show Failed Attempts", self.show_failed)
        
        # Font settings
        self.font_family = QLineEdit(self.config.lockscreen.font_family)
        self.font_family.textChanged.connect(self._on_change)
        form.addRow("Font Family", self.font_family)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 48)
        self.font_size.setValue(self.config.lockscreen.font_size)
        self.font_size.valueChanged.connect(self._on_change)
        form.addRow("Font Size", self.font_size)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Lockscreen Settings")
        save_btn.clicked.connect(self._save_to_config)
        apply_btn = QPushButton("Apply to System")
        apply_btn.clicked.connect(self._apply_to_system)
        test_btn = QPushButton("Test Lock")
        test_btn.clicked.connect(self._test_lock)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(test_btn)
        layout.addLayout(btn_layout)
        
        self._on_background_type_changed()
    
    def _on_change(self):
        self.config_changed.emit()
        if self.preview_window:
            self.preview_window.update_preview()
    
    def _on_background_type_changed(self):
        bg_type = self.background_type.currentText()
        # Show/hide relevant controls based on background type
        self.background_path.setEnabled(bg_type == "image")
        self.background_color.setEnabled(bg_type in ["color", "blur"])
        self._on_change()
    
    def _browse_background(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Background Image", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.background_path.setText(file_path)
    
    def _pick_background_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.background_color.setText(color.name())
    
    def _save_to_config(self):
        self.config.lockscreen.locker = self.locker.currentText()
        self.config.lockscreen.background_type = self.background_type.currentText()
        self.config.lockscreen.background_path = self.background_path.text()
        self.config.lockscreen.background_color = self.background_color.text()
        self.config.lockscreen.timeout = self.timeout.value()
        self.config.lockscreen.grace_period = self.grace_period.value()
        self.config.lockscreen.show_failed_attempts = self.show_failed.isChecked()
        self.config.lockscreen.font_family = self.font_family.text()
        self.config.lockscreen.font_size = self.font_size.value()
        self.config.save()
        if self.preview_window:
            self.preview_window.update_preview()
    
    def _apply_to_system(self):
        try:
            locker = self.config.lockscreen.locker
            if locker == "hyprlock":
                self._apply_hyprlock_config()
            elif locker == "swaylock":
                self._apply_swaylock_config()
            QMessageBox.information(self, "Apply Success", f"{locker} configuration applied.")
        except Exception as e:
            QMessageBox.critical(self, "Apply Failed", f"Failed to apply lockscreen config: {e}")
    
    def _apply_hyprlock_config(self):
        """Apply hyprlock configuration."""
        from ..utils import run_command
        import tempfile
        
        # Create hyprlock config
        config_content = f"""
general {{
    grace = {self.config.lockscreen.grace_period}
    hide_cursor = true
    no_fade_in = false
}}

background {{
    monitor =
    path = {self.config.lockscreen.background_path if self.config.lockscreen.background_type == 'image' else ''}
    color = {self.config.lockscreen.background_color}
    blur_size = {10 if self.config.lockscreen.background_type == 'blur' else 0}
    blur_passes = {3 if self.config.lockscreen.background_type == 'blur' else 0}
}}

input-field {{
    monitor =
    size = 200, 50
    outline_thickness = 3
    dots_size = 0.33
    dots_spacing = 0.15
    dots_center = true
    outer_color = {self.config.lockscreen.input_field_color}
    inner_color = rgb(200, 200, 200)
    font_color = {self.config.lockscreen.text_color}
    fade_on_empty = true
    placeholder_text = <i>Input Password...</i>
    hide_input = false
}}

label {{
    monitor =
    text = Hi there, $USER
    color = {self.config.lockscreen.text_color}
    font_size = {self.config.lockscreen.font_size}
    font_family = {self.config.lockscreen.font_family}
    position = 0, 160
    halign = center
    valign = center
}}
"""
        
        # Write config to temporary file and copy to proper location
        config_path = os.path.expanduser("~/.config/hypr/hyprlock.conf")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            f.write(config_content)
    
    def _apply_swaylock_config(self):
        """Apply swaylock configuration."""
        # swaylock uses command-line arguments, create a wrapper script
        script_content = f"""#!/bin/bash
swaylock \\
    --color {self.config.lockscreen.background_color.replace('#', '')} \\
    --font '{self.config.lockscreen.font_family}' \\
    --font-size {self.config.lockscreen.font_size} \\
    --grace {self.config.lockscreen.grace_period} \\
    {'--image ' + self.config.lockscreen.background_path if self.config.lockscreen.background_type == 'image' and self.config.lockscreen.background_path else ''}
"""
        
        script_path = os.path.expanduser("~/.hyprrice/swaylock_wrapper.sh")
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
    
    def _test_lock(self):
        """Test the lockscreen immediately."""
        try:
            locker = self.config.lockscreen.locker
            from ..utils import run_command
            
            if locker == "hyprlock":
                run_command(['hyprlock'], capture_output=False)
            elif locker == "swaylock":
                script_path = os.path.expanduser("~/.hyprrice/swaylock_wrapper.sh")
                if os.path.exists(script_path):
                    run_command([script_path], capture_output=False)
                else:
                    run_command(['swaylock'], capture_output=False)
        except Exception as e:
            QMessageBox.critical(self, "Test Failed", f"Failed to test lock: {e}")

class ThemesTab(QWidget):
    def __init__(self, config, theme_manager, preview_window=None):
        super().__init__()
        self.config = config
        self.theme_manager = theme_manager
        self.preview_window = preview_window
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        self.theme_list = QComboBox()
        self.theme_list.addItems(self.theme_manager.list_themes())
        form.addRow("Theme", self.theme_list)
        preview_btn = QPushButton("Preview Theme")
        preview_btn.clicked.connect(self._preview_theme)
        layout.addWidget(preview_btn)
        apply_btn = QPushButton("Apply Theme")
        apply_btn.clicked.connect(self._apply_theme)
        layout.addWidget(apply_btn)
    def _preview_theme(self):
        theme = self.theme_list.currentText()
        self.theme_manager.preview_theme(theme, self.config)
        if self.preview_window:
            self.preview_window.update_preview()
    def _apply_theme(self):
        theme = self.theme_list.currentText()
        self.theme_manager.apply_theme(theme, self.config)
        if self.preview_window:
            self.preview_window.update_preview()

def config_to_markdown(config):
    md = ["# HyprRice Configuration\n"]
    for section in ["general", "paths", "gui", "hyprland", "waybar", "rofi", "notifications"]:
        md.append(f"## {section.capitalize()}\n")
        sec = getattr(config, section)
        for k, v in sec.__dict__.items():
            md.append(f"- **{k}**: `{v}`\n")
    return "\n".join(md)

def config_to_html(config):
    html = ["<html><body><h1>HyprRice Configuration</h1>"]
    for section in ["general", "paths", "gui", "hyprland", "waybar", "rofi", "notifications"]:
        html.append(f"<h2>{section.capitalize()}</h2><ul>")
        sec = getattr(config, section)
        for k, v in sec.__dict__.items():
            html.append(f"<li><b>{k}</b>: <code>{v}</code></li>")
        html.append("</ul>")
    html.append("</body></html>")
    return "".join(html)

def config_to_semantic_map(config):
    return {section: list(getattr(config, section).__dict__.keys()) for section in ["general", "paths", "gui", "hyprland", "waybar", "rofi", "notifications"]}

class SettingsTab(QWidget):
    def __init__(self, config, preview_window=None):
        super().__init__()
        self.config = config
        self.preview_window = preview_window
        self.undo_stack = []
        self.redo_stack = []
        self.change_log = []
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        self.auto_backup = QCheckBox()
        self.auto_backup.setChecked(self.config.general.auto_backup)
        form.addRow("Auto Backup", self.auto_backup)
        self.backup_retention = QSpinBox()
        self.backup_retention.setRange(1, 100)
        self.backup_retention.setValue(self.config.general.backup_retention)
        form.addRow("Backup Retention", self.backup_retention)
        self.live_preview = QCheckBox()
        self.live_preview.setChecked(self.config.general.live_preview)
        form.addRow("Live Preview", self.live_preview)
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save_to_config)
        layout.addWidget(save_btn)
        # Advanced features
        adv_layout = QHBoxLayout()
        backup_btn = QPushButton("Backup Config")
        backup_btn.clicked.connect(self._backup_config)
        restore_btn = QPushButton("Restore Config")
        restore_btn.clicked.connect(self._restore_config)
        import_btn = QPushButton("Import Config")
        import_btn.clicked.connect(self._import_config)
        export_btn = QPushButton("Export Config")
        export_btn.clicked.connect(self._export_config)
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self._undo)
        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self._redo)
        adv_layout.addWidget(backup_btn)
        adv_layout.addWidget(restore_btn)
        adv_layout.addWidget(import_btn)
        adv_layout.addWidget(export_btn)
        adv_layout.addWidget(undo_btn)
        adv_layout.addWidget(redo_btn)
        layout.addLayout(adv_layout)
        # Change log
        self.log_label = QLabel("Change Log:")
        layout.addWidget(self.log_label)
        self.log_list = QLabel()
        self.log_list.setWordWrap(True)
        layout.addWidget(self.log_list)

    def _set_status(self, msg):
        p = self.parent()
        if p is not None and hasattr(p, 'set_status'):
            p.set_status(msg)

    def _on_change(self):
        if self.preview_window:
            self.preview_window.update_preview()

    def _save_to_config(self):
        self.undo_stack.append(copy.deepcopy(self.config))
        self.redo_stack.clear()
        self.config.general.auto_backup = self.auto_backup.isChecked()
        self.config.general.backup_retention = self.backup_retention.value()
        self.config.general.live_preview = self.live_preview.isChecked()
        self.config.save()
        self._log_change("Settings saved.")
        if self.preview_window:
            self.preview_window.update_preview()
        self._set_status("Settings saved.")

    def _backup_config(self):
        try:
            config_path = self.config._get_default_config_path()
            backup_dir = self.config.paths.backup_dir
            backup_file(config_path, backup_dir)
            QMessageBox.information(self, "Backup Success", "Configuration backed up.")
            self._log_change("Backup created.")
            self._set_status("Backup created.")
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed", f"Failed to backup: {e}")
            self._set_status("Backup failed.")

    def _restore_config(self):
        try:
            config_path = self.config._get_default_config_path()
            backup_dir = self.config.paths.backup_dir
            backups = os.listdir(backup_dir)
            backups = [b for b in backups if b.endswith(os.path.basename(config_path))]
            if not backups:
                QMessageBox.warning(self, "No Backups", "No backups found to restore.")
                self._set_status("No backups found to restore.")
                return
            latest_backup = sorted(backups)[-1]
            restore_file(os.path.join(backup_dir, latest_backup), config_path)
            QMessageBox.information(self, "Restore Success", "Configuration restored from backup.")
            self._log_change("Config restored from backup.")
            self._set_status("Config restored from backup.")
        except Exception as e:
            QMessageBox.critical(self, "Restore Failed", f"Failed to restore: {e}")
            self._set_status("Restore failed.")

    def _import_config(self):
        QMessageBox.information(self, "Import", "Import not yet implemented.")
        self._log_change("Import attempted.")
        self._set_status("Import attempted.")

    def _export_config(self):
        formats = ["Markdown (*.md)", "HTML (*.html)", "JSON (*.json)"]
        file_path, fmt = QFileDialog.getSaveFileName(self, "Export Config", "hyprrice_export", ";;".join(formats))
        if not file_path:
            return
        try:
            if "md" in fmt:
                content = config_to_markdown(self.config)
            elif "html" in fmt:
                content = config_to_html(self.config)
            elif "json" in fmt:
                data = self.config._to_dict()
                data["semantic_map"] = config_to_semantic_map(self.config)
                content = json.dumps(data, indent=2)
            else:
                raise Exception("Unknown format")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self._log_change(f"Exported config as {fmt}.")
            self._set_status(f"Exported config as {fmt}.")
            QMessageBox.information(self, "Export Success", f"Configuration exported as {fmt}.")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export: {e}")
            self._set_status("Export failed.")

    def _undo(self):
        if not self.undo_stack:
            QMessageBox.information(self, "Undo", "Nothing to undo.")
            self._set_status("Nothing to undo.")
            return
        self.redo_stack.append(copy.deepcopy(self.config))
        self.config = self.undo_stack.pop()
        self._log_change("Undo performed.")
        if self.preview_window:
            self.preview_window.update_preview()
        self._set_status("Undo performed.")

    def _redo(self):
        if not self.redo_stack:
            QMessageBox.information(self, "Redo", "Nothing to redo.")
            self._set_status("Nothing to redo.")
            return
        self.undo_stack.append(copy.deepcopy(self.config))
        self.config = self.redo_stack.pop()
        self._log_change("Redo performed.")
        if self.preview_window:
            self.preview_window.update_preview()
        self._set_status("Redo performed.")

    def _log_change(self, msg):
        self.change_log.append(msg)
        self.log_list.setText("\n".join(self.change_log))

class PluginsTab(QWidget):
    def __init__(self, config, plugin_manager, app=None):
        super().__init__()
        self.config = config
        self.plugin_manager = plugin_manager
        self.app = app
        layout = QVBoxLayout(self)
        self.plugin_list = QVBoxLayout()
        layout.addLayout(self.plugin_list)
        self.refresh_plugins()

    def refresh_plugins(self):
        # Clear layout
        while self.plugin_list.count():
            item = self.plugin_list.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        # List plugins
        for plugin_name in self.plugin_manager.list_plugins():
            row = QHBoxLayout()
            label = QLabel(plugin_name)
            row.addWidget(label)
            load_btn = QPushButton("Load")
            load_btn.clicked.connect(lambda checked, name=plugin_name: self.load_plugin(name))
            row.addWidget(load_btn)
            self.plugin_list.addLayout(row)

    def load_plugin(self, plugin_name):
        try:
            self.plugin_manager.load_plugin(plugin_name, self.app)
            QMessageBox.information(self, "Plugin Loaded", f"Plugin '{plugin_name}' loaded.")
        except Exception as e:
            QMessageBox.critical(self, "Plugin Error", f"Failed to load plugin '{plugin_name}': {e}")
        self.refresh_plugins() 