from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt5.QtGui import QColor, QPalette

class PreviewWindow(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("Live Preview")
        self.layout = QVBoxLayout(self)
        self.theme_label = QLabel(f"Theme: {getattr(self.config, 'theme', 'N/A')}")
        self.layout.addWidget(self.theme_label)
        self.preview_frame = QFrame()
        self.preview_frame.setFixedHeight(120)
        self.layout.addWidget(self.preview_frame)
        self.update_preview()

    def update_preview(self):
        # Example: Set background color to match Waybar background
        color = getattr(self.config.waybar, 'background_color', '#222222')
        palette = self.preview_frame.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.preview_frame.setAutoFillBackground(True)
        self.preview_frame.setPalette(palette)
        self.theme_label.setText(f"Theme: {getattr(self.config, 'theme', 'N/A')}") 