"""
Tests for theme security and validation.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import tempfile
import shutil
from pathlib import Path
import yaml
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hyprrice.gui.theme_manager import ThemeManager
from hyprrice.security import input_validator, SecureFileHandler
from hyprrice.exceptions import ValidationError, SecurityError


class TestThemeSecurity(unittest.TestCase):
    """Test theme security and validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
        
        self.theme_manager = ThemeManager(themes_dir=self.temp_dir)
        self.secure_handler = SecureFileHandler()
    
    def test_validate_theme_name_safe(self):
        """Test validating safe theme names."""
        safe_names = [
            "my-theme",
            "theme_1",
            "MyTheme",
            "theme-with-numbers-123",
            "a" * 50  # Long but valid
        ]
        
        for name in safe_names:
            result = input_validator.validate_theme_name(name)
            self.assertTrue(result)
    
    def test_validate_theme_name_unsafe(self):
        """Test validating unsafe theme names."""
        unsafe_names = [
            "../../../etc/passwd",
            "theme with spaces",
            "theme\nwith\nnewlines",
            "theme\twith\ttabs",
            "theme/with/slashes",
            "theme\\with\\backslashes",
            "theme|with|pipes",
            "theme&with&amps",
            "theme;with;semicolons",
            "theme`with`backticks",
            "theme$with$dollars",
            "theme(with)parens",
            "theme[with]brackets",
            "theme{with}braces",
            "theme*with*asterisks",
            "theme?with?questions",
            "theme<with>angles",
            "theme\"with\"quotes",
            "theme'with'apostrophes",
            "",  # Empty
            " " * 10,  # Only spaces
            "\x00",  # Null byte
            "theme\x01with\x02control",  # Control characters
        ]
        
        for name in unsafe_names:
            with self.assertRaises(ValidationError):
                input_validator.validate_theme_name(name)
    
    def test_validate_theme_data_safe(self):
        """Test validating safe theme data."""
        safe_theme = {
            "name": "safe-theme",
            "version": "1.0.0",
            "colors": {
                "background": "#2e3440",
                "foreground": "#d8dee9",
                "accent": "#5e81ac"
            },
            "hyprland": {
                "border_color": "#5e81ac",
                "gaps_in": 5,
                "gaps_out": 10
            },
            "tags": ["dark", "nord", "minimal"]
        }
        
        result = self.theme_manager._validate_theme_data(safe_theme)
        self.assertTrue(result)
    
    def test_validate_theme_data_unsafe(self):
        """Test validating unsafe theme data."""
        unsafe_themes = [
            # Missing required fields
            {"name": "incomplete"},
            {"version": "1.0.0"},
            
            # Invalid version format
            {"name": "test", "version": "invalid"},
            {"name": "test", "version": "1"},
            {"name": "test", "version": "1.0"},
            
            # Invalid colors
            {"name": "test", "version": "1.0.0", "colors": {"invalid": "not-a-color"}},
            {"name": "test", "version": "1.0.0", "colors": {"background": "../../../etc/passwd"}},
            
            # Invalid hyprland config
            {"name": "test", "version": "1.0.0", "hyprland": {"gaps_in": -1}},
            {"name": "test", "version": "1.0.0", "hyprland": {"gaps_in": "not-a-number"}},
            
            # Invalid tags
            {"name": "test", "version": "1.0.0", "tags": "not-a-list"},
            {"name": "test", "version": "1.0.0", "tags": [123, 456]},
            {"name": "test", "version": "1.0.0", "tags": ["tag\nwith\nnewline"]},
        ]
        
        for theme in unsafe_themes:
            result = self.theme_manager._validate_theme_data(theme)
            self.assertFalse(result)
    
    def test_import_theme_safe(self):
        """Test importing a safe theme."""
        safe_theme = {
            "name": "safe-theme",
            "version": "1.0.0",
            "colors": {
                "background": "#2e3440",
                "foreground": "#d8dee9"
            }
        }
        
        theme_file = Path(self.temp_dir) / "safe-theme.yaml"
        with open(theme_file, 'w') as f:
            yaml.dump(safe_theme, f)
        
        result = self.theme_manager.import_theme(str(theme_file))
        self.assertTrue(result)
    
    def test_import_theme_unsafe_path(self):
        """Test importing theme with unsafe path."""
        unsafe_paths = [
            "../../../etc/passwd",
            "/etc/passwd",
            "theme.yaml\nrm -rf /",
            "theme.yaml; rm -rf /",
            "theme.yaml|rm -rf /",
            "theme.yaml&rm -rf /",
        ]
        
        for path in unsafe_paths:
            with self.assertRaises((ValidationError, SecurityError)):
                self.theme_manager.import_theme(path)
    
    def test_import_theme_malicious_content(self):
        """Test importing theme with malicious content."""
        malicious_theme = {
            "name": "malicious-theme",
            "version": "1.0.0",
            "colors": {
                "background": "#2e3440",
                "foreground": "'; rm -rf /; echo '",
                "accent": "../../../etc/passwd"
            },
            "hyprland": {
                "border_color": "`rm -rf /`",
                "gaps_in": "eval('import os; os.system(\"rm -rf /\")')"
            }
        }
        
        theme_file = Path(self.temp_dir) / "malicious-theme.yaml"
        with open(theme_file, 'w') as f:
            yaml.dump(malicious_theme, f)
        
        # Should fail validation
        result = self.theme_manager.import_theme(str(theme_file))
        self.assertFalse(result)
    
    def test_export_theme_safe(self):
        """Test exporting a safe theme."""
        safe_theme = {
            "name": "safe-theme",
            "version": "1.0.0",
            "colors": {
                "background": "#2e3440",
                "foreground": "#d8dee9"
            }
        }
        
        export_file = Path(self.temp_dir) / "exported-theme.yaml"
        result = self.theme_manager.export_theme(safe_theme, str(export_file))
        self.assertTrue(result)
        self.assertTrue(export_file.exists())
    
    def test_export_theme_unsafe_path(self):
        """Test exporting theme to unsafe path."""
        safe_theme = {
            "name": "safe-theme",
            "version": "1.0.0",
            "colors": {"background": "#2e3440"}
        }
        
        unsafe_paths = [
            "../../../etc/passwd",
            "/etc/passwd",
            "theme.yaml\nrm -rf /",
            "theme.yaml; rm -rf /",
        ]
        
        for path in unsafe_paths:
            with self.assertRaises((ValidationError, SecurityError)):
                self.theme_manager.export_theme(safe_theme, path)
    
    def test_secure_file_handler_safe_yaml(self):
        """Test secure YAML file handling."""
        safe_data = {
            "name": "test",
            "version": "1.0.0",
            "colors": {"background": "#2e3440"}
        }
        
        yaml_file = Path(self.temp_dir) / "safe.yaml"
        
        # Test safe write
        result = self.secure_handler.safe_write_yaml(str(yaml_file), safe_data)
        self.assertTrue(result)
        self.assertTrue(yaml_file.exists())
        
        # Test safe read
        read_data = self.secure_handler.safe_read_yaml(str(yaml_file))
        self.assertEqual(read_data, safe_data)
    
    def test_secure_file_handler_unsafe_yaml(self):
        """Test secure YAML file handling with unsafe content."""
        unsafe_data = {
            "name": "test",
            "version": "1.0.0",
            "malicious": "!!python/object/apply:os.system ['rm -rf /']"
        }
        
        yaml_file = Path(self.temp_dir) / "unsafe.yaml"
        
        # Should fail to write unsafe content
        with self.assertRaises(SecurityError):
            self.secure_handler.safe_write_yaml(str(yaml_file), unsafe_data)
    
    def test_secure_file_handler_safe_json(self):
        """Test secure JSON file handling."""
        safe_data = {
            "name": "test",
            "version": "1.0.0",
            "colors": {"background": "#2e3440"}
        }
        
        json_file = Path(self.temp_dir) / "safe.json"
        
        # Test safe write
        result = self.secure_handler.safe_write_json(str(json_file), safe_data)
        self.assertTrue(result)
        self.assertTrue(json_file.exists())
        
        # Test safe read
        read_data = self.secure_handler.safe_read_json(str(json_file))
        self.assertEqual(read_data, safe_data)
    
    def test_secure_file_handler_large_file(self):
        """Test secure file handling with large files."""
        # Create a large data structure
        large_data = {
            "name": "large-theme",
            "version": "1.0.0",
            "colors": {},
            "large_data": "x" * (10 * 1024 * 1024)  # 10MB
        }
        
        yaml_file = Path(self.temp_dir) / "large.yaml"
        
        # Should fail due to size limit
        with self.assertRaises(SecurityError):
            self.secure_handler.safe_write_yaml(str(yaml_file), large_data)
    
    def test_validate_color_format(self):
        """Test color format validation."""
        valid_colors = [
            "#ffffff",
            "#000000",
            "#123456",
            "#abcdef",
            "#ABCDEF",
            "rgb(255, 255, 255)",
            "rgba(255, 255, 255, 1.0)",
            "hsl(0, 0%, 100%)",
            "hsla(0, 0%, 100%, 1.0)"
        ]
        
        for color in valid_colors:
            result = input_validator.validate_color_format(color)
            self.assertTrue(result)
        
        invalid_colors = [
            "not-a-color",
            "#gggggg",
            "#12345",
            "#1234567",
            "rgb(256, 256, 256)",
            "rgba(255, 255, 255, 2.0)",
            "hsl(400, 0%, 100%)",
            "hsla(0, 0%, 100%, 2.0)",
            "../../../etc/passwd",
            "'; rm -rf /; echo '",
            "`rm -rf /`"
        ]
        
        for color in invalid_colors:
            with self.assertRaises(ValidationError):
                input_validator.validate_color_format(color)
    
    def test_validate_file_extension(self):
        """Test file extension validation."""
        valid_extensions = [".yaml", ".yml", ".json"]
        
        for ext in valid_extensions:
            filename = f"theme{ext}"
            result = input_validator.validate_file_extension(filename)
            self.assertTrue(result)
        
        invalid_extensions = [".exe", ".sh", ".py", ".bat", ".cmd"]
        
        for ext in invalid_extensions:
            filename = f"theme{ext}"
            with self.assertRaises(ValidationError):
                input_validator.validate_file_extension(filename)
    
    def test_validate_file_size(self):
        """Test file size validation."""
        # Create a small file
        small_file = Path(self.temp_dir) / "small.yaml"
        small_file.write_text("name: test\nversion: 1.0.0")
        
        result = input_validator.validate_file_size(str(small_file))
        self.assertTrue(result)
        
        # Create a large file
        large_file = Path(self.temp_dir) / "large.yaml"
        large_file.write_text("x" * (10 * 1024 * 1024))  # 10MB
        
        with self.assertRaises(ValidationError):
            input_validator.validate_file_size(str(large_file))
    
    def test_theme_manager_security_integration(self):
        """Test theme manager security integration."""
        # Test with malicious theme name
        with self.assertRaises(ValidationError):
            self.theme_manager._validate_theme_name("../../../etc/passwd")
        
        # Test with safe theme name
        result = self.theme_manager._validate_theme_name("safe-theme")
        self.assertTrue(result)
        
        # Test theme creation with security validation
        safe_theme_data = {
            "name": "security-test",
            "version": "1.0.0",
            "colors": {
                "background": "#2e3440",
                "foreground": "#d8dee9"
            }
        }
        
        result = self.theme_manager.create_theme_template("security-test")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "security-test")
        
        # Test theme export with security validation
        export_file = Path(self.temp_dir) / "security-test.yaml"
        result = self.theme_manager.export_theme(safe_theme_data, str(export_file))
        self.assertTrue(result)
        self.assertTrue(export_file.exists())


if __name__ == '__main__':
    unittest.main()
