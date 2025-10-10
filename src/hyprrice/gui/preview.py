"""
Enhanced preview window with real-time updates for HyprRice
"""

import os
import logging
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QGroupBox, QGridLayout, QPushButton, QProgressBar, QTextEdit,
    QSlider, QColorDialog, QCheckBox, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer, QTime, pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QFont, QPixmap, QPainter, QBrush, QPen


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


class InteractivePreviewWidget(QWidget):
    """Interactive visual preview widget that shows a mockup of Hyprland windows."""
    
    # Signals for configuration changes
    configuration_changed = pyqtSignal(dict)
    
    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.gap = 10
        self.border_size = 4
        self.border_color = QColor("#ff00ff")  # default pink neon
        self.rounding = 12
        self.blur_enabled = True
        self.blur_size = 8
        self.blur_passes = 2
        self.shadow_enabled = True
        self.shadow_color = QColor("#000000")
        self.shadow_opacity = 0.3
        self.shadow_size = 6
        self.shadow_offset_x = 0
        self.shadow_offset_y = 4
        self.animation_enabled = True
        self.animation_duration = 300
        self.current_theme_type = "dark"  # Will be updated by theme manager
        self.setMinimumSize(400, 300)
        
        # Debounce timer for configuration changes
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._emit_configuration_changed)
        
        # Connect to theme manager if available
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme changes and update preview colors accordingly."""
        self.current_theme_type = theme
        
        # Update colors based on theme
        if self.theme_manager:
            theme_colors = self.theme_manager.get_current_colors()
            
            # Update border color to match theme accent
            if "accent_primary" in theme_colors:
                self.border_color = QColor(theme_colors["accent_primary"])
            
            # Update background colors for proper theme integration
            self.theme_bg_colors = [
                theme_colors.get("bg_primary", "#2e2e3e"),
                theme_colors.get("bg_secondary", "#3e3e4e"),
                theme_colors.get("bg_tertiary", "#2a2a3a"),
                theme_colors.get("bg_elevated", "#3a3a4a")
            ]
            
            # Update shadow color for theme consistency
            if self.theme_manager.is_dark_theme(theme):
                self.shadow_color = QColor(theme_colors.get("shadow_dark", "#000000"))
            else:
                self.shadow_color = QColor(theme_colors.get("shadow_light", "#888888"))
        
        self.update()  # Redraw with new theme
        
    def set_gap(self, gap: int):
        """Set the gap size and update display."""
        self.gap = gap
        self.update()
        
    def set_border_size(self, border_size: int):
        """Set the border size and update display."""
        self.border_size = border_size
        self.update()
        
    def set_border_color(self, color: QColor):
        """Set the border color and update display."""
        self.border_color = color
        self.update()
        
    def set_rounding(self, rounding: int):
        """Set the rounding radius and update display."""
        self.rounding = rounding
        self._debounce_update()
        
    def set_blur_enabled(self, enabled: bool):
        """Enable or disable blur effects."""
        self.blur_enabled = enabled
        self._debounce_update()
        
    def set_blur_size(self, size: int):
        """Set blur effect size."""
        self.blur_size = max(0, size)
        self._debounce_update()
        
    def set_blur_passes(self, passes: int):
        """Set blur effect passes."""
        self.blur_passes = max(1, passes)
        self._debounce_update()
        
    def set_shadow_enabled(self, enabled: bool):
        """Enable or disable shadow effects."""
        self.shadow_enabled = enabled
        self._debounce_update()
        
    def set_shadow_color(self, color: QColor):
        """Set shadow color."""
        self.shadow_color = color
        self._debounce_update()
        
    def set_shadow_opacity(self, opacity: float):
        """Set shadow opacity (0.0-1.0)."""
        self.shadow_opacity = max(0.0, min(1.0, opacity))
        self._debounce_update()
        
    def set_shadow_size(self, size: int):
        """Set shadow size."""
        self.shadow_size = max(0, size)
        self._debounce_update()
        
    def set_shadow_offset(self, x: int, y: int):
        """Set shadow offset."""
        self.shadow_offset_x = x
        self.shadow_offset_y = y
        self._debounce_update()
        
    def set_animation_enabled(self, enabled: bool):
        """Enable or disable animations."""
        self.animation_enabled = enabled
        self._debounce_update()
        
    def set_animation_duration(self, duration: int):
        """Set animation duration in milliseconds."""
        self.animation_duration = max(0, duration)
        self._debounce_update()
        
    def _debounce_update(self):
        """Debounced update to prevent excessive redraws."""
        self.debounce_timer.stop()
        self.debounce_timer.start(100)  # 100ms debounce
        
    def _emit_configuration_changed(self):
        """Emit configuration changed signal with current settings."""
        config = self.get_current_config()
        self.configuration_changed.emit(config)
        
    def get_current_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return {
            "general": {
                "gaps_in": self.gap,
                "gaps_out": self.gap * 2,
                "border_size": self.border_size,
                "col.active_border": self.border_color.name(),
                "col.inactive_border": self.border_color.name() + "66",  # Add transparency
            },
            "decoration": {
                "rounding": self.rounding,
                "blur": {
                    "enabled": self.blur_enabled,
                    "size": self.blur_size,
                    "passes": self.blur_passes,
                },
                "drop_shadow": self.shadow_enabled,
                "shadow_color": self.shadow_color.name(),
                "shadow_range": self.shadow_size,
                "shadow_offset": f"{self.shadow_offset_x} {self.shadow_offset_y}",
            },
            "animations": {
                "enabled": self.animation_enabled,
                "animation": ["windows", 1, int(self.animation_duration / 100), "myBezier"]
            }
        }
        
    def paintEvent(self, event):
        """Paint the window mockup."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background with theme-appropriate color
        if hasattr(self, 'theme_bg_colors') and self.theme_bg_colors:
            bg_color = QColor(self.theme_bg_colors[0])
        elif self.current_theme_type == "light":
            bg_color = QColor("#f5f5f5")  # Light theme background
        else:
            bg_color = QColor("#1e1e2e")  # Dark theme background
        
        painter.fillRect(self.rect(), bg_color)
        
        # Calculate window dimensions
        margin = 20
        available_width = self.width() - 2 * margin
        available_height = self.height() - 2 * margin
        
        # Draw multiple mock windows to show gaps
        window_width = (available_width - self.gap) // 2
        window_height = (available_height - self.gap) // 2
        
        windows = [
            (margin + self.gap, margin + self.gap, window_width, window_height),
            (margin + window_width + 2 * self.gap, margin + self.gap, window_width, window_height),
            (margin + self.gap, margin + window_height + 2 * self.gap, window_width, window_height),
            (margin + window_width + 2 * self.gap, margin + window_height + 2 * self.gap, window_width, window_height)
        ]
        
        # Draw each window
        for i, (x, y, w, h) in enumerate(windows):
            # Draw shadow if enabled
            if self.shadow_enabled:
                shadow_color = QColor(self.shadow_color)
                shadow_color.setAlphaF(self.shadow_opacity)
                painter.setPen(QPen(QColor(Qt.GlobalColor.transparent)))
                painter.setBrush(QBrush(shadow_color))
                shadow_rect = (
                    x + self.shadow_offset_x,
                    y + self.shadow_offset_y,
                    w + self.shadow_size,
                    h + self.shadow_size
                )
                painter.drawRoundedRect(*shadow_rect, self.rounding + self.shadow_size, self.rounding + self.shadow_size)
            
            # Set up pen for border
            pen = QPen(self.border_color, self.border_size)
            painter.setPen(pen)
            
            # Window background using theme colors
            if hasattr(self, 'theme_bg_colors') and self.theme_bg_colors:
                bg_colors = self.theme_bg_colors
            else:
                bg_colors = ["#2e2e3e", "#3e3e4e", "#2a2a3a", "#3a3a4a"]
            
            bg_color = QColor(bg_colors[i % len(bg_colors)])
            
            # Simulate blur effect by making background more transparent
            if self.blur_enabled:
                bg_color.setAlphaF(0.8)
            
            painter.setBrush(QBrush(bg_color))
            
            # Draw rounded rectangle
            painter.drawRoundedRect(x, y, w, h, self.rounding, self.rounding)
            
            # Simulate animation hint if enabled
            if self.animation_enabled and i == 0:
                # Draw a subtle animation indicator on the first window
                animation_color = QColor(self.border_color)
                animation_color.setAlphaF(0.4)
                painter.setPen(QPen(animation_color, 1))
                painter.setBrush(QBrush(QColor(Qt.GlobalColor.transparent)))
                # Draw a slightly expanded outline
                pulse_size = 2
                expanded_rect = (x - pulse_size, y - pulse_size, w + 2 * pulse_size, h + 2 * pulse_size)
                painter.drawRoundedRect(*expanded_rect, self.rounding + pulse_size, self.rounding + pulse_size)
            
            # Draw window title bar
            title_height = 25
            painter.setBrush(QBrush(QColor("#4e4e5e")))
            painter.setPen(QPen(self.border_color, 1))
            painter.drawRoundedRect(x + self.border_size, y + self.border_size, 
                                  w - 2 * self.border_size, title_height, 
                                  self.rounding // 2, self.rounding // 2)
            
            # Draw window controls (close, minimize, maximize)
            control_size = 12
            control_y = y + self.border_size + (title_height - control_size) // 2
            control_spacing = 18
            
            # Close button (red)
            painter.setBrush(QBrush(QColor("#ff5555")))
            painter.setPen(QPen(QColor("#ff5555"), 1))
            painter.drawEllipse(x + w - self.border_size - control_spacing, control_y, control_size, control_size)
            
            # Maximize button (green)
            painter.setBrush(QBrush(QColor("#50fa7b")))
            painter.setPen(QPen(QColor("#50fa7b"), 1))
            painter.drawEllipse(x + w - self.border_size - 2 * control_spacing, control_y, control_size, control_size)
            
            # Minimize button (yellow)
            painter.setBrush(QBrush(QColor("#f1fa8c")))
            painter.setPen(QPen(QColor("#f1fa8c"), 1))
            painter.drawEllipse(x + w - self.border_size - 3 * control_spacing, control_y, control_size, control_size)


class InteractiveConfiguratorWidget(QWidget):
    """Widget containing interactive controls for Hyprland configuration."""
    
    # Signals for configuration changes
    gap_changed = pyqtSignal(int)
    border_size_changed = pyqtSignal(int)
    border_color_changed = pyqtSignal(QColor)
    rounding_changed = pyqtSignal(int)
    blur_enabled_changed = pyqtSignal(bool)
    blur_size_changed = pyqtSignal(int)
    blur_passes_changed = pyqtSignal(int)
    shadow_enabled_changed = pyqtSignal(bool)
    shadow_color_changed = pyqtSignal(QColor)
    shadow_opacity_changed = pyqtSignal(float)
    shadow_size_changed = pyqtSignal(int)
    shadow_offset_changed = pyqtSignal(int, int)
    animation_enabled_changed = pyqtSignal(bool)
    animation_duration_changed = pyqtSignal(int)
    apply_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the control interface."""
        layout = QVBoxLayout(self)
        
        # Gap control
        gap_group = QGroupBox("Gap Size")
        gap_layout = QVBoxLayout(gap_group)
        
        self.gap_slider = QSlider(Qt.Orientation.Horizontal)
        self.gap_slider.setRange(0, 50)
        self.gap_slider.setValue(10)
        self.gap_slider.valueChanged.connect(self._on_gap_changed)
        
        self.gap_label = QLabel("10px")
        self.gap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        gap_layout.addWidget(self.gap_label)
        gap_layout.addWidget(self.gap_slider)
        layout.addWidget(gap_group)
        
        # Border size control
        border_group = QGroupBox("Border Size")
        border_layout = QVBoxLayout(border_group)
        
        self.border_slider = QSlider(Qt.Orientation.Horizontal)
        self.border_slider.setRange(1, 20)
        self.border_slider.setValue(4)
        self.border_slider.valueChanged.connect(self._on_border_size_changed)
        
        self.border_label = QLabel("4px")
        self.border_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        border_layout.addWidget(self.border_label)
        border_layout.addWidget(self.border_slider)
        layout.addWidget(border_group)
        
        # Rounding control
        rounding_group = QGroupBox("Corner Rounding")
        rounding_layout = QVBoxLayout(rounding_group)
        
        self.rounding_slider = QSlider(Qt.Orientation.Horizontal)
        self.rounding_slider.setRange(0, 20)
        self.rounding_slider.setValue(12)
        self.rounding_slider.valueChanged.connect(self._on_rounding_changed)
        
        self.rounding_label = QLabel("12px")
        self.rounding_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        rounding_layout.addWidget(self.rounding_label)
        rounding_layout.addWidget(self.rounding_slider)
        layout.addWidget(rounding_group)
        
        # Border color control
        color_group = QGroupBox("Border Color")
        color_layout = QVBoxLayout(color_group)
        
        self.color_button = QPushButton("Pick Border Color")
        self.color_button.clicked.connect(self._pick_color)
        self.color_button.setStyleSheet("QPushButton { background-color: #ff00ff; color: white; font-weight: bold; }")
        
        color_layout.addWidget(self.color_button)
        layout.addWidget(color_group)
        
        # Blur effects control
        blur_group = QGroupBox("Blur Effects")
        blur_layout = QVBoxLayout(blur_group)
        
        self.blur_enabled_checkbox = QCheckBox("Enable Blur")
        self.blur_enabled_checkbox.setChecked(True)
        self.blur_enabled_checkbox.toggled.connect(self.blur_enabled_changed.emit)
        blur_layout.addWidget(self.blur_enabled_checkbox)
        
        self.blur_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.blur_size_slider.setRange(1, 20)
        self.blur_size_slider.setValue(8)
        self.blur_size_slider.valueChanged.connect(self._on_blur_size_changed)
        
        blur_size_layout = QHBoxLayout()
        blur_size_layout.addWidget(QLabel("Blur Size:"))
        self.blur_size_label = QLabel("8px")
        blur_size_layout.addWidget(self.blur_size_label)
        blur_layout.addLayout(blur_size_layout)
        blur_layout.addWidget(self.blur_size_slider)
        
        self.blur_passes_slider = QSlider(Qt.Orientation.Horizontal)
        self.blur_passes_slider.setRange(1, 5)
        self.blur_passes_slider.setValue(2)
        self.blur_passes_slider.valueChanged.connect(self._on_blur_passes_changed)
        
        blur_passes_layout = QHBoxLayout()
        blur_passes_layout.addWidget(QLabel("Blur Passes:"))
        self.blur_passes_label = QLabel("2")
        blur_passes_layout.addWidget(self.blur_passes_label)
        blur_layout.addLayout(blur_passes_layout)
        blur_layout.addWidget(self.blur_passes_slider)
        
        layout.addWidget(blur_group)
        
        # Shadow effects control
        shadow_group = QGroupBox("Shadow Effects")
        shadow_layout = QVBoxLayout(shadow_group)
        
        self.shadow_enabled_checkbox = QCheckBox("Enable Shadows")
        self.shadow_enabled_checkbox.setChecked(True)
        self.shadow_enabled_checkbox.toggled.connect(self.shadow_enabled_changed.emit)
        shadow_layout.addWidget(self.shadow_enabled_checkbox)
        
        self.shadow_color_button = QPushButton("Shadow Color")
        self.shadow_color_button.clicked.connect(self._pick_shadow_color)
        self.shadow_color_button.setStyleSheet("QPushButton { background-color: #000000; color: white; }")
        shadow_layout.addWidget(self.shadow_color_button)
        
        self.shadow_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.shadow_opacity_slider.setRange(10, 100)
        self.shadow_opacity_slider.setValue(30)
        self.shadow_opacity_slider.valueChanged.connect(self._on_shadow_opacity_changed)
        
        shadow_opacity_layout = QHBoxLayout()
        shadow_opacity_layout.addWidget(QLabel("Shadow Opacity:"))
        self.shadow_opacity_label = QLabel("30%")
        shadow_opacity_layout.addWidget(self.shadow_opacity_label)
        shadow_layout.addLayout(shadow_opacity_layout)
        shadow_layout.addWidget(self.shadow_opacity_slider)
        
        self.shadow_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.shadow_size_slider.setRange(1, 20)
        self.shadow_size_slider.setValue(6)
        self.shadow_size_slider.valueChanged.connect(self._on_shadow_size_changed)
        
        shadow_size_layout = QHBoxLayout()
        shadow_size_layout.addWidget(QLabel("Shadow Size:"))
        self.shadow_size_label = QLabel("6px")
        shadow_size_layout.addWidget(self.shadow_size_label)
        shadow_layout.addLayout(shadow_size_layout)
        shadow_layout.addWidget(self.shadow_size_slider)
        
        layout.addWidget(shadow_group)
        
        # Animation control
        animation_group = QGroupBox("Animation")
        animation_layout = QVBoxLayout(animation_group)
        
        self.animation_enabled_checkbox = QCheckBox("Enable Animations")
        self.animation_enabled_checkbox.setChecked(True)
        self.animation_enabled_checkbox.toggled.connect(self.animation_enabled_changed.emit)
        animation_layout.addWidget(self.animation_enabled_checkbox)
        
        self.animation_duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.animation_duration_slider.setRange(100, 1000)
        self.animation_duration_slider.setValue(300)
        self.animation_duration_slider.valueChanged.connect(self._on_animation_duration_changed)
        
        animation_duration_layout = QHBoxLayout()
        animation_duration_layout.addWidget(QLabel("Duration:"))
        self.animation_duration_label = QLabel("300ms")
        animation_duration_layout.addWidget(self.animation_duration_label)
        animation_layout.addLayout(animation_duration_layout)
        animation_layout.addWidget(self.animation_duration_slider)
        
        layout.addWidget(animation_group)
        
        # Presets control
        presets_group = QGroupBox("Presets")
        presets_layout = QVBoxLayout(presets_group)
        
        presets_label = QLabel("Quick Apply Profiles:")
        presets_layout.addWidget(presets_label)
        
        presets_buttons_layout = QHBoxLayout()
        
        self.perf_preset_button = QPushButton("🚀 Performance")
        self.perf_preset_button.clicked.connect(lambda: self._apply_preset("performance"))
        self.perf_preset_button.setToolTip("Performance-focused configuration")
        presets_buttons_layout.addWidget(self.perf_preset_button)
        
        self.visual_preset_button = QPushButton("🎨 Visual")
        self.visual_preset_button.clicked.connect(lambda: self._apply_preset("visual"))
        self.visual_preset_button.setToolTip("Visual effects focused configuration")
        presets_buttons_layout.addWidget(self.visual_preset_button)
        
        self.battery_preset_button = QPushButton("🔋 Battery")
        self.battery_preset_button.clicked.connect(lambda: self._apply_preset("battery"))
        self.battery_preset_button.setToolTip("Battery saving configuration")
        presets_buttons_layout.addWidget(self.battery_preset_button)
        
        self.minimal_preset_button = QPushButton("⚡ Minimal")
        self.minimal_preset_button.clicked.connect(lambda: self._apply_preset("minimal"))
        self.minimal_preset_button.setToolTip("Minimal resource configuration")
        presets_buttons_layout.addWidget(self.minimal_preset_button)
        
        presets_layout.addLayout(presets_buttons_layout)
        layout.addWidget(presets_group)
        
        # Apply button
        self.apply_button = QPushButton("Apply to Hyprland")
        self.apply_button.clicked.connect(self._on_apply_requested)
        self.apply_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        layout.addWidget(self.apply_button)
        
        layout.addStretch()
        
    def _on_gap_changed(self, value):
        """Handle gap slider change."""
        self.gap_label.setText(f"{value}px")
        self.gap_changed.emit(value)
        
    def _on_border_size_changed(self, value):
        """Handle border size slider change."""
        self.border_label.setText(f"{value}px")
        self.border_size_changed.emit(value)
        
    def _on_rounding_changed(self, value):
        """Handle rounding slider change."""
        self.rounding_label.setText(f"{value}px")
        self.rounding_changed.emit(value)
        
    def _pick_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_button.setStyleSheet(f"QPushButton {{ background-color: {color.name()}; color: white; font-weight: bold; }}")
            self.border_color_changed.emit(color)
    
    def _pick_shadow_color(self):
        """Open shadow color picker dialog."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.shadow_color_button.setStyleSheet(f"QPushButton {{ background-color: {color.name()}; color: white; }}")
            self.shadow_color_changed.emit(color)
    
    def _on_shadow_opacity_changed(self, value):
        """Handle shadow opacity slider change."""
        opacity_percent = value
        opacity_decimal = value / 100.0
        self.shadow_opacity_label.setText(f"{opacity_percent}%")
        self.shadow_opacity_changed.emit(opacity_decimal)
    
    def _on_shadow_size_changed(self, value):
        """Handle shadow size slider change."""
        self.shadow_size_label.setText(f"{value}px")
        self.shadow_size_changed.emit(value)
    
    def _on_animation_duration_changed(self, value):
        """Handle animation duration slider change."""
        self.animation_duration_label.setText(f"{value}ms")
        self.animation_duration_changed.emit(value)
    
    def _on_blur_size_changed(self, value):
        """Handle blur size slider change."""
        self.blur_size_label.setText(f"{value}px")
        self.blur_size_changed.emit(value)
        
    def _on_blur_passes_changed(self, value):
        """Handle blur passes slider change."""
        self.blur_passes_label.setText(f"{value}")
        self.blur_passes_changed.emit(value)
            
    def _apply_preset(self, preset_type: str):
        """Apply a preset configuration based on Autoconfig profiles."""
        presets = {
            "performance": {
                "gaps_in": 5,
                "border_size": 2,
                "rounding": 8,
                "blur_enabled": False,
                "blur_size": 2,
                "blur_passes": 1,
                "shadow_enabled": True,
                "shadow_opacity": 0.2,
                "shadow_size": 4,
                "animation_enabled": True,
                "animation_duration": 200
            },
            "visual": {
                "gaps_in": 12,
                "border_size": 3,
                "rounding": 15,
                "blur_enabled": True,
                "blur_size": 15,
                "blur_passes": 3,
                "shadow_enabled": True,
                "shadow_opacity": 0.4,
                "shadow_size": 12,
                "animation_enabled": True,
                "animation_duration": 400
            },
            "battery": {
                "gaps_in": 3,
                "border_size": 1,
                "rounding": 5,
                "blur_enabled": False,
                "blur_size": 1,
                "blur_passes": 1,
                "shadow_enabled": False,
                "shadow_opacity": 0.1,
                "shadow_size": 2,
                "animation_enabled": False,
                "animation_duration": 100
            },
            "minimal": {
                "gaps_in": 2,
                "border_size": 1,
                "rounding": 0,
                "blur_enabled": False,
                "blur_size": 0,
                "blur_passes": 1,
                "shadow_enabled": False,
                "shadow_opacity": 0.0,
                "shadow_size": 0,
                "animation_enabled": False,
                "animation_duration": 0
            }
        }
        
        if preset_type in presets:
            preset = presets[preset_type]
            
            # Apply preset values
            self.gap_slider.setValue(preset["gaps_in"])
            self.border_slider.setValue(preset["border_size"])
            self.rounding_slider.setValue(preset["rounding"])
            
            self.blur_enabled_checkbox.setChecked(preset["blur_enabled"])
            self.blur_size_slider.setValue(preset["blur_size"])
            self.blur_passes_slider.setValue(preset["blur_passes"])
            
            self.shadow_enabled_checkbox.setChecked(preset["shadow_enabled"])
            self.shadow_opacity_slider.setValue(int(preset["shadow_opacity"] * 100))
            self.shadow_size_slider.setValue(preset["shadow_size"])
            
            self.animation_enabled_checkbox.setChecked(preset["animation_enabled"])
            self.animation_duration_slider.setValue(preset["animation_duration"])
            
            # Update labels
            self.gap_label.setText(f"{preset['gaps_in']}px")
            self.border_label.setText(f"{preset['border_size']}px")
            self.rounding_label.setText(f"{preset['rounding']}px")
            self.blur_size_label.setText(f"{preset['blur_size']}px")
            self.blur_passes_label.setText(f"{preset['blur_passes']}")
            self.shadow_opacity_label.setText(f"{int(preset['shadow_opacity'] * 100)}%")
            self.shadow_size_label.setText(f"{preset['shadow_size']}px")
            self.animation_duration_label.setText(f"{preset['animation_duration']}ms")
            
            # Emit signals to update preview
            self.gap_changed.emit(preset["gaps_in"])
            self.border_size_changed.emit(preset["border_size"])
            self.rounding_changed.emit(preset["rounding"])
            self.blur_enabled_changed.emit(preset["blur_enabled"])
            self.blur_size_changed.emit(preset["blur_size"])
            self.blur_passes_changed.emit(preset["blur_passes"])
            self.shadow_enabled_changed.emit(preset["shadow_enabled"])
            self.shadow_opacity_changed.emit(preset["shadow_opacity"])
            self.shadow_size_changed.emit(preset["shadow_size"])
            self.animation_enabled_changed.emit(preset["animation_enabled"])
            self.animation_duration_changed.emit(preset["animation_duration"])
    
    def _on_apply_requested(self):
        """Handle apply button click."""
        self.apply_requested.emit()
        
    def get_current_config(self) -> Dict[str, Any]:
        """Get current configuration values."""
        # Extract color from button style sheet
        style = self.color_button.styleSheet()
        border_color = "#ff00ff"  # default
        if "background-color:" in style:
            import re
            match = re.search(r'background-color:\s*(#[0-9a-fA-F]{6})', style)
            if match:
                border_color = match.group(1)
        
        # Extract shadow color from button style sheet
        shadow_style = self.shadow_color_button.styleSheet()
        shadow_color = "#000000"  # default
        if "background-color:" in shadow_style:
            import re
            match = re.search(r'background-color:\s*(#[0-9a-fA-F]{6})', shadow_style)
            if match:
                shadow_color = match.group(1)
        
        return {
            'general': {
                'gaps_in': self.gap_slider.value(),
                'gaps_out': self.gap_slider.value(),
                'border_size': self.border_slider.value(),
                'col.active_border': border_color,
                'col.inactive_border': border_color + "66"
            },
            'decoration': {
                'rounding': self.rounding_slider.value(),
                'blur': {
                    'enabled': self.blur_enabled_checkbox.isChecked(),
                    'size': self.blur_size_slider.value(),
                    'passes': self.blur_passes_slider.value(),
                },
                'drop_shadow': self.shadow_enabled_checkbox.isChecked(),
                'shadow_color': shadow_color,
                'shadow_range': self.shadow_size_slider.value(),
                'shadow_offset': f"0 {self.shadow_size_slider.value()}"
            },
            'animations': {
                'enabled': self.animation_enabled_checkbox.isChecked(),
                'windows_out': ["windows", 1, int(self.animation_duration_slider.value() / 100), "myBezier"]
            }
        }
        
    def set_config(self, config: Dict[str, Any]):
        """Set configuration values."""
        if 'gaps_in' in config:
            self.gap_slider.setValue(config['gaps_in'])
        if 'border_size' in config:
            self.border_slider.setValue(config['border_size'])
        if 'rounding' in config:
            self.rounding_slider.setValue(config['rounding'])
        if 'border_color' in config:
            color = QColor(config['border_color'])
            if color.isValid():
                self.color_button.setStyleSheet(f"QPushButton {{ background-color: {color.name()}; color: white; font-weight: bold; }}")


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
        """Create Hyprland settings preview with interactive and live configuration."""
        hyprland_group = QGroupBox("Hyprland Configuration Preview")
        hyprland_layout = QVBoxLayout(hyprland_group)
        
        # Add tab widget for different preview modes
        preview_tabs = QTabWidget()
        
        # Interactive Preview Tab
        interactive_tab = QWidget()
        interactive_layout = QHBoxLayout(interactive_tab)
        
        # Create interactive preview and controls
        self.interactive_preview = InteractivePreviewWidget()
        self.interactive_controls = InteractiveConfiguratorWidget()
        
        # Connect interactive controls to preview
        self.interactive_controls.gap_changed.connect(self.interactive_preview.set_gap)
        self.interactive_controls.border_size_changed.connect(self.interactive_preview.set_border_size)
        self.interactive_controls.border_color_changed.connect(self.interactive_preview.set_border_color)
        self.interactive_controls.rounding_changed.connect(self.interactive_preview.set_rounding)
        self.interactive_controls.apply_requested.connect(self.apply_interactive_config)
        
        # Load current Hyprland configuration into interactive controls
        self.load_current_config_to_interactive()
        
        # Layout interactive preview
        interactive_layout.addWidget(self.interactive_controls, 1)
        interactive_layout.addWidget(self.interactive_preview, 3)
        
        preview_tabs.addTab(interactive_tab, "Interactive Preview")
        
        # Static Comparison Tab (existing functionality)
        static_tab = QWidget()
        static_layout = QVBoxLayout(static_tab)
        
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
        static_layout.addLayout(comparison_layout)
        
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
        
        static_layout.addWidget(diff_group)
        
        preview_tabs.addTab(static_tab, "Static Comparison")
        
        # Add tabs to main layout
        hyprland_layout.addWidget(preview_tabs)
        
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
    
    def apply_interactive_config(self):
        """Apply interactive configuration to Hyprland."""
        try:
            from ..utils import hyprctl
            import subprocess
            import os
            
            self.status_label.setText("Applying interactive configuration to Hyprland...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 100)
            
            # Get current configuration from interactive controls
            config = self.interactive_controls.get_current_config()
            
            success_count = 0
            total_operations = 0
            applied_commands = []
            
            # Apply configuration using hyprctl
            commands = [
                ("general:gaps_in", config['gaps_in']),
                ("general:gaps_out", config['gaps_out']),
                ("general:border_size", config['border_size']),
                ("general:col.active_border", config['border_color']),
                ("decoration:rounding", config['rounding']),
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
            
            # Write configuration to file for persistence
            try:
                hypr_config_dir = os.path.expanduser("~/.config/hypr/conf.d")
                os.makedirs(hypr_config_dir, exist_ok=True)
                
                config_file = os.path.join(hypr_config_dir, "hyprrice_interactive.conf")
                with open(config_file, 'w') as f:
                    f.write("# HyprRice Interactive Configuration\n")
                    f.write("# Generated automatically - do not edit manually\n\n")
                    f.write("general {\n")
                    f.write(f"    gaps_in = {config['gaps_in']}\n")
                    f.write(f"    gaps_out = {config['gaps_out']}\n")
                    f.write(f"    border_size = {config['border_size']}\n")
                    f.write(f"    col.active_border = {config['border_color']}\n")
                    f.write("}\n\n")
                    f.write("decoration {\n")
                    f.write(f"    rounding = {config['rounding']}\n")
                    f.write("}\n")
                
                applied_commands.append(f"✓ Configuration saved to {config_file}")
                
            except Exception as e:
                applied_commands.append(f"✗ Failed to save config file: {str(e)}")
            
            self.progress_bar.setValue(100)
            
            # Show result
            if success_count == total_operations:
                self.status_label.setText("✅ Interactive configuration applied successfully!")
                self.config_applied.emit("success")
                
                # Update the static preview to reflect applied changes
                self.update_preview()
                
            elif success_count > 0:
                self.status_label.setText(f"⚠️ {success_count}/{total_operations} settings applied")
                self.config_applied.emit("partial")
            else:
                self.status_label.setText("❌ Failed to apply interactive configuration")
                self.config_applied.emit("failed")
            
            # Show detailed results in the diff text area
            result_text = "Interactive Configuration Applied:\n" + "\n".join(applied_commands)
            if hasattr(self, 'config_diff_text'):
                self.config_diff_text.setPlainText(result_text)
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"❌ Error applying interactive configuration: {str(e)}")
            self.config_applied.emit("error")
            self.logger.error(f"Error applying interactive config: {e}")
        
        finally:
            # Hide progress bar after a short delay
            QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))

    def load_current_config_to_interactive(self):
        """Load current Hyprland configuration into interactive controls."""
        try:
            current_config = self.get_current_hyprland_config()
            if current_config:
                # Set interactive controls to current values
                self.interactive_controls.set_config(current_config)
                
                # Update preview widget with current values
                self.interactive_preview.set_gap(current_config.get('gaps_in', 10))
                self.interactive_preview.set_border_size(current_config.get('border_size', 4))
                self.interactive_preview.set_rounding(current_config.get('rounding', 12))
                
                # Set border color
                border_color_str = current_config.get('border_color', '#ff00ff')
                if border_color_str.startswith('rgba') or border_color_str.startswith('rgb'):
                    # Convert rgba/rgb to hex (simplified)
                    border_color_str = '#5e81ac'  # fallback
                border_color = QColor(border_color_str)
                if border_color.isValid():
                    self.interactive_preview.set_border_color(border_color)
                
        except Exception as e:
            self.logger.error(f"Error loading current config to interactive: {e}")

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
