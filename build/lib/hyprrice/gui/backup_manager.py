"""
Backup selection dialog for HyprRice
"""

from typing import List, Optional
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QTextEdit, QSplitter
)
from PyQt5.QtCore import Qt


class BackupSelectionDialog(QDialog):
    """Dialog for selecting a backup to restore."""
    
    def __init__(self, backups: List[Path], parent=None):
        super().__init__(parent)
        self.backups = backups
        self.selected_backup = None
        
        self.setWindowTitle("Select Backup to Restore")
        self.setModal(True)
        self.resize(600, 400)
        
        self.setup_ui()
        self.load_backups()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title label
        title_label = QLabel("Select a backup to restore:")
        layout.addWidget(title_label)
        
        # Splitter for list and preview
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Backup list
        self.backup_list = QListWidget()
        self.backup_list.currentItemChanged.connect(self.on_backup_selected)
        splitter.addWidget(self.backup_list)
        
        # Backup info panel
        info_panel = QVBoxLayout()
        info_widget = QLabel()
        info_widget.setLayout(info_panel)
        
        self.info_label = QLabel("Select a backup to view details")
        self.info_label.setWordWrap(True)
        info_panel.addWidget(self.info_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        info_panel.addWidget(self.preview_text)
        
        splitter.addWidget(info_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.restore_button = QPushButton("Restore")
        self.restore_button.clicked.connect(self.accept)
        self.restore_button.setEnabled(False)
        button_layout.addWidget(self.restore_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def load_backups(self):
        """Load backups into the list."""
        for backup_path in self.backups:
            # Create display text
            backup_name = backup_path.name
            
            # Try to extract timestamp from filename
            try:
                # Assume format like: backup_2023-12-01_14-30-45.yaml
                if '_' in backup_name:
                    parts = backup_name.split('_')
                    if len(parts) >= 3:
                        date_part = parts[1]
                        time_part = parts[2].split('.')[0]  # Remove extension
                        
                        # Format display name
                        display_name = f"{date_part} {time_part.replace('-', ':')}"
                    else:
                        display_name = backup_name
                else:
                    display_name = backup_name
            except:
                display_name = backup_name
            
            # Add file size
            try:
                size_bytes = backup_path.stat().st_size
                size_kb = size_bytes / 1024
                if size_kb < 1024:
                    size_str = f"{size_kb:.1f} KB"
                else:
                    size_mb = size_kb / 1024
                    size_str = f"{size_mb:.1f} MB"
                
                display_name += f" ({size_str})"
            except:
                pass
            
            # Create list item
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, backup_path)
            self.backup_list.addItem(item)
        
        # Select first item if available
        if self.backup_list.count() > 0:
            self.backup_list.setCurrentRow(0)
    
    def on_backup_selected(self, current, previous):
        """Handle backup selection change."""
        if current is None:
            self.selected_backup = None
            self.restore_button.setEnabled(False)
            self.info_label.setText("Select a backup to view details")
            self.preview_text.clear()
            return
        
        backup_path = current.data(Qt.UserRole)
        self.selected_backup = backup_path
        self.restore_button.setEnabled(True)
        
        # Update info panel
        try:
            # Get file stats
            stat = backup_path.stat()
            created_time = datetime.fromtimestamp(stat.st_ctime)
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            size_bytes = stat.st_size
            
            info_text = f"""
<b>Backup Details:</b><br>
<b>File:</b> {backup_path.name}<br>
<b>Created:</b> {created_time.strftime('%Y-%m-%d %H:%M:%S')}<br>
<b>Modified:</b> {modified_time.strftime('%Y-%m-%d %H:%M:%S')}<br>
<b>Size:</b> {size_bytes:,} bytes<br>
<b>Path:</b> {backup_path}
            """.strip()
            
            self.info_label.setText(info_text)
            
            # Load preview of backup content
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Limit preview to first 1000 characters
                    if len(content) > 1000:
                        preview = content[:1000] + "\n... (truncated)"
                    else:
                        preview = content
                    
                    self.preview_text.setPlainText(preview)
            except Exception as e:
                self.preview_text.setPlainText(f"Error reading backup file: {str(e)}")
                
        except Exception as e:
            self.info_label.setText(f"Error reading backup info: {str(e)}")
            self.preview_text.clear()
    
    def get_selected_backup(self) -> Optional[Path]:
        """Get the selected backup path."""
        return self.selected_backup
