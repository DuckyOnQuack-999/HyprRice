"""
Theme editor dialog for creating and editing HyprRice themes.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QTextEdit, QPushButton, QDialogButtonBox,
    QTabWidget, QWidget, QGroupBox, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QColorDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from typing import Dict, Any


class ThemeEditorDialog(QDialog):
    """Dialog for editing theme properties."""
    
    theme_saved = pyqtSignal(dict)
    
    def __init__(self, theme_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.theme_data = theme_data.copy()
        self.setup_ui()
        self.load_theme_data()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Theme Editor")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # General tab
        self.general_tab = self.create_general_tab()
        self.tab_widget.addTab(self.general_tab, "General")
        
        # Hyprland tab
        self.hyprland_tab = self.create_hyprland_tab()
        self.tab_widget.addTab(self.hyprland_tab, "Hyprland")
        
        # Waybar tab
        self.waybar_tab = self.create_waybar_tab()
        self.tab_widget.addTab(self.waybar_tab, "Waybar")
        
        # Rofi tab
        self.rofi_tab = self.create_rofi_tab()
        self.tab_widget.addTab(self.rofi_tab, "Rofi")
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def create_general_tab(self) -> QWidget:
        """Create the general properties tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Theme name
        self.name_edit = QLineEdit()
        layout.addRow("Name:", self.name_edit)
        
        # Version
        self.version_edit = QLineEdit()
        layout.addRow("Version:", self.version_edit)
        
        # Author
        self.author_edit = QLineEdit()
        layout.addRow("Author:", self.author_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        layout.addRow("Description:", self.description_edit)
        
        return widget
    
    def create_hyprland_tab(self) -> QWidget:
        """Create the Hyprland settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Animations group
        anim_group = QGroupBox("Animations")
        anim_layout = QFormLayout(anim_group)
        
        self.animations_enabled = QCheckBox()
        anim_layout.addRow("Enable Animations:", self.animations_enabled)
        
        self.animation_duration = QDoubleSpinBox()
        self.animation_duration.setRange(0.1, 5.0)
        self.animation_duration.setSingleStep(0.1)
        anim_layout.addRow("Duration (s):", self.animation_duration)
        
        self.animation_curve = QComboBox()
        self.animation_curve.addItems(["linear", "ease-out", "ease-in", "ease-in-out"])
        anim_layout.addRow("Curve:", self.animation_curve)
        
        layout.addWidget(anim_group)
        
        # Window management group
        window_group = QGroupBox("Window Management")
        window_layout = QFormLayout(window_group)
        
        self.window_opacity = QDoubleSpinBox()
        self.window_opacity.setRange(0.0, 1.0)
        self.window_opacity.setSingleStep(0.05)
        window_layout.addRow("Opacity:", self.window_opacity)
        
        self.border_size = QSpinBox()
        self.border_size.setRange(0, 20)
        window_layout.addRow("Border Size:", self.border_size)
        
        # Border color
        color_layout = QHBoxLayout()
        self.border_color = QLineEdit()
        color_layout.addWidget(self.border_color)
        color_btn = QPushButton("Pick Color")
        color_btn.clicked.connect(self.pick_border_color)
        color_layout.addWidget(color_btn)
        window_layout.addRow("Border Color:", color_layout)
        
        # Gaps
        self.gaps_in = QSpinBox()
        self.gaps_in.setRange(0, 50)
        window_layout.addRow("Inner Gaps:", self.gaps_in)
        
        self.gaps_out = QSpinBox()
        self.gaps_out.setRange(0, 50)
        window_layout.addRow("Outer Gaps:", self.gaps_out)
        
        self.blur_enabled = QCheckBox()
        window_layout.addRow("Enable Blur:", self.blur_enabled)
        
        layout.addWidget(window_group)
        
        return widget
    
    def create_waybar_tab(self) -> QWidget:
        """Create the Waybar settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self.waybar_position = QComboBox()
        self.waybar_position.addItems(["top", "bottom", "left", "right"])
        layout.addRow("Position:", self.waybar_position)
        
        self.waybar_height = QSpinBox()
        self.waybar_height.setRange(10, 100)
        layout.addRow("Height:", self.waybar_height)
        
        # Colors
        color_layout = QHBoxLayout()
        self.waybar_bg_color = QLineEdit()
        color_layout.addWidget(self.waybar_bg_color)
        bg_color_btn = QPushButton("Pick")
        bg_color_btn.clicked.connect(self.pick_waybar_bg_color)
        color_layout.addWidget(bg_color_btn)
        layout.addRow("Background Color:", color_layout)
        
        text_color_layout = QHBoxLayout()
        self.waybar_text_color = QLineEdit()
        text_color_layout.addWidget(self.waybar_text_color)
        text_color_btn = QPushButton("Pick")
        text_color_btn.clicked.connect(self.pick_waybar_text_color)
        text_color_layout.addWidget(text_color_btn)
        layout.addRow("Text Color:", text_color_layout)
        
        self.waybar_font_family = QLineEdit()
        layout.addRow("Font Family:", self.waybar_font_family)
        
        self.waybar_font_size = QSpinBox()
        self.waybar_font_size.setRange(8, 32)
        layout.addRow("Font Size:", self.waybar_font_size)
        
        return widget
    
    def create_rofi_tab(self) -> QWidget:
        """Create the Rofi settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self.rofi_theme = QLineEdit()
        layout.addRow("Theme:", self.rofi_theme)
        
        self.rofi_width = QSpinBox()
        self.rofi_width.setRange(10, 100)
        layout.addRow("Width (%):", self.rofi_width)
        
        self.rofi_location = QComboBox()
        self.rofi_location.addItems(["center", "top", "bottom", "left", "right"])
        layout.addRow("Location:", self.rofi_location)
        
        # Colors
        bg_color_layout = QHBoxLayout()
        self.rofi_bg_color = QLineEdit()
        bg_color_layout.addWidget(self.rofi_bg_color)
        bg_color_btn = QPushButton("Pick")
        bg_color_btn.clicked.connect(self.pick_rofi_bg_color)
        bg_color_layout.addWidget(bg_color_btn)
        layout.addRow("Background Color:", bg_color_layout)
        
        text_color_layout = QHBoxLayout()
        self.rofi_text_color = QLineEdit()
        text_color_layout.addWidget(self.rofi_text_color)
        text_color_btn = QPushButton("Pick")
        text_color_btn.clicked.connect(self.pick_rofi_text_color)
        text_color_layout.addWidget(text_color_btn)
        layout.addRow("Text Color:", text_color_layout)
        
        border_color_layout = QHBoxLayout()
        self.rofi_border_color = QLineEdit()
        border_color_layout.addWidget(self.rofi_border_color)
        border_color_btn = QPushButton("Pick")
        border_color_btn.clicked.connect(self.pick_rofi_border_color)
        border_color_layout.addWidget(border_color_btn)
        layout.addRow("Border Color:", border_color_layout)
        
        self.rofi_font_family = QLineEdit()
        layout.addRow("Font Family:", self.rofi_font_family)
        
        self.rofi_font_size = QSpinBox()
        self.rofi_font_size.setRange(8, 32)
        layout.addRow("Font Size:", self.rofi_font_size)
        
        return widget
    
    def load_theme_data(self):
        """Load theme data into the form."""
        # General properties
        self.name_edit.setText(self.theme_data.get('name', ''))
        self.version_edit.setText(self.theme_data.get('version', '1.0.0'))
        self.author_edit.setText(self.theme_data.get('author', ''))
        self.description_edit.setPlainText(self.theme_data.get('description', ''))
        
        # Hyprland settings
        config = self.theme_data.get('config', {})
        hyprland = config.get('hyprland', {})
        
        self.animations_enabled.setChecked(hyprland.get('animations_enabled', True))
        self.animation_duration.setValue(hyprland.get('animation_duration', 0.5))
        self.animation_curve.setCurrentText(hyprland.get('animation_curve', 'ease-out'))
        self.window_opacity.setValue(hyprland.get('window_opacity', 1.0))
        self.border_size.setValue(hyprland.get('border_size', 1))
        self.border_color.setText(hyprland.get('border_color', '#ffffff'))
        self.gaps_in.setValue(hyprland.get('gaps_in', 5))
        self.gaps_out.setValue(hyprland.get('gaps_out', 10))
        self.blur_enabled.setChecked(hyprland.get('blur_enabled', True))
        
        # Waybar settings
        waybar = config.get('waybar', {})
        
        self.waybar_position.setCurrentText(waybar.get('position', 'top'))
        self.waybar_height.setValue(waybar.get('height', 30))
        self.waybar_bg_color.setText(waybar.get('background_color', 'rgba(43, 48, 59, 0.5)'))
        self.waybar_text_color.setText(waybar.get('text_color', '#ffffff'))
        self.waybar_font_family.setText(waybar.get('font_family', 'JetBrainsMono Nerd Font'))
        self.waybar_font_size.setValue(waybar.get('font_size', 13))
        
        # Rofi settings
        rofi = config.get('rofi', {})
        
        self.rofi_theme.setText(rofi.get('theme', 'default'))
        self.rofi_width.setValue(rofi.get('width', 40))
        self.rofi_location.setCurrentText(rofi.get('location', 'center'))
        self.rofi_bg_color.setText(rofi.get('background_color', '#2e3440'))
        self.rofi_text_color.setText(rofi.get('text_color', '#eceff4'))
        self.rofi_border_color.setText(rofi.get('border_color', '#5e81ac'))
        self.rofi_font_family.setText(rofi.get('font_family', 'JetBrainsMono Nerd Font'))
        self.rofi_font_size.setValue(rofi.get('font_size', 14))
    
    def get_theme_data(self) -> Dict[str, Any]:
        """Get the edited theme data."""
        return {
            'name': self.name_edit.text(),
            'version': self.version_edit.text(),
            'author': self.author_edit.text(),
            'description': self.description_edit.toPlainText(),
            'config': {
                'hyprland': {
                    'animations_enabled': self.animations_enabled.isChecked(),
                    'animation_duration': self.animation_duration.value(),
                    'animation_curve': self.animation_curve.currentText(),
                    'window_opacity': self.window_opacity.value(),
                    'border_size': self.border_size.value(),
                    'border_color': self.border_color.text(),
                    'gaps_in': self.gaps_in.value(),
                    'gaps_out': self.gaps_out.value(),
                    'blur_enabled': self.blur_enabled.isChecked()
                },
                'waybar': {
                    'position': self.waybar_position.currentText(),
                    'height': self.waybar_height.value(),
                    'background_color': self.waybar_bg_color.text(),
                    'text_color': self.waybar_text_color.text(),
                    'font_family': self.waybar_font_family.text(),
                    'font_size': self.waybar_font_size.value()
                },
                'rofi': {
                    'theme': self.rofi_theme.text(),
                    'width': self.rofi_width.value(),
                    'location': self.rofi_location.currentText(),
                    'background_color': self.rofi_bg_color.text(),
                    'text_color': self.rofi_text_color.text(),
                    'border_color': self.rofi_border_color.text(),
                    'font_family': self.rofi_font_family.text(),
                    'font_size': self.rofi_font_size.value()
                }
            }
        }
    
    def pick_border_color(self):
        """Pick border color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.border_color.setText(color.name())
    
    def pick_waybar_bg_color(self):
        """Pick waybar background color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.waybar_bg_color.setText(color.name())
    
    def pick_waybar_text_color(self):
        """Pick waybar text color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.waybar_text_color.setText(color.name())
    
    def pick_rofi_bg_color(self):
        """Pick rofi background color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.rofi_bg_color.setText(color.name())
    
    def pick_rofi_text_color(self):
        """Pick rofi text color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.rofi_text_color.setText(color.name())
    
    def pick_rofi_border_color(self):
        """Pick rofi border color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.rofi_border_color.setText(color.name())
    
    def accept(self):
        """Accept the dialog and validate data."""
        # Validate required fields
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Theme name is required.")
            return
        
        if not self.version_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Version is required.")
            return
        
        super().accept()