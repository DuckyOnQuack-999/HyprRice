"""
Configuration File Editor for HyprRice
Provides a dedicated text editor for manual configuration file editing
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
    QLabel, QFileDialog, QMessageBox, QMenuBar, QMenu, QStatusBar,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget, QWidget,
    QToolBar, QComboBox, QLineEdit, QCheckBox, QSpinBox, QFormLayout,
    QGroupBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QFileSystemWatcher
from PyQt6.QtGui import QFont, QTextCursor, QAction, QKeySequence, QIcon
from ..utils import backup_file, validate_sourced_file
from ..security import SecureFileHandler
import logging


class ConfigEditor(QDialog):
    """Dedicated configuration file editor with syntax highlighting and validation."""
    
    file_saved = pyqtSignal(str)  # Emitted when a file is saved
    file_modified = pyqtSignal(str, bool)  # Emitted when file modification status changes
    
    def __init__(self, parent=None, file_path: Optional[str] = None):
        super().__init__(parent)
        self.setWindowTitle("HyprRice Configuration Editor")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        self.current_file = None
        self.is_modified = False
        self.backup_manager = None
        self.logger = logging.getLogger(__name__)
        
        # File system watcher for external changes
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self._on_file_changed_externally)
        
        self._setup_ui()
        self._setup_shortcuts()
        self._setup_connections()
        
        # Load file if provided
        if file_path:
            self.load_file(file_path)
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create toolbar
        self._create_toolbar()
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - file browser and tools
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - editor tabs
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self._close_tab)
        splitter.addWidget(self.editor_tabs)
        
        # Set splitter proportions
        splitter.setSizes([300, 900])
        
        # Create status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        
        # Status bar widgets
        self.file_status_label = QLabel("No file open")
        self.cursor_position_label = QLabel("Line 1, Column 1")
        self.modified_label = QLabel("")
        
        self.status_bar.addWidget(self.file_status_label)
        self.status_bar.addPermanentWidget(self.cursor_position_label)
        self.status_bar.addPermanentWidget(self.modified_label)
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = QMenuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        close_action = QAction("&Close", self)
        close_action.setShortcut(QKeySequence.StandardKey.Close)
        close_action.triggered.connect(self._close_current_tab)
        file_menu.addAction(close_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Find", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self._find_text)
        edit_menu.addAction(find_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        validate_action = QAction("&Validate Configuration", self)
        validate_action.triggered.connect(self._validate_config)
        tools_menu.addAction(validate_action)
        
        format_action = QAction("&Format Configuration", self)
        format_action.triggered.connect(self._format_config)
        tools_menu.addAction(format_action)
        
        tools_menu.addSeparator()
        
        backup_action = QAction("&Create Backup", self)
        backup_action.triggered.connect(self._create_backup)
        tools_menu.addAction(backup_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
        # Add menubar to layout
        layout = self.layout()
        layout.setMenuBar(menubar)
    
    def _create_toolbar(self):
        """Create the toolbar."""
        toolbar = QToolBar()
        
        # File actions
        new_btn = toolbar.addAction("New")
        new_btn.triggered.connect(self._new_file)
        
        open_btn = toolbar.addAction("Open")
        open_btn.triggered.connect(self._open_file)
        
        save_btn = toolbar.addAction("Save")
        save_btn.triggered.connect(self._save_file)
        
        toolbar.addSeparator()
        
        # Edit actions
        undo_btn = toolbar.addAction("Undo")
        undo_btn.triggered.connect(self._undo)
        
        redo_btn = toolbar.addAction("Redo")
        redo_btn.triggered.connect(self._redo)
        
        toolbar.addSeparator()
        
        # Tools
        validate_btn = toolbar.addAction("Validate")
        validate_btn.triggered.connect(self._validate_config)
        
        format_btn = toolbar.addAction("Format")
        format_btn.triggered.connect(self._format_config)
        
        # Add toolbar to layout
        layout = self.layout()
        layout.insertWidget(0, toolbar)
    
    def _create_left_panel(self):
        """Create the left panel with file browser and tools."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # File browser
        browser_group = QGroupBox("Configuration Files")
        browser_layout = QVBoxLayout(browser_group)
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("Files")
        self.file_tree.itemDoubleClicked.connect(self._open_file_from_tree)
        browser_layout.addWidget(self.file_tree)
        
        # File browser buttons
        browser_btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_file_tree)
        browser_btn_layout.addWidget(refresh_btn)
        
        new_file_btn = QPushButton("New File")
        new_file_btn.clicked.connect(self._new_file)
        browser_btn_layout.addWidget(new_file_btn)
        
        browser_layout.addLayout(browser_btn_layout)
        layout.addWidget(browser_group)
        
        # Quick tools
        tools_group = QGroupBox("Quick Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        # Configuration type selector
        type_layout = QFormLayout()
        
        self.config_type_combo = QComboBox()
        self.config_type_combo.addItems([
            "Hyprland Main Config",
            "Environment Variables (env.conf)",
            "General Settings (general.conf)",
            "Input Settings (input.conf)",
            "Decoration Settings (decoration.conf)",
            "Animation Settings (animations.conf)",
            "Keybindings (keybinds.conf)",
            "Window Rules (rules.conf)",
            "Exec Commands (execs.conf)",
            "Workspace Rules",
            "Monitor Settings",
            "Plugin Settings",
            "Waybar Config",
            "Rofi Config",
            "Dunst Config",
            "Custom"
        ])
        type_layout.addRow("Type:", self.config_type_combo)
        
        tools_layout.addLayout(type_layout)
        
        # Template buttons
        template_btn = QPushButton("Insert Template")
        template_btn.clicked.connect(self._insert_template)
        tools_layout.addWidget(template_btn)
        
        validate_btn = QPushButton("Validate Current")
        validate_btn.clicked.connect(self._validate_config)
        tools_layout.addWidget(validate_btn)
        
        format_btn = QPushButton("Format Current")
        format_btn.clicked.connect(self._format_config)
        tools_layout.addWidget(format_btn)
        
        layout.addWidget(tools_group)
        
        # Configuration info
        info_group = QGroupBox("File Info")
        info_layout = QVBoxLayout(info_group)
        
        self.file_info_label = QLabel("No file selected")
        self.file_info_label.setWordWrap(True)
        info_layout.addWidget(self.file_info_label)
        
        layout.addWidget(info_group)
        
        # Initialize file tree
        self._refresh_file_tree()
        
        return panel
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Additional shortcuts can be added here
        pass
    
    def _setup_connections(self):
        """Setup signal connections."""
        # Timer for auto-save (if enabled)
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.setInterval(30000)  # 30 seconds
    
    def _create_editor_tab(self, file_path: str) -> QTextEdit:
        """Create a new editor tab for the given file."""
        editor = QTextEdit()
        editor.setFont(QFont("JetBrainsMono Nerd Font", 11))
        editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Connect signals
        editor.textChanged.connect(lambda: self._on_text_changed(file_path))
        editor.cursorPositionChanged.connect(self._update_cursor_position)
        
        # Add to tabs
        file_name = os.path.basename(file_path)
        tab_index = self.editor_tabs.addTab(editor, file_name)
        self.editor_tabs.setCurrentIndex(tab_index)
        
        # Set tooltip with full path
        self.editor_tabs.setTabToolTip(tab_index, file_path)
        
        return editor
    
    def load_file(self, file_path: str) -> bool:
        """Load a file into the editor."""
        try:
            file_path = os.path.expanduser(file_path)
            
            # Validate and canonicalize path
            from ..security import InputValidator
            validator = InputValidator()
            try:
                canonical_path = validator.validate_path(file_path)
            except Exception as e:
                QMessageBox.warning(self, "Security Warning", 
                                  f"Path is not safe: {file_path} - {e}")
                return False
            
            if not os.path.exists(canonical_path):
                # Create file if it doesn't exist
                os.makedirs(os.path.dirname(canonical_path), exist_ok=True)
                secure_handler.write_file(canonical_path, "")
            
            # Check if file is already open
            for i in range(self.editor_tabs.count()):
                if self.editor_tabs.tabToolTip(i) == canonical_path:
                    self.editor_tabs.setCurrentIndex(i)
                    return True
            
            # Create new tab
            editor = self._create_editor_tab(canonical_path)
            
            # Load file content securely
            content = secure_handler.read_file(canonical_path)
            
            editor.setPlainText(content)
            
            # Add to file watcher
            self.file_watcher.addPath(canonical_path)
            
            # Update status
            self.current_file = canonical_path
            self.file_status_label.setText(f"File: {os.path.basename(canonical_path)}")
            self._update_file_info(canonical_path)
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {e}")
            return False
    
    def _save_file(self) -> bool:
        """Save the current file."""
        current_editor = self._get_current_editor()
        if not current_editor or not self.current_file:
            return False
        
        try:
            # Validate path before saving
            from ..security import InputValidator
            validator = InputValidator()
            try:
                canonical_path = validator.validate_path(self.current_file)
            except Exception as e:
                QMessageBox.warning(self, "Security Warning", 
                                  f"Path is not safe: {self.current_file} - {e}")
                return False
            
            # Create backup before saving
            if os.path.exists(canonical_path):
                backup_file(canonical_path, os.path.dirname(canonical_path) + "/.backups/")
            
            # Save file securely
            content = current_editor.toPlainText()
            secure_handler.write_file(canonical_path, content)
            
            # Update status
            self.is_modified = False
            self._update_modified_status()
            self.file_saved.emit(canonical_path)
            
            self.status_bar.showMessage(f"File saved: {os.path.basename(canonical_path)}", 2000)
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
            return False
    
    def _get_current_editor(self) -> Optional[QTextEdit]:
        """Get the current editor widget."""
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, QTextEdit):
            return current_widget
        return None
    
    def _on_text_changed(self, file_path: str):
        """Handle text changes in the editor."""
        self.is_modified = True
        self._update_modified_status()
        self.file_modified.emit(file_path, True)
    
    def _update_modified_status(self):
        """Update the modified status indicator."""
        if self.is_modified:
            self.modified_label.setText("● Modified")
            self.modified_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.modified_label.setText("")
    
    def _update_cursor_position(self):
        """Update the cursor position display."""
        editor = self._get_current_editor()
        if editor:
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            column = cursor.columnNumber() + 1
            self.cursor_position_label.setText(f"Line {line}, Column {column}")
    
    def _update_file_info(self, file_path: str):
        """Update the file information display."""
        try:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                size = stat.st_size
                modified = stat.st_mtime
                
                info_text = f"<b>File:</b> {os.path.basename(file_path)}<br/>"
                info_text += f"<b>Path:</b> {file_path}<br/>"
                info_text += f"<b>Size:</b> {size} bytes<br/>"
                info_text += f"<b>Modified:</b> {modified}"
                
                self.file_info_label.setText(info_text)
            else:
                self.file_info_label.setText("File not found")
        except Exception as e:
            self.file_info_label.setText(f"Error: {e}")
    
    def _refresh_file_tree(self):
        """Refresh the file tree with common config directories."""
        self.file_tree.clear()
        
        # Common config directories
        config_dirs = [
            os.path.expanduser("~/.config/hypr/"),
            os.path.expanduser("~/.config/waybar/"),
            os.path.expanduser("~/.config/rofi/"),
            os.path.expanduser("~/.config/dunst/"),
            os.path.expanduser("~/.config/mako/"),
            os.path.expanduser("~/.hyprrice/")
        ]
        
        for config_dir in config_dirs:
            if os.path.exists(config_dir):
                dir_item = QTreeWidgetItem([os.path.basename(config_dir)])
                dir_item.setData(0, Qt.ItemDataRole.UserRole, config_dir)
                
                # Add files
                try:
                    for file_name in os.listdir(config_dir):
                        file_path = os.path.join(config_dir, file_name)
                        if os.path.isfile(file_path) and file_name.endswith(('.conf', '.yaml', '.yml', '.json')):
                            file_item = QTreeWidgetItem([file_name])
                            file_item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                            dir_item.addChild(file_item)
                except PermissionError:
                    pass
                
                self.file_tree.addTopLevelItem(dir_item)
        
        # Expand all items
        self.file_tree.expandAll()
    
    def _open_file_from_tree(self, item: QTreeWidgetItem, column: int):
        """Open a file from the file tree."""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path and os.path.isfile(file_path):
            self.load_file(file_path)
    
    def _close_tab(self, index: int):
        """Close a tab."""
        editor = self.editor_tabs.widget(index)
        if editor and self.is_modified:
            reply = QMessageBox.question(
                self, "Save Changes",
                "The file has been modified. Do you want to save changes?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if not self._save_file():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        # Remove from file watcher
        file_path = self.editor_tabs.tabToolTip(index)
        if file_path:
            self.file_watcher.removePath(file_path)
        
        self.editor_tabs.removeTab(index)
    
    def _close_current_tab(self):
        """Close the current tab."""
        current_index = self.editor_tabs.currentIndex()
        if current_index >= 0:
            self._close_tab(current_index)
    
    def _new_file(self):
        """Create a new file."""
        file_path, ok = QFileDialog.getSaveFileName(
            self, "New Configuration File",
            os.path.expanduser("~/.config/hypr/"),
            "Configuration Files (*.conf);;All Files (*)"
        )
        
        if ok and file_path:
            # Create empty file
            with open(file_path, 'w') as f:
                f.write("")
            self.load_file(file_path)
    
    def _open_file(self):
        """Open a file dialog to select a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Configuration File",
            os.path.expanduser("~/.config/"),
            "Configuration Files (*.conf *.yaml *.yml *.json);;All Files (*)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def _save_file_as(self):
        """Save the current file with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration File As",
            os.path.expanduser("~/.config/"),
            "Configuration Files (*.conf);;All Files (*)"
        )
        
        if file_path:
            # Validate path before setting
            from ..security import InputValidator
            validator = InputValidator()
            try:
                canonical_path = validator.validate_path(file_path)
                self.current_file = str(canonical_path)
            except Exception as e:
                QMessageBox.warning(self, "Security Warning", 
                                  f"Path is not safe: {file_path} - {e}")
                return
            self._save_file()
    
    def _undo(self):
        """Undo the last action."""
        editor = self._get_current_editor()
        if editor:
            editor.undo()
    
    def _redo(self):
        """Redo the last undone action."""
        editor = self._get_current_editor()
        if editor:
            editor.redo()
    
    def _find_text(self):
        """Open find dialog."""
        editor = self._get_current_editor()
        if not editor:
            QMessageBox.warning(self, "Find", "No editor is currently active.")
            return
        
        # Create find dialog
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QCheckBox, QLabel
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Find")
        dialog.setModal(True)
        dialog.resize(400, 150)
        
        layout = QVBoxLayout(dialog)
        
        # Find text input
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))
        find_input = QLineEdit()
        find_input.setPlaceholderText("Enter text to find...")
        find_layout.addWidget(find_input)
        layout.addLayout(find_layout)
        
        # Replace text input
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace:"))
        replace_input = QLineEdit()
        replace_input.setPlaceholderText("Enter replacement text...")
        replace_layout.addWidget(replace_input)
        layout.addLayout(replace_layout)
        
        # Options
        options_layout = QHBoxLayout()
        case_sensitive = QCheckBox("Case sensitive")
        whole_words = QCheckBox("Whole words only")
        options_layout.addWidget(case_sensitive)
        options_layout.addWidget(whole_words)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        find_btn = QPushButton("Find")
        replace_btn = QPushButton("Replace")
        replace_all_btn = QPushButton("Replace All")
        close_btn = QPushButton("Close")
        
        button_layout.addWidget(find_btn)
        button_layout.addWidget(replace_btn)
        button_layout.addWidget(replace_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        def find_text():
            text = find_input.text()
            if not text:
                return
            
            # Get current editor content
            content = editor.toPlainText()
            search_text = text if not case_sensitive.isChecked() else text
            
            # Find text
            if case_sensitive.isChecked():
                pos = content.find(search_text, editor.textCursor().position())
            else:
                pos = content.lower().find(search_text.lower(), editor.textCursor().position())
            
            if pos != -1:
                # Select found text
                cursor = editor.textCursor()
                cursor.setPosition(pos)
                cursor.setPosition(pos + len(text), cursor.KeepAnchor)
                editor.setTextCursor(cursor)
                editor.setFocus()
            else:
                QMessageBox.information(dialog, "Find", f"Text '{text}' not found.")
        
        def replace_text():
            find_text_val = find_input.text()
            replace_text_val = replace_input.text()
            
            if not find_text_val:
                return
            
            cursor = editor.textCursor()
            if cursor.hasSelection() and cursor.selectedText() == find_text_val:
                cursor.insertText(replace_text_val)
                editor.setTextCursor(cursor)
            else:
                find_text()
        
        def replace_all():
            find_text_val = find_input.text()
            replace_text_val = replace_input.text()
            
            if not find_text_val:
                return
            
            content = editor.toPlainText()
            if case_sensitive.isChecked():
                new_content = content.replace(find_text_val, replace_text_val)
            else:
                # Case-insensitive replace
                import re
                new_content = re.sub(re.escape(find_text_val), replace_text_val, content, flags=re.IGNORECASE)
            
            if new_content != content:
                editor.setPlainText(new_content)
                QMessageBox.information(dialog, "Replace All", f"Replaced all occurrences of '{find_text_val}'.")
            else:
                QMessageBox.information(dialog, "Replace All", f"No occurrences of '{find_text_val}' found.")
        
        find_btn.clicked.connect(find_text)
        replace_btn.clicked.connect(replace_text)
        replace_all_btn.clicked.connect(replace_all)
        close_btn.clicked.connect(dialog.accept)
        
        # Set focus to find input
        find_input.setFocus()
        
        # Show dialog
        dialog.exec()
    
    def _validate_config(self):
        """Validate the current configuration."""
        editor = self._get_current_editor()
        if not editor:
            return
        
        content = editor.toPlainText()
        file_path = self.current_file
        
        if not file_path:
            QMessageBox.warning(self, "Validation", "No file is currently open.")
            return
        
        try:
            # Basic validation based on file type
            if file_path.endswith('.conf'):
                self._validate_hyprland_config(content)
            elif file_path.endswith(('.yaml', '.yml')):
                self._validate_yaml_config(content)
            elif file_path.endswith('.json'):
                self._validate_json_config(content)
            else:
                QMessageBox.information(self, "Validation", "File type not supported for validation.")
                
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", f"Validation failed: {e}")
    
    def _validate_hyprland_config(self, content: str):
        """Validate Hyprland configuration."""
        errors = []
        warnings = []
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Check for basic syntax issues
            if line.endswith('{') and not line.startswith(('general', 'input', 'decoration', 'animations', 'plugin')):
                # Check if it's a valid section
                section = line.split()[0] if line.split() else ""
                if section not in ['general', 'input', 'decoration', 'animations', 'plugin']:
                    warnings.append(f"Line {i}: Unknown section '{section}'")
            
            # Check for common mistakes
            if '=' in line and not line.endswith('{'):
                parts = line.split('=')
                if len(parts) != 2:
                    errors.append(f"Line {i}: Invalid assignment syntax")
                else:
                    key, value = parts
                    key = key.strip()
                    value = value.strip()
                    
                    # Check for missing semicolon
                    if not value.endswith(','):
                        warnings.append(f"Line {i}: Missing comma at end of line")
        
        # Show results
        if errors or warnings:
            message = "Validation Results:\n\n"
            if errors:
                message += "Errors:\n" + "\n".join(f"• {error}" for error in errors) + "\n\n"
            if warnings:
                message += "Warnings:\n" + "\n".join(f"• {warning}" for warning in warnings)
            
            QMessageBox.warning(self, "Validation Results", message)
        else:
            QMessageBox.information(self, "Validation", "Configuration is valid!")
    
    def _validate_yaml_config(self, content: str):
        """Validate YAML configuration."""
        try:
            import yaml
            yaml.safe_load(content)
            QMessageBox.information(self, "Validation", "YAML configuration is valid!")
        except yaml.YAMLError as e:
            QMessageBox.critical(self, "YAML Validation Error", f"Invalid YAML: {e}")
    
    def _validate_json_config(self, content: str):
        """Validate JSON configuration."""
        try:
            import json
            json.loads(content)
            QMessageBox.information(self, "Validation", "JSON configuration is valid!")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "JSON Validation Error", f"Invalid JSON: {e}")
    
    def _format_config(self):
        """Format the current configuration."""
        editor = self._get_current_editor()
        if not editor:
            return
        
        content = editor.toPlainText()
        file_path = self.current_file
        
        if not file_path:
            QMessageBox.warning(self, "Format", "No file is currently open.")
            return
        
        try:
            if file_path.endswith('.conf'):
                formatted_content = self._format_hyprland_config(content)
            elif file_path.endswith(('.yaml', '.yml')):
                formatted_content = self._format_yaml_config(content)
            elif file_path.endswith('.json'):
                formatted_content = self._format_json_config(content)
            else:
                QMessageBox.information(self, "Format", "File type not supported for formatting.")
                return
            
            editor.setPlainText(formatted_content)
            QMessageBox.information(self, "Format", "Configuration formatted successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Format Error", f"Formatting failed: {e}")
    
    def _format_hyprland_config(self, content: str) -> str:
        """Format Hyprland configuration."""
        lines = content.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            # Skip empty lines
            if not line:
                formatted_lines.append("")
                continue
            
            # Handle comments
            if line.startswith('#'):
                formatted_lines.append(f"{'    ' * indent_level}{line}")
                continue
            
            # Handle section headers
            if line.endswith('{'):
                formatted_lines.append(f"{'    ' * indent_level}{line}")
                indent_level += 1
                continue
            
            # Handle section endings
            if line == '}':
                indent_level = max(0, indent_level - 1)
                formatted_lines.append(f"{'    ' * indent_level}{line}")
                continue
            
            # Handle regular assignments
            if '=' in line:
                # Ensure proper spacing around =
                parts = line.split('=')
                if len(parts) == 2:
                    key, value = parts
                    key = key.strip()
                    value = value.strip()
                    
                    # Ensure comma at end if not present
                    if not value.endswith(','):
                        value += ','
                    
                    formatted_lines.append(f"{'    ' * indent_level}{key} = {value}")
                else:
                    formatted_lines.append(f"{'    ' * indent_level}{line}")
            else:
                formatted_lines.append(f"{'    ' * indent_level}{line}")
        
        return '\n'.join(formatted_lines)
    
    def _format_yaml_config(self, content: str) -> str:
        """Format YAML configuration."""
        import yaml
        data = yaml.safe_load(content)
        return yaml.dump(data, default_flow_style=False, indent=2)
    
    def _format_json_config(self, content: str) -> str:
        """Format JSON configuration."""
        import json
        data = json.loads(content)
        return json.dumps(data, indent=2)
    
    def _insert_template(self):
        """Insert a template for the selected configuration type."""
        editor = self._get_current_editor()
        if not editor:
            return
        
        config_type = self.config_type_combo.currentText()
        template = self._get_template_content(config_type)
        
        # Insert template at cursor position
        cursor = editor.textCursor()
        cursor.insertText(template)
    
    def _get_template_content(self, config_type: str) -> str:
        """Get template content for the specified configuration type."""
        templates = {
            "Hyprland Main Config": """# Hyprland Configuration (end-4 inspired)
# Source modular configs
source = ~/.config/hypr/custom/env.conf
source = ~/.config/hypr/custom/general.conf
source = ~/.config/hypr/custom/input.conf
source = ~/.config/hypr/custom/decoration.conf
source = ~/.config/hypr/custom/animations.conf
source = ~/.config/hypr/custom/keybinds.conf
source = ~/.config/hypr/custom/rules.conf
source = ~/.config/hypr/custom/execs.conf

# General settings
general {
    gaps_in = 5
    gaps_out = 10
    border_size = 2
    col.active_border = rgba(5e81acff)
    col.inactive_border = rgba(2e3440ff)
    layout = dwindle
    no_border_on_floating = false
    resize_on_border = true
    extend_border_grab_area = 15
    hover_icon_on_border = true
}

# Input settings
input {
    kb_layout = us
    # Optional: keyboard variant, model, options, rules
    kb_variant = 
    kb_model = 
    kb_options = 
    kb_rules = 
    follow_mouse = 1
    touchpad {
        natural_scroll = no
        disable_while_typing = true
        scroll_factor = 1.0
        tap-to-click = true
    }
    sensitivity = 0
    accel_profile = flat
    force_no_accel = false
}

# Decoration settings
decoration {
    rounding = 8
    blur {
        enabled = true
        size = 8
        passes = 1
        new_optimizations = true
        xray = false
        ignore_opacity = false
    }
    drop_shadow = yes
    shadow_range = 4
    shadow_render_power = 3
    col.shadow = rgba(1a1a1aee)
    col.shadow_inactive = rgba(00000000)
    dim_inactive = false
    dim_strength = 0.5
    dim_special = 0.2
    dim_around = 0.4
}

# Animation settings
animations {
    enabled = yes
    bezier = myBezier, 0.05, 0.9, 0.1, 1.05
    bezier = linear, 0, 0, 1, 1
    bezier = wind, 0.05, 0.9, 0.1, 1.05
    bezier = winIn, 0.1, 1.1, 0.1, 1.1
    bezier = winOut, 0.3, -0.3, 0, 1
    bezier = slow, 0, 0.85, 0.3, 1
    bezier = overshot, 0.05, 0.9, 0.1, 1.05
    bezier = bounce, 1.1, 1.3, 0, 1.3
            bezier = slingshot, 1, -1, 0.15, 1.25
    bezier = nice, 0, 6.29, 0.5, -4.04
    animation = windows, 1, 7, myBezier, slide
    animation = windowsOut, 1, 7, winOut, slide
    animation = windowsMove, 1, 7, myBezier, slide
    animation = border, 1, 10, linear
    animation = borderangle, 1, 8, linear, loop
    animation = fade, 1, 7, myBezier
    animation = workspaces, 1, 6, wind, slide
    animation = workspaces, 1, 5, bounce, slide
    animation = specialWorkspace, 1, 5, myBezier, slide
}""",
            
            "Window Rules": """# Window Rules
windowrule = float, ^(pavucontrol)$
windowrule = float, ^(blueman-manager)$
windowrule = float, ^(nm-connection-editor)$
windowrule = float, ^(chromium)$
windowrule = float, ^(thunar)$
windowrule = float, ^(org.kde.polkit-kde-authentication-agent-1)$""",
            
            "Keybindings": """# Keybindings (end-4 inspired)
# Basic keybinds
bind = SUPER, Return, exec, kitty
bind = SUPER, Q, killactive,
bind = SUPER, M, exit,
bind = SUPER, E, exec, thunar
bind = SUPER, V, togglefloating,
bind = SUPER, R, exec, rofi -show drun
bind = SUPER, P, pseudo, # dwindle
bind = SUPER, J, togglesplit, # dwindle

# Workspace navigation
bind = SUPER, 1, workspace, 1
bind = SUPER, 2, workspace, 2
bind = SUPER, 3, workspace, 3
bind = SUPER, 4, workspace, 4
bind = SUPER, 5, workspace, 5
bind = SUPER, 6, workspace, 6
bind = SUPER, 7, workspace, 7
bind = SUPER, 8, workspace, 8
bind = SUPER, 9, workspace, 9
bind = SUPER, 0, workspace, 10

# Move to workspace
bind = SUPER SHIFT, 1, movetoworkspace, 1
bind = SUPER SHIFT, 2, movetoworkspace, 2
bind = SUPER SHIFT, 3, movetoworkspace, 3
bind = SUPER SHIFT, 4, movetoworkspace, 4
bind = SUPER SHIFT, 5, movetoworkspace, 5
bind = SUPER SHIFT, 6, movetoworkspace, 6
bind = SUPER SHIFT, 7, movetoworkspace, 7
bind = SUPER SHIFT, 8, movetoworkspace, 8
bind = SUPER SHIFT, 9, movetoworkspace, 9
bind = SUPER SHIFT, 0, movetoworkspace, 10

# Special workspace
bind = SUPER, S, togglespecialworkspace, magic
bind = SUPER SHIFT, S, movetoworkspace, special:magic

# Window focus
bind = SUPER, left, movefocus, l
bind = SUPER, right, movefocus, r
bind = SUPER, up, movefocus, u
bind = SUPER, down, movefocus, d

# Window resize
bind = SUPER SHIFT, left, movewindow, l
bind = SUPER SHIFT, right, movewindow, r
bind = SUPER SHIFT, up, movewindow, u
bind = SUPER SHIFT, down, movewindow, d

# Window resize with mouse
bind = SUPER, mouse:272, movewindow
bind = SUPER, mouse:273, resizewindow

# Screenshot
bind = , Print, exec, grim -g "$(slurp)" - | wl-copy
bind = SHIFT, Print, exec, grim -g "$(slurp)" ~/Pictures/Screenshots/$(date +'%Y%m%d_%H%M%S').png

# Volume control
bind = , XF86AudioRaiseVolume, exec, wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+
bind = , XF86AudioLowerVolume, exec, wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-
bind = , XF86AudioMute, exec, wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle

# Brightness control
bind = , XF86MonBrightnessUp, exec, brightnessctl set 10%+
bind = , XF86MonBrightnessDown, exec, brightnessctl set 10%-

# Lock screen
bind = SUPER, L, exec, hyprlock

# Show keybinds
bind = SUPER, slash, exec, rofi -show keys""",
            
            "Workspace Rules": """# Workspace Rules
workspace = 1, monitor:DP-1
workspace = 2, monitor:DP-1
workspace = 3, monitor:DP-1
workspace = 4, monitor:DP-1
workspace = 5, monitor:DP-1
workspace = 6, monitor:DP-2
workspace = 7, monitor:DP-2
workspace = 8, monitor:DP-2
workspace = 9, monitor:DP-2
workspace = 10, monitor:DP-2""",
            
            "Monitor Settings": """# Monitor Settings
monitor = DP-1, 2560x1440@144, 0x0, 1
monitor = DP-2, 2560x1440@144, 2560x0, 1
monitor = HDMI-A-1, disable""",
            
            "Input Settings": """# Input Settings
input {
    kb_layout = us
    kb_variant =
    kb_model =
    kb_options =
    follow_mouse = 1
    touchpad {
        natural_scroll = no
    }
    sensitivity = 0 # -1.0 - 1.0, 0 means no modification.
}""",
            
            "Decoration Settings": """# Decoration Settings
decoration {
    rounding = 8
    blur {
        enabled = true
        size = 8
        passes = 1
    }
    drop_shadow = yes
    shadow_range = 4
    shadow_render_power = 3
    col.shadow = rgba(1a1a1aee)
}""",
            
            "Animation Settings": """# Animation Settings
animations {
    enabled = yes
    bezier = myBezier, 0.05, 0.9, 0.1, 1.05
    animation = windows, 1, 7, myBezier
    animation = windowsOut, 1, 7, default, popin 80%
    animation = border, 1, 10, default
    animation = borderangle, 1, 8, default
    animation = fade, 1, 7, default
    animation = workspaces, 1, 6, default
}""",
            
            "Plugin Settings": """# Plugin Settings
plugin {
    hyprbars {
        bar_color = rgb(2e3440)
        bar_height = 28
        col_text = rgb(10, 10, 10)
        bar_text_size = 11
        bar_text_font = Ubuntu, Bold
        bar_button_padding = 10
        bar_padding = 10
        bar_precedence_over_border = true
        hyprbars-button = rgb(10, 10, 10), 16, 󰖭, hyprctl dispatch killactive
        hyprbars-button = rgb(10, 10, 10), 16, 󰖯, hyprctl dispatch fullscreen 1
        hyprbars-button = rgb(10, 10, 10), 16, 󰖰, hyprctl dispatch movetoworkspace +1
    }
}""",
            
            "Waybar Config": """# Waybar Configuration (end-4 inspired)
{
    "layer": "top",
    "position": "top",
    "height": 30,
    "spacing": 4,
    "margin-top": 0,
    "margin-bottom": 0,
    "margin-left": 0,
    "margin-right": 0,
    "modules-left": ["hyprland/workspaces", "hyprland/window"],
    "modules-center": ["clock"],
    "modules-right": ["idle_inhibitor", "pulseaudio", "network", "cpu", "memory", "temperature", "battery", "tray"],
    "hyprland/workspaces": {
        "disable-scroll": true,
        "all-outputs": true,
        "format": "{icon}",
        "format-icons": {
            "1": "",
            "2": "",
            "3": "",
            "4": "",
            "5": "",
            "urgent": "",
            "focused": "",
            "default": ""
        }
    },
    "hyprland/window": {
        "format": "{}",
        "separate-outputs": true
    },
    "clock": {
        "timezone": "America/New_York",
        "tooltip-format": "<big>{:%Y %B}</big>\\n<tt><small>{calendar}</small></tt>",
        "format-alt": "{:%Y-%m-%d}"
    },
    "idle_inhibitor": {
        "format": "{icon}",
        "format-icons": {
            "activated": "",
            "deactivated": ""
        }
    },
    "pulseaudio": {
        "format": "{icon} {volume}% {format_source}",
        "format-bluetooth": "{icon} {volume}% {format_source}",
        "format-bluetooth-muted": " {icon} {format_source}",
        "format-muted": " {format_source}",
        "format-source": "{volume}% ",
        "format-source-muted": "",
        "format-icons": {
            "headphone": "",
            "hands-free": "",
            "headset": "",
            "phone": "",
            "portable": "",
            "car": "",
            "default": ["", "", ""]
        },
        "on-click": "pavucontrol"
    },
    "network": {
        "format-wifi": "{essid} ({signalStrength}%) ",
        "format-ethernet": "{ipaddr}/{cidr} ",
        "tooltip-format": "{ifname} via {gwaddr} ",
        "format-linked": "{ifname} (No IP) ",
        "format-disconnected": "Disconnected ⚠",
        "format-alt": "{ifname}: {ipaddr}/{cidr}"
    },
    "cpu": {
        "format": "{usage}% ",
        "tooltip": false
    },
    "memory": {
        "format": "{}% "
    },
    "temperature": {
        "critical-threshold": 80,
        "tooltip": false,
        "format": "{temperatureC}°C {icon}",
        "format-icons": ["", "", ""]
    },
    "battery": {
        "states": {
            "warning": 30,
            "critical": 15
        },
        "format": "{capacity}% {icon}",
        "format-charging": "{capacity}% ",
        "format-plugged": "{capacity}% ",
        "format-alt": "{time} {icon}",
        "format-icons": ["", "", "", "", ""]
    },
    "tray": {
        "spacing": 10
    }
}""",
            
            "Rofi Config": """# Rofi Configuration
* {
    bg: #2e3440;
    bg-alt: #3b4252;
    fg: #eceff4;
    fg-alt: #d8dee9;
    border: 0;
    margin: 0;
    padding: 0;
    highlight: bold, #5e81ac;
    urgent: #bf616a;
}

window {
    width: 40%;
    location: center;
    anchor: center;
    y-offset: -50px;
    x-offset: 0px;
}""",
            
            "Dunst Config": """# Dunst Configuration
[global]
    monitor = 0
    follow = mouse
    geometry = "300x5-30+20"
    indicate_hidden = yes
    shrink = no
    transparency = 0
    notification_height = 0
    separator_height = 2
    padding = 8
    horizontal_padding = 8
    frame_width = 3
    frame_color = "#5e81ac"
    separator_color = frame
    sort = yes
    font = JetBrainsMono Nerd Font 11
    line_height = 0
    markup = full
    format = "<b>%s</b>\\n%b"
    alignment = left
    vertical_alignment = center
    show_age_threshold = 60
    word_wrap = yes
    ellipsize = middle
    ignore_newline = no
    stack_duplicates = true
    hide_duplicate_count = false
    show_indicators = yes
    icon_position = left
    min_icon_size = 0
    max_icon_size = 32
    icon_path = /usr/share/icons/gnome/16x16/status/:/usr/share/icons/gnome/16x16/devices/
    sticky_history = yes
    history_length = 20
    dmenu = /usr/bin/dmenu -p dunst:
    browser = /usr/bin/xdg-open
    always_run_script = true
    title = Dunst
    class = Dunst
    corner_radius = 0
    ignore_dbusclose = false
    force_xwayland = false
    force_xinerama = false

[experimental]
    per_monitor_dpi = false""",
            
            "Environment Variables (env.conf)": """# Environment Variables (end-4 inspired)
# XDG directories
env = XDG_CURRENT_DESKTOP,Hyprland
env = XDG_SESSION_TYPE,wayland
env = XDG_SESSION_DESKTOP,Hyprland

# Qt theming
env = QT_QPA_PLATFORM,wayland
env = QT_QPA_PLATFORMTHEME,qt6ct
env = QT_WAYLAND_DISABLE_WINDOWDECORATION,1
env = QT_AUTO_SCREEN_SCALE_FACTOR,1

# GTK theming
env = GDK_BACKEND,wayland
env = CLUTTER_BACKEND,wayland

# Electron apps
env = ELECTRON_OZONE_PLATFORM_HINT,wayland

# Firefox
env = MOZ_ENABLE_WAYLAND,1

# Java applications
env = _JAVA_AWT_WM_NONREPARENTING,1

# NVIDIA
env = LIBVA_DRIVER_NAME,nvidia
env = GBM_BACKEND,nvidia-drm
env = __GLX_VENDOR_LIBRARY_NAME,nvidia

# AMD
env = AMD_VULKAN_ICD,RADV

# Intel
env = VK_ICD_FILENAMES,/usr/share/vulkan/icd.d/intel_icd.x86_64.json

# Hyprland specific
env = HYPRLAND_LOG_WLR,1
env = HYPRLAND_NO_RT,1""",

            "General Settings (general.conf)": """# General Settings (end-4 inspired)
general {
    gaps_in = 5
    gaps_out = 10
    border_size = 2
    col.active_border = rgba(5e81acff) rgba(81a1c1ff) 45deg
    col.inactive_border = rgba(2e3440ff)
    layout = dwindle
    no_border_on_floating = false
    resize_on_border = true
    extend_border_grab_area = 15
    hover_icon_on_border = true
    allow_tearing = false
}""",

            "Input Settings (input.conf)": """# Input Settings (end-4 inspired)
input {
    kb_layout = us
    kb_variant = 
    kb_model = 
    kb_options = 
    kb_rules = 
    follow_mouse = 1
    touchpad {
        natural_scroll = no
        disable_while_typing = true
        scroll_factor = 1.0
        tap-to-click = true
        tap-and-drag = true
        drag_lock = false
    }
    sensitivity = 0
    accel_profile = flat
    force_no_accel = false
    repeat_rate = 25
    repeat_delay = 600
    numlock_by_default = true
    left_handed = false
    scroll_method = 2fg
    scroll_button = 0
    scroll_button_lock = false
    scroll_factor = 1.0
    scroll_up_on_right_edge = false
    scroll_down_on_right_edge = false
    scroll_up_on_left_edge = false
    scroll_down_on_left_edge = false
    scroll_up_on_left_edge = false
    scroll_down_on_left_edge = false
    scroll_up_on_left_edge = false
    scroll_down_on_left_edge = false
}""",

            "Decoration Settings (decoration.conf)": """# Decoration Settings (end-4 inspired)
decoration {
    rounding = 8
    blur {
        enabled = true
        size = 8
        passes = 1
        new_optimizations = true
        xray = false
        ignore_opacity = false
        contrast = 0.0
        brightness = 0.0
        vibrancy = 0.0
        vibrancy_darkness = 0.0
    }
    drop_shadow = yes
    shadow_range = 4
    shadow_render_power = 3
    col.shadow = rgba(1a1a1aee)
    col.shadow_inactive = rgba(00000000)
    dim_inactive = false
    dim_strength = 0.5
    dim_special = 0.2
    dim_around = 0.4
    screen_shader = 
}""",

            "Animation Settings (animations.conf)": """# Animation Settings (end-4 inspired)
animations {
    enabled = yes
    bezier = myBezier, 0.05, 0.9, 0.1, 1.05
    bezier = linear, 0, 0, 1, 1
    bezier = wind, 0.05, 0.9, 0.1, 1.05
    bezier = winIn, 0.1, 1.1, 0.1, 1.1
    bezier = winOut, 0.3, -0.3, 0, 1
    bezier = slow, 0, 0.85, 0.3, 1
    bezier = overshot, 0.05, 0.9, 0.1, 1.05
    bezier = bounce, 1.1, 1.3, 0, 1.3
            bezier = slingshot, 1, -1, 0.15, 1.25
    bezier = nice, 0, 6.29, 0.5, -4.04
    animation = windows, 1, 7, myBezier, slide
    animation = windowsOut, 1, 7, winOut, slide
    animation = windowsMove, 1, 7, myBezier, slide
    animation = border, 1, 10, linear
    animation = borderangle, 1, 8, linear, loop
    animation = fade, 1, 7, myBezier
    animation = workspaces, 1, 6, wind, slide
    animation = workspaces, 1, 5, bounce, slide
    animation = specialWorkspace, 1, 5, myBezier, slide
}""",

            "Window Rules (rules.conf)": """# Window Rules (end-4 inspired)
# Floating windows
windowrule = float, ^(pavucontrol)$
windowrule = float, ^(blueman-manager)$
windowrule = float, ^(nm-connection-editor)$
windowrule = float, ^(chromium)$
windowrule = float, ^(thunar)$
windowrule = float, ^(org.kde.polkit-kde-authentication-agent-1)$
windowrule = float, ^(waybar)$
windowrule = float, ^(rofi)$
windowrule = float, ^(dunst)$
windowrule = float, ^(mako)$

# Window sizing
windowrule = size 800 600, ^(pavucontrol)$
windowrule = size 800 600, ^(blueman-manager)$
windowrule = size 800 600, ^(nm-connection-editor)$

# Window positioning
windowrule = center, ^(pavucontrol)$
windowrule = center, ^(blueman-manager)$
windowrule = center, ^(nm-connection-editor)$

# Window opacity
windowrule = opacity 0.8, ^(waybar)$
windowrule = opacity 0.9, ^(rofi)$

# Window rounding
windowrule = rounding 10, ^(rofi)$
windowrule = rounding 5, ^(dunst)$

# Window pinning
windowrule = pin, ^(waybar)$

# Window focus
windowrule = nofocus, ^(waybar)$
windowrule = nofocus, ^(dunst)$
windowrule = nofocus, ^(mako)$

# Window workspace
windowrule = workspace 1, ^(kitty)$
windowrule = workspace 2, ^(firefox)$
windowrule = workspace 3, ^(thunar)$

# Window monitor
windowrule = monitor 0, ^(waybar)$
windowrule = monitor 1, ^(rofi)$""",

            "Exec Commands (execs.conf)": """# Exec Commands (end-4 inspired)
# Startup applications
exec-once = waybar
exec-once = dunst
exec-once = swww-daemon
exec-once = hypridle
exec-once = hyprlock
exec-once = cliphist
exec-once = wl-paste --type text --watch cliphist store
exec-once = wl-paste --type image --watch cliphist store

# Wallpaper
exec-once = swww img ~/Pictures/wallpapers/wallpaper.jpg

# Polkit agent
exec-once = /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1

# XDG portal
exec-once = /usr/lib/xdg-desktop-portal-hyprland

# Notification daemon
exec-once = dunst

# Screen locker
exec-once = hyprlock

# Idle daemon
exec-once = hypridle

# Clipboard manager
exec-once = cliphist

# Audio
exec-once = pipewire
exec-once = pipewire-pulse
exec-once = wireplumber

# Network manager
exec-once = nm-applet

# Bluetooth
exec-once = blueman-applet

# System tray
exec-once = waybar

# File manager
exec-once = thunar --daemon

# Terminal
exec-once = kitty

# Browser
exec-once = firefox

# Editor
exec-once = code

# Music player
exec-once = spotify

# Discord
exec-once = discord

# Steam
exec-once = steam

# Gaming
exec-once = lutris
exec-once = heroic

# Development
exec-once = github-desktop
exec-once = gitkraken

# Productivity
exec-once = notion-app
exec-once = obsidian

# Communication
exec-once = telegram-desktop
exec-once = signal-desktop
exec-once = whatsapp-for-linux

# Media
exec-once = vlc
exec-once = obs-studio

# System monitoring
exec-once = htop
exec-once = btop

# Backup
exec-once = timeshift

# Security
exec-once = bitwarden
exec-once = keepassxc""",

            "Custom": """# Custom Configuration
# Add your custom settings here
"""
        }
        
        return templates.get(config_type, "# Custom configuration\n# Add your settings here")
    
    def _create_backup(self):
        """Create a backup of the current file."""
        if not self.current_file:
            QMessageBox.warning(self, "Backup", "No file is currently open.")
            return
        
        try:
            backup_dir = os.path.dirname(self.current_file) + "/.backups/"
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_file(self.current_file, backup_dir)
            QMessageBox.information(self, "Backup", "Backup created successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to create backup: {e}")
    
    def _on_file_changed_externally(self, file_path: str):
        """Handle external file changes."""
        if file_path == self.current_file:
            reply = QMessageBox.question(
                self, "File Changed",
                f"The file {os.path.basename(file_path)} has been changed externally. Do you want to reload it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.load_file(file_path)
    
    def _auto_save(self):
        """Auto-save the current file if modified."""
        if self.is_modified and self.current_file:
            self._save_file()
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About HyprRice Configuration Editor",
            "HyprRice Configuration Editor v1.0.0\n\n"
            "A dedicated text editor for Hyprland configuration files.\n"
            "Features syntax highlighting, validation, and formatting.\n\n"
            "Part of the HyprRice project."
        )
    
    def closeEvent(self, event):
        """Handle close event."""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Save Changes",
                "The file has been modified. Do you want to save changes?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if not self._save_file():
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        # Clean up file watcher
        for path in self.file_watcher.files():
            self.file_watcher.removePath(path)
        
        event.accept()
