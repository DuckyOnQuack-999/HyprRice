"""Backup manager dialog for HyprRice."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QDialogButtonBox, QMessageBox
from PyQt6.QtCore import Qt
from pathlib import Path

class BackupSelectionDialog(QDialog):
    def __init__(self, backups, parent=None):
        super().__init__(parent)
        self.backups = backups
        self.selected_backup = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Select Backup")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        label = QLabel("Select a backup to restore:")
        layout.addWidget(label)
        
        # Backup list
        self.backup_list = QListWidget()
        for backup in self.backups:
            item = QListWidgetItem(f"{backup['filename']} - {backup['modified']}")
            item.setData(Qt.ItemDataRole.UserRole, backup)
            self.backup_list.addItem(item)
        
        layout.addWidget(self.backup_list)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_selected_backup(self):
        current_item = self.backup_list.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def accept(self):
        if not self.get_selected_backup():
            QMessageBox.warning(self, "No Selection", "Please select a backup to restore.")
            return
        super().accept()
