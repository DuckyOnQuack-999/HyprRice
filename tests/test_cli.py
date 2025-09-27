"""
Tests for the HyprRice CLI interface.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import tempfile
import shutil

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hyprrice.cli import (
    build_parser, dispatch, cmd_doctor, cmd_check, cmd_migrate, 
    cmd_plugins, cmd_gui, main
)


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
    
    def test_build_parser(self):
        """Test argument parser construction."""
        parser = build_parser()
        
        # Test that parser has expected subcommands
        # Find the _SubParsersAction (last action with choices)
        subparser_action = None
        for action in parser._subparsers._actions:
            if hasattr(action, 'choices') and action.choices:
                subparser_action = action
                break
        
        self.assertIsNotNone(subparser_action, "No subparsers found")
        subcommands = list(subparser_action.choices.keys())
        
        expected_commands = ['gui', 'doctor', 'check', 'migrate', 'plugins']
        for cmd in expected_commands:
            self.assertIn(cmd, subcommands)
    
    def test_parser_help(self):
        """Test that parser shows help correctly."""
        parser = build_parser()
        
        # Test main help
        with patch('sys.argv', ['hyprrice', '--help']):
            try:
                args = parser.parse_args()
                self.fail("Should have exited with help")
            except SystemExit as e:
                self.assertEqual(e.code, 0)
    
    def test_parser_version(self):
        """Test that parser shows version correctly."""
        parser = build_parser()
        
        with patch('sys.argv', ['hyprrice', '--version']):
            try:
                args = parser.parse_args()
                self.fail("Should have exited with version")
            except SystemExit as e:
                self.assertEqual(e.code, 0)
    
    @patch('hyprrice.cli.check_dependencies')
    @patch('hyprrice.cli.sys.version_info')
    @patch('pathlib.Path.exists')
    def test_cmd_doctor_success(self, mock_exists, mock_version_info, mock_check_deps):
        """Test doctor command with successful checks."""
        mock_check_deps.return_value = {
            # System dependencies
            'hyprland': {'available': True, 'version': '0.40.0'},
            'waybar': {'available': True, 'version': '0.9.17'},
            'rofi': {'available': True, 'version': '1.7.3'},
            'dunst': {'available': True, 'version': '1.9.0'},
            'mako': {'available': True, 'version': '1.7.0'},
            'grim': {'available': True, 'version': '1.3.2'},
            'slurp': {'available': True, 'version': '1.3.0'},
            'cliphist': {'available': True, 'version': '0.4.0'},
            'hyprlock': {'available': True, 'version': '0.1.0'},
            'swww': {'available': True, 'version': '0.8.0'},
            'hyprpaper': {'available': True, 'version': '0.1.0'},
            # Python dependencies
            'python_pyqt5': {'available': True, 'version': '5.15.11'},
            'python_pyyaml': {'available': True, 'version': '6.0'},
            'python_psutil': {'available': True, 'version': '5.9.0'},
            # System info
            'system': {'available': True, 'version': 'Linux 6.16.8'},
            'wayland': {'available': True, 'version': 'Wayland session detected'},
        }
        
        # Mock Python version
        mock_version_info.major = 3
        mock_version_info.minor = 10
        mock_version_info.micro = 0
        # Make it comparable to tuples
        mock_version_info.__lt__ = lambda self, other: (self.major, self.minor, self.micro) < other
        
        # Mock filesystem checks to return True
        mock_exists.return_value = True
        
        args = MagicMock()
        args.json = False
        args.fix = False
        
        with patch('builtins.print') as mock_print:
            result = cmd_doctor(args)
            self.assertEqual(result, 0)
            mock_print.assert_called()
    
    @patch('hyprrice.cli.check_dependencies')
    def test_cmd_doctor_json(self, mock_check_deps):
        """Test doctor command with JSON output."""
        mock_check_deps.return_value = {
            'hyprland': {'available': True, 'version': '0.40.0'},
        }
        
        args = MagicMock()
        args.json = True
        args.fix = False
        
        with patch('builtins.print') as mock_print:
            result = cmd_doctor(args)
            self.assertEqual(result, 0)
            # Check that JSON was printed
            mock_print.assert_called()
    
    @patch('hyprrice.cli.check_dependencies')
    def test_cmd_doctor_failures(self, mock_check_deps):
        """Test doctor command with failed checks."""
        mock_check_deps.return_value = {
            'hyprland': {'available': False},
            'waybar': {'available': False},
        }
        
        args = MagicMock()
        args.json = False
        args.fix = False
        
        with patch('builtins.print'):
            result = cmd_doctor(args)
            self.assertEqual(result, 1)
    
    @patch('hyprrice.cli.check_dependencies')
    def test_cmd_check(self, mock_check_deps):
        """Test check command."""
        mock_check_deps.return_value = {
            'hyprland': {'available': True},
            'waybar': {'available': True},
        }
        
        args = MagicMock()
        args.json = False
        
        with patch('builtins.print'):
            result = cmd_check(args)
            self.assertEqual(result, 0)
    
    @patch('hyprrice.cli.migrate_config')
    def test_cmd_migrate_success(self, mock_migrate):
        """Test migrate command with success."""
        mock_migrate.return_value = {
            'success': True,
            'backup_path': '/tmp/backup.yaml'
        }
        
        args = MagicMock()
        args.backup = True
        args.force = False
        
        with patch('hyprrice.cli.check_migration_needed', return_value=True):
            with patch('builtins.print'):
                result = cmd_migrate(args)
                self.assertEqual(result, 0)
    
    @patch('hyprrice.cli.migrate_config')
    def test_cmd_migrate_failure(self, mock_migrate):
        """Test migrate command with failure."""
        mock_migrate.return_value = {
            'success': False,
            'error': 'Migration failed'
        }
        
        args = MagicMock()
        args.backup = True
        args.force = True
        
        with patch('builtins.print'):
            result = cmd_migrate(args)
            self.assertEqual(result, 1)
    
    @patch('hyprrice.cli.EnhancedPluginManager')
    def test_cmd_plugins_list(self, mock_plugin_manager):
        """Test plugins list command."""
        mock_manager = MagicMock()
        mock_manager.list_available_plugins.return_value = ['plugin1', 'plugin2']
        mock_manager.list_loaded_plugins.return_value = ['plugin1']
        mock_manager.list_enabled_plugins.return_value = ['plugin1']
        mock_plugin_manager.return_value = mock_manager
        
        args = MagicMock()
        args.plugin_action = 'list'
        
        with patch('builtins.print'):
            result = cmd_plugins(args)
            self.assertEqual(result, 0)
    
    @patch('hyprrice.cli.EnhancedPluginManager')
    def test_cmd_plugins_load(self, mock_plugin_manager):
        """Test plugins load command."""
        mock_manager = MagicMock()
        mock_manager.load_plugin.return_value = True
        mock_plugin_manager.return_value = mock_manager
        
        args = MagicMock()
        args.plugin_action = 'load'
        args.plugin_name = 'test_plugin'
        
        with patch('builtins.print'):
            result = cmd_plugins(args)
            self.assertEqual(result, 0)
    
    @patch('hyprrice.cli.EnhancedPluginManager')
    def test_cmd_plugins_load_failure(self, mock_plugin_manager):
        """Test plugins load command with failure."""
        mock_manager = MagicMock()
        mock_manager.load_plugin.side_effect = Exception("Load failed")
        mock_plugin_manager.return_value = mock_manager
        
        args = MagicMock()
        args.plugin_action = 'load'
        args.plugin_name = 'test_plugin'
        
        with patch('builtins.print'):
            result = cmd_plugins(args)
            self.assertEqual(result, 1)
    
    @patch('hyprrice.cli.EnhancedPluginManager')
    def test_cmd_plugins_reload(self, mock_plugin_manager):
        """Test plugins reload command."""
        mock_manager = MagicMock()
        mock_manager.list_loaded_plugins.return_value = ['plugin1', 'plugin2']
        mock_manager.load_plugin.return_value = True
        mock_plugin_manager.return_value = mock_manager
        
        args = MagicMock()
        args.plugin_action = 'reload'
        
        with patch('builtins.print'):
            result = cmd_plugins(args)
            self.assertEqual(result, 0)
    
    @patch('hyprrice.cli.EnhancedPluginManager')
    def test_cmd_plugins_enable(self, mock_plugin_manager):
        """Test plugins enable command."""
        mock_manager = MagicMock()
        mock_manager.enable_plugin.return_value = True
        mock_plugin_manager.return_value = mock_manager
        
        args = MagicMock()
        args.plugin_action = 'enable'
        args.plugin_name = 'test_plugin'
        
        with patch('builtins.print'):
            result = cmd_plugins(args)
            self.assertEqual(result, 0)
    
    @patch('hyprrice.cli.EnhancedPluginManager')
    def test_cmd_plugins_disable(self, mock_plugin_manager):
        """Test plugins disable command."""
        mock_manager = MagicMock()
        mock_manager.disable_plugin.return_value = True
        mock_plugin_manager.return_value = mock_manager
        
        args = MagicMock()
        args.plugin_action = 'disable'
        args.plugin_name = 'test_plugin'
        
        with patch('builtins.print'):
            result = cmd_plugins(args)
            self.assertEqual(result, 0)
    
    def test_cmd_plugins_unknown_action(self):
        """Test plugins command with unknown action."""
        args = MagicMock()
        args.plugin_action = 'unknown'
        
        with patch('builtins.print'):
            result = cmd_plugins(args)
            self.assertEqual(result, 1)
    
    @patch('hyprrice.main_gui.QApplication')
    @patch('hyprrice.main_gui.HyprRiceGUI')
    def test_cmd_gui_success(self, mock_gui, mock_app):
        """Test GUI command with success."""
        mock_app_instance = MagicMock()
        mock_app_instance.exec_.return_value = 0
        mock_app.return_value = mock_app_instance
        
        mock_gui_instance = MagicMock()
        mock_gui.return_value = mock_gui_instance
        
        args = MagicMock()
        args.config = None
        args.theme = None
        
        result = cmd_gui(args)
        self.assertEqual(result, 0)
    
    def test_cmd_gui_import_error(self):
        """Test GUI command with import error."""
        import builtins
        real_import = builtins.__import__
        
        def side_effect(name, *args, **kwargs):
            if name == 'PyQt6.QtWidgets':
                raise ImportError("PyQt6 not found")
            return real_import(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=side_effect):
            args = MagicMock()
            args.config = None
            args.theme = None
            
            with patch('builtins.print'):
                result = cmd_gui(args)
                self.assertEqual(result, 1)
    
    def test_dispatch_unknown_command(self):
        """Test dispatch with unknown command."""
        args = MagicMock()
        args.command = 'unknown'
        args.verbose = False
        
        with patch('builtins.print'):
            result = dispatch(args)
            self.assertEqual(result, 1)
    
    def test_dispatch_no_command(self):
        """Test dispatch with no command."""
        args = MagicMock()
        args.command = None
        args.parser = MagicMock()
        
        with patch('builtins.print'):
            result = dispatch(args)
            self.assertEqual(result, 1)
    
    @patch('hyprrice.cli.dispatch')
    def test_main_success(self, mock_dispatch):
        """Test main function with success."""
        mock_dispatch.return_value = 0
        
        with patch('sys.argv', ['hyprrice', 'doctor']):
            result = main()
            self.assertEqual(result, 0)
    
    @patch('hyprrice.cli.dispatch')
    def test_main_keyboard_interrupt(self, mock_dispatch):
        """Test main function with keyboard interrupt."""
        mock_dispatch.side_effect = KeyboardInterrupt()
        
        with patch('sys.argv', ['hyprrice', 'doctor']):
            with patch('builtins.print'):
                result = main()
                self.assertEqual(result, 0)
    
    @patch('hyprrice.cli.dispatch')
    def test_main_exception(self, mock_dispatch):
        """Test main function with exception."""
        mock_dispatch.side_effect = Exception("Test error")
        
        with patch('sys.argv', ['hyprrice', 'doctor']):
            with patch('builtins.print'):
                result = main()
                self.assertEqual(result, 1)
    
    @patch('hyprrice.cli.dispatch')
    def test_main_exception_verbose(self, mock_dispatch):
        """Test main function with exception and verbose output."""
        mock_dispatch.side_effect = Exception("Test error")
        
        with patch('sys.argv', ['hyprrice', '--verbose', 'doctor']):
            with patch('builtins.print'):
                with patch('traceback.print_exc'):
                    result = main()
                    self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main()
