#!/usr/bin/env python3
"""
HyprRice CLI - Command-line interface for HyprRice theme manager.

This module provides a command-line interface for managing Hyprland themes,
configurations, and plugins without the GUI.
"""

import argparse
import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hyprrice.config import Config
from hyprrice.utils import check_dependencies, setup_logging
from hyprrice.plugins import EnhancedPluginManager
from hyprrice.migration import check_migration_needed, migrate_config
from hyprrice.gui.theme_manager import ThemeManager
from hyprrice.exceptions import HyprRiceError


def setup_cli_logging(verbose: bool = False) -> None:
    """Setup logging for CLI operations."""
    level = logging.DEBUG if verbose else logging.INFO
    setup_logging(level=level)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog='hyprrice',
        description='HyprRice - Comprehensive Hyprland theme manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hyprrice gui                    # Launch the GUI
  hyprrice doctor                 # Check system status
  hyprrice plugins list           # List available plugins
  hyprrice migrate                # Migrate configuration
  hyprrice check                  # Check dependencies
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='%(prog)s 1.0.0'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='COMMAND'
    )
    
    # GUI command
    gui_parser = subparsers.add_parser(
        'gui',
        help='Launch the HyprRice GUI'
    )
    gui_parser.add_argument(
        '--theme',
        type=str,
        help='Load specific theme on startup'
    )
    
    # Doctor command
    doctor_parser = subparsers.add_parser(
        'doctor',
        help='Check system status and dependencies'
    )
    doctor_parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix common issues'
    )
    doctor_parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    # Check command
    check_parser = subparsers.add_parser(
        'check',
        help='Check system dependencies'
    )
    check_parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    # Migrate command
    migrate_parser = subparsers.add_parser(
        'migrate',
        help='Migrate configuration to new format'
    )
    migrate_parser.add_argument(
        '--backup',
        action='store_true',
        default=True,
        help='Create backup before migration (default: True)'
    )
    migrate_parser.add_argument(
        '--force',
        action='store_true',
        help='Force migration even if not needed'
    )
    
    # Plugins command
    plugins_parser = subparsers.add_parser(
        'plugins',
        help='Manage plugins'
    )
    plugins_subparsers = plugins_parser.add_subparsers(
        dest='plugin_action',
        help='Plugin actions',
        metavar='ACTION'
    )
    
    # Plugin list
    plugins_subparsers.add_parser(
        'list',
        help='List available plugins'
    )
    
    # Plugin load
    load_parser = plugins_subparsers.add_parser(
        'load',
        help='Load a specific plugin'
    )
    load_parser.add_argument(
        'plugin_name',
        type=str,
        help='Name of plugin to load'
    )
    
    # Plugin reload
    reload_parser = plugins_subparsers.add_parser(
        'reload',
        help='Reload all plugins'
    )
    
    # Plugin enable
    enable_parser = plugins_subparsers.add_parser(
        'enable',
        help='Enable a plugin'
    )
    enable_parser.add_argument(
        'plugin_name',
        type=str,
        help='Name of plugin to enable'
    )
    
    # Plugin disable
    disable_parser = plugins_subparsers.add_parser(
        'disable',
        help='Disable a plugin'
    )
    disable_parser.add_argument(
        'plugin_name',
        type=str,
        help='Name of plugin to disable'
    )
    
    return parser


def cmd_gui(args: argparse.Namespace) -> int:
    """Launch the HyprRice GUI."""
    try:
        from hyprrice.main_gui import HyprRiceGUI
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        app.setApplicationName("HyprRice")
        app.setApplicationVersion("1.0.0")
        
        # Load config if specified
        config = None
        if args.config:
            config = Config.load(args.config)
        else:
            config = Config()
        
        # Create and show main window
        window = HyprRiceGUI(config)
        
        # Load theme if specified
        if args.theme:
            try:
                window.theme_manager.load_theme(args.theme)
                print(f"Loaded theme: {args.theme}")
            except Exception as e:
                print(f"Warning: Could not load theme '{args.theme}': {e}")
        
        window.show()
        
        return app.exec_()
        
    except ImportError as e:
        print(f"Error: Could not import GUI components: {e}")
        print("Make sure PyQt5 is installed: pip install PyQt5")
        return 1
    except Exception as e:
        print(f"Error launching GUI: {e}")
        return 1


def cmd_doctor(args: argparse.Namespace) -> int:
    """Check system status and dependencies."""
    try:
        results = check_dependencies()
        
        if args.json:
            print(json.dumps(results, indent=2))
            return 0
        
        print("🔍 HyprRice System Check")
        print("=" * 50)
        
        # Check Python version
        python_version = sys.version_info
        print(f"Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
        if python_version < (3, 10):
            print("❌ Python 3.10+ required")
            return 1
        else:
            print("✅ Python version OK")
        
        # Check dependencies
        print("\n📦 Dependencies:")
        for dep, status in results.items():
            if status['available']:
                print(f"✅ {dep}: {status.get('version', 'Available')}")
            else:
                print(f"❌ {dep}: Not found")
                if 'install_command' in status:
                    print(f"   Install: {status['install_command']}")
        
        # Check Hyprland
        print("\n🖥️  Hyprland:")
        hyprland_status = results.get('hyprland', {})
        if hyprland_status.get('available'):
            print("✅ Hyprland is running")
            if 'version' in hyprland_status:
                print(f"   Version: {hyprland_status['version']}")
        else:
            print("❌ Hyprland not running or not found")
            print("   Make sure Hyprland is installed and running")
        
        # Check configuration
        print("\n⚙️  Configuration:")
        config_path = Path.home() / '.config' / 'hyprrice' / 'config.yaml'
        if config_path.exists():
            print(f"✅ Config found: {config_path}")
        else:
            print(f"❌ Config not found: {config_path}")
            print("   Run 'hyprrice migrate' to create initial config")
        
        # Check plugins
        print("\n🔌 Plugins:")
        plugins_dir = Path.home() / '.hyprrice' / 'plugins'
        if plugins_dir.exists():
            plugin_files = list(plugins_dir.glob('*.py'))
            print(f"✅ Plugins directory: {plugins_dir}")
            print(f"   Found {len(plugin_files)} plugin(s)")
        else:
            print(f"❌ Plugins directory not found: {plugins_dir}")
        
        # Overall status
        critical_issues = sum(1 for status in results.values() 
                            if not status.get('available', False))
        
        if critical_issues == 0:
            print("\n🎉 All checks passed! System is ready.")
            return 0
        else:
            print(f"\n⚠️  Found {critical_issues} issue(s). See above for details.")
            if args.fix:
                print("🔧 Attempting to fix issues...")
                # TODO: Implement auto-fix logic
                print("   Auto-fix not yet implemented")
            return 1
            
    except Exception as e:
        print(f"Error during system check: {e}")
        return 1


def cmd_check(args: argparse.Namespace) -> int:
    """Check system dependencies."""
    try:
        results = check_dependencies()
        
        if args.json:
            print(json.dumps(results, indent=2))
            return 0
        
        print("📦 Dependency Check")
        print("=" * 30)
        
        all_ok = True
        for dep, status in results.items():
            if status['available']:
                print(f"✅ {dep}")
            else:
                print(f"❌ {dep}")
                all_ok = False
        
        if all_ok:
            print("\n🎉 All dependencies satisfied!")
            return 0
        else:
            print("\n⚠️  Some dependencies are missing.")
            return 1
            
    except Exception as e:
        print(f"Error checking dependencies: {e}")
        return 1


def cmd_migrate(args: argparse.Namespace) -> int:
    """Migrate configuration to new format."""
    try:
        print("🔄 Configuration Migration")
        print("=" * 30)
        
        # Check if migration is needed
        if not args.force:
            migration_needed = check_migration_needed()
            if not migration_needed:
                print("✅ Configuration is up to date. No migration needed.")
                return 0
        
        print("📋 Migrating configuration...")
        
        # Perform migration
        from hyprrice.migration import migrate_user_config
        success = migrate_user_config()
        
        if success:
            print("✅ Migration completed successfully!")
            print("📁 Backup created automatically")
            return 0
        else:
            print("ℹ️  No migration needed or no config file found")
            return 0
            
    except Exception as e:
        print(f"Error during migration: {e}")
        return 1


def cmd_plugins(args: argparse.Namespace) -> int:
    """Manage plugins."""
    try:
        plugins_dir = Path.home() / '.hyprrice' / 'plugins'
        plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize plugin manager
        plugin_manager = EnhancedPluginManager(
            plugins_dir=str(plugins_dir),
            enable_sandbox=True,
            security_level='medium'
        )
        
        if args.plugin_action == 'list':
            print("🔌 Available Plugins")
            print("=" * 30)
            
            available = plugin_manager.list_available_plugins()
            loaded = plugin_manager.list_loaded_plugins()
            enabled = plugin_manager.list_enabled_plugins()
            
            if not available:
                print("No plugins found.")
                print(f"Place plugin files in: {plugins_dir}")
                return 0
            
            for plugin_name in available:
                status = []
                if plugin_name in loaded:
                    status.append("loaded")
                if plugin_name in enabled:
                    status.append("enabled")
                
                status_str = f" ({', '.join(status)})" if status else " (available)"
                print(f"📦 {plugin_name}{status_str}")
            
            print(f"\nTotal: {len(available)} plugin(s)")
            return 0
        
        elif args.plugin_action == 'load':
            print(f"📦 Loading plugin: {args.plugin_name}")
            try:
                plugin_manager.load_plugin(args.plugin_name)
                print("✅ Plugin loaded successfully!")
                return 0
            except Exception as e:
                print(f"❌ Failed to load plugin: {e}")
                return 1
        
        elif args.plugin_action == 'reload':
            print("🔄 Reloading all plugins...")
            try:
                # Unload all plugins
                for plugin_name in list(plugin_manager.list_loaded_plugins()):
                    plugin_manager.unload_plugin(plugin_name)
                
                # Reload all available plugins
                for plugin_name in plugin_manager.list_available_plugins():
                    try:
                        plugin_manager.load_plugin(plugin_name)
                        print(f"✅ Reloaded: {plugin_name}")
                    except Exception as e:
                        print(f"❌ Failed to reload {plugin_name}: {e}")
                
                print("🎉 Plugin reload completed!")
                return 0
            except Exception as e:
                print(f"❌ Failed to reload plugins: {e}")
                return 1
        
        elif args.plugin_action == 'enable':
            print(f"✅ Enabling plugin: {args.plugin_name}")
            try:
                plugin_manager.enable_plugin(args.plugin_name)
                print("✅ Plugin enabled successfully!")
                return 0
            except Exception as e:
                print(f"❌ Failed to enable plugin: {e}")
                return 1
        
        elif args.plugin_action == 'disable':
            print(f"❌ Disabling plugin: {args.plugin_name}")
            try:
                plugin_manager.disable_plugin(args.plugin_name)
                print("✅ Plugin disabled successfully!")
                return 0
            except Exception as e:
                print(f"❌ Failed to disable plugin: {e}")
                return 1
        
        else:
            print("❌ Unknown plugin action. Use 'hyprrice plugins --help' for usage.")
            return 1
            
    except Exception as e:
        print(f"Error managing plugins: {e}")
        return 1


def dispatch(args: argparse.Namespace) -> int:
    """Dispatch command to appropriate handler."""
    if not args.command:
        # No command specified, show help
        args.parser.print_help()
        return 1
    
    # Setup logging
    setup_cli_logging(args.verbose)
    
    # Route to command handler
    command_map = {
        'gui': cmd_gui,
        'doctor': cmd_doctor,
        'check': cmd_check,
        'migrate': cmd_migrate,
        'plugins': cmd_plugins,
    }
    
    handler = command_map.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


def main() -> int:
    """Main entry point for the CLI."""
    try:
        parser = build_parser()
        args = parser.parse_args()
        args.parser = parser  # Store parser reference for help
        return dispatch(args)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if '--verbose' in sys.argv or '-v' in sys.argv:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
