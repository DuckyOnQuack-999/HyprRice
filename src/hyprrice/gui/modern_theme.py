"""
Modern theme system for HyprRice with dark/light modes and system accent colors.
"""

import os
import subprocess
import json
import re
from typing import Dict, Any, Optional
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtWidgets import QApplication


class ModernTheme(QObject):
    """Modern theme system with dark/light modes and system accent colors."""
    
    theme_changed = pyqtSignal(str)  # Emitted when theme changes
    
    def __init__(self):
        super().__init__()
        self.current_theme = "auto"
        self.system_accent_color = self._detect_system_accent_color()
        self.themes = {
            "dark": self._get_modern_dark_theme(),
            "light": self._get_greyish_light_theme(),
            "auto": None  # Will be determined dynamically
        }
    
    def _detect_system_accent_color(self) -> str:
        """Detect system accent color from various desktop environments."""
        try:
            # Try KDE/Plasma first
            kde_config = Path.home() / ".config" / "kdeglobals"
            if kde_config.exists():
                with open(kde_config, 'r') as f:
                    content = f.read()
                    # Look for accent color in KDE config
                    accent_match = re.search(r'AccentColor=(\d+,\d+,\d+)', content)
                    if accent_match:
                        r, g, b = map(int, accent_match.group(1).split(','))
                        return f"#{r:02x}{g:02x}{b:02x}"
            
            # Try GTK theme
            gtk_config = Path.home() / ".config" / "gtk-3.0" / "settings.ini"
            if gtk_config.exists():
                with open(gtk_config, 'r') as f:
                    content = f.read()
                    # Look for accent color in GTK config
                    accent_match = re.search(r'accent_color=([^;]+)', content)
                    if accent_match:
                        return accent_match.group(1)
            
            # Try GNOME settings
            try:
                result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'accent-color'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and result.stdout.strip() != "'default'":
                    color = result.stdout.strip().strip("'")
                    if color.startswith('#'):
                        return color
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Try XFCE
            xfce_config = Path.home() / ".config" / "xfce4" / "xfconf" / "xfce-perchannel-xml" / "xsettings.xml"
            if xfce_config.exists():
                with open(xfce_config, 'r') as f:
                    content = f.read()
                    # Look for accent color in XFCE config
                    accent_match = re.search(r'<property name="AccentColor" type="string" value="([^"]+)"', content)
                    if accent_match:
                        return accent_match.group(1)
            
            # Try system environment variables
            accent_env = os.environ.get('HYPRRICE_ACCENT_COLOR')
            if accent_env and accent_env.startswith('#'):
                return accent_env
            
            # Default modern accent color
            return "#6366f1"  # Modern indigo
            
        except Exception:
            # Fallback to default
            return "#6366f1"  # Modern indigo
    
    def _get_modern_dark_theme(self) -> Dict[str, str]:
        """Get modern dark theme colors with system accent."""
        accent = self.system_accent_color
        
        return {
            # Base colors - modern dark with proper contrast
            "bg_primary": "#0f0f0f",      # Deep black
            "bg_secondary": "#1a1a1a",    # Slightly lighter
            "bg_tertiary": "#262626",     # Card backgrounds
            "bg_hover": "#333333",        # Hover states
            "bg_pressed": "#404040",      # Pressed states
            "bg_elevated": "#1f1f1f",     # Elevated surfaces
            
            # Text colors - high contrast for accessibility
            "text_primary": "#ffffff",    # Primary text
            "text_secondary": "#e5e5e5",  # Secondary text
            "text_tertiary": "#a3a3a3",   # Tertiary text
            "text_disabled": "#737373",   # Disabled text
            "text_accent": accent,        # Accent text
            
            # Accent colors - system-based
            "accent": accent,
            "accent_hover": self._lighten_color(accent, 0.2),
            "accent_pressed": self._darken_color(accent, 0.2),
            "accent_light": self._lighten_color(accent, 0.8),
            
            # Status colors - modern and accessible
            "success": "#10b981",         # Emerald
            "warning": "#f59e0b",         # Amber
            "error": "#ef4444",           # Red
            "info": "#3b82f6",            # Blue
            
            # Border colors - subtle but defined
            "border": "#404040",          # Default borders
            "border_light": "#262626",    # Light borders
            "border_focus": accent,       # Focus borders
            "border_hover": "#525252",    # Hover borders
            
            # Shadow colors - deep and modern
            "shadow": "rgba(0, 0, 0, 0.5)",
            "shadow_hover": "rgba(0, 0, 0, 0.6)",
            "shadow_light": "rgba(0, 0, 0, 0.3)",
            
            # Glass effect colors
            "glass_bg": "rgba(26, 26, 26, 0.9)",
            "glass_border": "rgba(255, 255, 255, 0.1)",
        }
    
    def _get_greyish_light_theme(self) -> Dict[str, str]:
        """Get greyish light theme colors with system accent."""
        accent = self.system_accent_color
        
        return {
            # Base colors - greyish instead of bright white
            "bg_primary": "#f5f5f5",      # Light grey background
            "bg_secondary": "#e8e8e8",    # Slightly darker grey
            "bg_tertiary": "#d4d4d4",     # Card backgrounds
            "bg_hover": "#c7c7c7",        # Hover states
            "bg_pressed": "#b8b8b8",      # Pressed states
            "bg_elevated": "#f0f0f0",     # Elevated surfaces
            
            # Text colors - dark on light
            "text_primary": "#1a1a1a",    # Primary text
            "text_secondary": "#404040",  # Secondary text
            "text_tertiary": "#666666",   # Tertiary text
            "text_disabled": "#999999",   # Disabled text
            "text_accent": accent,        # Accent text
            
            # Accent colors - system-based
            "accent": accent,
            "accent_hover": self._darken_color(accent, 0.1),
            "accent_pressed": self._darken_color(accent, 0.2),
            "accent_light": self._lighten_color(accent, 0.9),
            
            # Status colors - accessible on light background
            "success": "#059669",         # Darker emerald
            "warning": "#d97706",         # Darker amber
            "error": "#dc2626",           # Darker red
            "info": "#2563eb",            # Darker blue
            
            # Border colors - subtle but defined
            "border": "#d4d4d4",          # Default borders
            "border_light": "#e5e5e5",    # Light borders
            "border_focus": accent,       # Focus borders
            "border_hover": "#a3a3a3",    # Hover borders
            
            # Shadow colors - light shadows
            "shadow": "rgba(0, 0, 0, 0.1)",
            "shadow_hover": "rgba(0, 0, 0, 0.15)",
            "shadow_light": "rgba(0, 0, 0, 0.05)",
            
            # Glass effect colors
            "glass_bg": "rgba(232, 232, 232, 0.9)",
            "glass_border": "rgba(0, 0, 0, 0.1)",
        }
    
    def _lighten_color(self, color: str, factor: float) -> str:
        """Lighten a hex color by a factor (0-1)."""
        if not color.startswith('#'):
            return color
        
        try:
            # Remove # and convert to RGB
            hex_color = color[1:]
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Lighten by factor
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return color
    
    def _darken_color(self, color: str, factor: float) -> str:
        """Darken a hex color by a factor (0-1)."""
        if not color.startswith('#'):
            return color
        
        try:
            # Remove # and convert to RGB
            hex_color = color[1:]
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Darken by factor
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return color
    
    def set_accent_color(self, color: str):
        """Set the accent color for the current theme."""
        self.system_accent_color = color
        # Update themes with new accent color
        self.themes["dark"] = self._get_modern_dark_theme()
        self.themes["light"] = self._get_greyish_light_theme()
        self.theme_changed.emit(self.current_theme)
    
    def set_theme(self, theme: str):
        """Set the current theme."""
        if theme == "auto":
            theme = self._detect_system_theme()
        
        if theme in self.themes:
            self.current_theme = theme
            self.theme_changed.emit(theme)
    
    def _detect_system_theme(self) -> str:
        """Detect system theme preference from various sources."""
        try:
            # Try GNOME settings first
            try:
                result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    scheme = result.stdout.strip().strip("'")
                    if 'dark' in scheme.lower():
                        return "dark"
                    elif 'light' in scheme.lower():
                        return "light"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Try KDE/Plasma
            kde_config = Path.home() / ".config" / "kdeglobals"
            if kde_config.exists():
                with open(kde_config, 'r') as f:
                    content = f.read()
                    if 'ColorScheme=Dark' in content or 'ColorScheme=BreezeDark' in content:
                        return "dark"
                    elif 'ColorScheme=Light' in content or 'ColorScheme=BreezeLight' in content:
                        return "light"
            
            # Try GTK theme
            gtk_theme = os.environ.get("GTK_THEME", "").lower()
            if "dark" in gtk_theme:
                return "dark"
            elif "light" in gtk_theme:
                return "light"
            
            # Check for common dark theme indicators
            color_scheme = os.environ.get("COLORFGBG", "")
            if color_scheme and color_scheme.startswith("15;"):  # Dark background
                return "dark"
            elif color_scheme and color_scheme.startswith("0;"):  # Light background
                return "light"
            
            # Try XFCE
            xfce_config = Path.home() / ".config" / "xfce4" / "xfconf" / "xfce-perchannel-xml" / "xsettings.xml"
            if xfce_config.exists():
                with open(xfce_config, 'r') as f:
                    content = f.read()
                    if 'Dark' in content:
                        return "dark"
                    elif 'Light' in content:
                        return "light"
            
            # Check system environment
            theme_env = os.environ.get('HYPRRICE_THEME')
            if theme_env in ['dark', 'light']:
                return theme_env
            
            # Default to dark theme for modern look
            return "dark"
            
        except Exception:
            # Fallback to dark theme
            return "dark"
    
    def get_current_colors(self) -> Dict[str, str]:
        """Get colors for the current theme."""
        if self.current_theme == "auto":
            theme = self._detect_system_theme()
        else:
            theme = self.current_theme
        
        return self.themes.get(theme, self.themes["dark"])
    
    def get_available_themes(self) -> list:
        """Get list of available themes."""
        return ["auto", "dark", "light"]
    
    def get_current_theme(self) -> str:
        """Get the current theme name."""
        return self.current_theme
    
    def get_system_accent_color(self) -> str:
        """Get the detected system accent color."""
        return self.system_accent_color
    
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
            /* removed unsupported backdrop-filter */
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
            /* removed unsupported box-shadow */
        }}
        
        QPushButton:hover {{
            background-color: {colors['accent_hover']};
            /* removed unsupported box-shadow/transform */
        }}
        
        QPushButton:pressed {{
            background-color: {colors['accent_pressed']};
            /* removed unsupported box-shadow/transform */
        }}
        
        QPushButton:disabled {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_disabled']};
            /* removed unsupported box-shadow */
        }}
        
        /* Secondary buttons */
        QPushButton[class="secondary"] {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            /* removed unsupported box-shadow */
        }}
        
        QPushButton[class="secondary"]:hover {{
            background-color: {colors['bg_hover']};
            border-color: {colors['border_hover']};
            /* removed unsupported box-shadow */
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
            /* removed unsupported box-shadow */
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
