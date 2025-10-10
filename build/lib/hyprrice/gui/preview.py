"""
Enhanced preview window with real-time updates for HyprRice
"""

import os
import logging
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QGroupBox, QGridLayout, QPushButton, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, QTime, pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QFont, QPixmap, QPainter


class ColorPreview(QFrame):
    """A widget that shows a color preview."""
    
    def __init__(self, color: str = "#000000", label: str = "Color"):
        super().__init__()
        self.color = color
        self.label = label
        self.setFixedSize(80, 60)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setAutoFillBackground(True)
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
        
        # Ensure proper background painting and mouse events
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        
        # Import UI tracing utilities
        from ..utils import trace_ui_event
        self.trace_ui_event = trace_ui_event
        
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
        
        # Auto-refresh settings with throttling and debouncing
        self.auto_refresh = True
        self.refresh_interval = 5000  # 5 seconds (reduced frequency)
        self._last_update_time = 0
        self._update_throttle_ms = 250  # Minimum 250ms between updates (debounced)
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._perform_update)
        self._pending_update = False
        
        self.setup_ui()
        self.start_auto_refresh()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Live Configuration Preview")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
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
        
        # Ensure scroll area content is properly painted
        scroll_widget.setAutoFillBackground(True)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        
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
        """Create Hyprland settings preview with live configuration."""
        hyprland_group = QGroupBox("Hyprland Configuration Preview")
        hyprland_layout = QVBoxLayout(hyprland_group)
        
        # Current vs Preview comparison
        comparison_layout = QHBoxLayout()
        
        # Current configuration
        current_group = QGroupBox("Current (Live)")
        current_layout = QGridLayout(current_group)
        
        # Preview configuration
        preview_group = QGroupBox("Preview (Pending)")
        preview_layout = QGridLayout(preview_group)
        
        # Window settings
        current_layout.addWidget(QLabel("Border Color:"), 0, 0)
        self.current_border_color = ColorPreview(label="Current Border")
        current_layout.addWidget(self.current_border_color, 0, 1)
        
        preview_layout.addWidget(QLabel("Border Color:"), 0, 0)
        self.preview_border_color = ColorPreview(label="Preview Border")
        preview_layout.addWidget(self.preview_border_color, 0, 1)
        
        # Gaps
        self.current_gaps_label = QLabel("Gaps: Loading...")
        current_layout.addWidget(self.current_gaps_label, 1, 0, 1, 2)
        
        self.preview_gaps_label = QLabel("Gaps: Loading...")
        preview_layout.addWidget(self.preview_gaps_label, 1, 0, 1, 2)
        
        # Border size
        self.current_border_size_label = QLabel("Border Size: Loading...")
        current_layout.addWidget(self.current_border_size_label, 2, 0, 1, 2)
        
        self.preview_border_size_label = QLabel("Border Size: Loading...")
        preview_layout.addWidget(self.preview_border_size_label, 2, 0, 1, 2)
        
        # Effects
        self.current_blur_label = QLabel("Blur: Loading...")
        current_layout.addWidget(self.current_blur_label, 3, 0, 1, 2)
        
        self.preview_blur_label = QLabel("Blur: Loading...")
        preview_layout.addWidget(self.preview_blur_label, 3, 0, 1, 2)
        
        # Animations
        self.current_animations_label = QLabel("Animations: Loading...")
        current_layout.addWidget(self.current_animations_label, 4, 0, 1, 2)
        
        self.preview_animations_label = QLabel("Animations: Loading...")
        preview_layout.addWidget(self.preview_animations_label, 4, 0, 1, 2)
        
        # Rounding
        self.current_rounding_label = QLabel("Rounding: Loading...")
        current_layout.addWidget(self.current_rounding_label, 5, 0, 1, 2)
        
        self.preview_rounding_label = QLabel("Rounding: Loading...")
        preview_layout.addWidget(self.preview_rounding_label, 5, 0, 1, 2)
        
        # Shadow
        self.current_shadow_label = QLabel("Shadow: Loading...")
        current_layout.addWidget(self.current_shadow_label, 6, 0, 1, 2)
        
        self.preview_shadow_label = QLabel("Shadow: Loading...")
        preview_layout.addWidget(self.preview_shadow_label, 6, 0, 1, 2)
        
        # Window Rules
        self.current_rules_label = QLabel("Window Rules: Loading...")
        current_layout.addWidget(self.current_rules_label, 7, 0, 1, 2)
        
        self.preview_rules_label = QLabel("Window Rules: Loading...")
        preview_layout.addWidget(self.preview_rules_label, 7, 0, 1, 2)
        
        comparison_layout.addWidget(current_group)
        comparison_layout.addWidget(preview_group)
        hyprland_layout.addLayout(comparison_layout)
        
        # Configuration diff
        diff_group = QGroupBox("Configuration Changes")
        diff_layout = QVBoxLayout(diff_group)
        
        self.config_diff_text = QTextEdit()
        self.config_diff_text.setMaximumHeight(150)
        self.config_diff_text.setReadOnly(True)
        self.config_diff_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
            }
        """)
        diff_layout.addWidget(self.config_diff_text)
        
        hyprland_layout.addWidget(diff_group)
        
        self.content_layout.addWidget(hyprland_group)
    
    def create_waybar_preview(self):
        """Create Waybar preview section."""
        waybar_group = QGroupBox("Waybar Configuration")
        waybar_layout = QVBoxLayout(waybar_group)
        
        # Waybar mockup
        waybar_mockup = QFrame()
        waybar_mockup.setFixedHeight(35)
        waybar_mockup.setFrameStyle(QFrame.Shape.Box)
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
        """Update the preview with current configuration (debounced)."""
        # Cancel any pending update and start debounce timer
        self._debounce_timer.stop()
        self._debounce_timer.start(250)  # 250ms debounce
        self._pending_update = True
    
    def _perform_update(self):
        """Perform the actual preview update (called after debounce)."""
        if not self._pending_update:
            return
            
        self._pending_update = False
        import time
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Throttle updates to prevent excessive CPU usage
        if current_time - self._last_update_time < self._update_throttle_ms:
            return
            
        self._last_update_time = current_time
        
        try:
            self.trace_ui_event("preview_update", "PreviewWindow", "starting update")
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
            self.status_label.setText(f"Preview updated at {QTime.currentTime().toString()}")
            self.trace_ui_event("preview_update", "PreviewWindow", "update completed")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"Update failed: {str(e)}")
            self.logger.error(f"Preview update error: {e}")
            self.trace_ui_event("preview_update", "PreviewWindow", f"error: {e}")
    
    def update_theme_info(self):
        """Update theme information with DPR-aware pixmap reloading."""
        try:
            theme_name = getattr(self.config, 'current_theme', 'Default')
            self.theme_info_label.setText(f"Theme: {theme_name}")
            
            # Update color previews with DPR-aware reloading
            if hasattr(self.config, 'colors'):
                colors = self.config.colors
                for color_name, preview in self.color_previews.items():
                    color_value = getattr(colors, color_name, '#000000')
                    preview.set_color(color_value)
            
            # Reload any pixmaps with proper DPR
            from ..utils import get_device_pixel_ratio
            dpr = get_device_pixel_ratio()
            if dpr > 1.0:
                # Force repaint for high-DPI displays
                self.repaint()
            
        except Exception as e:
            self.theme_info_label.setText(f"Theme: Error loading ({str(e)})")
    
    def update_hyprland_info(self):
        """Update Hyprland configuration info with live vs preview comparison."""
        try:
            from ..utils import hyprctl
            
            # Get current live Hyprland config
            current_config = self.get_current_hyprland_config()
            
            # Get preview config from HyprRice
            preview_config = self.get_preview_hyprland_config()
            
            # Update current (live) configuration
            self.current_border_color.set_color(current_config.get('border_color', '#5e81ac'))
            self.current_gaps_label.setText(f"Gaps: {current_config.get('gaps_in', 5)}/{current_config.get('gaps_out', 10)}")
            self.current_border_size_label.setText(f"Border: {current_config.get('border_size', 2)}px")
            self.current_blur_label.setText(f"Blur: {'On' if current_config.get('blur_enabled', True) else 'Off'} ({current_config.get('blur_size', 8)})")
            self.current_animations_label.setText(f"Animations: {'On' if current_config.get('animations_enabled', True) else 'Off'}")
            self.current_rounding_label.setText(f"Rounding: {current_config.get('rounding', 8)}px")
            self.current_shadow_label.setText(f"Shadow: {'On' if current_config.get('shadow_enabled', True) else 'Off'} ({current_config.get('shadow_range', 4)})")
            self.current_rules_label.setText(f"Floating Border: {'Off' if current_config.get('no_border_floating', False) else 'On'}")
            
            # Update preview configuration
            self.preview_border_color.set_color(preview_config.get('border_color', '#5e81ac'))
            self.preview_gaps_label.setText(f"Gaps: {preview_config.get('gaps_in', 5)}/{preview_config.get('gaps_out', 10)}")
            self.preview_border_size_label.setText(f"Border: {preview_config.get('border_size', 2)}px")
            self.preview_blur_label.setText(f"Blur: {'On' if preview_config.get('blur_enabled', True) else 'Off'} ({preview_config.get('blur_size', 8)})")
            self.preview_animations_label.setText(f"Animations: {'On' if preview_config.get('animations_enabled', True) else 'Off'}")
            self.preview_rounding_label.setText(f"Rounding: {preview_config.get('rounding', 8)}px")
            self.preview_shadow_label.setText(f"Shadow: {'On' if preview_config.get('shadow_enabled', True) else 'Off'} ({preview_config.get('shadow_range', 4)})")
            self.preview_rules_label.setText(f"Floating Border: {'Off' if preview_config.get('no_border_floating', False) else 'On'}")
            
            # Generate configuration diff
            self.update_config_diff(current_config, preview_config)
            
        except Exception as e:
            self.current_gaps_label.setText(f"Hyprland: Error ({str(e)})")
            self.preview_gaps_label.setText(f"Preview: Error ({str(e)})")
    
    def get_current_hyprland_config(self):
        """Get current live Hyprland configuration."""
        try:
            from ..utils import hyprctl
            
            # Get current Hyprland settings
            returncode, stdout, stderr = hyprctl("getoption general:gaps_in", json=True)
            gaps_in = 5
            if returncode == 0 and stdout:
                try:
                    import json
                    data = json.loads(stdout)
                    gaps_in = data.get('int', 5)
                except:
                    pass
            
            returncode, stdout, stderr = hyprctl("getoption general:gaps_out", json=True)
            gaps_out = 10
            if returncode == 0 and stdout:
                try:
                    import json
                    data = json.loads(stdout)
                    gaps_out = data.get('int', 10)
                except:
                    pass
            
            returncode, stdout, stderr = hyprctl("getoption general:col.active_border", json=True)
            border_color = "#5e81ac"
            if returncode == 0 and stdout:
                try:
                    import json
                    data = json.loads(stdout)
                    border_color = data.get('str', "#5e81ac")
                except:
                    pass
            
            returncode, stdout, stderr = hyprctl("getoption general:border_size", json=True)
            border_size = 2
            if returncode == 0 and stdout:
                try:
                    import json
                    data = json.loads(stdout)
                    border_size = data.get('int', 2)
                except:
                    pass
            
            returncode, stdout, stderr = hyprctl("getoption decoration:blur:enabled", json=True)
            blur_enabled = True
            if returncode == 0 and stdout:
                try:
                    import json
                    data = json.loads(stdout)
                    blur_enabled = data.get('int', 1) == 1
                except:
                    pass
            
            returncode, stdout, stderr = hyprctl("getoption decoration:blur:size", json=True)
            blur_size = 8
            if returncode == 0 and stdout:
                try:
                    import json
                    data = json.loads(stdout)
                    blur_size = data.get('int', 8)
                except:
                    pass
            
            # Get additional Hyprland options
            returncode, stdout, stderr = hyprctl("getoption decoration:rounding", json=True)
            rounding = 10
            if returncode == 0 and stdout:
                try:
                    import json
                    data = json.loads(stdout)
                    rounding = data.get('int', 10)
                except:
                    pass
            
            returncode, stdout, stderr = hyprctl("getoption decoration:drop_shadow", json=True)
            shadow_enabled = True
            if returncode == 0 and stdout:
                try:
                    import json
                    data = json.loads(stdout)
                    shadow_enabled = data.get('int', 1) == 1
                except:
                    pass
            
            returncode, stdout, stderr = hyprctl("getoption decoration:shadow_range", json=True)
            shadow_range = 4
            if returncode == 0 and stdout:
                try:
                    import json
                    data = json.loads(stdout)
                    shadow_range = data.get('int', 4)
                except:
                    pass
            
            returncode, stdout, stderr = hyprctl("getoption animations:enabled", json=True)
            animations_enabled = True
            if returncode == 0 and stdout:
                try:
                    import json
                    data = json.loads(stdout)
                    animations_enabled = data.get('int', 1) == 1
                except:
                    pass
            
            # Get window rules (textual preview)
            returncode, stdout, stderr = hyprctl("getoption general:no_border_on_floating", json=True)
            no_border_floating = False
            if returncode == 0 and stdout:
                try:
                    import json
                    data = json.loads(stdout)
                    no_border_floating = data.get('int', 0) == 1
                except:
                    pass
            
            return {
                'gaps_in': gaps_in,
                'gaps_out': gaps_out,
                'border_color': border_color,
                'border_size': border_size,
                'blur_enabled': blur_enabled,
                'blur_size': blur_size,
                'rounding': rounding,
                'shadow_enabled': shadow_enabled,
                'shadow_range': shadow_range,
                'animations_enabled': animations_enabled,
                'no_border_floating': no_border_floating
            }
            
        except Exception as e:
            self.logger.error(f"Error getting current Hyprland config: {e}")
            return {}
    
    def get_preview_hyprland_config(self):
        """Get preview configuration from HyprRice settings."""
        try:
            if hasattr(self.config, 'hyprland'):
                hyprland = self.config.hyprland
                return {
                    'gaps_in': getattr(hyprland, 'gaps_in', 5),
                    'gaps_out': getattr(hyprland, 'gaps_out', 10),
                    'border_color': getattr(hyprland, 'border_color', '#5e81ac'),
                    'border_size': getattr(hyprland, 'border_size', 2),
                    'blur_enabled': getattr(hyprland, 'blur_enabled', True),
                    'blur_size': getattr(hyprland, 'blur_size', 8),
                    'rounding': getattr(hyprland, 'rounding', 8),
                    'animations_enabled': getattr(hyprland, 'animations_enabled', True)
                }
            return {}
        except Exception as e:
            self.logger.error(f"Error getting preview config: {e}")
            return {}
    
    def update_config_diff(self, current_config, preview_config):
        """Update the configuration diff display."""
        try:
            diff_lines = []
            diff_lines.append("Configuration Changes:")
            diff_lines.append("=" * 50)
            
            changes_found = False
            
            for key, current_value in current_config.items():
                preview_value = preview_config.get(key, current_value)
                if current_value != preview_value:
                    changes_found = True
                    key_display = key.replace('_', ' ').title()
                    diff_lines.append(f"  {key_display}:")
                    diff_lines.append(f"    Current:  {current_value}")
                    diff_lines.append(f"    Preview:  {preview_value}")
                    diff_lines.append("")
            
            if not changes_found:
                diff_lines.append("  No changes detected")
                diff_lines.append("  Current configuration matches preview")
            
            self.config_diff_text.setPlainText("\n".join(diff_lines))
            
        except Exception as e:
            self.logger.error(f"Error updating config diff: {e}")
            self.config_diff_text.setPlainText(f"Error generating diff: {str(e)}")
    
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
            result = subprocess.run(
                ['pgrep', 'Hyprland'], 
                capture_output=True, 
                text=True, 
                timeout=2
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return False
    
    def apply_to_hyprland(self):
        """Apply current configuration to Hyprland using hyprctl."""
        try:
            from ..utils import hyprctl
            
            self.status_label.setText("Applying configuration to Hyprland...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 100)
            
            success_count = 0
            total_operations = 0
            applied_commands = []
            
            if hasattr(self.config, 'hyprland'):
                hyprland = self.config.hyprland
                
                # Apply general settings
                commands = [
                    ("general:gaps_in", getattr(hyprland, 'gaps_in', 5)),
                    ("general:gaps_out", getattr(hyprland, 'gaps_out', 10)),
                    ("general:border_size", getattr(hyprland, 'border_size', 2)),
                    ("general:col.active_border", getattr(hyprland, 'border_color', '#5e81ac')),
                    ("decoration:rounding", getattr(hyprland, 'rounding', 8)),
                    ("decoration:blur:enabled", 1 if getattr(hyprland, 'blur_enabled', True) else 0),
                    ("decoration:blur:size", getattr(hyprland, 'blur_size', 8)),
                    ("animations:enabled", 1 if getattr(hyprland, 'animations_enabled', True) else 0),
                ]
                
                total_operations = len(commands)
                
                for i, (option, value) in enumerate(commands):
                    try:
                        # Apply the setting
                        returncode, stdout, stderr = hyprctl(f"keyword {option} {value}")
                        
                        if returncode == 0:
                            success_count += 1
                            applied_commands.append(f"✓ {option} = {value}")
                        else:
                            applied_commands.append(f"✗ {option} = {value} (failed: {stderr})")
                        
                        # Update progress
                        progress = int((i + 1) / total_operations * 100)
                        self.progress_bar.setValue(progress)
                        
                    except Exception as e:
                        applied_commands.append(f"✗ {option} = {value} (error: {str(e)})")
            
            self.progress_bar.setValue(100)
            
            # Show result
            if success_count == total_operations:
                self.status_label.setText("✅ Configuration applied successfully!")
                self.config_applied.emit("success")
                
                # Update the preview to reflect applied changes
                self.update_preview()
                
            elif success_count > 0:
                self.status_label.setText(f"⚠️ {success_count}/{total_operations} settings applied")
                self.config_applied.emit("partial")
            else:
                self.status_label.setText("❌ Failed to apply configuration")
                self.config_applied.emit("failed")
            
            # Show detailed results
            result_text = "Applied Commands:\n" + "\n".join(applied_commands)
            self.config_diff_text.setPlainText(result_text)
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"❌ Error applying configuration: {str(e)}")
            self.config_applied.emit("error")
            self.logger.error(f"Error applying to Hyprland: {e}")
            
            # Refresh preview after applying
            QTimer.singleShot(1000, self.update_preview)
    
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
