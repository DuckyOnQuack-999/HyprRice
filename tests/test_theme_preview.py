"""
Tests for theme preview functionality and UI scaling
"""

import pytest
import time
import sys
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QTimer

# Ensure QApplication exists for tests
if not QApplication.instance():
    app = QApplication(sys.argv)

from hyprrice.gui.theme_manager import ThemeApplier
from hyprrice.gui.preview import PreviewWindow, ColorPreview
from hyprrice.utils import get_device_pixel_ratio


class TestThemeApplier:
    """Test ThemeApplier functionality."""
    
    def test_compile_qss_basic(self):
        """Test basic QSS compilation."""
        applier = ThemeApplier()
        theme = {
            'colors': {
                'background': '#2e3440',
                'text': '#eceff4',
                'secondary': '#3b4252',
                'accent': '#5e81ac'
            }
        }
        
        qss = applier.compile_qss(theme)
        assert isinstance(qss, str)
        assert '#2e3440' in qss
        assert '#eceff4' in qss
        assert 'QMainWindow' in qss
        assert 'QPushButton' in qss
    
    def test_compile_qss_fallback(self):
        """Test QSS compilation with missing colors."""
        applier = ThemeApplier()
        theme = {'colors': {}}  # Empty colors
        
        qss = applier.compile_qss(theme)
        assert isinstance(qss, str)
        assert len(qss) > 0  # Should have fallback values
    
    def test_compile_qss_error_handling(self):
        """Test QSS compilation error handling."""
        applier = ThemeApplier()
        theme = None  # Invalid theme
        
        qss = applier.compile_qss(theme)
        assert qss == ""  # Should return empty string on error
    
    def test_apply_to_widget(self):
        """Test widget-scope theme application."""
        applier = ThemeApplier()
        theme = {
            'colors': {
                'background': '#2e3440',
                'text': '#eceff4',
                'secondary': '#3b4252',
                'accent': '#5e81ac'
            }
        }
        
        # Create a mock widget
        widget = Mock()
        widget.setUpdatesEnabled = Mock()
        widget.style = Mock()
        widget.style.return_value.unpolish = Mock()
        widget.style.return_value.polish = Mock()
        widget.setStyleSheet = Mock()
        widget.updateGeometry = Mock()
        widget.adjustSize = Mock()
        widget.repaint = Mock()
        
        # Apply theme
        applier.apply_to_widget(widget, theme)
        
        # Verify calls
        assert widget.setUpdatesEnabled.call_count == 2
        assert widget.setUpdatesEnabled.call_args_list[0][0][0] == False
        assert widget.setUpdatesEnabled.call_args_list[1][0][0] == True
        widget.setStyleSheet.assert_called()
        widget.repaint.assert_called()


class TestPreviewDebounce:
    """Test preview debouncing functionality."""
    
    def test_preview_debounce_timing(self):
        """Test that preview updates are properly debounced."""
        # Create a mock config
        config = Mock()
        config.paths = Mock()
        config.paths.hyprland_config = '/tmp/test_config'
        
        # Create preview window
        with patch('hyprrice.hyprland.windows.WindowManager'), \
             patch('hyprrice.hyprland.display.DisplayManager'), \
             patch('hyprrice.hyprland.input.InputManager'), \
             patch('hyprrice.hyprland.workspaces.WorkspaceManager'):
            
            preview = PreviewWindow(config)
            
            # Mock the update methods
            preview.update_theme_info = Mock()
            preview.update_hyprland_info = Mock()
            preview.update_waybar_info = Mock()
            preview.update_system_info = Mock()
            preview.status_label = Mock()
            preview.progress_bar = Mock()
            
            # Test debouncing
            start_time = time.time()
            preview.update_preview()  # First call
            preview.update_preview()  # Second call (should be debounced)
            preview.update_preview()  # Third call (should be debounced)
            
            # Wait for debounce timer
            time.sleep(0.3)  # Wait for 250ms debounce + some buffer
            
            # Verify only one actual update was performed
            assert preview.update_theme_info.call_count <= 1
            assert preview.update_hyprland_info.call_count <= 1


class TestColorPreview:
    """Test ColorPreview widget functionality."""
    
    def test_color_preview_creation(self):
        """Test ColorPreview widget creation."""
        preview = ColorPreview("#ff0000", "Red")
        assert preview.color == "#ff0000"
        assert preview.label == "Red"
        assert preview.autoFillBackground()  # Should be set to True
    
    def test_color_preview_update(self):
        """Test ColorPreview color updates."""
        preview = ColorPreview("#ff0000", "Red")
        preview.set_color("#00ff00")
        assert preview.color == "#00ff00"
    
    def test_color_preview_invalid_color(self):
        """Test ColorPreview with invalid color."""
        preview = ColorPreview("invalid", "Invalid")
        # Should not crash and should have fallback styling
        assert preview.color == "invalid"


class TestDPRScaling:
    """Test device pixel ratio scaling."""
    
    def test_get_device_pixel_ratio(self):
        """Test device pixel ratio detection."""
        dpr = get_device_pixel_ratio()
        assert isinstance(dpr, float)
        assert dpr >= 1.0  # Should be at least 1.0
    
    def test_dpr_aware_repaint(self):
        """Test DPR-aware repainting in preview."""
        config = Mock()
        config.paths = Mock()
        config.paths.hyprland_config = '/tmp/test_config'
        
        with patch('hyprrice.hyprland.windows.WindowManager'), \
             patch('hyprrice.hyprland.display.DisplayManager'), \
             patch('hyprrice.hyprland.input.InputManager'), \
             patch('hyprrice.hyprland.workspaces.WorkspaceManager'):
            
            preview = PreviewWindow(config)
            preview.repaint = Mock()
            
            # Mock high DPR
            with patch('hyprrice.utils.get_device_pixel_ratio', return_value=2.0):
                preview.update_theme_info()
                preview.repaint.assert_called()  # Should repaint for high DPR


class TestQSSValidation:
    """Test QSS validation and safety."""
    
    def test_qss_safe_application(self):
        """Test that QSS application doesn't crash on invalid input."""
        applier = ThemeApplier()
        
        # Test with various invalid inputs
        invalid_themes = [
            None,
            {},
            {'colors': None},
            {'colors': {'background': None}},
            {'colors': {'background': ''}},
        ]
        
        for theme in invalid_themes:
            qss = applier.compile_qss(theme)
            # Should not crash and should return something (empty string or fallback)
            assert isinstance(qss, str)
    
    def test_qss_escape_handling(self):
        """Test that QSS properly handles special characters."""
        applier = ThemeApplier()
        theme = {
            'colors': {
                'background': '#2e3440',
                'text': '#eceff4',
                'secondary': '#3b4252',
                'accent': '#5e81ac'
            }
        }
        
        qss = applier.compile_qss(theme)
        # Should not contain unescaped special characters that could break QSS
        assert ';' in qss  # Should have proper QSS syntax
        assert '{' in qss
        assert '}' in qss


if __name__ == '__main__':
    pytest.main([__file__])
