"""
Plugin Management GUI for HyprRice

Provides a comprehensive interface for managing plugins including:
- Plugin discovery and browsing
- Plugin installation and removal
- Plugin configuration
- Plugin status monitoring
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QTextEdit,
    QGroupBox, QFormLayout, QLineEdit, QSpinBox, QCheckBox,
    QComboBox, QMessageBox, QProgressBar, QSplitter, QFrame,
    QScrollArea, QGridLayout, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap

from ..plugins import EnhancedPluginManager, PluginMetadata


class PluginConfigWidget(QWidget):
    """Widget for configuring plugin settings"""
    
    def __init__(self, plugin_name: str, config_schema: Dict[str, Any], current_config: Dict[str, Any]):
        super().__init__()
        self.plugin_name = plugin_name
        self.config_schema = config_schema
        self.current_config = current_config
        self.config_widgets = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the configuration UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(f"Configure {self.plugin_name}")
        title.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Scroll area for config options
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        config_widget = QWidget()
        config_layout = QFormLayout(config_widget)
        
        # Generate config widgets based on schema
        for key, schema in self.config_schema.items():
            widget = self._create_config_widget(key, schema)
            if widget:
                label = QLabel(key.replace('_', ' ').title())
                if 'description' in schema:
                    label.setToolTip(schema['description'])
                config_layout.addRow(label, widget)
                self.config_widgets[key] = widget
        
        scroll.setWidget(config_widget)
        layout.addWidget(scroll)
        
    def _create_config_widget(self, key: str, schema: Dict[str, Any]) -> Optional[QWidget]:
        """Create appropriate widget for config option"""
        current_value = self.current_config.get(key, schema.get('default'))
        
        widget_type = schema.get('type', 'string')
        
        if widget_type == 'boolean':
            widget = QCheckBox()
            widget.setChecked(current_value if current_value is not None else False)
            return widget
            
        elif widget_type == 'integer':
            widget = QSpinBox()
            widget.setRange(schema.get('minimum', 0), schema.get('maximum', 999999))
            widget.setValue(current_value if current_value is not None else schema.get('default', 0))
            return widget
            
        elif widget_type == 'string':
            if 'enum' in schema:
                widget = QComboBox()
                widget.addItems(schema['enum'])
                if current_value in schema['enum']:
                    widget.setCurrentText(current_value)
                return widget
            else:
                widget = QLineEdit()
                widget.setText(str(current_value) if current_value is not None else '')
                return widget
                
        elif widget_type == 'array':
            # For arrays, create a text edit with comma-separated values
            widget = QLineEdit()
            if current_value:
                widget.setText(', '.join(str(v) for v in current_value))
            return widget
            
        return None
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration from widgets"""
        config = {}
        
        for key, widget in self.config_widgets.items():
            schema = self.config_schema[key]
            widget_type = schema.get('type', 'string')
            
            if widget_type == 'boolean':
                config[key] = widget.isChecked()
            elif widget_type == 'integer':
                config[key] = widget.value()
            elif widget_type == 'string':
                if isinstance(widget, QComboBox):
                    config[key] = widget.currentText()
                else:
                    config[key] = widget.text()
            elif widget_type == 'array':
                text = widget.text().strip()
                if text:
                    config[key] = [item.strip() for item in text.split(',')]
                else:
                    config[key] = []
                    
        return config


class PluginDetailsWidget(QWidget):
    """Widget showing detailed plugin information"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the details UI"""
        layout = QVBoxLayout(self)
        
        # Plugin info section
        info_group = QGroupBox("Plugin Information")
        info_layout = QFormLayout(info_group)
        
        self.name_label = QLabel()
        self.name_label.setFont(QFont("", 12, QFont.Weight.Bold))
        self.version_label = QLabel()
        self.author_label = QLabel()
        self.description_text = QTextEdit()
        self.description_text.setMaximumHeight(100)
        self.description_text.setReadOnly(True)
        
        info_layout.addRow("Name:", self.name_label)
        info_layout.addRow("Version:", self.version_label)
        info_layout.addRow("Author:", self.author_label)
        info_layout.addRow("Description:", self.description_text)
        
        layout.addWidget(info_group)
        
        # Status section
        status_group = QGroupBox("Status")
        status_layout = QFormLayout(status_group)
        
        self.loaded_label = QLabel()
        self.enabled_label = QLabel()
        self.dependencies_label = QLabel()
        
        status_layout.addRow("Loaded:", self.loaded_label)
        status_layout.addRow("Enabled:", self.enabled_label)
        status_layout.addRow("Dependencies:", self.dependencies_label)
        
        layout.addWidget(status_group)
        
        # Actions section
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.load_button = QPushButton("Load")
        self.unload_button = QPushButton("Unload")
        self.enable_button = QPushButton("Enable")
        self.disable_button = QPushButton("Disable")
        self.configure_button = QPushButton("Configure")
        self.reload_button = QPushButton("Reload")
        
        actions_layout.addWidget(self.load_button)
        actions_layout.addWidget(self.unload_button)
        actions_layout.addWidget(self.enable_button)
        actions_layout.addWidget(self.disable_button)
        actions_layout.addWidget(self.configure_button)
        actions_layout.addWidget(self.reload_button)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
    def update_plugin_info(self, plugin_info: Dict[str, Any]):
        """Update the display with plugin information"""
        metadata = plugin_info.get('metadata')
        if metadata:
            self.name_label.setText(metadata['name'])
            self.version_label.setText(metadata['version'])
            self.author_label.setText(metadata['author'])
            self.description_text.setText(metadata['description'])
            
            # Format dependencies
            deps = metadata.get('dependencies', [])
            if deps:
                self.dependencies_label.setText(', '.join(deps))
            else:
                self.dependencies_label.setText("None")
        
        # Update status
        self.loaded_label.setText("Yes" if plugin_info['loaded'] else "No")
        self.enabled_label.setText("Yes" if plugin_info['enabled'] else "No")
        
        # Update button states
        is_loaded = plugin_info['loaded']
        is_enabled = plugin_info['enabled']
        
        self.load_button.setEnabled(not is_loaded)
        self.unload_button.setEnabled(is_loaded)
        self.enable_button.setEnabled(not is_enabled)
        self.disable_button.setEnabled(is_enabled)
        self.configure_button.setEnabled(True)
        self.reload_button.setEnabled(is_loaded)


class PluginManagerDialog(QDialog):
    """Main plugin manager dialog"""
    
    plugin_status_changed = pyqtSignal(str, str)  # plugin_name, action
    
    def __init__(self, plugin_manager: EnhancedPluginManager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.logger = logging.getLogger("PluginManagerGUI")
        self.current_plugin = None
        self.setup_ui()
        self.refresh_plugin_list()
        
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("Plugin Manager")
        self.setMinimumSize(900, 600)
        
        layout = QVBoxLayout(self)
        
        # Create splitter for plugin list and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Plugin list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Plugin list header
        list_header = QLabel("Available Plugins")
        list_header.setFont(QFont("", 12, QFont.Weight.Bold))
        left_layout.addWidget(list_header)
        
        # Plugin list
        self.plugin_list = QListWidget()
        self.plugin_list.currentItemChanged.connect(self.on_plugin_selected)
        left_layout.addWidget(self.plugin_list)
        
        # List controls
        list_controls = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_plugin_list)
        list_controls.addWidget(self.refresh_button)
        list_controls.addStretch()
        left_layout.addLayout(list_controls)
        
        splitter.addWidget(left_widget)
        
        # Right side: Plugin details and configuration
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Plugin details
        self.details_widget = PluginDetailsWidget()
        right_layout.addWidget(self.details_widget)
        
        # Connect action buttons
        self.details_widget.load_button.clicked.connect(self.load_plugin)
        self.details_widget.unload_button.clicked.connect(self.unload_plugin)
        self.details_widget.enable_button.clicked.connect(self.enable_plugin)
        self.details_widget.disable_button.clicked.connect(self.disable_plugin)
        self.details_widget.configure_button.clicked.connect(self.configure_plugin)
        self.details_widget.reload_button.clicked.connect(self.reload_plugin)
        
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setSizes([300, 600])
        layout.addWidget(splitter)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
    def refresh_plugin_list(self):
        """Refresh the plugin list"""
        self.plugin_list.clear()
        
        plugins = self.plugin_manager.list_available_plugins()
        for plugin_info in plugins:
            item = QListWidgetItem()
            
            # Format display text
            name = plugin_info['name']
            status_indicators = []
            
            if plugin_info['loaded']:
                status_indicators.append("●")  # Loaded indicator
            if plugin_info['enabled']:
                status_indicators.append("✓")  # Enabled indicator
                
            display_text = f"{name}"
            if status_indicators:
                display_text += f" [{' '.join(status_indicators)}]"
                
            item.setText(display_text)
            item.setData(Qt.UserRole, plugin_info)
            
            # Color coding
            if plugin_info['loaded']:
                item.setForeground(QColor("green"))
            elif plugin_info['enabled']:
                item.setForeground(QColor("blue"))
            else:
                item.setForeground(QColor("gray"))
                
            self.plugin_list.addItem(item)
    
    def on_plugin_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Handle plugin selection"""
        if current:
            plugin_info = current.data(Qt.UserRole)
            self.current_plugin = plugin_info['name']
            self.details_widget.update_plugin_info(plugin_info)
    
    def load_plugin(self):
        """Load the selected plugin"""
        if not self.current_plugin:
            return
            
        try:
            success = self.plugin_manager.load_plugin(self.current_plugin)
            if success:
                QMessageBox.information(self, "Success", f"Plugin '{self.current_plugin}' loaded successfully")
                self.refresh_plugin_list()
                self.plugin_status_changed.emit(self.current_plugin, "loaded")
            else:
                QMessageBox.warning(self, "Error", f"Failed to load plugin '{self.current_plugin}'")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading plugin '{self.current_plugin}':\n{str(e)}")
    
    def unload_plugin(self):
        """Unload the selected plugin"""
        if not self.current_plugin:
            return
            
        try:
            success = self.plugin_manager.unload_plugin(self.current_plugin)
            if success:
                QMessageBox.information(self, "Success", f"Plugin '{self.current_plugin}' unloaded successfully")
                self.refresh_plugin_list()
                self.plugin_status_changed.emit(self.current_plugin, "unloaded")
            else:
                QMessageBox.warning(self, "Error", f"Failed to unload plugin '{self.current_plugin}'")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error unloading plugin '{self.current_plugin}':\n{str(e)}")
    
    def enable_plugin(self):
        """Enable the selected plugin"""
        if not self.current_plugin:
            return
            
        success = self.plugin_manager.enable_plugin(self.current_plugin)
        if success:
            QMessageBox.information(self, "Success", f"Plugin '{self.current_plugin}' enabled")
            self.refresh_plugin_list()
            self.plugin_status_changed.emit(self.current_plugin, "enabled")
        else:
            QMessageBox.warning(self, "Error", f"Failed to enable plugin '{self.current_plugin}'")
    
    def disable_plugin(self):
        """Disable the selected plugin"""
        if not self.current_plugin:
            return
            
        success = self.plugin_manager.disable_plugin(self.current_plugin)
        if success:
            QMessageBox.information(self, "Success", f"Plugin '{self.current_plugin}' disabled")
            self.refresh_plugin_list()
            self.plugin_status_changed.emit(self.current_plugin, "disabled")
        else:
            QMessageBox.warning(self, "Error", f"Failed to disable plugin '{self.current_plugin}'")
    
    def configure_plugin(self):
        """Configure the selected plugin"""
        if not self.current_plugin:
            return
            
        # Get plugin metadata and current config
        plugins = self.plugin_manager.list_available_plugins()
        plugin_info = next((p for p in plugins if p['name'] == self.current_plugin), None)
        
        if not plugin_info or not plugin_info['metadata']:
            QMessageBox.warning(self, "Error", "Plugin metadata not available")
            return
            
        config_schema = plugin_info['metadata'].get('config_schema', {})
        if not config_schema:
            QMessageBox.information(self, "Info", f"Plugin '{self.current_plugin}' has no configuration options")
            return
            
        current_config = self.plugin_manager.get_plugin_config(self.current_plugin)
        
        # Create configuration dialog
        config_dialog = QDialog(self)
        config_dialog.setWindowTitle(f"Configure {self.current_plugin}")
        config_dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(config_dialog)
        
        # Config widget
        config_widget = PluginConfigWidget(self.current_plugin, config_schema, current_config)
        layout.addWidget(config_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(config_dialog.accept)
        cancel_button.clicked.connect(config_dialog.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Show dialog
        if config_dialog.exec_() == QDialog.Accepted:
            new_config = config_widget.get_config()
            self.plugin_manager.configure_plugin(self.current_plugin, new_config)
            QMessageBox.information(self, "Success", f"Configuration saved for '{self.current_plugin}'")
            self.plugin_status_changed.emit(self.current_plugin, "configured")
    
    def reload_plugin(self):
        """Reload the selected plugin"""
        if not self.current_plugin:
            return
            
        try:
            success = self.plugin_manager.reload_plugin(self.current_plugin)
            if success:
                QMessageBox.information(self, "Success", f"Plugin '{self.current_plugin}' reloaded successfully")
                self.refresh_plugin_list()
                self.plugin_status_changed.emit(self.current_plugin, "reloaded")
            else:
                QMessageBox.warning(self, "Error", f"Failed to reload plugin '{self.current_plugin}'")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reloading plugin '{self.current_plugin}':\n{str(e)}")


# Convenience function for showing plugin manager
def show_plugin_manager(plugin_manager: EnhancedPluginManager, parent=None):
    """Show the plugin manager dialog"""
    dialog = PluginManagerDialog(plugin_manager, parent)
    return dialog.exec_()
