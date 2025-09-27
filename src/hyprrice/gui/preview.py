"""
Live preview system for HyprRice themes and configurations.
"""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QSizePolicy, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen

from ..config import Config
from ..utils import hyprctl, get_monitors, get_workspaces, get_windows


class PreviewRenderer(QThread):
    """Background thread for rendering preview images."""
    
    preview_ready = pyqtSignal(QPixmap)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config: Config, width: int = 800, height: int = 600):
        super().__init__()
        self.config = config
        self.width = width
        self.height = height
        self.cancelled = False
    
    def run(self):
        """Render the preview image."""
        try:
            if self.cancelled:
                return
            
            # Create a pixmap for the preview
            pixmap = QPixmap(self.width, self.height)
            pixmap.fill(QColor("#2e3440"))  # Default background
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Render the preview based on current config
            self._render_hyprland_preview(painter)
            
            painter.end()
            
            if not self.cancelled:
                self.preview_ready.emit(pixmap)
                
        except Exception as e:
            if not self.cancelled:
                self.error_occurred.emit(str(e))
    
    def _render_hyprland_preview(self, painter: QPainter):
        """Render Hyprland-specific preview elements."""
        # Draw desktop background
        bg_color = QColor(self.config.hyprland.border_color if hasattr(self.config.hyprland, 'border_color') else "#2e3440")
        painter.fillRect(0, 0, self.width, self.height, bg_color)
        
        # Draw waybar
        self._render_waybar(painter)
        
        # Draw windows
        self._render_windows(painter)
        
        # Draw workspaces
        self._render_workspaces(painter)
    
    def _render_waybar(self, painter: QPainter):
        """Render waybar preview."""
        waybar_height = getattr(self.config.waybar, 'height', 30)
        waybar_bg = QColor(getattr(self.config.waybar, 'background_color', 'rgba(43, 48, 59, 0.5)'))
        
        # Draw waybar background
        painter.fillRect(0, 0, self.width, waybar_height, waybar_bg)
        
        # Draw waybar modules
        font = QFont("JetBrainsMono Nerd Font", 10)
        painter.setFont(font)
        painter.setPen(QColor(getattr(self.config.waybar, 'text_color', '#ffffff')))
        
        # Draw clock
        painter.drawText(10, waybar_height - 5, "12:34")
        
        # Draw battery
        painter.drawText(self.width - 100, waybar_height - 5, "100%")
    
    def _render_windows(self, painter: QPainter):
        """Render window previews."""
        # Draw some example windows
        windows = [
            {"x": 50, "y": 80, "width": 300, "height": 200, "title": "Terminal"},
            {"x": 400, "y": 80, "width": 300, "height": 200, "title": "Browser"},
            {"x": 50, "y": 320, "width": 650, "height": 200, "title": "Code Editor"}
        ]
        
        for window in windows:
            # Window background
            painter.fillRect(window["x"], window["y"], window["width"], window["height"], 
                           QColor("#3b4252"))
            
            # Window border
            border_size = getattr(self.config.hyprland, 'border_size', 1)
            border_color = QColor(getattr(self.config.hyprland, 'border_color', '#ffffff'))
            painter.setPen(QPen(border_color, border_size))
            painter.drawRect(window["x"], window["y"], window["width"], window["height"])
            
            # Title bar
            title_height = 25
            painter.fillRect(window["x"], window["y"], window["width"], title_height, 
                           QColor("#4c566a"))
            
            # Title text
            font = QFont("Inter", 10)
            painter.setFont(font)
            painter.setPen(QColor("#eceff4"))
            painter.drawText(window["x"] + 10, window["y"] + 18, window["title"])
    
    def _render_workspaces(self, painter: QPainter):
        """Render workspace indicators."""
        # Draw workspace indicators at the bottom
        workspace_count = 5
        indicator_size = 8
        spacing = 15
        start_x = (self.width - (workspace_count * indicator_size + (workspace_count - 1) * spacing)) // 2
        start_y = self.height - 30
        
        for i in range(workspace_count):
            x = start_x + i * (indicator_size + spacing)
            color = QColor("#5e81ac") if i == 0 else QColor("#4c566a")  # First workspace active
            painter.fillRect(x, start_y, indicator_size, indicator_size, color)
    
    def cancel(self):
        """Cancel the rendering operation."""
        self.cancelled = True


class PreviewWindow(QWidget):
    """Live preview window for HyprRice configurations."""
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.renderer: Optional[PreviewRenderer] = None
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """Setup the preview window UI."""
        self.setWindowTitle("HyprRice Live Preview")
        self.setGeometry(100, 100, 900, 700)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Live Preview")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #eceff4;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Control buttons
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update_preview)
        header_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_preview)
        header_layout.addWidget(export_btn)
        
        layout.addLayout(header_layout)
        
        # Preview area
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.preview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(800, 600)
        self.preview_label.setStyleSheet("background-color: #2e3440; border: 1px solid #4c566a;")
        
        self.preview_scroll.setWidget(self.preview_label)
        layout.addWidget(self.preview_scroll)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #88c0d0; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
    
    def setup_timer(self):
        """Setup auto-refresh timer."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_preview)
        # Auto-refresh every 5 seconds
        self.refresh_timer.start(5000)
    
    def update_preview(self):
        """Update the preview image."""
        if self.renderer and self.renderer.isRunning():
            self.renderer.cancel()
            self.renderer.wait()
        
        self.status_label.setText("Rendering preview...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        self.renderer = PreviewRenderer(self.config, 800, 600)
        self.renderer.preview_ready.connect(self.on_preview_ready)
        self.renderer.error_occurred.connect(self.on_preview_error)
        self.renderer.start()
    
    @pyqtSlot(QPixmap)
    def on_preview_ready(self, pixmap: QPixmap):
        """Handle preview rendering completion."""
        self.preview_label.setPixmap(pixmap)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Preview updated")
        
        # Auto-hide status after 3 seconds
        QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))
    
    @pyqtSlot(str)
    def on_preview_error(self, error: str):
        """Handle preview rendering error."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error}")
        
        # Show error message
        QMessageBox.warning(self, "Preview Error", f"Failed to render preview:\n{error}")
    
    def export_preview(self):
        """Export the current preview as an image."""
        if not self.preview_label.pixmap():
            QMessageBox.warning(self, "No Preview", "No preview available to export.")
            return
        
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Preview",
            "hyprrice_preview.png",
            "PNG Images (*.png);;JPEG Images (*.jpg);;All Files (*)"
        )
        
        if file_path:
            try:
                self.preview_label.pixmap().save(file_path)
                QMessageBox.information(self, "Export Success", f"Preview exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export preview:\n{e}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.renderer and self.renderer.isRunning():
            self.renderer.cancel()
            self.renderer.wait()
        
        self.refresh_timer.stop()
        event.accept()