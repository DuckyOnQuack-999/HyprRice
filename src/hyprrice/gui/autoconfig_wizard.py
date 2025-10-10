#!/usr/bin/env python3
"""
Autoconfig Wizard GUI

Provides an interactive wizard interface for HyprRice autoconfig system.
"""

import os
import threading
from typing import Optional, Dict, Any, Callable
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QTextEdit, QGroupBox,
    QRadioButton, QButtonGroup, QCheckBox, QSpinBox,
    QComboBox, QScrollArea, QWidget, QGridLayout,
    QMessageBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

from ..autoconfig import (
    SystemProfiler, ConfigurationGenerator, AutoconfigManager,
    PerformanceProfile, SystemProfile, AutoconfigResult
)
from ..config import Config
from ..exceptions import HyprRiceError


def show_autoconfig_wizard(main_app=None, parent=None):
    """Show the autoconfig wizard dialog."""
    wizard = AutoconfigWizard(main_app=main_app, parent=parent)
    wizard.exec()


class AutoconfigWorker(QThread):
    """Worker thread for autoconfig operations."""
    
    progress_update = pyqtSignal(int, str)  # progress_percent, message
    finished = pyqtSignal(bool, dict)  # success, result_data
    error = pyqtSignal(str, str)  # error_type, error_message
    
    def __init__(self, operation: str, profile: PerformanceProfile, **kwargs):
        super().__init__()
        self.operation = operation
        self.profile = profile
        self.kwargs = kwargs
        self._canceled = False
    
    def cancel(self):
        """Cancel the operation."""
        self._canceled = True
    
    def run(self):
        """Run the autoconfig operation."""
        try:
            if self.operation == "profile":
                self._run_profiling()
            elif self.operation == "generate":
                self._run_generation()
            elif self.operation == "apply":
                self._run_application()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
                
        except Exception as e:
            self.error.emit("operation_failed", str(e))
    
    def _run_profiling(self):
        """Run system profiling."""
        self.progress_update.emit(10, "Initializing profiler...")
        
        if self._canceled:
            return
            
        profiler = SystemProfiler()
        self.progress_update.emit(30, "Analyzing CPU and memory...")
        
        if self._canceled:
            return
            
        cpu_info = profiler.get_cpu_info()
        memory_info = profiler.get_memory_info()
        self.progress_update.emit(50, "Detecting GPU...")
        
        if self._canceled:
            return
            
        gpu_info = profiler.get_gpu_info()
        self.progress_update.emit(70, "Analyzing display configuration...")
        
        if self._canceled:
            return
            
        display_info = profiler.get_display_info()
        self.progress_update.emit(90, "Analyzing storage...")
        
        if self._canceled:
            return
            
        storage_info = profiler.get_storage_info()
        self.progress_update.emit(100, "Profiling complete!")
        
        profile_result = profiler.profile_system()
        
        result = {
            "profile": profile_result,
            "cpu": cpu_info,
            "memory": memory_info,
            "gpu": gpu_info,
            "display": display_info,
            "storage": storage_info
        }
        
        self.finished.emit(True, result)
    
    def _run_generation(self):
        """Run configuration generation."""
        self.progress_update.emit(10, "Initializing configuration generator...")
        
        if self._canceled:
            return
            
        profiler = SystemProfiler()
        generator = ConfigurationGenerator(profiler)
        self.progress_update.emit(30, "Generating base configuration...")
        
        if self._canceled:
            return
            
        config = generator.generate_config(self.profile)
        self.progress_update.emit(50, "Optimizing for hardware...")
        
        if self._canceled:
            return
            
        optimized_config = generator.optimize_for_hardware(config)
        self.progress_update.emit(70, "Validating configuration...")
        
        if self._canceled:
            return
            
        validated_config = generator.validate_config(optimized_config)
        self.progress_update.emit(90, "Finalizing configuration...")
        
        if self._canceled:
            return
            
        final_config = generator.finalize_config(validated_config)
        self.progress_update.emit(100, "Configuration generated!")
        
        result = {
            "config": final_config,
            "optimizations": generator.get_applied_optimizations(),
            "performance_impact": generator.get_performance_impact()
        }
        
        self.finished.emit(True, result)
    
    def _run_application(self):
        """Run configuration application."""
        manager = AutoconfigManager()
        
        self.progress_update.emit(10, "Starting autoconfiguration...")
        
        if self._canceled:
            return
            
        result = manager.run_autoconfig(
            profile=self.profile,
            interactive=False,
            backup=True,
            auto_reload=self.kwargs.get('auto_reload', True)
        )
        
        if result.success:
            self.progress_update.emit(100, "Configuration applied successfully!")
            self.finished.emit(True, {
                "result": result,
                "backup_path": result.backup_path,
                "applied_config": result.applied_config
            })
        else:
            self.error.emit("apply_failed", result.error)


class SystemAnalysisWidget(QWidget):
    """Widget showing system analysis results."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("System Analysis Results")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Analysis results
        self.results_label = QLabel("Run system analysis to see results here.")
        self.results_label.setWordWrap(True)
        layout.addWidget(self.results_label)
    
    def update_results(self, profile_data: Dict[str, Any]):
        """Update the display with profile results."""
        cpu_info = profile_data.get("cpu", {})
        memory_info = profile_data.get("memory", {})
        gpu_info = profile_data.get("gpu", {})
        display_info = profile_data.get("display", {})
        storage_info = profile_data.get("storage", {})
        profile = profile_data.get("profile", {})
        
        text = f"""
System Capabilities Analysis:

Performance Level: {profile.get('performance_level', 'Unknown')}
Total Score: {profile.get('total_score', 0)}/11

Hardware Profile:
• CPU: {cpu_info.get('model', 'Unknown')} ({cpu_info.get('cores', 0)} cores)
• Memory: {memory_info.get('total_gb', 0.0)} GB RAM
• GPU: {gpu_info.get('type', 'Unknown')} ({gpu_info.get('memory_gb', 0.0)} GB)
• Storage: {storage_info.get('type', 'Unknown')} ({storage_info.get('size_gb', 0.0)} GB)
• Displays: {len(display_info.get('monitors', []))} monitor(s)

Recommendations:
• Recommended Profile: {profile.get('recommended_profile', 'Performance')}
• Max Visual Effects: {'Yes' if profile.get('supports_blur', True) else 'No'}
• Suitable for Gaming: {'Yes' if profile.get('gaming_ready', True) else 'No'}
"""
        
        self.results_label.setText(text)


class ProfileSelectionWidget(QWidget):
    """Widget for selecting performance profiles."""
    
    profile_selected = pyqtSignal(object)  # PerformanceProfile
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.system_analysis = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Select Performance Profile")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Profile buttons
        self.profile_group = QButtonGroup(self)
        
        # Performance profile
        self.perf_radio = QRadioButton("🚀 Performance Profile")
        self.perf_radio.setChecked(True)  # Default selection
        self.perf_radio.profile = PerformanceProfile.PERFORMANCE
        self.profile_group.addButton(self.perf_radio, 0)
        layout.addWidget(self.perf_radio)
        
        perf_desc = QLabel("Optimized for speed and responsiveness. Reduced animations, efficient settings.")
        perf_desc.setStyleSheet("margin-left: 20px; color: gray; font-size: 10px;")
        layout.addWidget(perf_desc)
        
        # Visual profile
        self.visual_radio = QRadioButton("🎨 Visual Profile")
        self.visual_radio.profile = PerformanceProfile.VISUAL
        self.profile_group.addButton(self.visual_radio, 1)
        layout.addWidget(self.visual_radio)
        
        visual_desc = QLabel("Maximum visual effects and animations. Enhanced blur, smooth transitions.")
        visual_desc.setStyleSheet("margin-left: 20px; color: gray; font-size: 10px;")
        layout.addWidget(visual_desc)
        
        # Battery profile
        self.battery_radio = QRadioButton("🔋 Battery Profile")
        self.battery_radio.profile = PerformanceProfile.BATTERY
        self.profile_group.addButton(self.battery_radio, 2)
        layout.addWidget(self.battery_radio)
        
        battery_desc = QLabel("Power-saving optimizations. Minimal animations, reduced effects.")
        battery_desc.setStyleSheet("margin-left: 20px; color: gray; font-size: 10px;")
        layout.addWidget(battery_desc)
        
        # Minimal profile
        self.minimal_radio = QRadioButton("⚡ Minimal Profile")
        self.minimal_radio.profile = PerformanceProfile.MINIMAL
        self.profile_group.addButton(self.minimal_radio, 3)
        layout.addWidget(self.minimal_radio)
        
        minimal_desc = QLabel("Lightweight configuration. Minimal resources, clean interface.")
        minimal_desc.setStyleSheet("margin-left: 20px; color: gray; font-size: 10px;")
        layout.addWidget(minimal_desc)
        
        # Connect signals
        self.profile_group.buttonClicked.connect(self._on_profile_selected)
    
    def _on_profile_selected(self):
        """Handle profile selection."""
        button = self.profile_group.checkedButton()
        if button:
            self.profile_selected.emit(button.profile)
    
    def set_recommended_profile(self, profile: PerformanceProfile):
        """Set the recommended profile based on system analysis."""
        if profile == PerformanceProfile.PERFORMANCE:
            self.perf_radio.setChecked(True)
        elif profile == PerformanceProfile.VISUAL:
            self.visual_radio.setChecked(True)
        elif profile == PerformanceProfile.BATTERY:
            self.battery_radio.setChecked(True)
        elif profile == PerformanceProfile.MINIMAL:
            self.minimal_radio.setChecked(True)


class ConfigurationPreviewWidget(QWidget):
    """Widget showing configuration preview."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Configuration Preview")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Preview area
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlainText("Generate configuration to preview changes here.")
        layout.addWidget(self.preview_text)
    
    def update_preview(self, config: Dict[str, Any]):
        """Update the preview with generated configuration."""
        formatted_config = self._format_config(config)
        self.preview_text.setPlainText(formatted_config)
    
    def _format_config(self, config: Dict[str, Any]) -> str:
        """Format configuration for display."""
        lines = ["Generated Configuration Preview:"]
        lines.append("=" * 40)
        
        for section, values in config.items():
            lines.append(f"\n[{section}]")
            if isinstance(values, dict):
                for key, value in values.items():
                    lines.append(f"{key} = {value}")
            else:
                lines.append(f"{values}")
        
        return "\n".join(lines)


class AutoconfigWizard(QDialog):
    """Main autoconfig wizard dialog."""
    
    def __init__(self, main_app=None, parent=None):
        super().__init__(parent)
        self.main_app = main_app
        self.system_analysis_data = None
        self.generated_config = None
        self.selected_profile = PerformanceProfile.PERFORMANCE
        self.worker = None
        
        self.setup_ui()
        self.setup_menu()
    
    def setup_ui(self):
        """Setup the wizard UI."""
        self.setWindowTitle("HyprRice Autoconfig Wizard")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowTitleHint)
        self.resize(800, 700)
        
        layout = QVBoxLayout(self)
        
        # Wizard steps
        self.create_steps_layout(layout)
        
        # Navigation buttons
        self.create_navigation_buttons(layout)
    
    def create_steps_layout(self, parent_layout):
        """Create the steps layout."""
        steps_layout = QHBoxLayout()
        
        # Left panel - system analysis
        left_panel = QGroupBox("System Analysis")
        left_layout = QVBoxLayout(left_panel)
        
        self.analyze_button = QPushButton("🔍 Analyze System")
        self.analyze_button.clicked.connect(self.start_analysis)
        left_layout.addWidget(self.analyze_button)
        
        self.analysis_progress = QProgressBar()
        self.analysis_progress.setVisible(False)
        left_layout.addWidget(self.analysis_progress)
        
        self.system_analysis_widget = SystemAnalysisWidget()
        left_layout.addWidget(self.system_analysis_widget)
        
        self.generate_button = QPushButton("⚙️ Generate Configuration")
        self.generate_button.clicked.connect(self.start_generation)
        self.generate_button.setEnabled(False)
        left_layout.addWidget(self.generate_button)
        
        steps_layout.addWidget(left_panel, 1)
        
        # Right panel - profile selection and preview
        right_panel = QGroupBox("Configuration")
        right_layout = QVBoxLayout(right_panel)
        
        self.profile_selection_widget = ProfileSelectionWidget()
        self.profile_selection_widget.profile_selected.connect(self._on_profile_selected)
        right_layout.addWidget(self.profile_selection_widget)
        
        self.config_preview_widget = ConfigurationPreviewWidget()
        right_layout.addWidget(self.config_preview_widget, 1)
        
        self.apply_button = QPushButton("✅ Apply Configuration")
        self.apply_button.clicked.connect(self.start_application)
        self.apply_button.setEnabled(False)
        right_layout.addWidget(self.apply_button)
        
        steps_layout.addWidget(right_panel, 1)
        
        parent_layout.addLayout(steps_layout)
    
    def create_navigation_buttons(self, parent_layout):
        """Create navigation buttons."""
        nav_layout = QHBoxLayout()
        
        self.help_button = QPushButton("❓ Help")
        self.help_button.clicked.connect(self.show_help)
        nav_layout.addWidget(self.help_button)
        
        nav_layout.addStretch()
        
        # Rollback button
        self.rollback_button = QPushButton("↩️ Rollback Changes")
        self.rollback_button.clicked.connect(self.show_rollback)
        self.rollback_button.setEnabled(False)
        nav_layout.addWidget(self.rollback_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        nav_layout.addWidget(self.close_button)
        
        parent_layout.addLayout(nav_layout)
    
    def setup_menu(self):
        """Setup additional options."""
        # Add some checkbox options
        options_layout = QHBoxLayout()
        
        self.auto_reload_checkbox = QCheckBox("Auto-reload Hyprland configuration")
        self.auto_reload_checkbox.setChecked(True)
        options_layout.addWidget(self.auto_reload_checkbox)
        
        self.backup_checkbox = QCheckBox("Create backup before applying")
        self.backup_checkbox.setChecked(True)
        options_layout.addWidget(self.backup_checkbox)
        
        # Add to main layout
        # (This would be added to the main layout in a real implementation)
    
    def start_analysis(self):
        """Start system analysis."""
        self.analyze_button.setEnabled(False)
        self.analysis_progress.setVisible(True)
        self.analysis_progress.setValue(0)
        
        self.worker = AutoconfigWorker("profile", PerformanceProfile.PERFORMANCE)
        self.worker.progress_update.connect(self._update_progress)
        self.worker.finished.connect(self._on_analysis_finished)
        self.worker.error.connect(self._on_worker_error)
        self.worker.start()
    
    def start_generation(self):
        """Start configuration generation."""
        if not self.system_analysis_data:
            QMessageBox.warning(self, "Error", "Please run system analysis first.")
            return
        
        self.generate_button.setEnabled(False)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.worker = AutoconfigWorker("generate", self.selected_profile)
        self.worker.progress_update.connect(self._update_progress)
        self.worker.finished.connect(self._on_generation_finished)
        self.worker.error.connect(self._on_worker_error)
        self.worker.start()
    
    def start_application(self):
        """Start configuration application."""
        if not self.generated_config:
            QMessageBox.warning(self, "Error", "Please generate configuration first.")
            return
        
        # Confirm before applying
        reply = QMessageBox.question(
            self, "Confirm Apply", 
            "Apply the generated configuration? This will modify your Hyprland setup.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.apply_button.setEnabled(False)
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            self.worker = AutoconfigWorker(
                "apply", 
                self.selected_profile,
                auto_reload=self.auto_reload_checkbox.isChecked()
            )
            self.worker.progress_update.connect(self._update_progress)
            self.worker.finished.connect(self._on_application_finished)
            self.worker.error.connect(self._on_worker_error)
            self.worker.start()
    
    def _update_progress(self, value: int, message: str):
        """Update progress bar."""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(value)
        
        # Update status labels if they exist
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
    
    def _on_analysis_finished(self, success: bool, data: Dict[str, Any]):
        """Handle analysis completion."""
        self.analyze_button.setEnabled(True)
        self.analysis_progress.setVisible(False)
        
        if success:
            self.system_analysis_data = data
            self.system_analysis_widget.update_results(data)
            self.generate_button.setEnabled(True)
            
            # Set recommended profile
            recommended = data.get("profile", {}).get("recommended_profile")
            if recommended:
                profile_map = {
                    "performance": PerformanceProfile.PERFORMANCE,
                    "visual": PerformanceProfile.VISUAL,
                    "battery": PerformanceProfile.BATTERY,
                    "minimal": PerformanceProfile.MINIMAL
                }
                if recommended in profile_map:
                    self.profile_selection_widget.set_recommended_profile(
                        profile_map[recommended]
                    )
            
            QMessageBox.information(self, "Success", "System analysis completed successfully!")
        else:
            QMessageBox.critical(self, "Error", "System analysis failed.")
    
    def _on_generation_finished(self, success: bool, data: Dict[str, Any]):
        """Handle generation completion."""
        self.generate_button.setEnabled(True)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(False)
        
        if success:
            self.generated_config = data["config"]
            self.config_preview_widget.update_preview(data["config"])
            self.apply_button.setEnabled(True)
            
            QMessageBox.information(
                self, "Success", 
                f"Configuration generated successfully!\n\nPerformance Impact: {data.get('performance_impact', 'Unknown')}"
            )
        else:
            QMessageBox.critical(self, "Error", "Configuration generation failed.")
    
    def _on_application_finished(self, success: bool, data: Dict[str, Any]):
        """Handle application completion."""
        self.apply_button.setEnabled(True)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(False)
        
        if success:
            self.rollback_button.setEnabled(True)
            QMessageBox.information(
                self, "Success", 
                f"Configuration applied successfully!\n\nBackup created at: {data.get('backup_path', 'Unknown')}"
            )
        else:
            QMessageBox.critical(self, "Error", "Configuration application failed.")
    
    def _on_worker_error(self, error_type: str, message: str):
        """Handle worker errors."""
        # Enable buttons
        self.analyze_button.setEnabled(True)
        self.generate_button.setEnabled(True)
        self.apply_button.setEnabled(True)
        
        # Hide progress bars
        self.analysis_progress.setVisible(False)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(False)
        
        QMessageBox.critical(self, f"Error ({error_type})", message)


    def _on_profile_selected(self, profile: PerformanceProfile):
        """Handle profile selection change."""
        self.selected_profile = profile
    
    def show_help(self):
        """Show help dialog."""
        help_text = """
HyprRice Autoconfig Wizard

This wizard helps you automatically optimize your Hyprland configuration based on your system capabilities.

Steps:
1. Analyze System - Detects CPU, memory, GPU, and storage capabilities
2. Select Profile - Choose optimization profile (Performance, Visual, Battery, Minimal)
3. Generate Config - Creates optimized configuration for your system
4. Apply Changes - Applies the configuration to Hyprland

Profiles:
• Performance - Optimized for speed and responsiveness
• Visual - Maximum visual effects and animations  
• Battery - Power-saving optimizations for laptops
• Minimal - Lightweight for low-end systems

The wizard creates automatic backups and allows rollback if needed.
"""
        
        QMessageBox.information(self, "Autoconfig Wizard Help", help_text)
    
    def show_rollback(self):
        """Show rollback dialog."""
        if not self.system_analysis_data:
            QMessageBox.information(self, "Rollback", "No configuration has been applied yet.")
            return
        
        reply = QMessageBox.question(
            self, "Rollback Changes", 
            "Rollback to the previous configuration?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Implement rollback functionality
                if hasattr(self.main_app, 'backup_manager') and self.main_app.backup_manager:
                    backup_manager = self.main_app.backup_manager
                    if backup_manager.get_backups():
                        # Get the most recent backup
                        backups = backup_manager.get_backups()
                        latest_backup = max(backups, key=lambda b: b.timestamp)
                        
                        # Restore from backup
                        if backup_manager.restore_backup(latest_backup.name):
                            QMessageBox.information(
                                self, "Rollback Success", 
                                f"Configuration restored from backup: {latest_backup.name}"
                            )
                            self.rollback_button.setEnabled(False)
                            # Reload configuration in main app
                            self.main_app.config.load()
                        else:
                            QMessageBox.critical(self, "Rollback Failed", "Failed to restore backup.")
                    else:
                        QMessageBox.warning(self, "No Backups", "No backups available for rollback.")
                else:
                    QMessageBox.warning(self, "Backup System", "Backup system not available.")
            except Exception as e:
                QMessageBox.critical(self, "Rollback Error", f"Error during rollback: {e}")
    
    def closeEvent(self, event):
        """Handle dialog close."""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "Confirm Close", 
                "An operation is running. Close anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.cancel()
                self.worker.wait()
            else:
                event.ignore()
                return
        
        super().closeEvent(event)


def show_autoconfig_wizard(main_app=None, parent=None):
    """Show the autoconfig wizard."""
    wizard = AutoconfigWizard(main_app, parent)
    wizard.exec()
