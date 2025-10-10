"""
Modern sidebar navigation for HyprRice
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QScrollArea, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QIcon, QFont, QPainter, QColor, QLinearGradient
from typing import Dict, List, Optional


class ModernSidebar(QWidget):
    """Modern sidebar navigation with icons and smooth animations."""
    
    section_changed = pyqtSignal(str)  # Emitted when a section is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_section = "Hyprland"
        self.sections = {
            "Hyprland": {"icon": "🖥️", "description": "Core Hyprland settings"},
            "Waybar": {"icon": "📊", "description": "Status bar configuration"},
            "Rofi": {"icon": "🔍", "description": "Application launcher"},
            "Notifications": {"icon": "🔔", "description": "Notification daemon"},
            "Clipboard": {"icon": "📋", "description": "Clipboard manager"},
            "Lockscreen": {"icon": "🔒", "description": "Screen lock settings"},
            "Themes": {"icon": "🎨", "description": "Theme management"},
            "Settings": {"icon": "⚙️", "description": "General settings"},
            "Plugins": {"icon": "🔌", "description": "Plugin management"}
        }
        
        self.setup_ui()
        self.setup_styling()
    
    def setup_ui(self):
        """Setup the sidebar UI."""
        self.setFixedWidth(280)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Navigation buttons
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        nav_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        nav_scroll.setFrameStyle(QFrame.Shape.NoFrame)
        
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(20, 20, 20, 20)
        nav_layout.setSpacing(8)
        
        # Create navigation buttons
        self.nav_buttons = {}
        for section_name, section_data in self.sections.items():
            btn = self.create_nav_button(section_name, section_data)
            self.nav_buttons[section_name] = btn
            nav_layout.addWidget(btn)
        
        # Add spacer
        nav_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        nav_scroll.setWidget(nav_widget)
        layout.addWidget(nav_scroll)
        
        # Footer
        footer = self.create_footer()
        layout.addWidget(footer)
    
    def create_header(self) -> QWidget:
        """Create the sidebar header."""
        header = QFrame()
        header.setFixedHeight(80)
        header.setObjectName("sidebarHeader")
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # App title
        title = QLabel("HyprRice")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setObjectName("appTitle")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Hyprland Configuration Tool")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setObjectName("appSubtitle")
        layout.addWidget(subtitle)
        
        return header
    
    def create_nav_button(self, section_name: str, section_data: Dict) -> QPushButton:
        """Create a navigation button."""
        btn = QPushButton()
        btn.setObjectName(f"navButton_{section_name}")
        btn.setCheckable(True)
        btn.setFixedHeight(50)
        btn.setText(f"{section_data['icon']}  {section_name}")
        btn.setToolTip(section_data['description'])
        
        # Set initial state
        if section_name == self.current_section:
            btn.setChecked(True)
        
        # Connect signal
        btn.clicked.connect(lambda: self.select_section(section_name))
        
        return btn
    
    def create_footer(self) -> QWidget:
        """Create the sidebar footer."""
        footer = QFrame()
        footer.setFixedHeight(60)
        footer.setObjectName("sidebarFooter")
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Version info
        version = QLabel("v1.0.0")
        version.setFont(QFont("Arial", 9))
        version.setObjectName("versionLabel")
        layout.addWidget(version)
        
        layout.addStretch()
        
        # Status indicator
        status = QLabel("●")
        status.setObjectName("statusIndicator")
        status.setToolTip("Application status")
        layout.addWidget(status)
        
        return footer
    
    def setup_styling(self):
        """Setup the sidebar styling."""
        self.setStyleSheet("""
            ModernSidebar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2d3748, stop:1 #1a202c);
                border-right: 1px solid #4a5568;
            }
            
            #sidebarHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a5568, stop:1 #2d3748);
                border-bottom: 1px solid #4a5568;
            }
            
            #appTitle {
                color: #f7fafc;
                background: transparent;
            }
            
            #appSubtitle {
                color: #a0aec0;
                background: transparent;
            }
            
            #sidebarFooter {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2d3748, stop:1 #1a202c);
                border-top: 1px solid #4a5568;
            }
            
            #versionLabel {
                color: #a0aec0;
                background: transparent;
            }
            
            #statusIndicator {
                color: #48bb78;
                font-size: 12px;
                background: transparent;
            }
            
            QPushButton[class="navButton"] {
                background: transparent;
                border: none;
                text-align: left;
                padding: 12px 16px;
                color: #e2e8f0;
                font-size: 14px;
                font-weight: 500;
                border-radius: 8px;
            }
            
            QPushButton[class="navButton"]:hover {
                background: rgba(255, 255, 255, 0.1);
                color: #f7fafc;
            }
            
            QPushButton[class="navButton"]:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: #ffffff;
                font-weight: 600;
            }
            
            QPushButton[class="navButton"]:pressed {
                background: rgba(102, 126, 234, 0.8);
            }
            
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background: #4a5568;
                border-radius: 4px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #718096;
            }
        """)
    
    def select_section(self, section_name: str):
        """Select a navigation section."""
        if section_name == self.current_section:
            return
        
        # Update button states
        for name, btn in self.nav_buttons.items():
            btn.setChecked(name == section_name)
        
        self.current_section = section_name
        self.section_changed.emit(section_name)
    
    def get_current_section(self) -> str:
        """Get the currently selected section."""
        return self.current_section


class ModernContentArea(QWidget):
    """Modern content area that displays the selected section."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.content_widgets = {}
        self.current_widget = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the content area UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Content container
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        
        layout.addWidget(self.content_frame)
        
        # Setup styling
        self.setStyleSheet("""
            #contentFrame {
                background: #f7fafc;
                border-radius: 12px;
                margin: 10px;
            }
        """)
    
    def add_content_widget(self, section_name: str, widget: QWidget):
        """Add a content widget for a section."""
        self.content_widgets[section_name] = widget
        widget.hide()
        self.content_layout.addWidget(widget)
    
    def show_section(self, section_name: str):
        """Show the content for a specific section."""
        if self.current_widget:
            self.current_widget.hide()
        
        if section_name in self.content_widgets:
            self.current_widget = self.content_widgets[section_name]
            self.current_widget.show()
    
    def get_content_widget(self, section_name: str) -> Optional[QWidget]:
        """Get the content widget for a section."""
        return self.content_widgets.get(section_name)
