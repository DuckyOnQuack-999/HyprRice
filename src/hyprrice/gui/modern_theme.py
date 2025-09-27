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
        """Get dark theme colors - ultra modern and sleek."""
        return {
            # Base colors - deeper, more modern
            "bg_primary": "#1a1a1a",
            "bg_secondary": "#252525", 
            "bg_tertiary": "#2a2a2a",
            "bg_hover": "#333333",
            "bg_pressed": "#404040",
            "bg_elevated": "#2d2d2d",
            
            # Text colors - high contrast
            "text_primary": "#ffffff",
            "text_secondary": "#e0e0e0",
            "text_tertiary": "#b0b0b0",
            "text_disabled": "#666666",
            "text_accent": self.accent_color,
            
            # Accent colors - vibrant and modern
            "accent": self.accent_color,
            "accent_hover": "#7c9eff",
            "accent_pressed": "#4a6bff",
            "accent_light": "#e8f0ff",
            
            # Status colors - modern palette
            "success": "#00d4aa",
            "warning": "#ffb800", 
            "error": "#ff4757",
            "info": "#3742fa",
            
            # Border colors - subtle but defined
            "border": "#404040",
            "border_light": "#333333",
            "border_focus": self.accent_color,
            "border_hover": "#555555",
            
            # Shadow colors - deeper shadows
            "shadow": "rgba(0, 0, 0, 0.4)",
            "shadow_hover": "rgba(0, 0, 0, 0.5)",
            "shadow_light": "rgba(0, 0, 0, 0.2)",
            
            # Glass effect colors
            "glass_bg": "rgba(42, 42, 42, 0.8)",
            "glass_border": "rgba(255, 255, 255, 0.1)",
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
        /* Ultra Modern HyprRice Theme */
        QMainWindow {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border: none;
        }}
        
        /* Sidebar with glass effect */
        QFrame {{
            background-color: {colors['bg_secondary']};
            border: 1px solid {colors['border_light']};
            border-radius: 12px;
            margin: 8px;
        }}
        
        /* Glass effect panels */
        QFrame[class="glass"] {{
            background-color: {colors['glass_bg']};
            border: 1px solid {colors['glass_border']};
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }}
        
        /* Navigation Tree - Modern */
        QTreeWidget {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: none;
            outline: none;
            selection-background-color: {colors['accent']};
            selection-color: {colors['text_primary']};
            border-radius: 8px;
            padding: 4px;
        }}
        
        QTreeWidget::item {{
            padding: 12px 16px;
            border-radius: 8px;
            margin: 2px;
            border: none;
        }}
        
        QTreeWidget::item:hover {{
            background-color: {colors['bg_hover']};
            color: {colors['text_primary']};
        }}
        
        QTreeWidget::item:selected {{
            background-color: {colors['accent']};
            color: {colors['text_primary']};
            font-weight: 600;
        }}
        
        QTreeWidget::item:selected:hover {{
            background-color: {colors['accent_hover']};
        }}
        
        /* Tabs - Ultra Modern */
        QTabWidget::pane {{
            border: 1px solid {colors['border_light']};
            border-radius: 16px;
            background-color: {colors['bg_primary']};
            margin-top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_secondary']};
            padding: 16px 24px;
            margin-right: 4px;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            border: 1px solid {colors['border_light']};
            border-bottom: none;
            font-weight: 500;
            min-width: 120px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border-bottom: 3px solid {colors['accent']};
            font-weight: 600;
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors['bg_hover']};
            color: {colors['text_primary']};
            border-color: {colors['border_hover']};
        }}
        
        QTabBar::tab:selected:hover {{
            background-color: {colors['bg_primary']};
        }}
        
        /* Buttons - Ultra Modern */
        QPushButton {{
            background-color: {colors['accent']};
            color: {colors['text_primary']};
            border: none;
            border-radius: 12px;
            padding: 14px 24px;
            font-weight: 600;
            min-height: 24px;
            font-size: 14px;
            box-shadow: 0 2px 8px {colors['shadow_light']};
        }}
        
        QPushButton:hover {{
            background-color: {colors['accent_hover']};
            box-shadow: 0 4px 12px {colors['shadow']};
            transform: translateY(-1px);
        }}
        
        QPushButton:pressed {{
            background-color: {colors['accent_pressed']};
            box-shadow: 0 1px 4px {colors['shadow']};
            transform: translateY(0px);
        }}
        
        QPushButton:disabled {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_disabled']};
            box-shadow: none;
        }}
        
        /* Secondary buttons */
        QPushButton[class="secondary"] {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            box-shadow: 0 2px 4px {colors['shadow_light']};
        }}
        
        QPushButton[class="secondary"]:hover {{
            background-color: {colors['bg_hover']};
            border-color: {colors['border_hover']};
            box-shadow: 0 4px 8px {colors['shadow']};
        }}
        
        /* Ghost buttons */
        QPushButton[class="ghost"] {{
            background-color: transparent;
            color: {colors['text_secondary']};
            border: 1px solid {colors['border']};
        }}
        
        QPushButton[class="ghost"]:hover {{
            background-color: {colors['bg_hover']};
            color: {colors['text_primary']};
            border-color: {colors['accent']};
        }}
        
        /* Input fields - Modern */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 12px;
            padding: 12px 16px;
            selection-background-color: {colors['accent']};
            font-size: 14px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {colors['border_focus']};
            border-width: 2px;
            outline: none;
            box-shadow: 0 0 0 3px {colors['accent_light']};
        }}
        
        QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
            border-color: {colors['border_hover']};
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
        
        /* Group boxes - Modern */
        QGroupBox {{
            color: {colors['text_primary']};
            border: 1px solid {colors['border_light']};
            border-radius: 16px;
            margin-top: 16px;
            padding-top: 16px;
            background-color: {colors['bg_elevated']};
            font-weight: 600;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 12px 0 12px;
            background-color: {colors['bg_primary']};
            color: {colors['text_accent']};
            font-size: 14px;
            font-weight: 700;
        }}
        
        /* Labels - Modern Typography */
        QLabel {{
            color: {colors['text_primary']};
            font-size: 14px;
        }}
        
        QLabel[class="title"] {{
            font-size: 24px;
            font-weight: 700;
            color: {colors['text_primary']};
            letter-spacing: -0.5px;
        }}
        
        QLabel[class="subtitle"] {{
            font-size: 18px;
            font-weight: 600;
            color: {colors['text_secondary']};
            letter-spacing: -0.25px;
        }}
        
        QLabel[class="caption"] {{
            font-size: 12px;
            font-weight: 500;
            color: {colors['text_tertiary']};
            letter-spacing: 0.25px;
        }}
        
        QLabel[class="heading"] {{
            font-size: 16px;
            font-weight: 600;
            color: {colors['text_primary']};
        }}
        
        QLabel[class="body"] {{
            font-size: 14px;
            font-weight: 400;
            color: {colors['text_secondary']};
            line-height: 1.5;
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
