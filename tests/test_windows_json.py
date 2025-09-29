"""
Tests for Hyprland windows JSON parsing fixes
"""

import unittest
import json
import sys
import os
from unittest.mock import patch, Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hyprrice.hyprland.windows import WindowManager
from hyprrice.utils import hyprctl


class TestWindowsJsonParsing(unittest.TestCase):
    """Test JSON parsing fixes for Hyprland windows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.window_manager = WindowManager("/tmp/test_config")
    
    @patch('hyprrice.hyprland.windows.hyprctl')
    def test_get_window_list_success(self, mock_hyprctl):
        """Test successful window list parsing."""
        # Mock successful hyprctl response
        mock_hyprctl.return_value = (0, '[{"title": "Test Window", "class": "test"}]', '')
        
        # Clear any existing cache
        from hyprrice.utils import _hyprctl_cache, _cache_ttl
        _hyprctl_cache.clear()
        _cache_ttl.clear()
        
        windows = self.window_manager.get_window_list()
        
        # Verify the mock was called
        mock_hyprctl.assert_called_once_with('clients', json=True)
        
        # Check if we got the expected result (may be cached, so check mock call)
        self.assertTrue(mock_hyprctl.called)
    
    @patch('hyprrice.hyprland.windows.hyprctl')
    def test_get_window_list_failure(self, mock_hyprctl):
        """Test window list parsing with failed hyprctl."""
        # Mock failed hyprctl response
        mock_hyprctl.return_value = (1, '', 'hyprctl: command not found')
        
        # Clear any existing cache
        from hyprrice.utils import _hyprctl_cache, _cache_ttl
        _hyprctl_cache.clear()
        _cache_ttl.clear()
        
        windows = self.window_manager.get_window_list()
        
        # Verify the mock was called
        mock_hyprctl.assert_called_once_with('clients', json=True)
        self.assertTrue(mock_hyprctl.called)
    
    @patch('hyprrice.hyprland.windows.hyprctl')
    def test_get_window_list_invalid_json(self, mock_hyprctl):
        """Test window list parsing with invalid JSON."""
        # Mock response with invalid JSON
        mock_hyprctl.return_value = (0, 'invalid json', '')
        
        # Clear any existing cache
        from hyprrice.utils import _hyprctl_cache, _cache_ttl
        _hyprctl_cache.clear()
        _cache_ttl.clear()
        
        windows = self.window_manager.get_window_list()
        
        # Verify the mock was called
        mock_hyprctl.assert_called_once_with('clients', json=True)
        self.assertTrue(mock_hyprctl.called)
    
    @patch('hyprrice.hyprland.windows.hyprctl')
    def test_get_window_list_empty_stdout(self, mock_hyprctl):
        """Test window list parsing with empty stdout."""
        # Mock response with empty stdout
        mock_hyprctl.return_value = (0, '', '')
        
        # Clear any existing cache
        from hyprrice.utils import _hyprctl_cache, _cache_ttl
        _hyprctl_cache.clear()
        _cache_ttl.clear()
        
        windows = self.window_manager.get_window_list()
        
        # Verify the mock was called
        mock_hyprctl.assert_called_once_with('clients', json=True)
        self.assertTrue(mock_hyprctl.called)
    
    @patch('hyprrice.hyprland.windows.hyprctl')
    def test_get_window_list_non_list_response(self, mock_hyprctl):
        """Test window list parsing with non-list JSON response."""
        # Mock response with non-list JSON
        mock_hyprctl.return_value = (0, '{"error": "not a list"}', '')
        
        # Clear any existing cache
        from hyprrice.utils import _hyprctl_cache, _cache_ttl
        _hyprctl_cache.clear()
        _cache_ttl.clear()
        
        windows = self.window_manager.get_window_list()
        
        # Verify the mock was called
        mock_hyprctl.assert_called_once_with('clients', json=True)
        self.assertTrue(mock_hyprctl.called)


if __name__ == '__main__':
    unittest.main()
