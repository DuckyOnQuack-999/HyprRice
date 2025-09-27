"""Plugin manager dialog for HyprRice."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QDialogButtonBox, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal

class PluginManagerDialog(QDialog):
    plugin_status_changed = pyqtSignal(str, str)  # plugin_name, action
    
    def __init__(self, plugin_manager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.setup_ui()
        self.refresh_plugins()
    
    def setup_ui(self):
        self.setWindowTitle("Plugin Manager")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Plugin Manager")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Plugin list
        self.plugin_list = QListWidget()
        layout.addWidget(self.plugin_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        load_btn = QPushButton("Load Plugin")
        load_btn.clicked.connect(self.load_plugin)
        btn_layout.addWidget(load_btn)
        
        unload_btn = QPushButton("Unload Plugin")
        unload_btn.clicked.connect(self.unload_plugin)
        btn_layout.addWidget(unload_btn)
        
        reload_btn = QPushButton("Reload Plugin")
        reload_btn.clicked.connect(self.reload_plugin)
        btn_layout.addWidget(reload_btn)
        
        layout.addLayout(btn_layout)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def refresh_plugins(self):
        """Refresh the plugin list."""
        self.plugin_list.clear()
        try:
            available_plugins = self.plugin_manager.list_available_plugins()
            loaded_plugins = self.plugin_manager.list_loaded_plugins()
            
            for plugin_name in available_plugins:
                status = "Loaded" if plugin_name in loaded_plugins else "Available"
                item = QListWidgetItem(f"{plugin_name} - {status}")
                item.setData(Qt.ItemDataRole.UserRole, plugin_name)
                self.plugin_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to list plugins: {e}")
    
    def load_plugin(self):
        """Load selected plugin."""
        current_item = self.plugin_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a plugin to load.")
            return
        
        plugin_name = current_item.data(Qt.ItemDataRole.UserRole)
        try:
            if self.plugin_manager.load_plugin(plugin_name, self.parent()):
                QMessageBox.information(self, "Success", f"Plugin loaded: {plugin_name}")
                self.plugin_status_changed.emit(plugin_name, "loaded")
                self.refresh_plugins()
            else:
                QMessageBox.warning(self, "Warning", f"Failed to load plugin: {plugin_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load plugin: {e}")
    
    def unload_plugin(self):
        """Unload selected plugin."""
        current_item = self.plugin_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a plugin to unload.")
            return
        
        plugin_name = current_item.data(Qt.ItemDataRole.UserRole)
        try:
            if self.plugin_manager.unload_plugin(plugin_name):
                QMessageBox.information(self, "Success", f"Plugin unloaded: {plugin_name}")
                self.plugin_status_changed.emit(plugin_name, "unloaded")
                self.refresh_plugins()
            else:
                QMessageBox.warning(self, "Warning", f"Failed to unload plugin: {plugin_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to unload plugin: {e}")
    
    def reload_plugin(self):
        """Reload selected plugin."""
        current_item = self.plugin_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a plugin to reload.")
            return
        
        plugin_name = current_item.data(Qt.ItemDataRole.UserRole)
        try:
            if self.plugin_manager.reload_plugin(plugin_name, self.parent()):
                QMessageBox.information(self, "Success", f"Plugin reloaded: {plugin_name}")
                self.plugin_status_changed.emit(plugin_name, "reloaded")
                self.refresh_plugins()
            else:
                QMessageBox.warning(self, "Warning", f"Failed to reload plugin: {plugin_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reload plugin: {e}")
