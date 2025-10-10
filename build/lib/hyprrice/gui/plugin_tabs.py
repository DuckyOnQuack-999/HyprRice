"""
Plugin-specific GUI tabs for HyprRice

Provides GUI interfaces for Hyprbars, Hyprexpo, Glow, and Blur Shaders configuration.
"""

import logging
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QCheckBox,
    QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox, QPushButton, QGroupBox,
    QSlider, QColorDialog, QFontComboBox, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from ..config import Config


class HyprbarsTab(QWidget):
    """Tab for configuring Hyprbars (titlebars + buttons)."""
    
    config_changed = pyqtSignal()
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Enable/Disable checkbox
        self.enabled_checkbox = QCheckBox("Enable Hyprbars")
        self.enabled_checkbox.setChecked(self.config.hyprland.hyprbars_enabled)
        layout.addWidget(self.enabled_checkbox)
        
        # Main configuration group
        self.config_group = QGroupBox("Hyprbars Configuration")
        config_layout = QGridLayout(self.config_group)
        
        # Height
        config_layout.addWidget(QLabel("Height:"), 0, 0)
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(20, 60)
        self.height_spinbox.setValue(self.config.hyprland.hyprbars_height)
        config_layout.addWidget(self.height_spinbox, 0, 1)
        
        # Buttons size
        config_layout.addWidget(QLabel("Buttons Size:"), 1, 0)
        self.buttons_size_spinbox = QSpinBox()
        self.buttons_size_spinbox.setRange(8, 20)
        self.buttons_size_spinbox.setValue(self.config.hyprland.hyprbars_buttons_size)
        config_layout.addWidget(self.buttons_size_spinbox, 1, 1)
        
        # Buttons gap
        config_layout.addWidget(QLabel("Buttons Gap:"), 2, 0)
        self.buttons_gap_spinbox = QSpinBox()
        self.buttons_gap_spinbox.setRange(4, 16)
        self.buttons_gap_spinbox.setValue(self.config.hyprland.hyprbars_buttons_gap)
        config_layout.addWidget(self.buttons_gap_spinbox, 2, 1)
        
        # Buttons color
        config_layout.addWidget(QLabel("Buttons Color:"), 3, 0)
        self.buttons_color_button = QPushButton()
        self.buttons_color_button.setStyleSheet(f"background-color: {self.config.hyprland.hyprbars_buttons_color}")
        self.buttons_color_button.clicked.connect(self._choose_buttons_color)
        config_layout.addWidget(self.buttons_color_button, 3, 1)
        
        # Buttons hover color
        config_layout.addWidget(QLabel("Buttons Hover Color:"), 4, 0)
        self.buttons_hover_color_button = QPushButton()
        self.buttons_hover_color_button.setStyleSheet(f"background-color: {self.config.hyprland.hyprbars_buttons_hover_color}")
        self.buttons_hover_color_button.clicked.connect(self._choose_buttons_hover_color)
        config_layout.addWidget(self.buttons_hover_color_button, 4, 1)
        
        # Title color
        config_layout.addWidget(QLabel("Title Color:"), 5, 0)
        self.title_color_button = QPushButton()
        self.title_color_button.setStyleSheet(f"background-color: {self.config.hyprland.hyprbars_title_color}")
        self.title_color_button.clicked.connect(self._choose_title_color)
        config_layout.addWidget(self.title_color_button, 5, 1)
        
        # Title font
        config_layout.addWidget(QLabel("Title Font:"), 6, 0)
        self.title_font_combo = QFontComboBox()
        self.title_font_combo.setCurrentFont(QFont(self.config.hyprland.hyprbars_title_font))
        config_layout.addWidget(self.title_font_combo, 6, 1)
        
        # Title size
        config_layout.addWidget(QLabel("Title Size:"), 7, 0)
        self.title_size_spinbox = QSpinBox()
        self.title_size_spinbox.setRange(8, 20)
        self.title_size_spinbox.setValue(self.config.hyprland.hyprbars_title_size)
        config_layout.addWidget(self.title_size_spinbox, 7, 1)
        
        layout.addWidget(self.config_group)
        layout.addStretch()
        
        # Update enabled state
        self._update_enabled_state()
    
    def _connect_signals(self):
        """Connect signals."""
        self.enabled_checkbox.toggled.connect(self._update_enabled_state)
        self.enabled_checkbox.toggled.connect(self.config_changed.emit)
        
        # Connect all config changes
        for widget in [self.height_spinbox, self.buttons_size_spinbox, self.buttons_gap_spinbox,
                      self.title_size_spinbox]:
            widget.valueChanged.connect(self.config_changed.emit)
        
        self.title_font_combo.currentFontChanged.connect(self.config_changed.emit)
    
    def _update_enabled_state(self):
        """Update the enabled state of configuration widgets."""
        enabled = self.enabled_checkbox.isChecked()
        self.config_group.setEnabled(enabled)
    
    def _choose_buttons_color(self):
        """Choose buttons color."""
        color = QColorDialog.getColor(QColor(self.config.hyprland.hyprbars_buttons_color), self)
        if color.isValid():
            self.config.hyprland.hyprbars_buttons_color = color.name()
            self.buttons_color_button.setStyleSheet(f"background-color: {color.name()}")
            self.config_changed.emit()
    
    def _choose_buttons_hover_color(self):
        """Choose buttons hover color."""
        color = QColorDialog.getColor(QColor(self.config.hyprland.hyprbars_buttons_hover_color), self)
        if color.isValid():
            self.config.hyprland.hyprbars_buttons_hover_color = color.name()
            self.buttons_hover_color_button.setStyleSheet(f"background-color: {color.name()}")
            self.config_changed.emit()
    
    def _choose_title_color(self):
        """Choose title color."""
        color = QColorDialog.getColor(QColor(self.config.hyprland.hyprbars_title_color), self)
        if color.isValid():
            self.config.hyprland.hyprbars_title_color = color.name()
            self.title_color_button.setStyleSheet(f"background-color: {color.name()}")
            self.config_changed.emit()
    
    def apply_config(self):
        """Apply configuration changes."""
        self.config.hyprland.hyprbars_enabled = self.enabled_checkbox.isChecked()
        self.config.hyprland.hyprbars_height = self.height_spinbox.value()
        self.config.hyprland.hyprbars_buttons_size = self.buttons_size_spinbox.value()
        self.config.hyprland.hyprbars_buttons_gap = self.buttons_gap_spinbox.value()
        self.config.hyprland.hyprbars_title_font = self.title_font_combo.currentFont().family()
        self.config.hyprland.hyprbars_title_size = self.title_size_spinbox.value()


class HyprexpoTab(QWidget):
    """Tab for configuring Hyprexpo (exposure / effects plugin)."""
    
    config_changed = pyqtSignal()
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Enable/Disable checkbox
        self.enabled_checkbox = QCheckBox("Enable Hyprexpo")
        self.enabled_checkbox.setChecked(self.config.hyprland.hyprexpo_enabled)
        layout.addWidget(self.enabled_checkbox)
        
        # Main configuration group
        self.config_group = QGroupBox("Hyprexpo Configuration")
        config_layout = QGridLayout(self.config_group)
        
        # Workspace method
        config_layout.addWidget(QLabel("Workspace Method:"), 0, 0)
        self.workspace_method_combo = QComboBox()
        self.workspace_method_combo.addItems(["first 1", "all", "workspace 1", "workspace 2", "workspace 3"])
        self.workspace_method_combo.setCurrentText(self.config.hyprland.hyprexpo_workspace_method)
        config_layout.addWidget(self.workspace_method_combo, 0, 1)
        
        # Workspace gaps
        config_layout.addWidget(QLabel("Workspace Gaps:"), 1, 0)
        self.workspace_gaps_spinbox = QSpinBox()
        self.workspace_gaps_spinbox.setRange(0, 20)
        self.workspace_gaps_spinbox.setValue(self.config.hyprland.hyprexpo_workspace_gaps)
        config_layout.addWidget(self.workspace_gaps_spinbox, 1, 1)
        
        # Workspace rounding
        config_layout.addWidget(QLabel("Workspace Rounding:"), 2, 0)
        self.workspace_rounding_spinbox = QSpinBox()
        self.workspace_rounding_spinbox.setRange(0, 20)
        self.workspace_rounding_spinbox.setValue(self.config.hyprland.hyprexpo_workspace_rounding)
        config_layout.addWidget(self.workspace_rounding_spinbox, 2, 1)
        
        # Workspace shadow
        self.workspace_shadow_checkbox = QCheckBox("Enable Workspace Shadow")
        self.workspace_shadow_checkbox.setChecked(self.config.hyprland.hyprexpo_workspace_shadow)
        config_layout.addWidget(self.workspace_shadow_checkbox, 3, 0, 1, 2)
        
        # Shadow color
        config_layout.addWidget(QLabel("Shadow Color:"), 4, 0)
        self.shadow_color_button = QPushButton()
        self.shadow_color_button.setStyleSheet(f"background-color: {self.config.hyprland.hyprexpo_workspace_shadow_color}")
        self.shadow_color_button.clicked.connect(self._choose_shadow_color)
        config_layout.addWidget(self.shadow_color_button, 4, 1)
        
        # Shadow size
        config_layout.addWidget(QLabel("Shadow Size:"), 5, 0)
        self.shadow_size_spinbox = QSpinBox()
        self.shadow_size_spinbox.setRange(0, 20)
        self.shadow_size_spinbox.setValue(self.config.hyprland.hyprexpo_workspace_shadow_size)
        config_layout.addWidget(self.shadow_size_spinbox, 5, 1)
        
        # Shadow offset
        config_layout.addWidget(QLabel("Shadow Offset:"), 6, 0)
        self.shadow_offset_edit = QLineEdit(self.config.hyprland.hyprexpo_workspace_shadow_offset)
        config_layout.addWidget(self.shadow_offset_edit, 6, 1)
        
        layout.addWidget(self.config_group)
        layout.addStretch()
        
        # Update enabled state
        self._update_enabled_state()
    
    def _connect_signals(self):
        """Connect signals."""
        self.enabled_checkbox.toggled.connect(self._update_enabled_state)
        self.enabled_checkbox.toggled.connect(self.config_changed.emit)
        
        # Connect all config changes
        for widget in [self.workspace_gaps_spinbox, self.workspace_rounding_spinbox,
                      self.shadow_size_spinbox]:
            widget.valueChanged.connect(self.config_changed.emit)
        
        self.workspace_method_combo.currentTextChanged.connect(self.config_changed.emit)
        self.workspace_shadow_checkbox.toggled.connect(self.config_changed.emit)
        self.shadow_offset_edit.textChanged.connect(self.config_changed.emit)
    
    def _update_enabled_state(self):
        """Update the enabled state of configuration widgets."""
        enabled = self.enabled_checkbox.isChecked()
        self.config_group.setEnabled(enabled)
    
    def _choose_shadow_color(self):
        """Choose shadow color."""
        color = QColorDialog.getColor(QColor(self.config.hyprland.hyprexpo_workspace_shadow_color), self)
        if color.isValid():
            self.config.hyprland.hyprexpo_workspace_shadow_color = color.name()
            self.shadow_color_button.setStyleSheet(f"background-color: {color.name()}")
            self.config_changed.emit()
    
    def apply_config(self):
        """Apply configuration changes."""
        self.config.hyprland.hyprexpo_enabled = self.enabled_checkbox.isChecked()
        self.config.hyprland.hyprexpo_workspace_method = self.workspace_method_combo.currentText()
        self.config.hyprland.hyprexpo_workspace_gaps = self.workspace_gaps_spinbox.value()
        self.config.hyprland.hyprexpo_workspace_rounding = self.workspace_rounding_spinbox.value()
        self.config.hyprland.hyprexpo_workspace_shadow = self.workspace_shadow_checkbox.isChecked()
        self.config.hyprland.hyprexpo_workspace_shadow_size = self.shadow_size_spinbox.value()
        self.config.hyprland.hyprexpo_workspace_shadow_offset = self.shadow_offset_edit.text()


class GlowTab(QWidget):
    """Tab for configuring Glow via shadows."""
    
    config_changed = pyqtSignal()
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Enable/Disable checkbox
        self.enabled_checkbox = QCheckBox("Enable Glow Effects")
        self.enabled_checkbox.setChecked(self.config.hyprland.glow_enabled)
        layout.addWidget(self.enabled_checkbox)
        
        # Main configuration group
        self.config_group = QGroupBox("Glow Configuration")
        config_layout = QGridLayout(self.config_group)
        
        # Glow color
        config_layout.addWidget(QLabel("Glow Color:"), 0, 0)
        self.glow_color_button = QPushButton()
        self.glow_color_button.setStyleSheet(f"background-color: {self.config.hyprland.glow_color}")
        self.glow_color_button.clicked.connect(self._choose_glow_color)
        config_layout.addWidget(self.glow_color_button, 0, 1)
        
        # Glow size
        config_layout.addWidget(QLabel("Glow Size:"), 1, 0)
        self.glow_size_spinbox = QSpinBox()
        self.glow_size_spinbox.setRange(0, 50)
        self.glow_size_spinbox.setValue(self.config.hyprland.glow_size)
        config_layout.addWidget(self.glow_size_spinbox, 1, 1)
        
        # Glow offset
        config_layout.addWidget(QLabel("Glow Offset:"), 2, 0)
        self.glow_offset_edit = QLineEdit(self.config.hyprland.glow_offset)
        config_layout.addWidget(self.glow_offset_edit, 2, 1)
        
        # Glow opacity
        config_layout.addWidget(QLabel("Glow Opacity:"), 3, 0)
        self.glow_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.glow_opacity_slider.setRange(0, 100)
        self.glow_opacity_slider.setValue(int(self.config.hyprland.glow_opacity * 100))
        self.glow_opacity_label = QLabel(f"{self.config.hyprland.glow_opacity:.2f}")
        config_layout.addWidget(self.glow_opacity_slider, 3, 1)
        config_layout.addWidget(self.glow_opacity_label, 3, 2)
        
        # Glow blur
        config_layout.addWidget(QLabel("Glow Blur:"), 4, 0)
        self.glow_blur_spinbox = QSpinBox()
        self.glow_blur_spinbox.setRange(0, 20)
        self.glow_blur_spinbox.setValue(self.config.hyprland.glow_blur)
        config_layout.addWidget(self.glow_blur_spinbox, 4, 1)
        
        layout.addWidget(self.config_group)
        layout.addStretch()
        
        # Update enabled state
        self._update_enabled_state()
    
    def _connect_signals(self):
        """Connect signals."""
        self.enabled_checkbox.toggled.connect(self._update_enabled_state)
        self.enabled_checkbox.toggled.connect(self.config_changed.emit)
        
        # Connect all config changes
        self.glow_size_spinbox.valueChanged.connect(self.config_changed.emit)
        self.glow_blur_spinbox.valueChanged.connect(self.config_changed.emit)
        self.glow_offset_edit.textChanged.connect(self.config_changed.emit)
        
        self.glow_opacity_slider.valueChanged.connect(self._update_opacity_label)
        self.glow_opacity_slider.valueChanged.connect(self.config_changed.emit)
    
    def _update_enabled_state(self):
        """Update the enabled state of configuration widgets."""
        enabled = self.enabled_checkbox.isChecked()
        self.config_group.setEnabled(enabled)
    
    def _update_opacity_label(self, value):
        """Update opacity label."""
        opacity = value / 100.0
        self.glow_opacity_label.setText(f"{opacity:.2f}")
    
    def _choose_glow_color(self):
        """Choose glow color."""
        color = QColorDialog.getColor(QColor(self.config.hyprland.glow_color), self)
        if color.isValid():
            self.config.hyprland.glow_color = color.name()
            self.glow_color_button.setStyleSheet(f"background-color: {color.name()}")
            self.config_changed.emit()
    
    def apply_config(self):
        """Apply configuration changes."""
        self.config.hyprland.glow_enabled = self.enabled_checkbox.isChecked()
        self.config.hyprland.glow_size = self.glow_size_spinbox.value()
        self.config.hyprland.glow_offset = self.glow_offset_edit.text()
        self.config.hyprland.glow_opacity = self.glow_opacity_slider.value() / 100.0
        self.config.hyprland.glow_blur = self.glow_blur_spinbox.value()


class BlurShadersTab(QWidget):
    """Tab for configuring Blur Shaders."""
    
    config_changed = pyqtSignal()
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Enable/Disable checkbox
        self.enabled_checkbox = QCheckBox("Enable Blur Shaders")
        self.enabled_checkbox.setChecked(self.config.hyprland.blur_shaders_enabled)
        layout.addWidget(self.enabled_checkbox)
        
        # Main configuration group
        self.config_group = QGroupBox("Blur Shaders Configuration")
        config_layout = QGridLayout(self.config_group)
        
        # Shader type
        config_layout.addWidget(QLabel("Shader Type:"), 0, 0)
        self.shader_type_combo = QComboBox()
        self.shader_type_combo.addItems(["kawase", "gaussian", "custom"])
        self.shader_type_combo.setCurrentText(self.config.hyprland.blur_shader_type)
        config_layout.addWidget(self.shader_type_combo, 0, 1)
        
        # Shader passes
        config_layout.addWidget(QLabel("Shader Passes:"), 1, 0)
        self.shader_passes_spinbox = QSpinBox()
        self.shader_passes_spinbox.setRange(1, 10)
        self.shader_passes_spinbox.setValue(self.config.hyprland.blur_shader_passes)
        config_layout.addWidget(self.shader_passes_spinbox, 1, 1)
        
        # Shader size
        config_layout.addWidget(QLabel("Shader Size:"), 2, 0)
        self.shader_size_spinbox = QSpinBox()
        self.shader_size_spinbox.setRange(1, 20)
        self.shader_size_spinbox.setValue(self.config.hyprland.blur_shader_size)
        config_layout.addWidget(self.shader_size_spinbox, 2, 1)
        
        # Shader noise
        config_layout.addWidget(QLabel("Shader Noise:"), 3, 0)
        self.shader_noise_slider = QSlider(Qt.Orientation.Horizontal)
        self.shader_noise_slider.setRange(0, 100)
        self.shader_noise_slider.setValue(int(self.config.hyprland.blur_shader_noise * 100))
        self.shader_noise_label = QLabel(f"{self.config.hyprland.blur_shader_noise:.2f}")
        config_layout.addWidget(self.shader_noise_slider, 3, 1)
        config_layout.addWidget(self.shader_noise_label, 3, 2)
        
        # Shader contrast
        config_layout.addWidget(QLabel("Shader Contrast:"), 4, 0)
        self.shader_contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.shader_contrast_slider.setRange(0, 200)
        self.shader_contrast_slider.setValue(int(self.config.hyprland.blur_shader_contrast * 100))
        self.shader_contrast_label = QLabel(f"{self.config.hyprland.blur_shader_contrast:.2f}")
        config_layout.addWidget(self.shader_contrast_slider, 4, 1)
        config_layout.addWidget(self.shader_contrast_label, 4, 2)
        
        # Shader brightness
        config_layout.addWidget(QLabel("Shader Brightness:"), 5, 0)
        self.shader_brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.shader_brightness_slider.setRange(-100, 100)
        self.shader_brightness_slider.setValue(int(self.config.hyprland.blur_shader_brightness * 100))
        self.shader_brightness_label = QLabel(f"{self.config.hyprland.blur_shader_brightness:.2f}")
        config_layout.addWidget(self.shader_brightness_slider, 5, 1)
        config_layout.addWidget(self.shader_brightness_label, 5, 2)
        
        # Shader vibrancy
        config_layout.addWidget(QLabel("Shader Vibrancy:"), 6, 0)
        self.shader_vibrancy_slider = QSlider(Qt.Orientation.Horizontal)
        self.shader_vibrancy_slider.setRange(0, 100)
        self.shader_vibrancy_slider.setValue(int(self.config.hyprland.blur_shader_vibrancy * 100))
        self.shader_vibrancy_label = QLabel(f"{self.config.hyprland.blur_shader_vibrancy:.2f}")
        config_layout.addWidget(self.shader_vibrancy_slider, 6, 1)
        config_layout.addWidget(self.shader_vibrancy_label, 6, 2)
        
        # Shader vibrancy darkness
        config_layout.addWidget(QLabel("Shader Vibrancy Darkness:"), 7, 0)
        self.shader_vibrancy_darkness_slider = QSlider(Qt.Orientation.Horizontal)
        self.shader_vibrancy_darkness_slider.setRange(0, 100)
        self.shader_vibrancy_darkness_slider.setValue(int(self.config.hyprland.blur_shader_vibrancy_darkness * 100))
        self.shader_vibrancy_darkness_label = QLabel(f"{self.config.hyprland.blur_shader_vibrancy_darkness:.2f}")
        config_layout.addWidget(self.shader_vibrancy_darkness_slider, 7, 1)
        config_layout.addWidget(self.shader_vibrancy_darkness_label, 7, 2)
        
        layout.addWidget(self.config_group)
        layout.addStretch()
        
        # Update enabled state
        self._update_enabled_state()
    
    def _connect_signals(self):
        """Connect signals."""
        self.enabled_checkbox.toggled.connect(self._update_enabled_state)
        self.enabled_checkbox.toggled.connect(self.config_changed.emit)
        
        # Connect all config changes
        self.shader_passes_spinbox.valueChanged.connect(self.config_changed.emit)
        self.shader_size_spinbox.valueChanged.connect(self.config_changed.emit)
        self.shader_type_combo.currentTextChanged.connect(self.config_changed.emit)
        
        # Connect sliders
        self.shader_noise_slider.valueChanged.connect(self._update_noise_label)
        self.shader_noise_slider.valueChanged.connect(self.config_changed.emit)
        
        self.shader_contrast_slider.valueChanged.connect(self._update_contrast_label)
        self.shader_contrast_slider.valueChanged.connect(self.config_changed.emit)
        
        self.shader_brightness_slider.valueChanged.connect(self._update_brightness_label)
        self.shader_brightness_slider.valueChanged.connect(self.config_changed.emit)
        
        self.shader_vibrancy_slider.valueChanged.connect(self._update_vibrancy_label)
        self.shader_vibrancy_slider.valueChanged.connect(self.config_changed.emit)
        
        self.shader_vibrancy_darkness_slider.valueChanged.connect(self._update_vibrancy_darkness_label)
        self.shader_vibrancy_darkness_slider.valueChanged.connect(self.config_changed.emit)
    
    def _update_enabled_state(self):
        """Update the enabled state of configuration widgets."""
        enabled = self.enabled_checkbox.isChecked()
        self.config_group.setEnabled(enabled)
    
    def _update_noise_label(self, value):
        """Update noise label."""
        noise = value / 100.0
        self.shader_noise_label.setText(f"{noise:.2f}")
    
    def _update_contrast_label(self, value):
        """Update contrast label."""
        contrast = value / 100.0
        self.shader_contrast_label.setText(f"{contrast:.2f}")
    
    def _update_brightness_label(self, value):
        """Update brightness label."""
        brightness = value / 100.0
        self.shader_brightness_label.setText(f"{brightness:.2f}")
    
    def _update_vibrancy_label(self, value):
        """Update vibrancy label."""
        vibrancy = value / 100.0
        self.shader_vibrancy_label.setText(f"{vibrancy:.2f}")
    
    def _update_vibrancy_darkness_label(self, value):
        """Update vibrancy darkness label."""
        vibrancy_darkness = value / 100.0
        self.shader_vibrancy_darkness_label.setText(f"{vibrancy_darkness:.2f}")
    
    def apply_config(self):
        """Apply configuration changes."""
        self.config.hyprland.blur_shaders_enabled = self.enabled_checkbox.isChecked()
        self.config.hyprland.blur_shader_type = self.shader_type_combo.currentText()
        self.config.hyprland.blur_shader_passes = self.shader_passes_spinbox.value()
        self.config.hyprland.blur_shader_size = self.shader_size_spinbox.value()
        self.config.hyprland.blur_shader_noise = self.shader_noise_slider.value() / 100.0
        self.config.hyprland.blur_shader_contrast = self.shader_contrast_slider.value() / 100.0
        self.config.hyprland.blur_shader_brightness = self.shader_brightness_slider.value() / 100.0
        self.config.hyprland.blur_shader_vibrancy = self.shader_vibrancy_slider.value() / 100.0
        self.config.hyprland.blur_shader_vibrancy_darkness = self.shader_vibrancy_darkness_slider.value() / 100.0


class PluginsTab(QWidget):
    """Main tab containing all plugin configuration tabs."""
    
    config_changed = pyqtSignal()
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add plugin tabs
        self.hyprbars_tab = HyprbarsTab(self.config)
        self.hyprexpo_tab = HyprexpoTab(self.config)
        self.glow_tab = GlowTab(self.config)
        self.blur_shaders_tab = BlurShadersTab(self.config)
        
        self.tab_widget.addTab(self.hyprbars_tab, "Hyprbars")
        self.tab_widget.addTab(self.hyprexpo_tab, "Hyprexpo")
        self.tab_widget.addTab(self.glow_tab, "Glow")
        self.tab_widget.addTab(self.blur_shaders_tab, "Blur Shaders")
        
        layout.addWidget(self.tab_widget)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Apply Configuration")
        self.apply_button.clicked.connect(self.apply_config)
        button_layout.addWidget(self.apply_button)
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_config)
        button_layout.addWidget(self.reset_button)
        
        self.generate_button = QPushButton("Generate Modular Configs")
        self.generate_button.clicked.connect(self.generate_modular_configs)
        button_layout.addWidget(self.generate_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals."""
        # Connect all plugin tab signals
        self.hyprbars_tab.config_changed.connect(self.config_changed.emit)
        self.hyprexpo_tab.config_changed.connect(self.config_changed.emit)
        self.glow_tab.config_changed.connect(self.config_changed.emit)
        self.blur_shaders_tab.config_changed.connect(self.config_changed.emit)
    
    def apply_config(self):
        """Apply all plugin configurations."""
        try:
            self.hyprbars_tab.apply_config()
            self.hyprexpo_tab.apply_config()
            self.glow_tab.apply_config()
            self.blur_shaders_tab.apply_config()
            
            # Save configuration
            self.config.save()
            
            QMessageBox.information(self, "Success", "Plugin configurations applied successfully!")
            self.config_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply configurations: {e}")
            self.logger.error(f"Failed to apply plugin configurations: {e}")
    
    def reset_config(self):
        """Reset all plugin configurations to defaults."""
        try:
            # Reset to default values
            from ..config import HyprlandConfig
            default_config = HyprlandConfig()
            
            # Apply defaults
            self.config.hyprland.hyprbars_enabled = default_config.hyprbars_enabled
            self.config.hyprland.hyprbars_height = default_config.hyprbars_height
            self.config.hyprland.hyprbars_buttons_size = default_config.hyprbars_buttons_size
            self.config.hyprland.hyprbars_buttons_gap = default_config.hyprbars_buttons_gap
            self.config.hyprland.hyprbars_buttons_color = default_config.hyprbars_buttons_color
            self.config.hyprland.hyprbars_buttons_hover_color = default_config.hyprbars_buttons_hover_color
            self.config.hyprland.hyprbars_title_color = default_config.hyprbars_title_color
            self.config.hyprland.hyprbars_title_font = default_config.hyprbars_title_font
            self.config.hyprland.hyprbars_title_size = default_config.hyprbars_title_size
            
            self.config.hyprland.hyprexpo_enabled = default_config.hyprexpo_enabled
            self.config.hyprland.hyprexpo_workspace_method = default_config.hyprexpo_workspace_method
            self.config.hyprland.hyprexpo_workspace_gaps = default_config.hyprexpo_workspace_gaps
            self.config.hyprland.hyprexpo_workspace_rounding = default_config.hyprexpo_workspace_rounding
            self.config.hyprland.hyprexpo_workspace_shadow = default_config.hyprexpo_workspace_shadow
            self.config.hyprland.hyprexpo_workspace_shadow_color = default_config.hyprexpo_workspace_shadow_color
            self.config.hyprland.hyprexpo_workspace_shadow_size = default_config.hyprexpo_workspace_shadow_size
            self.config.hyprland.hyprexpo_workspace_shadow_offset = default_config.hyprexpo_workspace_shadow_offset
            
            self.config.hyprland.glow_enabled = default_config.glow_enabled
            self.config.hyprland.glow_color = default_config.glow_color
            self.config.hyprland.glow_size = default_config.glow_size
            self.config.hyprland.glow_offset = default_config.glow_offset
            self.config.hyprland.glow_opacity = default_config.glow_opacity
            self.config.hyprland.glow_blur = default_config.glow_blur
            
            self.config.hyprland.blur_shaders_enabled = default_config.blur_shaders_enabled
            self.config.hyprland.blur_shader_type = default_config.blur_shader_type
            self.config.hyprland.blur_shader_passes = default_config.blur_shader_passes
            self.config.hyprland.blur_shader_size = default_config.blur_shader_size
            self.config.hyprland.blur_shader_noise = default_config.blur_shader_noise
            self.config.hyprland.blur_shader_contrast = default_config.blur_shader_contrast
            self.config.hyprland.blur_shader_brightness = default_config.blur_shader_brightness
            self.config.hyprland.blur_shader_vibrancy = default_config.blur_shader_vibrancy
            self.config.hyprland.blur_shader_vibrancy_darkness = default_config.blur_shader_vibrancy_darkness
            
            # Save configuration
            self.config.save()
            
            # Refresh UI
            self._refresh_ui()
            
            QMessageBox.information(self, "Success", "Plugin configurations reset to defaults!")
            self.config_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset configurations: {e}")
            self.logger.error(f"Failed to reset plugin configurations: {e}")
    
    def generate_modular_configs(self):
        """Generate modular configuration files."""
        try:
            from ..hyprland.modular_config import ModularConfigGenerator
            
            generator = ModularConfigGenerator(self.config)
            configs = generator.generate_all_configs()
            
            # Reload Hyprland
            if generator.reload_hyprland():
                QMessageBox.information(self, "Success", 
                                      f"Generated modular configs:\n" +
                                      "\n".join(configs.keys()) +
                                      "\n\nHyprland configuration reloaded!")
            else:
                QMessageBox.warning(self, "Warning", 
                                  f"Generated modular configs:\n" +
                                  "\n".join(configs.keys()) +
                                  "\n\nFailed to reload Hyprland configuration.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate modular configs: {e}")
            self.logger.error(f"Failed to generate modular configs: {e}")
    
    def _refresh_ui(self):
        """Refresh the UI to reflect current configuration."""
        # Recreate tabs with current config
        current_index = self.tab_widget.currentIndex()
        
        # Remove old tabs
        self.tab_widget.removeTab(0)  # Hyprbars
        self.tab_widget.removeTab(0)  # Hyprexpo
        self.tab_widget.removeTab(0)  # Glow
        self.tab_widget.removeTab(0)  # Blur Shaders
        
        # Create new tabs
        self.hyprbars_tab = HyprbarsTab(self.config)
        self.hyprexpo_tab = HyprexpoTab(self.config)
        self.glow_tab = GlowTab(self.config)
        self.blur_shaders_tab = BlurShadersTab(self.config)
        
        # Add new tabs
        self.tab_widget.addTab(self.hyprbars_tab, "Hyprbars")
        self.tab_widget.addTab(self.hyprexpo_tab, "Hyprexpo")
        self.tab_widget.addTab(self.glow_tab, "Glow")
        self.tab_widget.addTab(self.blur_shaders_tab, "Blur Shaders")
        
        # Restore current tab
        if 0 <= current_index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(current_index)
        
        # Reconnect signals
        self._connect_signals()
