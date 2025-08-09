from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QScrollArea, QGroupBox, QPushButton, QSplitter
)
from PyQt5.QtGui import QColor, QPalette, QFont, QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
import logging

class PreviewWindow(QWidget):
    """Enhanced live preview window with comprehensive theme visualization."""
    
    preview_updated = pyqtSignal()
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.setWindowTitle("HyprRice - Live Preview")
        self.setMinimumSize(800, 600)
        
        # Auto-update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.setSingleShot(True)
        
        self.setup_ui()
        self.update_preview()
    
    def setup_ui(self):
        """Setup the preview UI layout."""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        self.theme_label = QLabel(f"Theme: {getattr(self.config, 'theme', 'N/A')}")
        self.theme_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(self.theme_label)
        
        refresh_btn = QPushButton("Refresh Preview")
        refresh_btn.clicked.connect(self.update_preview)
        header_layout.addWidget(refresh_btn)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Main preview area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        preview_content = QWidget()
        preview_layout = QVBoxLayout(preview_content)
        
        # Waybar preview
        self.waybar_preview = WaybarPreview(self.config)
        preview_layout.addWidget(self.waybar_preview)
        
        # Desktop preview
        self.desktop_preview = DesktopPreview(self.config)
        preview_layout.addWidget(self.desktop_preview)
        
        # Rofi preview
        self.rofi_preview = RofiPreview(self.config)
        preview_layout.addWidget(self.rofi_preview)
        
        # Notification preview
        self.notification_preview = NotificationPreview(self.config)
        preview_layout.addWidget(self.notification_preview)
        
        # Clipboard preview
        self.clipboard_preview = ClipboardPreview(self.config)
        preview_layout.addWidget(self.clipboard_preview)
        
        # Lockscreen preview
        self.lockscreen_preview = LockscreenPreview(self.config)
        preview_layout.addWidget(self.lockscreen_preview)
        
        scroll_area.setWidget(preview_content)
        layout.addWidget(scroll_area)
    
    def update_preview(self):
        """Update all preview components."""
        try:
            self.theme_label.setText(f"Theme: {getattr(self.config, 'theme', 'N/A')}")
            
            # Update individual preview components
            self.waybar_preview.update_preview(self.config)
            self.desktop_preview.update_preview(self.config)
            self.rofi_preview.update_preview(self.config)
            self.notification_preview.update_preview(self.config)
            self.clipboard_preview.update_preview(self.config)
            self.lockscreen_preview.update_preview(self.config)
            
            self.preview_updated.emit()
            self.logger.debug("Preview updated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to update preview: {e}")
    
    def schedule_update(self):
        """Schedule a preview update with debouncing."""
        self.update_timer.start(200)  # 200ms delay


class WaybarPreview(QGroupBox):
    """Waybar preview component."""
    
    def __init__(self, config):
        super().__init__("Waybar Preview")
        self.setup_ui()
        self.update_preview(config)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.waybar_frame = QFrame()
        self.waybar_frame.setFixedHeight(40)
        self.waybar_frame.setFrameStyle(QFrame.StyledPanel)
        
        # Create mock waybar content
        waybar_layout = QHBoxLayout(self.waybar_frame)
        waybar_layout.setContentsMargins(10, 5, 10, 5)
        
        # Left modules
        self.left_modules = QLabel("  Workspaces")
        waybar_layout.addWidget(self.left_modules)
        
        waybar_layout.addStretch()
        
        # Center modules
        self.center_modules = QLabel("Clock: 12:34 PM")
        waybar_layout.addWidget(self.center_modules)
        
        waybar_layout.addStretch()
        
        # Right modules
        self.right_modules = QLabel("CPU: 45% | RAM: 60% | 󰂄")
        waybar_layout.addWidget(self.right_modules)
        
        layout.addWidget(self.waybar_frame)
    
    def update_preview(self, config):
        """Update waybar preview based on configuration."""
        try:
            # Apply background color
            bg_color = getattr(config.waybar, 'background_color', '#2e3440')
            text_color = getattr(config.waybar, 'text_color', '#ffffff')
            font_family = getattr(config.waybar, 'font_family', 'Arial')
            font_size = getattr(config.waybar, 'font_size', 12)
            
            # Set stylesheet
            stylesheet = f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 1px solid {getattr(config.waybar, 'border_color', '#5e81ac')};
                    border-radius: 5px;
                }}
                QLabel {{
                    color: {text_color};
                    font-family: {font_family};
                    font-size: {font_size}px;
                    padding: 2px 5px;
                }}
            """
            self.waybar_frame.setStyleSheet(stylesheet)
            
            # Update modules based on configuration
            modules = getattr(config.waybar, 'modules', ['workspaces', 'clock', 'cpu', 'memory'])
            self.left_modules.setText("  " + " | ".join(modules[:2]))
            self.right_modules.setText(" | ".join(modules[2:]) + " 󰂄")
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to update waybar preview: {e}")


class DesktopPreview(QGroupBox):
    """Desktop/window preview component."""
    
    def __init__(self, config):
        super().__init__("Desktop Preview")
        self.setup_ui()
        self.update_preview(config)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.desktop_frame = QFrame()
        self.desktop_frame.setFixedHeight(200)
        self.desktop_frame.setFrameStyle(QFrame.StyledPanel)
        
        # Create mock windows
        desktop_layout = QHBoxLayout(self.desktop_frame)
        desktop_layout.setSpacing(10)
        desktop_layout.setContentsMargins(10, 10, 10, 10)
        
        # Window 1
        self.window1 = QFrame()
        self.window1.setFixedSize(120, 80)
        self.window1.setFrameStyle(QFrame.StyledPanel)
        window1_layout = QVBoxLayout(self.window1)
        window1_layout.addWidget(QLabel("Terminal"))
        desktop_layout.addWidget(self.window1)
        
        # Window 2
        self.window2 = QFrame()
        self.window2.setFixedSize(120, 80)
        self.window2.setFrameStyle(QFrame.StyledPanel)
        window2_layout = QVBoxLayout(self.window2)
        window2_layout.addWidget(QLabel("Browser"))
        desktop_layout.addWidget(self.window2)
        
        desktop_layout.addStretch()
        layout.addWidget(self.desktop_frame)
    
    def update_preview(self, config):
        """Update desktop preview based on configuration."""
        try:
            # Apply window styling
            border_size = getattr(config.hyprland, 'border_size', 1)
            border_color = getattr(config.hyprland, 'border_color', '#ffffff')
            window_opacity = getattr(config.hyprland, 'window_opacity', 1.0)
            
            window_style = f"""
                QFrame {{
                    border: {border_size}px solid {border_color};
                    border-radius: 5px;
                    background-color: rgba(60, 60, 60, {int(window_opacity * 255)});
                }}
                QLabel {{
                    color: white;
                    text-align: center;
                    padding: 5px;
                }}
            """
            
            self.window1.setStyleSheet(window_style)
            self.window2.setStyleSheet(window_style)
            
            # Apply gaps
            gaps_out = getattr(config.hyprland, 'gaps_out', 10)
            gaps_in = getattr(config.hyprland, 'gaps_in', 5)
            
            desktop_layout = self.desktop_frame.layout()
            desktop_layout.setSpacing(gaps_in)
            desktop_layout.setContentsMargins(gaps_out, gaps_out, gaps_out, gaps_out)
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to update desktop preview: {e}")


class RofiPreview(QGroupBox):
    """Rofi launcher preview component."""
    
    def __init__(self, config):
        super().__init__("Rofi Preview")
        self.setup_ui()
        self.update_preview(config)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.rofi_frame = QFrame()
        self.rofi_frame.setFixedHeight(100)
        self.rofi_frame.setFrameStyle(QFrame.StyledPanel)
        
        rofi_layout = QVBoxLayout(self.rofi_frame)
        
        # Search input mockup
        self.search_input = QLabel("Type to search...")
        self.search_input.setAlignment(Qt.AlignCenter)
        rofi_layout.addWidget(self.search_input)
        
        # Results mockup
        self.results = QLabel("Firefox\nTerminal\nFile Manager")
        self.results.setAlignment(Qt.AlignCenter)
        rofi_layout.addWidget(self.results)
        
        layout.addWidget(self.rofi_frame)
    
    def update_preview(self, config):
        """Update rofi preview based on configuration."""
        try:
            bg_color = getattr(config.rofi, 'background_color', '#2e3440')
            text_color = getattr(config.rofi, 'text_color', '#eceff4')
            border_color = getattr(config.rofi, 'border_color', '#5e81ac')
            font_family = getattr(config.rofi, 'font_family', 'Arial')
            font_size = getattr(config.rofi, 'font_size', 12)
            
            stylesheet = f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 2px solid {border_color};
                    border-radius: 8px;
                }}
                QLabel {{
                    color: {text_color};
                    font-family: {font_family};
                    font-size: {font_size}px;
                    padding: 5px;
                }}
            """
            self.rofi_frame.setStyleSheet(stylesheet)
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to update rofi preview: {e}")


class NotificationPreview(QGroupBox):
    """Notification preview component."""
    
    def __init__(self, config):
        super().__init__("Notification Preview")
        self.setup_ui()
        self.update_preview(config)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.notification_frame = QFrame()
        self.notification_frame.setFixedHeight(80)
        self.notification_frame.setFrameStyle(QFrame.StyledPanel)
        
        notif_layout = QVBoxLayout(self.notification_frame)
        
        # Notification header
        self.notif_header = QLabel("HyprRice")
        self.notif_header.setFont(QFont("Arial", 10, QFont.Bold))
        notif_layout.addWidget(self.notif_header)
        
        # Notification body
        self.notif_body = QLabel("Configuration updated successfully!")
        notif_layout.addWidget(self.notif_body)
        
        layout.addWidget(self.notification_frame)
    
    def update_preview(self, config):
        """Update notification preview based on configuration."""
        try:
            bg_color = getattr(config.notifications, 'background_color', '#2e3440')
            text_color = getattr(config.notifications, 'text_color', '#eceff4')
            border_color = getattr(config.notifications, 'border_color', '#5e81ac')
            font_family = getattr(config.notifications, 'font_family', 'Arial')
            font_size = getattr(config.notifications, 'font_size', 12)
            
            stylesheet = f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 6px;
                }}
                QLabel {{
                    color: {text_color};
                    font-family: {font_family};
                    font-size: {font_size}px;
                    padding: 3px;
                }}
            """
            self.notification_frame.setStyleSheet(stylesheet)
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to update notification preview: {e}")


class ClipboardPreview(QGroupBox):
    """Clipboard manager preview component."""
    
    def __init__(self, config):
        super().__init__("Clipboard Preview")
        self.setup_ui()
        self.update_preview(config)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.clipboard_frame = QFrame()
        self.clipboard_frame.setFixedHeight(120)
        self.clipboard_frame.setFrameStyle(QFrame.StyledPanel)
        
        clipboard_layout = QVBoxLayout(self.clipboard_frame)
        
        # Manager info
        self.manager_label = QLabel("Clipboard Manager: cliphist")
        self.manager_label.setFont(QFont("Arial", 10, QFont.Bold))
        clipboard_layout.addWidget(self.manager_label)
        
        # History items mockup
        self.history_items = QLabel("Recent items:\n• Text copied at 12:30\n• Image copied at 12:25\n• Link copied at 12:20")
        clipboard_layout.addWidget(self.history_items)
        
        layout.addWidget(self.clipboard_frame)
    
    def update_preview(self, config):
        """Update clipboard preview based on configuration."""
        try:
            manager = getattr(config.clipboard, 'manager', 'cliphist')
            history_size = getattr(config.clipboard, 'history_size', 100)
            enable_images = getattr(config.clipboard, 'enable_images', True)
            
            self.manager_label.setText(f"Clipboard Manager: {manager}")
            
            items_text = f"Recent items (max {history_size}):\n• Text copied at 12:30\n"
            if enable_images:
                items_text += "• Image copied at 12:25\n"
            items_text += "• Link copied at 12:20"
            
            self.history_items.setText(items_text)
            
            # Basic styling
            stylesheet = """
                QFrame {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }
                QLabel {
                    color: #333;
                    padding: 3px;
                }
            """
            self.clipboard_frame.setStyleSheet(stylesheet)
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to update clipboard preview: {e}")


class LockscreenPreview(QGroupBox):
    """Lockscreen preview component."""
    
    def __init__(self, config):
        super().__init__("Lockscreen Preview")
        self.setup_ui()
        self.update_preview(config)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.lockscreen_frame = QFrame()
        self.lockscreen_frame.setFixedHeight(150)
        self.lockscreen_frame.setFrameStyle(QFrame.StyledPanel)
        
        lock_layout = QVBoxLayout(self.lockscreen_frame)
        lock_layout.setAlignment(Qt.AlignCenter)
        
        # Locker info
        self.locker_label = QLabel("Locker: hyprlock")
        self.locker_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.locker_label.setAlignment(Qt.AlignCenter)
        lock_layout.addWidget(self.locker_label)
        
        # User greeting
        self.greeting_label = QLabel("Hi there, $USER")
        self.greeting_label.setAlignment(Qt.AlignCenter)
        lock_layout.addWidget(self.greeting_label)
        
        # Input field mockup
        self.input_field = QFrame()
        self.input_field.setFixedSize(200, 30)
        self.input_field.setFrameStyle(QFrame.StyledPanel)
        input_layout = QHBoxLayout(self.input_field)
        input_layout.addWidget(QLabel("Password: ●●●●●"))
        lock_layout.addWidget(self.input_field)
        
        layout.addWidget(self.lockscreen_frame)
    
    def update_preview(self, config):
        """Update lockscreen preview based on configuration."""
        try:
            locker = getattr(config.lockscreen, 'locker', 'hyprlock')
            bg_color = getattr(config.lockscreen, 'background_color', '#000000')
            text_color = getattr(config.lockscreen, 'text_color', '#ffffff')
            font_family = getattr(config.lockscreen, 'font_family', 'Arial')
            font_size = getattr(config.lockscreen, 'font_size', 14)
            
            self.locker_label.setText(f"Locker: {locker}")
            
            # Apply styling
            stylesheet = f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 1px solid #555;
                    border-radius: 8px;
                }}
                QLabel {{
                    color: {text_color};
                    font-family: {font_family};
                    font-size: {font_size}px;
                    padding: 5px;
                }}
            """
            self.lockscreen_frame.setStyleSheet(stylesheet)
            
            # Input field styling
            input_style = f"""
                QFrame {{
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 2px solid {getattr(config.lockscreen, 'input_field_color', '#ffffff')};
                    border-radius: 4px;
                }}
                QLabel {{
                    color: {text_color};
                    font-size: {font_size - 2}px;
                }}
            """
            self.input_field.setStyleSheet(input_style)
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to update lockscreen preview: {e}") 