"""
Modern theme system for HyprRice with dark/light modes and accent colors.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtWidgets import QApplication


class ModernTheme(QObject):
    """Modern theme system with dark/light modes and accent colors."""
    
    theme_changed = pyqtSignal(str)  # Emitted when theme changes
    
    def __init__(self):
        super().__init__()
        self.current_theme = "dark"
        self.accent_color = "#5e81ac"  # Default accent color
        self.themes = {
            "dark": self._get_dark_theme(),
            "light": self._get_light_theme(),
            "auto": None  # Will be determined dynamically
        }
    
    def _get_dark_theme(self) -> Dict[str, str]:
        """Get dark theme colors."""
        return {
            # Base colors
            "bg_primary": "#2e3440",
            "bg_secondary": "#3b4252", 
            "bg_tertiary": "#434c5e",
            "bg_hover": "#4c566a",
            "bg_pressed": "#5e81ac",
            
            # Text colors
            "text_primary": "#eceff4",
            "text_secondary": "#d8dee9",
            "text_tertiary": "#88c0d0",
            "text_disabled": "#4c566a",
            
            # Accent colors
            "accent": self.accent_color,
            "accent_hover": "#81a1c1",
            "accent_pressed": "#5e81ac",
            
            # Status colors
            "success": "#a3be8c",
            "warning": "#ebcb8b", 
            "error": "#bf616a",
            "info": "#88c0d0",
            
            # Border colors
            "border": "#4c566a",
            "border_focus": self.accent_color,
            "border_hover": "#81a1c1",
            
            # Shadow colors
            "shadow": "rgba(0, 0, 0, 0.3)",
            "shadow_hover": "rgba(0, 0, 0, 0.4)",
        }
    
    def _get_light_theme(self) -> Dict[str, str]:
        """Get light theme colors."""
        return {
            # Base colors
            "bg_primary": "#f8f9fa",
            "bg_secondary": "#e9ecef",
            "bg_tertiary": "#dee2e6",
            "bg_hover": "#ced4da",
            "bg_pressed": "#adb5bd",
            
            # Text colors
            "text_primary": "#212529",
            "text_secondary": "#495057",
            "text_tertiary": "#6c757d",
            "text_disabled": "#adb5bd",
            
            # Accent colors
            "accent": self.accent_color,
            "accent_hover": "#4a6fa5",
            "accent_pressed": "#3d5a8a",
            
            # Status colors
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545",
            "info": "#17a2b8",
            
            # Border colors
            "border": "#ced4da",
            "border_focus": self.accent_color,
            "border_hover": "#4a6fa5",
            
            # Shadow colors
            "shadow": "rgba(0, 0, 0, 0.1)",
            "shadow_hover": "rgba(0, 0, 0, 0.15)",
        }
    
    def set_accent_color(self, color: str):
        """Set the accent color for the current theme."""
        self.accent_color = color
        # Update themes with new accent color
        self.themes["dark"] = self._get_dark_theme()
        self.themes["light"] = self._get_light_theme()
        self.theme_changed.emit(self.current_theme)
    
    def set_theme(self, theme: str):
        """Set the current theme."""
        if theme == "auto":
            theme = self._detect_system_theme()
        
        if theme in self.themes:
            self.current_theme = theme
            self.theme_changed.emit(theme)
    
    def _detect_system_theme(self) -> str:
        """Detect system theme preference."""
        # Try to detect from environment variables
        gtk_theme = os.environ.get("GTK_THEME", "").lower()
        if "dark" in gtk_theme:
            return "dark"
        
        # Check for common dark theme indicators
        color_scheme = os.environ.get("COLORFGBG", "")
        if color_scheme and color_scheme.startswith("15;"):  # Dark background
            return "dark"
        
        # Default to dark theme for modern look
        return "dark"
    
    def get_current_colors(self) -> Dict[str, str]:
        """Get colors for the current theme."""
        if self.current_theme == "auto":
            theme = self._detect_system_theme()
        else:
            theme = self.current_theme
        
        return self.themes.get(theme, self.themes["dark"])
    
    def get_qss(self) -> str:
        """Get QSS stylesheet for the current theme."""
        colors = self.get_current_colors()
        
        return f"""
        /* Modern HyprRice Theme */
        QMainWindow {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
        }}
        
        /* Sidebar */
        QFrame {{
            background-color: {colors['bg_secondary']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
        }}
        
        /* Navigation Tree */
        QTreeWidget {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: none;
            outline: none;
            selection-background-color: {colors['accent']};
            selection-color: {colors['text_primary']};
        }}
        
        QTreeWidget::item {{
            padding: 8px;
            border-radius: 4px;
            margin: 2px;
        }}
        
        QTreeWidget::item:hover {{
            background-color: {colors['bg_hover']};
        }}
        
        QTreeWidget::item:selected {{
            background-color: {colors['accent']};
            color: {colors['text_primary']};
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            border-radius: 8px;
            background-color: {colors['bg_primary']};
        }}
        
        QTabBar::tab {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_secondary']};
            padding: 12px 20px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border: 1px solid {colors['border']};
            border-bottom: none;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border-bottom: 2px solid {colors['accent']};
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors['bg_hover']};
            color: {colors['text_primary']};
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {colors['accent']};
            color: {colors['text_primary']};
            border: none;
            border-radius: 6px;
            padding: 10px 16px;
            font-weight: 500;
            min-height: 20px;
        }}
        
        QPushButton:hover {{
            background-color: {colors['accent_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['accent_pressed']};
        }}
        
        QPushButton:disabled {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_disabled']};
        }}
        
        /* Secondary buttons */
        QPushButton[class="secondary"] {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
        }}
        
        QPushButton[class="secondary"]:hover {{
            background-color: {colors['bg_hover']};
            border-color: {colors['border_hover']};
        }}
        
        /* Input fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            selection-background-color: {colors['accent']};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {colors['border_focus']};
            outline: none;
        }}
        
        /* Combo boxes */
        QComboBox {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            min-width: 100px;
        }}
        
        QComboBox:hover {{
            border-color: {colors['border_hover']};
        }}
        
        QComboBox:focus {{
            border-color: {colors['border_focus']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {colors['text_secondary']};
            margin-right: 5px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            selection-background-color: {colors['accent']};
        }}
        
        /* Checkboxes and radio buttons */
        QCheckBox, QRadioButton {{
            color: {colors['text_primary']};
            spacing: 8px;
        }}
        
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {colors['border']};
            border-radius: 3px;
            background-color: {colors['bg_secondary']};
        }}
        
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background-color: {colors['accent']};
            border-color: {colors['accent']};
        }}
        
        QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
            border-color: {colors['border_hover']};
        }}
        
        QRadioButton::indicator {{
            border-radius: 9px;
        }}
        
        /* Sliders */
        QSlider::groove:horizontal {{
            height: 6px;
            background-color: {colors['bg_tertiary']};
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {colors['accent']};
            border: none;
            width: 18px;
            height: 18px;
            border-radius: 9px;
            margin: -6px 0;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {colors['accent_hover']};
        }}
        
        /* Progress bars */
        QProgressBar {{
            background-color: {colors['bg_tertiary']};
            border: none;
            border-radius: 6px;
            text-align: center;
            color: {colors['text_primary']};
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['accent']};
            border-radius: 6px;
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {colors['bg_secondary']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['bg_tertiary']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['bg_hover']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        /* Status bar */
        QStatusBar {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_secondary']};
            border-top: 1px solid {colors['border']};
        }}
        
        /* Menu bar */
        QMenuBar {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border-bottom: 1px solid {colors['border']};
        }}
        
        QMenuBar::item {{
            padding: 8px 12px;
            border-radius: 4px;
            margin: 2px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors['bg_hover']};
        }}
        
        QMenu {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
        }}
        
        QMenu::item {{
            padding: 8px 20px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors['accent']};
        }}
        
        /* Tooltips */
        QToolTip {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px 8px;
        }}
        
        /* Group boxes */
        QGroupBox {{
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            background-color: {colors['bg_primary']};
        }}
        
        /* Labels */
        QLabel {{
            color: {colors['text_primary']};
        }}
        
        QLabel[class="title"] {{
            font-size: 16px;
            font-weight: bold;
            color: {colors['text_primary']};
        }}
        
        QLabel[class="subtitle"] {{
            font-size: 14px;
            font-weight: 500;
            color: {colors['text_secondary']};
        }}
        
        QLabel[class="caption"] {{
            font-size: 12px;
            color: {colors['text_tertiary']};
        }}
        
        /* Success, warning, error states */
        QLabel[class="success"] {{
            color: {colors['success']};
        }}
        
        QLabel[class="warning"] {{
            color: {colors['warning']};
        }}
        
        QLabel[class="error"] {{
            color: {colors['error']};
        }}
        
        QLabel[class="info"] {{
            color: {colors['info']};
        }}
        """
    
    def apply_to_application(self, app: QApplication):
        """Apply the current theme to the application."""
        app.setStyleSheet(self.get_qss())
        
        # Set application font
        font = QFont("Inter", 10)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        app.setFont(font)
        
        # Set palette for better integration
        palette = QPalette()
        colors = self.get_current_colors()
        
        # Set palette colors
        palette.setColor(QPalette.ColorRole.Window, QColor(colors['bg_primary']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors['bg_secondary']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors['bg_tertiary']))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors['bg_tertiary']))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors['bg_secondary']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors['accent']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['accent']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors['text_primary']))
        
        app.setPalette(palette)
