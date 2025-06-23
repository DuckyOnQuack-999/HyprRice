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
    def __init__(self, config, preview_window=None):
        super().__init__()
        self.config = config
        self.preview_window = preview_window
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        self.manager = QComboBox()
        self.manager.addItems(["cliphist", "wl-clipboard"])
        form.addRow("Manager", self.manager)
        self.history_size = QSpinBox()
        self.history_size.setRange(10, 1000)
        form.addRow("History Size", self.history_size)
        save_btn = QPushButton("Save Clipboard Settings")
        save_btn.clicked.connect(self._save_to_config)
        layout.addWidget(save_btn)
        # TODO: Bind to config when clipboard config is added
    def _on_change(self):
        if self.preview_window:
            self.preview_window.update_preview()
    def _save_to_config(self):
        # TODO: Bind to config when clipboard config is added
        if self.preview_window:
            self.preview_window.update_preview()

class LockscreenTab(QWidget):
    def __init__(self, config, preview_window=None):
        super().__init__()
        self.config = config
        self.preview_window = preview_window
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        self.background = QLineEdit()
        form.addRow("Background", self.background)
        self.timeout = QSpinBox()
        self.timeout.setRange(0, 3600)
        form.addRow("Timeout (s)", self.timeout)
        save_btn = QPushButton("Save Lockscreen Settings")
        save_btn.clicked.connect(self._save_to_config)
        layout.addWidget(save_btn)
        # TODO: Bind to config when lockscreen config is added
    def _on_change(self):
        if self.preview_window:
            self.preview_window.update_preview()
    def _save_to_config(self):
        # TODO: Bind to config when lockscreen config is added
        if self.preview_window:
            self.preview_window.update_preview()

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