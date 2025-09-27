"""Backup tab for HyprRice."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem, QMessageBox
from PyQt6.QtCore import Qt
from ..backup import BackupManager

class BackupTab(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.backup_manager = BackupManager(config.paths.backup_dir)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Backup Management")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create Backup")
        create_btn.clicked.connect(self.create_backup)
        btn_layout.addWidget(create_btn)
        
        restore_btn = QPushButton("Restore Backup")
        restore_btn.clicked.connect(self.restore_backup)
        btn_layout.addWidget(restore_btn)
        
        delete_btn = QPushButton("Delete Backup")
        delete_btn.clicked.connect(self.delete_backup)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        # Backup list
        self.backup_list = QListWidget()
        layout.addWidget(self.backup_list)
        
        self.refresh_backups()
    
    def refresh_backups(self):
        """Refresh the backup list."""
        self.backup_list.clear()
        try:
            backups = self.backup_manager.list_backups()
            for backup in backups:
                item = QListWidgetItem(f"{backup[\"filename\"]} - {backup[\"modified\"]}")
                item.setData(Qt.ItemDataRole.UserRole, backup)
                self.backup_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to list backups: {e}")
    
    def create_backup(self):
        """Create a new backup."""
        try:
            backup_file = self.backup_manager.create_backup(self.config)
            if backup_file:
                QMessageBox.information(self, "Success", f"Backup created: {backup_file.name}")
                self.refresh_backups()
            else:
                QMessageBox.warning(self, "Warning", "Failed to create backup")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create backup: {e}")
    
    def restore_backup(self):
        """Restore selected backup."""
        current_item = self.backup_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a backup to restore.")
            return
        
        backup = current_item.data(Qt.ItemDataRole.UserRole)
        try:
            if self.backup_manager.restore_backup(backup, self.config):
                QMessageBox.information(self, "Success", f"Backup restored: {backup[\"filename\"]}")
            else:
                QMessageBox.warning(self, "Warning", "Failed to restore backup")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restore backup: {e}")
    
    def delete_backup(self):
        """Delete selected backup."""
        current_item = self.backup_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a backup to delete.")
            return
        
        backup = current_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete backup {backup[\"filename\"]}?")
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.backup_manager.delete_backup(backup):
                    QMessageBox.information(self, "Success", "Backup deleted")
                    self.refresh_backups()
                else:
                    QMessageBox.warning(self, "Warning", "Failed to delete backup")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete backup: {e}")
