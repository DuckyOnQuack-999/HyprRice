from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QCheckBox, QDoubleSpinBox, QComboBox, QSpinBox, QLineEdit, QPushButton, QColorDialog, QHBoxLayout, QMessageBox, QFileDialog, QGroupBox, QListWidget, QListWidgetItem, QInputDialog
from PyQt5.QtCore import pyqtSignal
from ..hyprland.animations import AnimationManager
from ..hyprland.windows import WindowManager
from ..utils import backup_file, restore_file, parse_hyprland_config, write_hyprland_config
from ..plugins import PluginManager
import os
import copy
import json

# Each tab emits config_changed when its config is modified

class BaseTab(QWidget):
    """Base class for all configuration tabs."""
    config_changed = pyqtSignal()
    
    def __init__(self, config, preview_window=None):
        super().__init__()
        self.config = config
        self.preview_window = preview_window


class HyprlandTab(BaseTab):
    def __init__(self, config, preview_window=None):
        super().__init__(config, preview_window)
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

        # Sourced Files Section
        sourced_group = QGroupBox("Sourced Configuration Files")
        sourced_layout = QVBoxLayout(sourced_group)
        
        # List of sourced files
        self.sourced_files_list = QListWidget()
        self.sourced_files_list.setMaximumHeight(120)
        self._populate_sourced_files()
        sourced_layout.addWidget(self.sourced_files_list)
        
        # Buttons for managing sourced files
        sourced_btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add File")
        add_btn.clicked.connect(self._add_sourced_file)
        sourced_btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._remove_sourced_file)
        sourced_btn_layout.addWidget(remove_btn)
        
        create_btn = QPushButton("Create File")
        create_btn.clicked.connect(self._create_sourced_file)
        sourced_btn_layout.addWidget(create_btn)
        
        sourced_layout.addLayout(sourced_btn_layout)
        layout.addWidget(sourced_group)

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
        try:
            color = QColorDialog.getColor()
            if color.isValid():
                self.border_color.setText(color.name())
                self._on_change()
        except Exception as e:
            QMessageBox.critical(self, "Color Error", f"Failed to pick color: {e}")

    def _on_change(self):
        if self.preview_window:
            self.preview_window.update_preview()

    def _save_to_config(self):
        try:
            # Validate color
            from ..utils import validate_color
            if not validate_color(self.border_color.text()):
                QMessageBox.warning(self, "Invalid Color", "Please enter a valid color format (e.g., #RRGGBB)")
                return
            
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
            QMessageBox.information(self, "Success", "Hyprland settings saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save Hyprland settings: {e}")

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
            # Include sourced files
            sections['_sourced_files'] = self.config.hyprland.sourced_files
            write_hyprland_config(config_path, sections)
            
            # Clear hyprctl cache after applying changes
            from ..utils import clear_hyprctl_cache
            clear_hyprctl_cache()
            
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
            
            # Clear hyprctl cache after rollback
            from ..utils import clear_hyprctl_cache
            clear_hyprctl_cache()
            
            QMessageBox.information(self, "Rollback Success", "Hyprland config restored from backup.")
        except Exception as e:
            QMessageBox.critical(self, "Rollback Failed", f"Failed to rollback config: {e}")

    def _populate_sourced_files(self):
        """Populate the sourced files list from config."""
        self.sourced_files_list.clear()
        for file_path in self.config.hyprland.sourced_files:
            item = QListWidgetItem(file_path)
            # Check if file exists and add status indicator
            from ..utils import validate_sourced_file
            if validate_sourced_file(file_path):
                item.setIcon(self.style().standardIcon(self.style().SP_DialogApplyButton))
            else:
                item.setIcon(self.style().standardIcon(self.style().SP_MessageBoxWarning))
            self.sourced_files_list.addItem(item)

    def _add_sourced_file(self):
        """Add a new sourced file."""
        file_path, ok = QInputDialog.getText(
            self, "Add Sourced File", "Enter the path to the configuration file:",
            text="~/.config/hypr/custom.conf"
        )
        if ok and file_path:
            # Expand tilde if present
            expanded_path = os.path.expanduser(file_path)
            if expanded_path not in self.config.hyprland.sourced_files:
                self.config.hyprland.sourced_files.append(expanded_path)
                self._populate_sourced_files()
                self._on_change()

    def _remove_sourced_file(self):
        """Remove the selected sourced file."""
        current_item = self.sourced_files_list.currentItem()
        if current_item:
            file_path = current_item.text()
            if file_path in self.config.hyprland.sourced_files:
                self.config.hyprland.sourced_files.remove(file_path)
                self._populate_sourced_files()
                self._on_change()

    def _create_sourced_file(self):
        """Create a new sourced file with default content."""
        file_path, ok = QInputDialog.getText(
            self, "Create Sourced File", "Enter the path for the new configuration file:",
            text="~/.config/hypr/custom.conf"
        )
        if ok and file_path:
            expanded_path = os.path.expanduser(file_path)
            from ..utils import create_sourced_file
            if create_sourced_file(expanded_path):
                # Add to sourced files if not already present
                if expanded_path not in self.config.hyprland.sourced_files:
                    self.config.hyprland.sourced_files.append(expanded_path)
                    self._populate_sourced_files()
                    self._on_change()
                QMessageBox.information(self, "File Created", f"Created configuration file: {expanded_path}")
            else:
                QMessageBox.critical(self, "Creation Failed", f"Failed to create file: {expanded_path}")

class WaybarTab(BaseTab):
    def __init__(self, config, preview_window=None):
        super().__init__(config, preview_window)
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

class RofiTab(BaseTab):
    def __init__(self, config, preview_window=None):
        super().__init__(config, preview_window)
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

class NotificationsTab(BaseTab):
    def __init__(self, config, preview_window=None):
        super().__init__(config, preview_window)
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

class ClipboardTab(BaseTab):
    def __init__(self, config, preview_window=None):
        super().__init__(config, preview_window)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        
        self.manager = QComboBox()
        self.manager.addItems(["cliphist", "wl-clipboard"])
        self.manager.setCurrentText(self.config.clipboard.manager)
        self.manager.currentTextChanged.connect(self._on_change)
        form.addRow("Manager", self.manager)
        
        self.history_size = QSpinBox()
        self.history_size.setRange(10, 10000)
        self.history_size.setValue(self.config.clipboard.history_size)
        self.history_size.valueChanged.connect(self._on_change)
        form.addRow("History Size", self.history_size)
        
        self.auto_sync = QCheckBox()
        self.auto_sync.setChecked(self.config.clipboard.auto_sync)
        self.auto_sync.toggled.connect(self._on_change)
        form.addRow("Auto Sync", self.auto_sync)
        
        self.sync_interval = QSpinBox()
        self.sync_interval.setRange(1, 3600)
        self.sync_interval.setValue(self.config.clipboard.sync_interval)
        self.sync_interval.valueChanged.connect(self._on_change)
        form.addRow("Sync Interval (s)", self.sync_interval)
        
        self.include_images = QCheckBox()
        self.include_images.setChecked(self.config.clipboard.include_images)
        self.include_images.toggled.connect(self._on_change)
        form.addRow("Include Images", self.include_images)
        
        self.include_text = QCheckBox()
        self.include_text.setChecked(self.config.clipboard.include_text)
        self.include_text.toggled.connect(self._on_change)
        form.addRow("Include Text", self.include_text)
        
        self.include_files = QCheckBox()
        self.include_files.setChecked(self.config.clipboard.include_files)
        self.include_files.toggled.connect(self._on_change)
        form.addRow("Include Files", self.include_files)
        
        save_btn = QPushButton("Save Clipboard Settings")
        save_btn.clicked.connect(self._save_to_config)
        layout.addWidget(save_btn)
    
    def _on_change(self):
        if self.preview_window:
            self.preview_window.update_preview()
    
    def _save_to_config(self):
        self.config.clipboard.manager = self.manager.currentText()
        self.config.clipboard.history_size = self.history_size.value()
        self.config.clipboard.auto_sync = self.auto_sync.isChecked()
        self.config.clipboard.sync_interval = self.sync_interval.value()
        self.config.clipboard.include_images = self.include_images.isChecked()
        self.config.clipboard.include_text = self.include_text.isChecked()
        self.config.clipboard.include_files = self.include_files.isChecked()
        self.config.save()
        if self.preview_window:
            self.preview_window.update_preview()

class LockscreenTab(BaseTab):
    def __init__(self, config, preview_window=None):
        super().__init__(config, preview_window)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        
        self.daemon = QComboBox()
        self.daemon.addItems(["hyprlock", "swaylock"])
        self.daemon.setCurrentText(self.config.lockscreen.daemon)
        self.daemon.currentTextChanged.connect(self._on_change)
        form.addRow("Daemon", self.daemon)
        
        self.background = QLineEdit(self.config.lockscreen.background)
        self.background.textChanged.connect(self._on_change)
        form.addRow("Background", self.background)
        
        self.timeout = QSpinBox()
        self.timeout.setRange(0, 3600)
        self.timeout.setValue(self.config.lockscreen.timeout)
        self.timeout.valueChanged.connect(self._on_change)
        form.addRow("Timeout (s)", self.timeout)
        
        self.grace_period = QSpinBox()
        self.grace_period.setRange(0, 60)
        self.grace_period.setValue(self.config.lockscreen.grace_period)
        self.grace_period.valueChanged.connect(self._on_change)
        form.addRow("Grace Period (s)", self.grace_period)
        
        self.show_clock = QCheckBox()
        self.show_clock.setChecked(self.config.lockscreen.show_clock)
        self.show_clock.toggled.connect(self._on_change)
        form.addRow("Show Clock", self.show_clock)
        
        self.show_date = QCheckBox()
        self.show_date.setChecked(self.config.lockscreen.show_date)
        self.show_date.toggled.connect(self._on_change)
        form.addRow("Show Date", self.show_date)
        
        self.clock_format = QLineEdit(self.config.lockscreen.clock_format)
        self.clock_format.textChanged.connect(self._on_change)
        form.addRow("Clock Format", self.clock_format)
        
        self.date_format = QLineEdit(self.config.lockscreen.date_format)
        self.date_format.textChanged.connect(self._on_change)
        form.addRow("Date Format", self.date_format)
        
        self.font_family = QLineEdit(self.config.lockscreen.font_family)
        self.font_family.textChanged.connect(self._on_change)
        form.addRow("Font Family", self.font_family)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 48)
        self.font_size.setValue(self.config.lockscreen.font_size)
        self.font_size.valueChanged.connect(self._on_change)
        form.addRow("Font Size", self.font_size)
        
        self.text_color = QLineEdit(self.config.lockscreen.text_color)
        self.text_color.textChanged.connect(self._on_change)
        form.addRow("Text Color", self.text_color)
        
        self.background_color = QLineEdit(self.config.lockscreen.background_color)
        self.background_color.textChanged.connect(self._on_change)
        form.addRow("Background Color", self.background_color)
        
        self.border_color = QLineEdit(self.config.lockscreen.border_color)
        self.border_color.textChanged.connect(self._on_change)
        form.addRow("Border Color", self.border_color)
        
        self.border_size = QSpinBox()
        self.border_size.setRange(0, 20)
        self.border_size.setValue(self.config.lockscreen.border_size)
        self.border_size.valueChanged.connect(self._on_change)
        form.addRow("Border Size", self.border_size)
        
        self.blur_background = QCheckBox()
        self.blur_background.setChecked(self.config.lockscreen.blur_background)
        self.blur_background.toggled.connect(self._on_change)
        form.addRow("Blur Background", self.blur_background)
        
        self.blur_size = QSpinBox()
        self.blur_size.setRange(0, 50)
        self.blur_size.setValue(self.config.lockscreen.blur_size)
        self.blur_size.valueChanged.connect(self._on_change)
        form.addRow("Blur Size", self.blur_size)
        
        self.fade_in = QCheckBox()
        self.fade_in.setChecked(self.config.lockscreen.fade_in)
        self.fade_in.toggled.connect(self._on_change)
        form.addRow("Fade In", self.fade_in)
        
        self.fade_out = QCheckBox()
        self.fade_out.setChecked(self.config.lockscreen.fade_out)
        self.fade_out.toggled.connect(self._on_change)
        form.addRow("Fade Out", self.fade_out)
        
        self.animation_duration = QDoubleSpinBox()
        self.animation_duration.setRange(0.1, 2.0)
        self.animation_duration.setValue(self.config.lockscreen.animation_duration)
        self.animation_duration.setSingleStep(0.1)
        self.animation_duration.valueChanged.connect(self._on_change)
        form.addRow("Animation Duration (s)", self.animation_duration)
        
        save_btn = QPushButton("Save Lockscreen Settings")
        save_btn.clicked.connect(self._save_to_config)
        layout.addWidget(save_btn)
    
    def _on_change(self):
        if self.preview_window:
            self.preview_window.update_preview()
    
    def _save_to_config(self):
        self.config.lockscreen.daemon = self.daemon.currentText()
        self.config.lockscreen.background = self.background.text()
        self.config.lockscreen.timeout = self.timeout.value()
        self.config.lockscreen.grace_period = self.grace_period.value()
        self.config.lockscreen.show_clock = self.show_clock.isChecked()
        self.config.lockscreen.show_date = self.show_date.isChecked()
        self.config.lockscreen.clock_format = self.clock_format.text()
        self.config.lockscreen.date_format = self.date_format.text()
        self.config.lockscreen.font_family = self.font_family.text()
        self.config.lockscreen.font_size = self.font_size.value()
        self.config.lockscreen.text_color = self.text_color.text()
        self.config.lockscreen.background_color = self.background_color.text()
        self.config.lockscreen.border_color = self.border_color.text()
        self.config.lockscreen.border_size = self.border_size.value()
        self.config.lockscreen.blur_background = self.blur_background.isChecked()
        self.config.lockscreen.blur_size = self.blur_size.value()
        self.config.lockscreen.fade_in = self.fade_in.isChecked()
        self.config.lockscreen.fade_out = self.fade_out.isChecked()
        self.config.lockscreen.animation_duration = self.animation_duration.value()
        self.config.save()
        if self.preview_window:
            self.preview_window.update_preview()

class ThemesTab(BaseTab):
    def __init__(self, config, theme_manager, preview_window=None):
        super().__init__(config, preview_window)
        self.theme_manager = theme_manager
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        
        # Theme selection
        self.theme_list = QComboBox()
        self.refresh_themes()
        form.addRow("Theme", self.theme_list)
        
        # Theme info
        self.theme_info = QLabel("Select a theme to see information")
        self.theme_info.setWordWrap(True)
        self.theme_info.setStyleSheet("color: #88c0d0; padding: 10px;")
        layout.addWidget(self.theme_info)
        
        # Connect theme selection change
        self.theme_list.currentTextChanged.connect(self._on_theme_changed)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        preview_btn = QPushButton("Preview Theme")
        preview_btn.clicked.connect(self._preview_theme)
        btn_layout.addWidget(preview_btn)
        
        apply_btn = QPushButton("Apply Theme")
        apply_btn.clicked.connect(self._apply_theme)
        btn_layout.addWidget(apply_btn)
        
        layout.addLayout(btn_layout)
        
        # Theme management buttons
        mgmt_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_themes)
        mgmt_layout.addWidget(refresh_btn)
        
        import_btn = QPushButton("Import Theme")
        import_btn.clicked.connect(self._import_theme)
        mgmt_layout.addWidget(import_btn)
        
        export_btn = QPushButton("Export Current")
        export_btn.clicked.connect(self._export_theme)
        mgmt_layout.addWidget(export_btn)
        
        layout.addLayout(mgmt_layout)
    
    def refresh_themes(self):
        """Refresh the theme list."""
        try:
            current_theme = self.theme_list.currentText()
            self.theme_list.clear()
            themes = self.theme_manager.list_themes()
            self.theme_list.addItems(themes)
            
            # Restore selection if possible
            if current_theme in themes:
                self.theme_list.setCurrentText(current_theme)
            elif themes:
                self.theme_list.setCurrentIndex(0)
                
            self._on_theme_changed()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh themes: {e}")
    
    def _on_theme_changed(self):
        """Handle theme selection change."""
        try:
            theme_name = self.theme_list.currentText()
            if theme_name:
                theme_info = self.theme_manager.get_theme_info(theme_name)
                if theme_info:
                    info_text = f"<b>{theme_info.get('name', theme_name)}</b><br/>"
                    info_text += f"Description: {theme_info.get('description', 'No description')}<br/>"
                    info_text += f"Author: {theme_info.get('author', 'Unknown')}<br/>"
                    info_text += f"Version: {theme_info.get('version', '1.0.0')}"
                    self.theme_info.setText(info_text)
                else:
                    self.theme_info.setText(f"Theme '{theme_name}' not found")
            else:
                self.theme_info.setText("No theme selected")
                
        except Exception as e:
            self.theme_info.setText(f"Error loading theme info: {e}")
    
    def _preview_theme(self):
        """Preview the selected theme."""
        try:
            theme = self.theme_list.currentText()
            if not theme:
                QMessageBox.warning(self, "No Theme", "Please select a theme to preview.")
                return
                
            if self.theme_manager.preview_theme(theme, self.config):
                if self.preview_window:
                    self.preview_window.update_preview()
                QMessageBox.information(self, "Preview", f"Theme '{theme}' previewed successfully.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to preview theme '{theme}'.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to preview theme: {e}")
    
    def _apply_theme(self):
        """Apply the selected theme."""
        try:
            theme = self.theme_list.currentText()
            if not theme:
                QMessageBox.warning(self, "No Theme", "Please select a theme to apply.")
                return
            
            # Confirm application
            reply = QMessageBox.question(
                self, 
                "Apply Theme", 
                f"Are you sure you want to apply theme '{theme}'?\n"
                "This will modify your current configuration.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.theme_manager.apply_theme(theme, self.config):
                    if self.preview_window:
                        self.preview_window.update_preview()
                    QMessageBox.information(self, "Success", f"Theme '{theme}' applied successfully.")
                else:
                    QMessageBox.critical(self, "Error", f"Failed to apply theme '{theme}'.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply theme: {e}")
    
    def _import_theme(self):
        """Import a theme from file."""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Import Theme", 
                str(self.theme_manager.themes_dir),
                "HyprRice Themes (*.hyprrice);;All Files (*)"
            )
            
            if file_path:
                if self.theme_manager.import_theme(file_path):
                    self.refresh_themes()
                    QMessageBox.information(self, "Success", "Theme imported successfully.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to import theme.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import theme: {e}")
    
    def _export_theme(self):
        """Export current configuration as theme."""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Theme",
                str(self.theme_manager.themes_dir),
                "HyprRice Themes (*.hyprrice);;All Files (*)"
            )
            
            if file_path:
                if self.theme_manager.export_theme(self.config, file_path):
                    QMessageBox.information(self, "Success", "Theme exported successfully.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to export theme.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export theme: {e}")

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

class SettingsTab(BaseTab):
    def __init__(self, config, preview_window=None):
        super().__init__(config, preview_window)
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

class PluginsTab(BaseTab):
    def __init__(self, config, plugin_manager, app=None):
        super().__init__(config)
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
        for plugin_info in self.plugin_manager.list_available_plugins():
            plugin_name = plugin_info['name']
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
