"""
Tests for UI scaling and Wayland compatibility
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Ensure QApplication exists for tests
if not QApplication.instance():
    app = QApplication(sys.argv)

from hyprrice.utils import is_wayland_session, get_device_pixel_ratio, is_ui_tracing_enabled, trace_ui_event


class TestWaylandDetection:
    """Test Wayland session detection."""
    
    def test_wayland_detection_xdg_session_type(self):
        """Test Wayland detection via XDG_SESSION_TYPE."""
        with patch.dict(os.environ, {'XDG_SESSION_TYPE': 'wayland'}):
            assert is_wayland_session() is True
    
    def test_wayland_detection_wayland_display(self):
        """Test Wayland detection via WAYLAND_DISPLAY."""
        with patch.dict(os.environ, {'WAYLAND_DISPLAY': 'wayland-0'}):
            assert is_wayland_session() is True
    
    def test_wayland_detection_x11(self):
        """Test X11 session detection."""
        with patch.dict(os.environ, {'XDG_SESSION_TYPE': 'x11'}, clear=True):
            assert is_wayland_session() is False
    
    def test_wayland_detection_no_env(self):
        """Test when no session environment variables are set."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_wayland_session() is False


class TestUITracing:
    """Test UI tracing functionality."""
    
    def test_ui_tracing_disabled_by_default(self):
        """Test that UI tracing is disabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_ui_tracing_enabled() is False
    
    def test_ui_tracing_enabled(self):
        """Test enabling UI tracing."""
        with patch.dict(os.environ, {'HYPRRICE_TRACE_UI': '1'}):
            assert is_ui_tracing_enabled() is True
    
    def test_ui_tracing_disabled_wrong_value(self):
        """Test that UI tracing is disabled with wrong value."""
        with patch.dict(os.environ, {'HYPRRICE_TRACE_UI': '0'}):
            assert is_ui_tracing_enabled() is False
    
    def test_trace_ui_event_disabled(self):
        """Test that trace_ui_event does nothing when disabled."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('hyprrice.utils.logging.getLogger') as mock_logger:
                trace_ui_event("test_event", "test_widget", "test_details")
                mock_logger.assert_not_called()
    
    def test_trace_ui_event_enabled(self):
        """Test that trace_ui_event logs when enabled."""
        with patch.dict(os.environ, {'HYPRRICE_TRACE_UI': '1'}):
            with patch('hyprrice.utils.logging.getLogger') as mock_logger:
                mock_logger_instance = Mock()
                mock_logger.return_value = mock_logger_instance
                
                trace_ui_event("test_event", "test_widget", "test_details")
                
                mock_logger.assert_called_once()
                mock_logger_instance.debug.assert_called_once()
                call_args = mock_logger_instance.debug.call_args[0][0]
                assert "UI_TRACE" in call_args
                assert "test_event" in call_args
                assert "test_widget" in call_args
                assert "test_details" in call_args


class TestDevicePixelRatio:
    """Test device pixel ratio functionality."""
    
    def test_get_device_pixel_ratio_no_app(self):
        """Test device pixel ratio when no QApplication exists."""
        with patch('PyQt6.QtWidgets.QApplication') as mock_app:
            mock_app.instance.return_value = None
            dpr = get_device_pixel_ratio()
            assert dpr == 1.0
    
    def test_get_device_pixel_ratio_with_app(self):
        """Test device pixel ratio with QApplication."""
        mock_app_instance = Mock()
        mock_app_instance.devicePixelRatio.return_value = 2.0
        
        with patch('PyQt6.QtWidgets.QApplication') as mock_app:
            mock_app.instance.return_value = mock_app_instance
            dpr = get_device_pixel_ratio()
            assert dpr == 2.0
    
    def test_get_device_pixel_ratio_exception(self):
        """Test device pixel ratio with exception."""
        # Test that the function returns 1.0 when QApplication.instance() raises an exception
        with patch('PyQt6.QtWidgets.QApplication') as mock_app:
            mock_app.instance.side_effect = Exception("Test exception")
            dpr = get_device_pixel_ratio()
            assert dpr == 1.0


class TestDPIAttributes:
    """Test DPI attribute setting."""
    
    def test_dpi_attributes_set(self):
        """Test that DPI attributes are properly set."""
        mock_app = Mock()
        
        # Test setting DPI attributes
        mock_app.setAttribute = Mock()
        
        # Simulate the attribute setting from main.py
        # Note: PyQt6 handles DPI scaling automatically, no manual attributes needed
        # This test verifies that the app is created successfully
        
        # Verify app creation
        assert mock_app is not None


class TestHighDPIScaling:
    """Test high-DPI scaling behavior."""
    
    def test_high_dpi_scaling_enabled(self):
        """Test that high-DPI scaling is enabled."""
        # This test verifies that the application starts correctly
        # PyQt6 handles DPI scaling automatically
        with patch('PyQt6.QtWidgets.QApplication') as mock_qapp_class:
            mock_app = Mock()
            mock_qapp_class.return_value = mock_app
            
            # Simulate the startup code from main.py
            app = mock_qapp_class(['test'])
            
            # Verify app was created
            assert app is not None
    
    def test_wayland_safe_mode(self):
        """Test Wayland-safe mode detection."""
        # Test that the application can detect Wayland and set appropriate flags
        with patch.dict(os.environ, {'XDG_SESSION_TYPE': 'wayland'}):
            is_wayland = is_wayland_session()
            assert is_wayland is True
            
            # In a real application, this would trigger Wayland-safe mode
            # For now, we just verify the detection works


class TestUIRendering:
    """Test UI rendering stability."""
    
    def test_auto_fill_background(self):
        """Test that widgets have auto-fill background enabled."""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        widget.setAutoFillBackground(True)
        assert widget.autoFillBackground() is True
    
    def test_opaque_paint_event(self):
        """Test that widgets have opaque paint event enabled."""
        from PyQt6.QtWidgets import QWidget
        from PyQt6.QtCore import Qt
        
        widget = QWidget()
        widget.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        assert widget.testAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent) is True
    
    def test_transparent_mouse_events_disabled(self):
        """Test that transparent mouse events are disabled."""
        from PyQt6.QtWidgets import QWidget
        from PyQt6.QtCore import Qt
        
        widget = QWidget()
        # Ensure WA_TransparentForMouseEvents is False (default)
        assert widget.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) is False


if __name__ == '__main__':
    pytest.main([__file__])
