"""
AI Workflow Tab for HyprRice GUI

This module provides a GUI interface for the AI workflow system,
allowing users to enhance components through the AI pipeline.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QLabel, QPushButton, QLineEdit, QTextEdit, QFileDialog, QProgressBar,
    QGroupBox, QCheckBox, QComboBox, QSpinBox, QSlider, QListWidget,
    QListWidgetItem, QTreeWidget, QTreeWidgetItem, QSplitter, QFrame,
    QMessageBox, QScrollArea, QFormLayout, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor

from ..ai_workflow import AIWorkflowEngine, WorkflowResult, ComponentAnalysis, ResearchData
from ..config import Config
from ..exceptions import HyprRiceError


class AIWorkflowWorker(QThread):
    """Background worker for AI workflow operations"""
    
    progress = pyqtSignal(int, str)  # progress, status message
    finished = pyqtSignal(object)    # result
    error = pyqtSignal(str)          # error message
    
    def __init__(self, workflow_engine: AIWorkflowEngine, component_path: str, 
                 component_name: str, prompt: str, reference_image: Optional[str] = None):
        super().__init__()
        self.workflow_engine = workflow_engine
        self.component_path = component_path
        self.component_name = component_name
        self.prompt = prompt
        self.reference_image = reference_image
    
    def run(self):
        """Execute the AI workflow pipeline"""
        try:
            self.progress.emit(10, "Setting up environment...")
            result = self.workflow_engine.ai_component_pipeline(
                self.component_path, self.component_name, self.prompt, self.reference_image
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ComponentAnalysisWidget(QWidget):
    """Widget for displaying component analysis results"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the analysis display UI"""
        layout = QVBoxLayout(self)
        
        # Analysis tabs
        self.analysis_tabs = QTabWidget()
        
        # Logic Map tab
        self.logic_map_widget = QTreeWidget()
        self.logic_map_widget.setHeaderLabels(["Element", "Type", "Details"])
        self.analysis_tabs.addTab(self.logic_map_widget, "Logic Map")
        
        # Missing Logic tab
        self.missing_logic_list = QListWidget()
        self.analysis_tabs.addTab(self.missing_logic_list, "Missing Logic")
        
        # Improvements tab
        self.improvements_list = QListWidget()
        self.analysis_tabs.addTab(self.improvements_list, "Improvements")
        
        # Features tab
        self.features_list = QListWidget()
        self.analysis_tabs.addTab(self.features_list, "New Features")
        
        # Performance tab
        self.performance_list = QListWidget()
        self.analysis_tabs.addTab(self.performance_list, "Performance")
        
        # Security tab
        self.security_list = QListWidget()
        self.analysis_tabs.addTab(self.security_list, "Security")
        
        layout.addWidget(self.analysis_tabs)
    
    def update_analysis(self, analysis: ComponentAnalysis):
        """Update the analysis display with new data"""
        # Update logic map
        self.logic_map_widget.clear()
        
        # Add classes
        classes_item = QTreeWidgetItem(["Classes", "Category", ""])
        for cls in analysis.logic_map.get("classes", []):
            class_item = QTreeWidgetItem([cls["name"], "Class", f"Methods: {len(cls['methods'])}"])
            for method in cls["methods"]:
                QTreeWidgetItem(class_item, [method, "Method", ""])
            classes_item.addChild(class_item)
        self.logic_map_widget.addTopLevelItem(classes_item)
        
        # Add functions
        functions_item = QTreeWidgetItem(["Functions", "Category", ""])
        for func in analysis.logic_map.get("functions", []):
            func_item = QTreeWidgetItem([
                func["name"], 
                "Function", 
                f"Args: {len(func['args'])}, Complexity: {func['complexity']}"
            ])
            functions_item.addChild(func_item)
        self.logic_map_widget.addTopLevelItem(functions_item)
        
        # Update lists
        self.missing_logic_list.clear()
        for logic in analysis.missing_logic:
            self.missing_logic_list.addItem(logic)
        
        self.improvements_list.clear()
        for improvement in analysis.improvements:
            self.improvements_list.addItem(improvement)
        
        self.features_list.clear()
        for feature in analysis.possible_features:
            self.features_list.addItem(feature)
        
        self.performance_list.clear()
        for issue in analysis.performance_issues:
            self.performance_list.addItem(issue)
        
        self.security_list.clear()
        for concern in analysis.security_concerns:
            self.security_list.addItem(concern)
        
        # Expand all items
        self.logic_map_widget.expandAll()


class ResearchDataWidget(QWidget):
    """Widget for displaying research data"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the research display UI"""
        layout = QVBoxLayout(self)
        
        # Research tabs
        self.research_tabs = QTabWidget()
        
        # Web Resources tab
        self.web_resources_list = QListWidget()
        self.research_tabs.addTab(self.web_resources_list, "Web Resources")
        
        # Known Issues tab
        self.issues_list = QListWidget()
        self.research_tabs.addTab(self.issues_list, "Known Issues")
        
        # Examples tab
        self.examples_list = QListWidget()
        self.research_tabs.addTab(self.examples_list, "Examples")
        
        # Best Practices tab
        self.best_practices_list = QListWidget()
        self.research_tabs.addTab(self.best_practices_list, "Best Practices")
        
        # Performance Tips tab
        self.performance_tips_list = QListWidget()
        self.research_tabs.addTab(self.performance_tips_list, "Performance Tips")
        
        # Security tab
        self.security_considerations_list = QListWidget()
        self.research_tabs.addTab(self.security_considerations_list, "Security")
        
        layout.addWidget(self.research_tabs)
    
    def update_research(self, research: ResearchData):
        """Update the research display with new data"""
        # Update web resources
        self.web_resources_list.clear()
        for resource in research.web_resources:
            item = QListWidgetItem(f"{resource['title']} - {resource['url']}")
            item.setToolTip(resource.get('content', ''))
            self.web_resources_list.addItem(item)
        
        # Update known issues
        self.issues_list.clear()
        for issue in research.known_issues:
            item = QListWidgetItem(f"{issue['issue_id']}: {issue['description']}")
            item.setToolTip(f"Severity: {issue['severity']}, Status: {issue['status']}")
            self.issues_list.addItem(item)
        
        # Update examples
        self.examples_list.clear()
        for example in research.examples:
            item = QListWidgetItem(f"{example['source']}: {example['description']}")
            item.setToolTip(example['url'])
            self.examples_list.addItem(item)
        
        # Update best practices
        self.best_practices_list.clear()
        for practice in research.best_practices:
            self.best_practices_list.addItem(practice)
        
        # Update performance tips
        self.performance_tips_list.clear()
        for tip in research.performance_tips:
            self.performance_tips_list.addItem(tip)
        
        # Update security considerations
        self.security_considerations_list.clear()
        for consideration in research.security_considerations:
            self.security_considerations_list.addItem(consideration)


class AIWorkflowTab(QWidget):
    """Main AI Workflow tab for the HyprRice GUI"""
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.workflow_engine = AIWorkflowEngine(config)
        self.worker = None
        self.current_analysis = None
        self.current_research = None
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the main UI"""
        layout = QVBoxLayout(self)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Input and controls
        left_panel = self.create_input_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Results and analysis
        right_panel = self.create_results_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
    
    def create_input_panel(self) -> QWidget:
        """Create the input panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Component selection group
        component_group = QGroupBox("Component Selection")
        component_layout = QFormLayout(component_group)
        
        # Component file path
        self.component_path_edit = QLineEdit()
        self.component_path_edit.setPlaceholderText("Select component file...")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_component_file)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.component_path_edit)
        path_layout.addWidget(self.browse_button)
        component_layout.addRow("Component File:", path_layout)
        
        # Component name
        self.component_name_edit = QLineEdit()
        self.component_name_edit.setPlaceholderText("Enter component name...")
        component_layout.addRow("Component Name:", self.component_name_edit)
        
        layout.addWidget(component_group)
        
        # Enhancement prompt group
        prompt_group = QGroupBox("Enhancement Prompt")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Describe what you want to enhance...")
        self.prompt_edit.setMaximumHeight(100)
        prompt_layout.addWidget(self.prompt_edit)
        
        layout.addWidget(prompt_group)
        
        # Reference image group
        image_group = QGroupBox("Reference Image (Optional)")
        image_layout = QFormLayout(image_group)
        
        self.reference_image_edit = QLineEdit()
        self.reference_image_edit.setPlaceholderText("Select reference image...")
        self.browse_image_button = QPushButton("Browse...")
        self.browse_image_button.clicked.connect(self.browse_reference_image)
        
        image_path_layout = QHBoxLayout()
        image_path_layout.addWidget(self.reference_image_edit)
        image_path_layout.addWidget(self.browse_image_button)
        image_layout.addRow("Reference Image:", image_path_layout)
        
        layout.addWidget(image_group)
        
        # Workflow options group
        options_group = QGroupBox("Workflow Options")
        options_layout = QFormLayout(options_group)
        
        # Research phase
        self.enable_research = QCheckBox("Enable Research Phase")
        self.enable_research.setChecked(True)
        options_layout.addRow("Research:", self.enable_research)
        
        # Analysis phase
        self.enable_analysis = QCheckBox("Enable Analysis Phase")
        self.enable_analysis.setChecked(True)
        options_layout.addRow("Analysis:", self.enable_analysis)
        
        # GUI design phase
        self.enable_gui_design = QCheckBox("Enable GUI Design Phase")
        self.enable_gui_design.setChecked(True)
        options_layout.addRow("GUI Design:", self.enable_gui_design)
        
        # Testing phase
        self.enable_testing = QCheckBox("Enable Testing Phase")
        self.enable_testing.setChecked(True)
        options_layout.addRow("Testing:", self.enable_testing)
        
        layout.addWidget(options_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start AI Workflow")
        self.start_button.setStyleSheet("QPushButton { background-color: #007acc; color: white; font-weight: bold; }")
        self.start_button.clicked.connect(self.start_workflow)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_workflow)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_form)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to start AI workflow")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        return panel
    
    def create_results_panel(self) -> QWidget:
        """Create the results panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Results tabs
        self.results_tabs = QTabWidget()
        
        # Research tab
        self.research_widget = ResearchDataWidget()
        self.results_tabs.addTab(self.research_widget, "Research")
        
        # Analysis tab
        self.analysis_widget = ComponentAnalysisWidget()
        self.results_tabs.addTab(self.analysis_widget, "Analysis")
        
        # Results tab
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_tabs.addTab(self.results_text, "Results")
        
        # Log tab
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.results_tabs.addTab(self.log_text, "Log")
        
        layout.addWidget(self.results_tabs)
        
        return panel
    
    def setup_connections(self):
        """Setup signal connections"""
        # Auto-fill component name when path changes
        self.component_path_edit.textChanged.connect(self.auto_fill_component_name)
    
    def browse_component_file(self):
        """Browse for component file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Component File", "",
            "Python Files (*.py);;JavaScript Files (*.js);;TypeScript Files (*.ts);;All Files (*)"
        )
        if file_path:
            self.component_path_edit.setText(file_path)
    
    def browse_reference_image(self):
        """Browse for reference image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Reference Image", "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )
        if file_path:
            self.reference_image_edit.setText(file_path)
    
    def auto_fill_component_name(self):
        """Auto-fill component name from file path"""
        if not self.component_name_edit.text():
            file_path = self.component_path_edit.text()
            if file_path:
                component_name = Path(file_path).stem
                self.component_name_edit.setText(component_name)
    
    def start_workflow(self):
        """Start the AI workflow"""
        # Validate inputs
        if not self.component_path_edit.text():
            QMessageBox.warning(self, "Validation Error", "Please select a component file")
            return
        
        if not self.component_name_edit.text():
            QMessageBox.warning(self, "Validation Error", "Please enter a component name")
            return
        
        if not self.prompt_edit.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter an enhancement prompt")
            return
        
        # Check if file exists
        if not os.path.exists(self.component_path_edit.text()):
            QMessageBox.warning(self, "File Error", "Component file does not exist")
            return
        
        # Start the workflow
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Create and start worker
        reference_image = self.reference_image_edit.text() if self.reference_image_edit.text() else None
        
        self.worker = AIWorkflowWorker(
            self.workflow_engine,
            self.component_path_edit.text(),
            self.component_name_edit.text(),
            self.prompt_edit.toPlainText(),
            reference_image
        )
        
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.workflow_finished)
        self.worker.error.connect(self.workflow_error)
        
        self.worker.start()
        
        self.log_message("AI Workflow started...")
    
    def stop_workflow(self):
        """Stop the AI workflow"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.log_message("AI Workflow stopped by user")
    
    def reset_form(self):
        """Reset the form to initial state"""
        self.component_path_edit.clear()
        self.component_name_edit.clear()
        self.prompt_edit.clear()
        self.reference_image_edit.clear()
        
        self.results_text.clear()
        self.log_text.clear()
        
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready to start AI workflow")
        
        # Reset research and analysis widgets
        self.research_widget.update_research(ResearchData([], [], [], [], [], []))
        self.analysis_widget.update_analysis(ComponentAnalysis({}, [], [], [], [], [], 0.0))
    
    def update_progress(self, value: int, message: str):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        self.log_message(message)
    
    def workflow_finished(self, result: WorkflowResult):
        """Handle workflow completion"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if result.success:
            self.status_label.setText("AI Workflow completed successfully!")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            
            # Display results
            self.display_results(result)
        else:
            self.status_label.setText("AI Workflow failed")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            
            # Display errors
            error_text = "Workflow failed with the following errors:\n\n"
            for error in result.error_log:
                error_text += f"• {error}\n"
            self.results_text.setPlainText(error_text)
        
        self.log_message(f"Workflow completed in {result.execution_time:.2f} seconds")
    
    def workflow_error(self, error_message: str):
        """Handle workflow error"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.status_label.setText("AI Workflow error")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        self.log_message(f"Error: {error_message}")
        QMessageBox.critical(self, "Workflow Error", f"An error occurred:\n{error_message}")
    
    def display_results(self, result: WorkflowResult):
        """Display workflow results"""
        results_text = f"""AI Workflow Results
====================

Component: {result.component_path}
Success: {result.success}
Tests Passed: {result.tests_passed}
Execution Time: {result.execution_time:.2f} seconds
Performance Improvement: {result.performance_improvement:.2%}

Changes Applied:
"""
        
        for change in result.changes_applied:
            results_text += f"• {change}\n"
        
        if result.error_log:
            results_text += "\nErrors:\n"
            for error in result.error_log:
                results_text += f"• {error}\n"
        
        self.results_text.setPlainText(results_text)
    
    def log_message(self, message: str):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.append(log_entry)
        
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def update_research_display(self, research: ResearchData):
        """Update research display"""
        self.current_research = research
        self.research_widget.update_research(research)
        self.results_tabs.setCurrentIndex(0)  # Switch to research tab
    
    def update_analysis_display(self, analysis: ComponentAnalysis):
        """Update analysis display"""
        self.current_analysis = analysis
        self.analysis_widget.update_analysis(analysis)
        self.results_tabs.setCurrentIndex(1)  # Switch to analysis tab