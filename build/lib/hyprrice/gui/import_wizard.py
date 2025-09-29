"""
Import From Dotfiles Wizard for HyprRice

Provides a wizard to import configurations from popular Hyprland dotfiles repositories
like ML4W and end-4, with automatic detection and mapping to HyprRice themes/configs.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QTextEdit, QPushButton, QLabel, QComboBox, QFormLayout,
    QGroupBox, QMessageBox, QScrollArea, QFrame, QSplitter,
    QListWidget, QListWidgetItem, QCheckBox, QSpinBox,
    QLineEdit, QFileDialog, QProgressBar, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QTableWidget, QTableWidgetItem,
    QWizard, QWizardPage, QGridLayout, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QClipboard
import logging
import subprocess
import requests
import tempfile
import zipfile


class ImportWizard(QWizard):
    """Wizard for importing configurations from popular dotfiles repositories."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import From Dotfiles - HyprRice")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        self.logger = logging.getLogger(__name__)
        self.temp_dir = None
        self.imported_configs = {}
        
        self._setup_pages()
        self._setup_connections()
    
    def _setup_pages(self):
        """Setup wizard pages."""
        # Page 1: Source Selection
        self.addPage(SourceSelectionPage(self))
        
        # Page 2: Configuration Detection
        self.addPage(ConfigDetectionPage(self))
        
        # Page 3: Preview and Mapping
        self.addPage(PreviewMappingPage(self))
        
        # Page 4: Import Progress
        self.addPage(ImportProgressPage(self))
        
        # Page 5: Completion
        self.addPage(CompletionPage(self))
    
    def _setup_connections(self):
        """Setup signal connections."""
        self.currentIdChanged.connect(self._on_page_changed)
    
    def _on_page_changed(self, page_id: int):
        """Handle page changes."""
        if page_id == 1:  # Config Detection Page
            self._detect_configurations()
        elif page_id == 2:  # Preview Mapping Page
            self._prepare_preview()
        elif page_id == 3:  # Import Progress Page
            self._start_import()
    
    def _detect_configurations(self):
        """Detect configurations from the selected source."""
        # Implementation for detecting configurations
        pass
    
    def _prepare_preview(self):
        """Prepare preview of configurations to be imported."""
        # Implementation for preparing preview
        pass
    
    def _start_import(self):
        """Start the import process."""
        # Implementation for starting import
        pass


class SourceSelectionPage(QWizardPage):
    """Page for selecting the source of dotfiles to import."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Select Source")
        self.setSubTitle("Choose where to import configurations from")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Source selection group
        source_group = QGroupBox("Import Source")
        source_layout = QVBoxLayout(source_group)
        
        # Radio buttons for different sources
        self.source_buttons = QButtonGroup()
        
        # ML4W Dotfiles
        ml4w_radio = QRadioButton("ML4W Dotfiles (mylinuxforwork/dotfiles)")
        ml4w_radio.setChecked(True)
        self.source_buttons.addButton(ml4w_radio, 0)
        source_layout.addWidget(ml4w_radio)
        
        # end-4 dots-hyprland
        end4_radio = QRadioButton("end-4 dots-hyprland (end-4/dots-hyprland)")
        self.source_buttons.addButton(end4_radio, 1)
        source_layout.addWidget(end4_radio)
        
        # Local directory
        local_radio = QRadioButton("Local Directory")
        self.source_buttons.addButton(local_radio, 2)
        source_layout.addWidget(local_radio)
        
        # GitHub repository
        github_radio = QRadioButton("GitHub Repository")
        self.source_buttons.addButton(github_radio, 3)
        source_layout.addWidget(github_radio)
        
        layout.addWidget(source_group)
        
        # GitHub URL input (shown when GitHub is selected)
        self.github_group = QGroupBox("GitHub Repository")
        github_layout = QFormLayout(self.github_group)
        
        self.github_url_edit = QLineEdit()
        self.github_url_edit.setPlaceholderText("https://github.com/username/repository")
        github_layout.addRow("Repository URL:", self.github_url_edit)
        
        layout.addWidget(self.github_group)
        self.github_group.setVisible(False)
        
        # Local directory input (shown when Local is selected)
        self.local_group = QGroupBox("Local Directory")
        local_layout = QHBoxLayout(self.local_group)
        
        self.local_path_edit = QLineEdit()
        self.local_path_edit.setPlaceholderText("/path/to/dotfiles")
        local_layout.addWidget(self.local_path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_directory)
        local_layout.addWidget(browse_btn)
        
        layout.addWidget(self.local_group)
        self.local_group.setVisible(False)
        
        # Connect radio button changes
        self.source_buttons.buttonClicked.connect(self._on_source_changed)
        
        # Description
        desc_label = QLabel(
            "Select the source of dotfiles you want to import. "
            "HyprRice will automatically detect and map configurations to create themes and settings."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
    
    def _on_source_changed(self, button):
        """Handle source selection change."""
        source_id = self.source_buttons.id(button)
        
        # Show/hide relevant input groups
        self.github_group.setVisible(source_id == 3)
        self.local_group.setVisible(source_id == 2)
    
    def _browse_directory(self):
        """Browse for local directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Dotfiles Directory", 
            os.path.expanduser("~")
        )
        if directory:
            self.local_path_edit.setText(directory)
    
    def get_selected_source(self) -> Tuple[int, str]:
        """Get the selected source and its configuration."""
        source_id = self.source_buttons.checkedId()
        
        if source_id == 0:  # ML4W
            return source_id, "https://github.com/mylinuxforwork/dotfiles"
        elif source_id == 1:  # end-4
            return source_id, "https://github.com/end-4/dots-hyprland"
        elif source_id == 2:  # Local
            return source_id, self.local_path_edit.text()
        elif source_id == 3:  # GitHub
            return source_id, self.github_url_edit.text()
        
        return source_id, ""


class ConfigDetectionPage(QWizardPage):
    """Page for detecting configurations from the selected source."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Detect Configurations")
        self.setSubTitle("Analyzing the selected source for Hyprland configurations")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Preparing to analyze source...")
        layout.addWidget(self.status_label)
        
        # Detection results
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("JetBrainsMono Nerd Font", 10))
        layout.addWidget(self.results_text)
        
        # Detected configurations list
        self.configs_list = QListWidget()
        self.configs_list.setMaximumHeight(150)
        layout.addWidget(QLabel("Detected Configurations:"))
        layout.addWidget(self.configs_list)
    
    def update_progress(self, value: int, text: str):
        """Update progress bar and status."""
        self.progress_bar.setValue(value)
        self.status_label.setText(text)
    
    def add_result(self, text: str):
        """Add result text."""
        self.results_text.append(text)
    
    def initializePage(self):
        """Initialize the page and start detection."""
        wizard = self.wizard()
        if not wizard:
            return
        
        # Get source information
        source_id, source_path = wizard.get_source_info()
        
        if not source_path:
            self.add_result("No source path provided")
            return
        
        # Start detection
        self.update_progress(0, "Starting configuration detection...")
        self.detect_configurations(source_id, source_path)
    
    def detect_configurations(self, source_id: int, source_path: str):
        """Detect configurations from the source."""
        try:
            if source_id == 0:  # Local path
                self.detect_local_configs(source_path)
            elif source_id == 1:  # ML4W
                self.detect_ml4w_configs(source_path)
            elif source_id == 2:  # end-4
                self.detect_end4_configs(source_path)
            elif source_id == 3:  # GitHub
                self.add_result("GitHub import coming soon...")
                self.update_progress(100, "GitHub import not yet implemented")
            else:
                self.add_result("Unknown source type")
        except Exception as e:
            self.add_result(f"Error during detection: {e}")
            self.update_progress(100, "Detection failed")
    
    def detect_local_configs(self, path: str):
        """Detect configurations from a local path."""
        self.update_progress(25, "Scanning local directory...")
        
        import os
        from pathlib import Path
        
        base_path = Path(os.path.expanduser(path))
        if not base_path.exists():
            self.add_result(f"Path does not exist: {base_path}")
            return
        
        detected_configs = {}
        
        # Look for Hyprland configs
        hypr_config_dir = base_path / ".config" / "hypr"
        if hypr_config_dir.exists():
            self.add_result(f"Found Hyprland config directory: {hypr_config_dir}")
            
            # Check for modular configs
            custom_dir = hypr_config_dir / "custom"
            if custom_dir.exists():
                self.add_result("Found modular configuration structure")
                
                config_files = {
                    "env.conf": "Environment Variables",
                    "general.conf": "General Settings", 
                    "keybinds.conf": "Keybindings",
                    "rules.conf": "Window Rules",
                    "execs.conf": "Exec Commands",
                    "input.conf": "Input Settings",
                    "decoration.conf": "Decoration Settings",
                    "animations.conf": "Animation Settings"
                }
                
                for filename, description in config_files.items():
                    file_path = custom_dir / filename
                    if file_path.exists():
                        detected_configs[description] = str(file_path)
                        self.add_result(f"  ✓ {description}: {filename}")
                        self.configs_list.addItem(f"{description} ({filename})")
            
            # Check for main config
            main_config = hypr_config_dir / "hyprland.conf"
            if main_config.exists():
                detected_configs["Hyprland Main Config"] = str(main_config)
                self.add_result(f"  ✓ Main config: hyprland.conf")
                self.configs_list.addItem("Hyprland Main Config (hyprland.conf)")
        
        # Look for Waybar configs
        waybar_config_dir = base_path / ".config" / "waybar"
        if waybar_config_dir.exists():
            self.add_result(f"Found Waybar config directory: {waybar_config_dir}")
            
            config_file = waybar_config_dir / "config"
            style_file = waybar_config_dir / "style.css"
            
            if config_file.exists():
                detected_configs["Waybar Config"] = str(config_file)
                self.add_result(f"  ✓ Waybar config: config")
                self.configs_list.addItem("Waybar Config (config)")
            
            if style_file.exists():
                detected_configs["Waybar Style"] = str(style_file)
                self.add_result(f"  ✓ Waybar style: style.css")
                self.configs_list.addItem("Waybar Style (style.css)")
        
        # Look for Rofi configs
        rofi_config_dir = base_path / ".config" / "rofi"
        if rofi_config_dir.exists():
            self.add_result(f"Found Rofi config directory: {rofi_config_dir}")
            
            config_file = rofi_config_dir / "config.rasi"
            if config_file.exists():
                detected_configs["Rofi Config"] = str(config_file)
                self.add_result(f"  ✓ Rofi config: config.rasi")
                self.configs_list.addItem("Rofi Config (config.rasi)")
        
        # Store detected configs in wizard
        wizard = self.wizard()
        if wizard:
            wizard.detected_configs = detected_configs
        
        self.update_progress(100, f"Detection complete. Found {len(detected_configs)} configurations.")
    
    def detect_ml4w_configs(self, path: str):
        """Detect ML4W-style configurations."""
        self.add_result("Detecting ML4W-style configurations...")
        # ML4W uses similar structure to local detection
        self.detect_local_configs(path)
    
    def detect_end4_configs(self, path: str):
        """Detect end-4-style configurations."""
        self.add_result("Detecting end-4-style configurations...")
        # end-4 uses modular structure similar to local detection
        self.detect_local_configs(path)
    
    def add_config(self, name: str, path: str, type: str):
        """Add detected configuration."""
        item = QListWidgetItem(f"{name} ({type}) - {path}")
        item.setData(Qt.ItemDataRole.UserRole, {"name": name, "path": path, "type": type})
        self.configs_list.addItem(item)


class PreviewMappingPage(QWizardPage):
    """Page for previewing and mapping configurations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Preview and Map")
        self.setSubTitle("Review detected configurations and map them to HyprRice")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Splitter for preview and mapping
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Configuration preview
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("Configuration Preview:"))
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("JetBrainsMono Nerd Font", 9))
        left_layout.addWidget(self.preview_text)
        
        splitter.addWidget(left_widget)
        
        # Right side - Mapping options
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        right_layout.addWidget(QLabel("Mapping Options:"))
        
        # Theme name
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_name_edit = QLineEdit()
        self.theme_name_edit.setPlaceholderText("Imported Theme")
        theme_layout.addRow("Theme Name:", self.theme_name_edit)
        
        self.theme_description_edit = QLineEdit()
        self.theme_description_edit.setPlaceholderText("Description of the imported theme")
        theme_layout.addRow("Description:", self.theme_description_edit)
        
        right_layout.addWidget(theme_group)
        
        # Import options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout(options_group)
        
        self.import_hyprland_check = QCheckBox("Import Hyprland configuration")
        self.import_hyprland_check.setChecked(True)
        options_layout.addWidget(self.import_hyprland_check)
        
        self.import_waybar_check = QCheckBox("Import Waybar configuration")
        self.import_waybar_check.setChecked(True)
        options_layout.addWidget(self.import_waybar_check)
        
        self.import_rofi_check = QCheckBox("Import Rofi configuration")
        self.import_rofi_check.setChecked(True)
        options_layout.addWidget(self.import_rofi_check)
        
        self.import_dunst_check = QCheckBox("Import Dunst configuration")
        self.import_dunst_check.setChecked(True)
        options_layout.addWidget(self.import_dunst_check)
        
        self.create_backup_check = QCheckBox("Create backup of existing configurations")
        self.create_backup_check.setChecked(True)
        options_layout.addWidget(self.create_backup_check)
        
        right_layout.addWidget(options_group)
        
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setSizes([400, 300])


class ImportProgressPage(QWizardPage):
    """Page showing import progress."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Importing Configurations")
        self.setSubTitle("Importing and applying the selected configurations")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Starting import...")
        layout.addWidget(self.status_label)
        
        # Import log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("JetBrainsMono Nerd Font", 9))
        layout.addWidget(self.log_text)
    
    def update_progress(self, value: int, text: str):
        """Update progress bar and status."""
        self.progress_bar.setValue(value)
        self.status_label.setText(text)
    
    def add_log(self, text: str):
        """Add log message."""
        self.log_text.append(text)
    
    def initializePage(self):
        """Initialize the page and start import."""
        wizard = self.wizard()
        if not wizard:
            return
        
        # Start import process
        self.import_configurations()
    
    def import_configurations(self):
        """Import the detected configurations."""
        wizard = self.wizard()
        if not wizard or not hasattr(wizard, 'detected_configs'):
            self.add_log("No configurations to import")
            return
        
        try:
            self.update_progress(10, "Preparing import...")
            
            # Get theme name from previous page
            theme_name = "Imported Theme"
            if hasattr(wizard, 'theme_name_edit'):
                theme_name = wizard.theme_name_edit.text().strip() or "Imported Theme"
            
            # Create theme directory
            import os
            from pathlib import Path
            
            # Get config from wizard's parent (main GUI)
            parent = wizard.parent()
            if hasattr(parent, 'config'):
                config = parent.config
                theme_dir = Path(config.paths.theme_dir) / theme_name
            else:
                theme_dir = Path.home() / '.hyprrice' / 'themes' / theme_name
            
            theme_dir.mkdir(parents=True, exist_ok=True)
            self.add_log(f"Created theme directory: {theme_dir}")
            
            self.update_progress(30, "Copying configuration files...")
            
            # Copy detected configurations
            imported_count = 0
            for config_name, source_path in wizard.detected_configs.items():
                try:
                    source_file = Path(source_path)
                    if source_file.exists():
                        # Create target filename
                        target_filename = config_name.lower().replace(' ', '_') + '.conf'
                        target_path = theme_dir / target_filename
                        
                        # Copy file
                        import shutil
                        shutil.copy2(source_file, target_path)
                        
                        self.add_log(f"✓ Copied {config_name}: {target_filename}")
                        imported_count += 1
                    else:
                        self.add_log(f"✗ Source file not found: {source_path}")
                except Exception as e:
                    self.add_log(f"✗ Failed to copy {config_name}: {e}")
            
            self.update_progress(80, "Creating theme metadata...")
            
            # Create theme metadata file
            metadata = {
                "name": theme_name,
                "description": "Imported from external dotfiles",
                "version": "1.0.0",
                "author": "HyprRice Import Wizard",
                "created": "2024-01-01",
                "files": list(wizard.detected_configs.keys())
            }
            
            import json
            metadata_file = theme_dir / "theme.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.add_log(f"✓ Created theme metadata: {metadata_file}")
            
            self.update_progress(100, f"Import complete! Imported {imported_count} configurations.")
            self.add_log(f"\n🎉 Successfully imported {imported_count} configurations to theme: {theme_name}")
            self.add_log(f"Theme location: {theme_dir}")
            
        except Exception as e:
            self.add_log(f"❌ Import failed: {e}")
            self.update_progress(100, "Import failed")


class CompletionPage(QWizardPage):
    """Page shown after successful import."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Import Complete")
        self.setSubTitle("Configuration import has been completed successfully")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Success message
        success_label = QLabel("✅ Import completed successfully!")
        success_label.setStyleSheet("color: green; font-size: 16px; font-weight: bold;")
        layout.addWidget(success_label)
        
        # Summary
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(200)
        layout.addWidget(QLabel("Import Summary:"))
        layout.addWidget(self.summary_text)
        
        # Next steps
        next_steps_label = QLabel("Next Steps:")
        next_steps_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(next_steps_label)
        
        steps_text = QLabel(
            "• Review the imported theme in the Theme Manager\n"
            "• Apply the theme to see the changes\n"
            "• Customize the theme as needed\n"
            "• Create backups of your configurations"
        )
        steps_text.setStyleSheet("margin-left: 20px;")
        layout.addWidget(steps_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        open_theme_manager_btn = QPushButton("Open Theme Manager")
        open_theme_manager_btn.clicked.connect(self._open_theme_manager)
        button_layout.addWidget(open_theme_manager_btn)
        
        apply_theme_btn = QPushButton("Apply Theme")
        apply_theme_btn.clicked.connect(self._apply_theme)
        button_layout.addWidget(apply_theme_btn)
        
        layout.addLayout(button_layout)
    
    def set_summary(self, summary: str):
        """Set the import summary."""
        self.summary_text.setPlainText(summary)
    
    def _open_theme_manager(self):
        """Open the theme manager."""
        # Implementation to open theme manager
        pass
    
    def _apply_theme(self):
        """Apply the imported theme."""
        # Implementation to apply theme
        pass
