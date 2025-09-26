"""
Tests for ThemeManager functionality
"""

import unittest
import tempfile
import os
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.hyprrice.gui.theme_manager import ThemeManager
from src.hyprrice.config import Config


class TestThemeManager(unittest.TestCase):
    """Test ThemeManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.theme_manager = ThemeManager(self.temp_dir)
        self.config = Config()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_list_themes(self):
        """Test listing themes."""
        themes = self.theme_manager.list_themes()
        
        self.assertIsInstance(themes, list)
        # Should have default themes
        self.assertIn('minimal', themes)
        self.assertIn('cyberpunk', themes)
        self.assertIn('pastel', themes)
    
    def test_get_theme_info(self):
        """Test getting theme information."""
        info = self.theme_manager.get_theme_info('minimal')
        
        self.assertIsInstance(info, dict)
        self.assertIn('name', info)
        self.assertIn('description', info)
        self.assertIn('colors', info)
    
    def test_apply_theme(self):
        """Test applying a theme."""
        with patch.object(self.config, 'save') as mock_save:
            result = self.theme_manager.apply_theme('minimal', self.config)
            
            self.assertTrue(result)
            mock_save.assert_called_once()
    
    def test_preview_theme(self):
        """Test previewing a theme."""
        result = self.theme_manager.preview_theme('minimal', self.config)
        
        self.assertTrue(result)
    
    def test_save_theme(self):
        """Test saving a theme."""
        result = self.theme_manager.save_theme('test_theme', self.config, 'Test theme')
        
        self.assertTrue(result)
        
        # Check if theme file was created
        theme_path = Path(self.temp_dir) / "test_theme.hyprrice"
        self.assertTrue(theme_path.exists())
    
    def test_load_theme(self):
        """Test loading a theme."""
        # Create a theme first
        self.theme_manager.save_theme('test_theme', self.config, 'Test theme')
        
        # Load the theme
        theme_data = self.theme_manager.load_theme('test_theme')
        
        self.assertIsInstance(theme_data, dict)
        self.assertIn('name', theme_data)
    
    def test_delete_theme(self):
        """Test deleting a theme."""
        # Create a theme first
        self.theme_manager.save_theme('test_theme', self.config, 'Test theme')
        
        # Delete the theme
        result = self.theme_manager.delete_theme('test_theme')
        
        self.assertTrue(result)
        
        # Check if theme file was deleted
        theme_path = Path(self.temp_dir) / "test_theme.hyprrice"
        self.assertFalse(theme_path.exists())
    
    def test_get_custom_themes(self):
        """Test getting custom themes."""
        # Create a custom theme
        self.theme_manager.save_theme('custom_theme', self.config, 'Custom theme')
        
        custom_themes = self.theme_manager.get_custom_themes()
        
        self.assertIn('custom_theme', custom_themes)
        self.assertNotIn('minimal', custom_themes)  # Default theme
    
    def test_get_theme_preview(self):
        """Test getting theme preview."""
        preview = self.theme_manager.get_theme_preview('minimal')
        
        self.assertIsInstance(preview, str)
        self.assertIn('Theme:', preview)
        self.assertIn('Description:', preview)
    
    def test_import_theme(self):
        """Test importing a theme."""
        # Create a temporary theme file
        theme_data = {
            'name': 'Imported Theme',
            'description': 'An imported theme',
            'version': '1.0.0',
            'colors': {
                'primary': '#ff0000',
                'secondary': '#00ff00'
            }
        }
        
        temp_file = os.path.join(self.temp_dir, 'imported_theme.yaml')
        with open(temp_file, 'w') as f:
            yaml.dump(theme_data, f)
        
        # Import the theme
        result = self.theme_manager.import_theme(temp_file)
        
        self.assertTrue(result)
        
        # Check if theme was imported
        themes = self.theme_manager.list_themes()
        self.assertIn('imported_theme', themes)
    
    def test_export_theme(self):
        """Test exporting a theme."""
        # Create a theme first
        self.theme_manager.save_theme('export_theme', self.config, 'Export theme')
        
        # Export the theme
        export_path = os.path.join(self.temp_dir, 'exported_theme.yaml')
        result = self.theme_manager.export_theme('export_theme', export_path)
        
        self.assertTrue(result)
        
        # Check if export file was created
        self.assertTrue(os.path.exists(export_path))
    
    def test_validate_theme_data(self):
        """Test theme data validation."""
        # Valid theme data
        valid_theme = {
            'name': 'Valid Theme',
            'version': '1.0.0',
            'colors': {
                'primary': '#ff0000'
            }
        }
        
        result = self.theme_manager._validate_theme_data(valid_theme)
        self.assertTrue(result)
        
        # Invalid theme data (missing name)
        invalid_theme = {
            'version': '1.0.0'
        }
        
        result = self.theme_manager._validate_theme_data(invalid_theme)
        self.assertFalse(result)
    
    def test_validate_theme_name(self):
        """Test theme name validation."""
        # Valid names
        self.assertTrue(self.theme_manager._validate_theme_name('valid_theme'))
        self.assertTrue(self.theme_manager._validate_theme_name('valid-theme'))
        self.assertTrue(self.theme_manager._validate_theme_name('validtheme123'))
        
        # Invalid names
        self.assertFalse(self.theme_manager._validate_theme_name(''))
        self.assertFalse(self.theme_manager._validate_theme_name('invalid theme'))
        self.assertFalse(self.theme_manager._validate_theme_name('invalid@theme'))
    
    def test_apply_theme_to_config(self):
        """Test applying theme data to configuration."""
        theme_data = {
            'hyprland': {
                'border_color': '#ff0000',
                'gaps_in': 10
            },
            'waybar': {
                'background_color': '#000000',
                'text_color': '#ffffff'
            }
        }
        
        # Apply theme
        self.theme_manager._apply_theme_to_config(theme_data, self.config)
        
        # Check if config was updated
        self.assertEqual(self.config.hyprland.border_color, '#ff0000')
        self.assertEqual(self.config.hyprland.gaps_in, 10)
        self.assertEqual(self.config.waybar.background_color, '#000000')
        self.assertEqual(self.config.waybar.text_color, '#ffffff')
    
    def test_create_theme_from_config(self):
        """Test creating theme data from configuration."""
        theme_data = self.theme_manager._create_theme_from_config(self.config, 'Test theme')
        
        self.assertIsInstance(theme_data, dict)
        self.assertEqual(theme_data['description'], 'Test theme')
        self.assertIn('general', theme_data)
        self.assertIn('hyprland', theme_data)
        self.assertIn('waybar', theme_data)
    
    def test_error_handling(self):
        """Test error handling in theme operations."""
        # Test with non-existent theme
        result = self.theme_manager.apply_theme('nonexistent', self.config)
        self.assertFalse(result)
        
        # Test with invalid theme data
        result = self.theme_manager._validate_theme_data({})
        self.assertFalse(result)
        
        # Test with invalid theme name
        result = self.theme_manager._validate_theme_name('')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
