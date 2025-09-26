"""
Enhanced preview window with real-time updates for HyprRice
"""

import os
import logging
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QGroupBox, QGridLayout, QPushButton, QProgressBar, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QPalette, QFont, QPixmap, QPainter


class ColorPreview(QFrame):
    """A widget that shows a color preview."""
    
    def __init__(self, color: str = "#000000", label: str = "Color"):
        super().__init__()
        self.color = color
        self.label = label
        self.setFixedSize(80, 60)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        self.update_color()
    
    def set_color(self, color: str):
        """Set the preview color."""
        self.color = color
        self.update_color()
    
    def update_color(self):
        """Update the color display."""
        try:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.color};
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }}
            """)
            self.setToolTip(f"{self.label}: {self.color}")
        except:
            self.setStyleSheet("background-color: #fff; border: 1px solid red;")
            self.setToolTip(f"{self.label}: Invalid color")


class PreviewWindow(QWidget):
    """Enhanced preview window showing live configuration preview."""
    
    # Signals
    config_applied = pyqtSignal(str)  # Emitted when config is applied
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Import managers
        from ..hyprland.windows import WindowManager
        from ..hyprland.display import DisplayManager
        from ..hyprland.input import InputManager
        from ..hyprland.workspaces import WorkspaceManager
        
        # Initialize managers
        hyprland_config_path = getattr(config.paths, 'hyprland_config', '~/.config/hypr/hyprland.conf')
        self.window_manager = WindowManager(os.path.expanduser(hyprland_config_path))
        self.display_manager = DisplayManager(os.path.expanduser(hyprland_config_path))
        self.input_manager = InputManager(os.path.expanduser(hyprland_config_path))
        self.workspace_manager = WorkspaceManager(os.path.expanduser(hyprland_config_path))
        
        self.setWindowTitle("HyprRice - Live Preview")
        self.setGeometry(100, 100, 800, 600)
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_preview)
        
        # Auto-refresh settings
        self.auto_refresh = True
        self.refresh_interval = 2000  # 2 seconds
        
        self.setup_ui()
        self.start_auto_refresh()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Live Configuration Preview")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh Now")
        self.refresh_button.clicked.connect(self.update_preview)
        header_layout.addWidget(self.refresh_button)
        
        # Auto-refresh toggle
        self.auto_refresh_button = QPushButton("Auto-Refresh: ON")
        self.auto_refresh_button.clicked.connect(self.toggle_auto_refresh)
        header_layout.addWidget(self.auto_refresh_button)
        
        # Apply to Hyprland button
        self.apply_button = QPushButton("Apply to Hyprland")
        self.apply_button.clicked.connect(self.apply_to_hyprland)
        self.apply_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        header_layout.addWidget(self.apply_button)
        
        layout.addLayout(header_layout)
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.content_layout = QVBoxLayout(scroll_widget)
        
        # Create preview sections
        self.create_theme_preview()
        self.create_hyprland_preview()
        self.create_waybar_preview()
        self.create_system_info()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("QLabel { padding: 5px; background-color: #f0f0f0; }")
        layout.addWidget(self.status_label)
    
    def create_theme_preview(self):
        """Create theme preview section."""
        theme_group = QGroupBox("Current Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        # Theme info
        self.theme_info_label = QLabel("Theme: Loading...")
        theme_layout.addWidget(self.theme_info_label)
        
        # Color palette
        colors_layout = QHBoxLayout()
        colors_layout.addWidget(QLabel("Colors:"))
        
        self.color_previews = {}
        color_names = ['primary', 'secondary', 'accent', 'text', 'background']
        for color_name in color_names:
            color_preview = ColorPreview(label=color_name.capitalize())
            self.color_previews[color_name] = color_preview
            colors_layout.addWidget(color_preview)
        
        colors_layout.addStretch()
        theme_layout.addLayout(colors_layout)
        
        self.content_layout.addWidget(theme_group)
    
    def create_hyprland_preview(self):
        """Create Hyprland settings preview."""
        hyprland_group = QGroupBox("Hyprland Configuration")
        hyprland_layout = QGridLayout(hyprland_group)
        
        # Window settings
        hyprland_layout.addWidget(QLabel("Border Color:"), 0, 0)
        self.border_color_preview = ColorPreview(label="Border")
        hyprland_layout.addWidget(self.border_color_preview, 0, 1)
        
        self.gaps_label = QLabel("Gaps: Loading...")
        hyprland_layout.addWidget(self.gaps_label, 0, 2)
        
        self.border_size_label = QLabel("Border Size: Loading...")
        hyprland_layout.addWidget(self.border_size_label, 0, 3)
        
        # Effects settings
        self.blur_label = QLabel("Blur: Loading...")
        hyprland_layout.addWidget(self.blur_label, 1, 0)
        
        self.animations_label = QLabel("Animations: Loading...")
        hyprland_layout.addWidget(self.animations_label, 1, 1)
        
        self.rounding_label = QLabel("Rounding: Loading...")
        hyprland_layout.addWidget(self.rounding_label, 1, 2)
        
        self.content_layout.addWidget(hyprland_group)
    
    def create_waybar_preview(self):
        """Create Waybar preview section."""
        waybar_group = QGroupBox("Waybar Configuration")
        waybar_layout = QVBoxLayout(waybar_group)
        
        # Waybar mockup
        waybar_mockup = QFrame()
        waybar_mockup.setFixedHeight(35)
        waybar_mockup.setFrameStyle(QFrame.Box)
        waybar_layout.addWidget(waybar_mockup)
        self.waybar_mockup = waybar_mockup
        
        # Waybar info
        info_layout = QHBoxLayout()
        
        self.waybar_bg_preview = ColorPreview(label="Background")
        info_layout.addWidget(self.waybar_bg_preview)
        
        self.waybar_text_preview = ColorPreview(label="Text")
        info_layout.addWidget(self.waybar_text_preview)
        
        self.waybar_info_label = QLabel("Height: Loading...")
        info_layout.addWidget(self.waybar_info_label)
        
        info_layout.addStretch()
        waybar_layout.addLayout(info_layout)
        
        self.content_layout.addWidget(waybar_group)
    
    def create_system_info(self):
        """Create system information section."""
        system_group = QGroupBox("System Status")
        system_layout = QVBoxLayout(system_group)
        
        # System info text
        self.system_info_text = QTextEdit()
        self.system_info_text.setMaximumHeight(150)
        self.system_info_text.setReadOnly(True)
        system_layout.addWidget(self.system_info_text)
        
        self.content_layout.addWidget(system_group)
    
    def update_preview(self):
        """Update the preview with current configuration."""
        try:
            self.status_label.setText("Updating preview...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            
            # Update theme info
            self.update_theme_info()
            
            # Update Hyprland info
            self.update_hyprland_info()
            
            # Update Waybar info
            self.update_waybar_info()
            
            # Update system info
            self.update_system_info()
            
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"Preview updated at {QTimer().currentTime().toString()}")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"Update failed: {str(e)}")
            self.logger.error(f"Preview update error: {e}")
    
    def update_theme_info(self):
        """Update theme information."""
        try:
            theme_name = getattr(self.config, 'current_theme', 'Default')
            self.theme_info_label.setText(f"Theme: {theme_name}")
            
            # Update color previews
            if hasattr(self.config, 'colors'):
                colors = self.config.colors
                for color_name, preview in self.color_previews.items():
                    color_value = getattr(colors, color_name, '#000000')
                    preview.set_color(color_value)
            
        except Exception as e:
            self.theme_info_label.setText(f"Theme: Error loading ({str(e)})")
    
    def update_hyprland_info(self):
        """Update Hyprland configuration info."""
        try:
            # Get current Hyprland config
            window_config = self.window_manager.get_window_config()
            
            # Update border color
            border_color = window_config.get('general_col_active_border', '#5e81ac')
            if isinstance(border_color, str):
                self.border_color_preview.set_color(border_color)
            
            # Update gaps
            gaps_in = window_config.get('general_gaps_in', 5)
            gaps_out = window_config.get('general_gaps_out', 10)
            self.gaps_label.setText(f"Gaps: {gaps_in}/{gaps_out}")
            
            # Update border size
            border_size = window_config.get('general_border_size', 2)
            self.border_size_label.setText(f"Border: {border_size}px")
            
            # Update blur
            blur_enabled = window_config.get('decoration_blur_enabled', True)
            blur_size = window_config.get('decoration_blur_size', 8)
            self.blur_label.setText(f"Blur: {'On' if blur_enabled else 'Off'} ({blur_size})")
            
            # Update animations
            animations = window_config.get('animations_enabled', True)
            self.animations_label.setText(f"Animations: {'On' if animations else 'Off'}")
            
            # Update rounding
            rounding = window_config.get('decoration_rounding', 8)
            self.rounding_label.setText(f"Rounding: {rounding}px")
            
        except Exception as e:
            self.gaps_label.setText(f"Hyprland: Error ({str(e)})")
    
    def update_waybar_info(self):
        """Update Waybar configuration info."""
        try:
            if hasattr(self.config, 'waybar'):
                waybar = self.config.waybar
                
                # Update colors
                bg_color = getattr(waybar, 'background_color', 'rgba(46, 52, 64, 0.8)')
                text_color = getattr(waybar, 'text_color', '#eceff4')
                
                # Convert rgba to hex for preview (simplified)
                if bg_color.startswith('rgba'):
                    bg_color = '#2e3440'  # Fallback
                if text_color.startswith('rgba'):
                    text_color = '#eceff4'  # Fallback
                
                self.waybar_bg_preview.set_color(bg_color)
                self.waybar_text_preview.set_color(text_color)
                
                # Update waybar mockup
                self.waybar_mockup.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                        border: 1px solid {text_color};
                        border-radius: 4px;
            }}
        """)
        
                # Update info
                height = getattr(waybar, 'height', 30)
                self.waybar_info_label.setText(f"Height: {height}px")
            
        except Exception as e:
            self.waybar_info_label.setText(f"Waybar: Error ({str(e)})")
    
    def update_system_info(self):
        """Update system information."""
        try:
            info_lines = []
            
            # Get monitor info
            monitors = self.display_manager.get_monitors()
            info_lines.append(f"Monitors: {len(monitors)} detected")
            
            # Get workspace info
            workspaces = self.workspace_manager.get_workspaces()
            info_lines.append(f"Workspaces: {len(workspaces)} active")
            
            # Get window info
            windows = self.window_manager.get_window_list()
            info_lines.append(f"Windows: {len(windows)} open")
            
            # Get input devices
            devices = self.input_manager.get_input_devices()
            if isinstance(devices, dict):
                keyboard_count = len(devices.get('keyboards', []))
                mouse_count = len(devices.get('mice', []))
                info_lines.append(f"Input: {keyboard_count} keyboards, {mouse_count} mice")
            else:
                info_lines.append("Input: Device info unavailable")
            
            # System status
            info_lines.append("\\nHyprland Status: " + ("✅ Running" if self.is_hyprland_running() else "❌ Not detected"))
            
            self.system_info_text.setPlainText("\\n".join(info_lines))
            
        except Exception as e:
            self.system_info_text.setPlainText(f"System info error: {str(e)}")
    
    def is_hyprland_running(self) -> bool:
        """Check if Hyprland is running."""
        try:
            import subprocess
            result = subprocess.run(['pgrep', 'Hyprland'], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def apply_to_hyprland(self):
        """Apply current configuration to Hyprland."""
        try:
            self.status_label.setText("Applying configuration to Hyprland...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 100)
            
            success_count = 0
            total_operations = 4
            
            # Apply window settings
            if hasattr(self.config, 'hyprland'):
                hyprland_config = {
                    'general_border_size': getattr(self.config.hyprland, 'border_size', 2),
                    'general_gaps_in': getattr(self.config.hyprland, 'gaps_in', 5),
                    'general_gaps_out': getattr(self.config.hyprland, 'gaps_out', 10),
                    'general_col_active_border': getattr(self.config.hyprland, 'border_color', '#5e81ac'),
                }
                
                if self.window_manager.set_window_config(hyprland_config):
                    success_count += 1
            
            self.progress_bar.setValue(25)
            
            # Apply display settings
            display_config = {}
            if self.display_manager.set_display_config(display_config):
                success_count += 1
            
            self.progress_bar.setValue(50)
            
            # Apply input settings  
            input_config = {}
            if self.input_manager.set_input_config(input_config):
                success_count += 1
            
            self.progress_bar.setValue(75)
            
            # Apply workspace settings
            workspace_config = {}
            if self.workspace_manager.set_workspace_config(workspace_config):
                success_count += 1
            
            self.progress_bar.setValue(100)
            
            # Show result
            if success_count == total_operations:
                self.status_label.setText("✅ Configuration applied successfully!")
                self.config_applied.emit("success")
            else:
                self.status_label.setText(f"⚠️ Partial success: {success_count}/{total_operations} operations")
                self.config_applied.emit("partial")
            
            self.progress_bar.setVisible(False)
            
            # Refresh preview after applying
            QTimer.singleShot(1000, self.update_preview)
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"❌ Apply failed: {str(e)}")
            self.config_applied.emit("error")
            self.logger.error(f"Apply to Hyprland error: {e}")
    
    def start_auto_refresh(self):
        """Start auto-refresh timer."""
        if self.auto_refresh:
            self.update_timer.start(self.refresh_interval)
            self.update_preview()  # Initial update
    
    def stop_auto_refresh(self):
        """Stop auto-refresh timer."""
        self.update_timer.stop()
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh mode."""
        self.auto_refresh = not self.auto_refresh
        
        if self.auto_refresh:
            self.auto_refresh_button.setText("Auto-Refresh: ON")
            self.start_auto_refresh()
        else:
            self.auto_refresh_button.setText("Auto-Refresh: OFF")
            self.stop_auto_refresh()
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.stop_auto_refresh()
        super().closeEvent(event) 
