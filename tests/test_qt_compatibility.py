"""
Tests for PyQt6 compatibility fixes
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QSplitter


class TestQtCompatibility(unittest.TestCase):
    """Test PyQt6 enum compatibility fixes."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
    
    def test_qt_user_role_enum(self):
        """Test that Qt.ItemDataRole.UserRole is accessible."""
        # This should not raise AttributeError
        role = Qt.ItemDataRole.UserRole
        self.assertIsNotNone(role)
    
    def test_qt_horizontal_enum(self):
        """Test that Qt.Orientation.Horizontal is accessible."""
        # This should not raise AttributeError
        orientation = Qt.Orientation.Horizontal
        self.assertIsNotNone(orientation)
    
    def test_list_widget_item_data_role(self):
        """Test that QListWidgetItem can use the new enum."""
        item = QListWidgetItem("Test Item")
        test_data = {"test": "data"}
        
        # Set data using new enum
        item.setData(Qt.ItemDataRole.UserRole, test_data)
        
        # Get data using new enum
        retrieved_data = item.data(Qt.ItemDataRole.UserRole)
        self.assertEqual(retrieved_data, test_data)
    
    def test_splitter_orientation(self):
        """Test that QSplitter can use the new enum."""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.assertEqual(splitter.orientation(), Qt.Orientation.Horizontal)


if __name__ == '__main__':
    unittest.main()
