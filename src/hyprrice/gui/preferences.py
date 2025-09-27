"""Preferences dialog for HyprRice settings."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QCheckBox, QSpinBox, QComboBox, QDialogButtonBox, QMessageBox
from PyQt6.QtCore import pyqtSignal
from ..config import Config

class PreferencesDialog(QDialog):
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)
        
        # General settings
        self.auto_backup = QCheckBox()
        form.addRow("Auto Backup:", self.auto_backup)
        
        self.backup_retention = QSpinBox()
        self.backup_retention.setRange(1, 100)
        form.addRow("Backup Retention:", self.backup_retention)
        
        self.live_preview = QCheckBox()
        form.addRow("Live Preview:", self.live_preview)
        
        # GUI settings
        self.gui_theme = QComboBox()
        self.gui_theme.addItems(["dark", "light", "auto"])
        form.addRow("Theme:", self.gui_theme)
        
        self.auto_save = QCheckBox()
        form.addRow("Auto Save:", self.auto_save)
        
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(5, 300)
        form.addRow("Auto Save Interval (s):", self.auto_save_interval)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_settings(self):
        self.auto_backup.setChecked(self.config.general.auto_backup)
        self.backup_retention.setValue(self.config.general.backup_retention)
        self.live_preview.setChecked(self.config.general.live_preview)
        self.gui_theme.setCurrentText(self.config.gui.theme)
        self.auto_save.setChecked(self.config.gui.auto_save)
        self.auto_save_interval.setValue(self.config.gui.auto_save_interval)
    
    def save_settings(self):
        self.config.general.auto_backup = self.auto_backup.isChecked()
        self.config.general.backup_retention = self.backup_retention.value()
        self.config.general.live_preview = self.live_preview.isChecked()
        self.config.gui.theme = self.gui_theme.currentText()
        self.config.gui.auto_save = self.auto_save.isChecked()
        self.config.gui.auto_save_interval = self.auto_save_interval.value()
        
        try:
            self.config.save()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save preferences:\n{e}")
    
    def accept(self):
        self.save_settings()
        super().accept()
