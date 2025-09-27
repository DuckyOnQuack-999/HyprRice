"""
Tests for sourced configuration files functionality.
"""

import os
import tempfile
import unittest
from pathlib import Path
from src.hyprrice.utils import (
    parse_hyprland_config, 
    write_hyprland_config, 
    get_sourced_files_from_config,
    create_sourced_file,
    validate_sourced_file
)


class TestSourcedFiles(unittest.TestCase):
    """Test sourced files functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "hyprland.conf")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_parse_config_with_source_directives(self):
        """Test parsing config with source directives."""
        config_content = """source = ~/.config/hypr/rules.conf
source = ~/.config/hypr/workspace.conf

general {
    animations_enabled = true
    animation_duration = 0.5
}

windowrule {
    float, ^(pavucontrol)$
}
"""
        
        with open(self.config_path, 'w') as f:
            f.write(config_content)
        
        sections = parse_hyprland_config(self.config_path)
        
        # Check that sourced files are extracted
        self.assertIn('_sourced_files', sections)
        self.assertEqual(len(sections['_sourced_files']), 2)
        self.assertIn('~/.config/hypr/rules.conf', sections['_sourced_files'])
        self.assertIn('~/.config/hypr/workspace.conf', sections['_sourced_files'])
        
        # Check that other sections are parsed correctly
        self.assertIn('general', sections)
        self.assertIn('windowrule', sections)

    def test_write_config_with_source_directives(self):
        """Test writing config with source directives."""
        sections = {
            '_sourced_files': [
                '~/.config/hypr/rules.conf',
                '~/.config/hypr/workspace.conf'
            ],
            'general': [
                'animations_enabled = true',
                'animation_duration = 0.5'
            ],
            'windowrule': [
                'float, ^(pavucontrol)$'
            ]
        }
        
        write_hyprland_config(self.config_path, sections)
        
        # Read back and verify
        with open(self.config_path, 'r') as f:
            content = f.read()
        
        # Check that source directives are written first
        self.assertTrue(content.startswith('source = ~/.config/hypr/rules.conf'))
        self.assertIn('source = ~/.config/hypr/workspace.conf', content)
        
        # Check that sections are written correctly
        # Note: 'general' section doesn't get a header in the writer
        self.assertIn('animations_enabled = true', content)
        self.assertIn('windowrule {', content)

    def test_get_sourced_files_from_config(self):
        """Test extracting sourced files from config."""
        config_content = """source = ~/.config/hypr/rules.conf
source = ~/.config/hypr/workspace.conf

general {
    animations_enabled = true
}
"""
        
        with open(self.config_path, 'w') as f:
            f.write(config_content)
        
        sourced_files = get_sourced_files_from_config(self.config_path)
        
        self.assertEqual(len(sourced_files), 2)
        self.assertIn('~/.config/hypr/rules.conf', sourced_files)
        self.assertIn('~/.config/hypr/workspace.conf', sourced_files)

    def test_create_sourced_file(self):
        """Test creating sourced files with default content."""
        # Test creating a rules file
        rules_path = os.path.join(self.temp_dir, "rules.conf")
        success = create_sourced_file(rules_path)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(rules_path))
        
        # Check content
        with open(rules_path, 'r') as f:
            content = f.read()
        
        self.assertIn('Window rules', content)
        self.assertIn('windowrule', content)

    def test_create_sourced_file_with_custom_content(self):
        """Test creating sourced files with custom content."""
        custom_path = os.path.join(self.temp_dir, "custom.conf")
        custom_content = "# Custom configuration\ncustom_setting = value"
        
        success = create_sourced_file(custom_path, custom_content)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(custom_path))
        
        with open(custom_path, 'r') as f:
            content = f.read()
        
        self.assertEqual(content, custom_content)

    def test_validate_sourced_file(self):
        """Test validating sourced files."""
        # Test non-existent file
        non_existent = os.path.join(self.temp_dir, "nonexistent.conf")
        self.assertFalse(validate_sourced_file(non_existent))
        
        # Test empty file
        empty_file = os.path.join(self.temp_dir, "empty.conf")
        with open(empty_file, 'w') as f:
            pass
        self.assertFalse(validate_sourced_file(empty_file))
        
        # Test valid file
        valid_file = os.path.join(self.temp_dir, "valid.conf")
        with open(valid_file, 'w') as f:
            f.write("# Valid configuration\nsetting = value")
        self.assertTrue(validate_sourced_file(valid_file))

    def test_roundtrip_config_with_sources(self):
        """Test roundtrip: parse -> modify -> write -> parse."""
        # Initial config
        initial_content = """source = ~/.config/hypr/rules.conf

general {
    animations_enabled = true
}
"""
        
        with open(self.config_path, 'w') as f:
            f.write(initial_content)
        
        # Parse
        sections = parse_hyprland_config(self.config_path)
        
        # Modify
        sections['_sourced_files'].append('~/.config/hypr/exec.conf')
        sections['general'].append('animation_duration = 0.3')
        
        # Write
        write_hyprland_config(self.config_path, sections)
        
        # Parse again
        new_sections = parse_hyprland_config(self.config_path)
        
        # Verify
        self.assertEqual(len(new_sections['_sourced_files']), 2)
        self.assertIn('~/.config/hypr/rules.conf', new_sections['_sourced_files'])
        self.assertIn('~/.config/hypr/exec.conf', new_sections['_sourced_files'])
        self.assertIn('animation_duration = 0.3', new_sections['general'])


if __name__ == '__main__':
    unittest.main()
