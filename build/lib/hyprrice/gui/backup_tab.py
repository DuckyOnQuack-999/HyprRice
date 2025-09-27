"""
Backup and history management tab for HyprRice GUI
"""

import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, 
    QListWidget, QListWidgetItem, QLabel, QLineEdit, QTextEdit,
    QMessageBox, QFileDialog, QGroupBox, QSplitter, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QSpinBox, QComboBox, QProgressBar, QFrame, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from ..backup_manager import BackupManager


class BackupTab(QWidget):
    """Tab for managing backups and history."""
    
    # Signals
    backup_created = pyqtSignal(str)
    backup_restored = pyqtSignal(str)
    history_updated = pyqtSignal()
    
    def __init__(self, config, backup_manager: BackupManager, preview_window=None):
        super().__init__()
        self.config = config
        self.backup_manager = backup_manager
        self.preview_window = preview_window
        
        self.init_ui()
        self.refresh_backups()
        self.refresh_history()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_backups)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Backup tab
        backup_tab = self.create_backup_tab()
        tab_widget.addTab(backup_tab, "Backups")
        
        # History tab
        history_tab = self.create_history_tab()
        tab_widget.addTab(history_tab, "History")
        
        # Undo/Redo tab
        undo_tab = self.create_undo_tab()
        tab_widget.addTab(undo_tab, "Undo/Redo")
    
    def create_backup_tab(self):
        """Create the backup management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Backup controls
        controls_group = QGroupBox("Backup Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Manual backup
        manual_layout = QHBoxLayout()
        self.backup_description = QLineEdit()
        self.backup_description.setPlaceholderText("Enter backup description...")
        manual_layout.addWidget(QLabel("Description:"))
        manual_layout.addWidget(self.backup_description)
        
        self.create_backup_btn = QPushButton("Create Backup")
        self.create_backup_btn.clicked.connect(self.create_backup)
        manual_layout.addWidget(self.create_backup_btn)
        
        controls_layout.addLayout(manual_layout)
        
        # Auto backup settings
        auto_layout = QHBoxLayout()
        self.auto_backup_checkbox = QCheckBox("Enable automatic backups")
        self.auto_backup_checkbox.setChecked(self.config.general.auto_backup)
        self.auto_backup_checkbox.toggled.connect(self.toggle_auto_backup)
        auto_layout.addWidget(self.auto_backup_checkbox)
        
        auto_layout.addStretch()
        
        self.backup_retention = QSpinBox()
        self.backup_retention.setRange(1, 365)
        self.backup_retention.setValue(self.config.general.backup_retention)
        self.backup_retention.valueChanged.connect(self.update_backup_retention)
        auto_layout.addWidget(QLabel("Retention (days):"))
        auto_layout.addWidget(self.backup_retention)
        
        controls_layout.addLayout(auto_layout)
        
        layout.addWidget(controls_group)
        
        # Backup list
        list_group = QGroupBox("Available Backups")
        list_layout = QVBoxLayout(list_group)
        
        # Backup list widget
        self.backup_list = QListWidget()
        self.backup_list.setSelectionMode(QListWidget.SingleSelection)
        self.backup_list.itemSelectionChanged.connect(self.on_backup_selection_changed)
        list_layout.addWidget(self.backup_list)
        
        # Backup actions
        actions_layout = QHBoxLayout()
        
        self.restore_backup_btn = QPushButton("Restore Selected")
        self.restore_backup_btn.clicked.connect(self.restore_backup)
        self.restore_backup_btn.setEnabled(False)
        actions_layout.addWidget(self.restore_backup_btn)
        
        self.delete_backup_btn = QPushButton("Delete Selected")
        self.delete_backup_btn.clicked.connect(self.delete_backup)
        self.delete_backup_btn.setEnabled(False)
        actions_layout.addWidget(self.delete_backup_btn)
        
        self.refresh_backups_btn = QPushButton("Refresh")
        self.refresh_backups_btn.clicked.connect(self.refresh_backups)
        actions_layout.addWidget(self.refresh_backups_btn)
        
        actions_layout.addStretch()
        
        self.export_backup_btn = QPushButton("Export Backup")
        self.export_backup_btn.clicked.connect(self.export_backup)
        self.export_backup_btn.setEnabled(False)
        actions_layout.addWidget(self.export_backup_btn)
        
        list_layout.addLayout(actions_layout)
        
        layout.addWidget(list_group)
        
        return widget
    
    def create_history_tab(self):
        """Create the history management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # History controls
        controls_group = QGroupBox("History Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.clicked.connect(self.clear_history)
        controls_layout.addWidget(self.clear_history_btn)
        
        self.export_history_btn = QPushButton("Export History")
        self.export_history_btn.clicked.connect(self.export_history)
        controls_layout.addWidget(self.export_history_btn)
        
        self.import_history_btn = QPushButton("Import History")
        self.import_history_btn.clicked.connect(self.import_history)
        controls_layout.addWidget(self.import_history_btn)
        
        controls_layout.addStretch()
        
        self.refresh_history_btn = QPushButton("Refresh")
        self.refresh_history_btn.clicked.connect(self.refresh_history)
        controls_layout.addWidget(self.refresh_history_btn)
        
        layout.addWidget(controls_group)
        
        # History table
        table_group = QGroupBox("History Entries")
        table_layout = QVBoxLayout(table_group)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Timestamp", "Action", "Description", "Details"])
        
        # Set column widths
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        table_layout.addWidget(self.history_table)
        
        layout.addWidget(table_group)
        
        return widget
    
    def create_undo_tab(self):
        """Create the undo/redo management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Undo/Redo controls
        controls_group = QGroupBox("Undo/Redo Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Status display
        status_layout = QHBoxLayout()
        
        self.undo_status = QLabel("Undo: Not available")
        self.undo_status.setStyleSheet("color: #d08770;")
        status_layout.addWidget(self.undo_status)
        
        self.redo_status = QLabel("Redo: Not available")
        self.redo_status.setStyleSheet("color: #d08770;")
        status_layout.addWidget(self.redo_status)
        
        status_layout.addStretch()
        
        controls_layout.addLayout(status_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo_action)
        self.undo_btn.setEnabled(False)
        button_layout.addWidget(self.undo_btn)
        
        self.redo_btn = QPushButton("Redo")
        self.redo_btn.clicked.connect(self.redo_action)
        self.redo_btn.setEnabled(False)
        button_layout.addWidget(self.redo_btn)
        
        button_layout.addStretch()
        
        self.save_state_btn = QPushButton("Save Current State")
        self.save_state_btn.clicked.connect(self.save_current_state)
        button_layout.addWidget(self.save_state_btn)
        
        controls_layout.addLayout(button_layout)
        
        layout.addWidget(controls_group)
        
        # Undo/Redo stacks
        stacks_group = QGroupBox("Action Stacks")
        stacks_layout = QHBoxLayout(stacks_group)
        
        # Undo stack
        undo_group = QGroupBox("Undo Stack")
        undo_layout = QVBoxLayout(undo_group)
        
        self.undo_stack_list = QListWidget()
        self.undo_stack_list.setMaximumHeight(200)
        undo_layout.addWidget(self.undo_stack_list)
        
        stacks_layout.addWidget(undo_group)
        
        # Redo stack
        redo_group = QGroupBox("Redo Stack")
        redo_layout = QVBoxLayout(redo_group)
        
        self.redo_stack_list = QListWidget()
        self.redo_stack_list.setMaximumHeight(200)
        redo_layout.addWidget(self.redo_stack_list)
        
        stacks_layout.addWidget(redo_group)
        
        layout.addWidget(stacks_group)
        
        # Update undo/redo status
        self.update_undo_redo_status()
        
        return widget
    
    def create_backup(self):
        """Create a new backup."""
        description = self.backup_description.text().strip()
        if not description:
            description = "Manual backup"
        
        if self.backup_manager.create_backup(description):
            self.backup_description.clear()
            self.refresh_backups()
            self.backup_created.emit(description)
            QMessageBox.information(self, "Success", f"Backup created: {description}")
        else:
            QMessageBox.warning(self, "Error", "Failed to create backup")
    
    def restore_backup(self):
        """Restore the selected backup."""
        current_item = self.backup_list.currentItem()
        if not current_item:
            return
        
        backup_name = current_item.text()
        
        reply = QMessageBox.question(
            self, "Confirm Restore",
            f"Are you sure you want to restore backup '{backup_name}'?\n"
            "This will overwrite your current configuration.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.backup_manager.restore_backup(backup_name):
                self.refresh_backups()
                self.backup_restored.emit(backup_name)
                QMessageBox.information(self, "Success", f"Configuration restored from: {backup_name}")
            else:
                QMessageBox.warning(self, "Error", "Failed to restore backup")
    
    def delete_backup(self):
        """Delete the selected backup."""
        current_item = self.backup_list.currentItem()
        if not current_item:
            return
        
        backup_name = current_item.text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete backup '{backup_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.backup_manager.delete_backup(backup_name):
                self.refresh_backups()
                QMessageBox.information(self, "Success", f"Backup deleted: {backup_name}")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete backup")
    
    def export_backup(self):
        """Export the selected backup."""
        current_item = self.backup_list.currentItem()
        if not current_item:
            return
        
        backup_name = current_item.text()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Backup", f"{backup_name}.tar.gz",
            "Archive Files (*.tar.gz);;All Files (*)"
        )
        
        if file_path:
            try:
                import shutil
                source_path = os.path.join(self.config.paths.backup_dir, backup_name)
                shutil.copy2(source_path, file_path)
                QMessageBox.information(self, "Success", f"Backup exported to: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export backup: {e}")
    
    def refresh_backups(self):
        """Refresh the backup list."""
        self.backup_list.clear()
        
        backups = self.backup_manager.list_backups()
        for backup in backups:
            item = QListWidgetItem(backup['name'])
            item.setToolTip(f"Created: {backup['created']}\nSize: {backup['size']} bytes")
            self.backup_list.addItem(item)
    
    def on_backup_selection_changed(self):
        """Handle backup selection change."""
        has_selection = self.backup_list.currentItem() is not None
        self.restore_backup_btn.setEnabled(has_selection)
        self.delete_backup_btn.setEnabled(has_selection)
        self.export_backup_btn.setEnabled(has_selection)
    
    def toggle_auto_backup(self, enabled):
        """Toggle automatic backup."""
        self.config.general.auto_backup = enabled
        self.config.save()
    
    def update_backup_retention(self, days):
        """Update backup retention period."""
        self.config.general.backup_retention = days
        self.config.save()
    
    def clear_history(self):
        """Clear all history."""
        reply = QMessageBox.question(
            self, "Confirm Clear",
            "Are you sure you want to clear all history?\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.backup_manager.clear_history():
                self.refresh_history()
                self.history_updated.emit()
                QMessageBox.information(self, "Success", "History cleared")
            else:
                QMessageBox.warning(self, "Error", "Failed to clear history")
    
    def export_history(self):
        """Export history to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export History", "hyprrice_history.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            if self.backup_manager.export_history(file_path):
                QMessageBox.information(self, "Success", f"History exported to: {file_path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to export history")
    
    def import_history(self):
        """Import history from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import History", "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            if self.backup_manager.import_history(file_path):
                self.refresh_history()
                self.history_updated.emit()
                QMessageBox.information(self, "Success", f"History imported from: {file_path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to import history")
    
    def refresh_history(self):
        """Refresh the history table."""
        self.history_table.setRowCount(0)
        
        history = self.backup_manager.get_history(100)  # Get last 100 entries
        
        for entry in history:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            # Timestamp
            timestamp_item = QTableWidgetItem(entry['timestamp'])
            self.history_table.setItem(row, 0, timestamp_item)
            
            # Action
            action_item = QTableWidgetItem(entry['action'])
            self.history_table.setItem(row, 1, action_item)
            
            # Description
            desc_item = QTableWidgetItem(entry['description'])
            self.history_table.setItem(row, 2, desc_item)
            
            # Details
            details = ""
            if entry.get('file_path'):
                details = f"File: {entry['file_path']}"
            elif entry.get('config_snapshot'):
                details = "Config snapshot available"
            
            details_item = QTableWidgetItem(details)
            self.history_table.setItem(row, 3, details_item)
    
    def undo_action(self):
        """Undo the last action."""
        if self.backup_manager.undo():
            self.update_undo_redo_status()
            self.refresh_history()
            self.history_updated.emit()
            QMessageBox.information(self, "Success", "Action undone")
        else:
            QMessageBox.warning(self, "Error", "Nothing to undo")
    
    def redo_action(self):
        """Redo the last undone action."""
        if self.backup_manager.redo():
            self.update_undo_redo_status()
            self.refresh_history()
            self.history_updated.emit()
            QMessageBox.information(self, "Success", "Action redone")
        else:
            QMessageBox.warning(self, "Error", "Nothing to redo")
    
    def save_current_state(self):
        """Save current state for undo/redo."""
        description, ok = QInputDialog.getText(
            self, "Save State", "Enter description for this state:"
        )
        
        if ok and description:
            self.backup_manager.save_state("manual_save", description)
            self.update_undo_redo_status()
            self.refresh_history()
            self.history_updated.emit()
            QMessageBox.information(self, "Success", "State saved")
    
    def update_undo_redo_status(self):
        """Update undo/redo status and button states."""
        can_undo = self.backup_manager.can_undo()
        can_redo = self.backup_manager.can_redo()
        
        self.undo_btn.setEnabled(can_undo)
        self.redo_btn.setEnabled(can_redo)
        
        if can_undo:
            self.undo_status.setText("Undo: Available")
            self.undo_status.setStyleSheet("color: #a3be8c;")
        else:
            self.undo_status.setText("Undo: Not available")
            self.undo_status.setStyleSheet("color: #d08770;")
        
        if can_redo:
            self.redo_status.setText("Redo: Available")
            self.redo_status.setStyleSheet("color: #a3be8c;")
        else:
            self.redo_status.setText("Redo: Not available")
            self.redo_status.setStyleSheet("color: #d08770;")
        
        # Update stack lists
        self.undo_stack_list.clear()
        self.redo_stack_list.clear()
        
        # Note: We don't have direct access to the stacks, so we'll show placeholder text
        if can_undo:
            self.undo_stack_list.addItem("Actions available for undo")
        if can_redo:
            self.redo_stack_list.addItem("Actions available for redo")
    
    def closeEvent(self, event):
        """Handle close event."""
        self.refresh_timer.stop()
        event.accept()
