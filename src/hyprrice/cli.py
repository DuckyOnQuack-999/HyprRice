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
from datetime import datetime
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from hyprrice.config import Config
from hyprrice.utils import check_dependencies, setup_logging
from hyprrice.plugins import EnhancedPluginManager
from hyprrice.migration import check_migration_needed, migrate_config
from hyprrice.backup_manager import BackupManager
from hyprrice.cli_plugins import cmd_plugins
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
  hyprrice autoconfig             # Run intelligent autoconfiguration
  hyprrice autoconfig --profile visual  # Apply visual profile
  hyprrice plugins list           # List available plugins
  hyprrice plugins enable hyprbars  # Enable Hyprbars plugin
  hyprrice plugins generate --reload  # Generate modular configs and reload
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
    gui_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with comprehensive system analysis'
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
        '--rollback',
        action='store_true',
        help='Rollback the last doctor --fix operation'
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
    
    
    # Autoconfig command
    autoconfig_parser = subparsers.add_parser(
        'autoconfig',
        help='Run intelligent autoconfiguration'
    )
    autoconfig_parser.add_argument(
        '--profile',
        type=str,
        choices=['performance', 'visual', 'battery', 'minimal'],
        default='performance',
        help='Performance profile to apply (default: performance)'
    )
    autoconfig_parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    autoconfig_parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup before autoconfig'
    )
    autoconfig_parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    # Plugins command - integrated directly to avoid conflicts
    plugins_parser = subparsers.add_parser(
        'plugins',
        help='Manage plugins (list, enable, disable, generate, apply)'
    )
    plugins_parser.add_argument(
        'action',
        choices=['list', 'enable', 'disable', 'generate', 'apply', 'status'],
        help='Plugin action to perform'
    )
    plugins_parser.add_argument(
        '--plugin',
        type=str,
        help='Plugin name (required for enable/disable)'
    )
    plugins_parser.add_argument(
        '--reload',
        action='store_true',
        help='Reload Hyprland after applying changes'
    )
    
    return parser


def _create_gui_app(config: Config = None) -> tuple:
    """Create QApplication and HyprRiceGUI window for testing."""
    from PyQt6.QtCore import QCoreApplication, Qt
    from PyQt6.QtWidgets import QApplication
    from hyprrice.main_gui import HyprRiceGUI
    
    # Set attributes before QApplication is created
    if not QApplication.instance():
        # High-DPI attributes are deprecated in PyQt6, but we can still set them
        try:
            QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            # These attributes may not be available in newer PyQt6 versions
            pass
        app = QApplication(sys.argv or [])
    else:
        app = QApplication.instance()
    
    app.setApplicationName("HyprRice")
    app.setApplicationVersion("1.0.0")
    
    # Load config if not provided
    if config is None:
        config = Config()
    
    # Create main window
    window = HyprRiceGUI(config)
    
    return app, window


def cmd_gui(args: argparse.Namespace) -> int:
    """Launch the HyprRice GUI."""
    try:
        # Load config if specified
        config = None
        if hasattr(args, 'config') and args.config:
            config = Config.load(args.config)
        else:
            config = Config()
        
        # Create app and window
        app, window = _create_gui_app(config)
        
        # Load theme if specified
        if hasattr(args, 'theme') and args.theme:
            try:
                window.theme_manager.load_theme(args.theme)
                print(f"Loaded theme: {args.theme}")
            except Exception as e:
                print(f"Warning: Could not load theme '{args.theme}': {e}")
        
        window.show()
        
        return app.exec()
        
    except ImportError as e:
        print(f"Error: Could not import GUI components: {e}")
        print("Make sure PyQt6 is installed: pip install PyQt6")
        return 1
    except Exception as e:
        print(f"Error launching GUI: {e}")
        return 1


def cmd_doctor(args: argparse.Namespace) -> int:
    """Check system status and dependencies."""
    try:
        # Handle rollback first
        if args.rollback:
            return cmd_doctor_rollback(args)
        
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
                
                # Create backup before fixing
                backup_manager = None
                backup_created = False
                try:
                    config = Config.load()
                    backup_manager = BackupManager(config, compression_enabled=True)
                    backup_created = backup_manager.create_backup("Pre-doctor-fix backup")
                    if backup_created:
                        # Generate backup filename based on timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        backup_name = f"hyprrice_backup_{timestamp}.json.gz"
                        print(f"📦 Created backup: {backup_name}")
                    else:
                        backup_name = None
                        print("⚠️  Warning: Failed to create backup")
                except Exception as e:
                    backup_name = None
                    backup_created = False
                    print(f"⚠️  Warning: Could not create backup: {e}")
                
                fixed_issues = 0
                
                # Fix missing dependencies
                for dep, status in results.items():
                    if not status['available'] and status.get('required', False):
                        if 'install_command' in status:
                            install_cmd = status['install_command'].split('\n')[0]  # Get first install command
                            print(f"   Installing {dep}...")
                            try:
                                import subprocess
                                # Extract the actual command (remove comments)
                                if 'sudo pacman -S' in install_cmd:
                                    cmd = ['sudo', 'pacman', '-S', '--noconfirm', dep]
                                elif 'sudo apt install' in install_cmd:
                                    cmd = ['sudo', 'apt', 'install', '-y', dep]
                                elif 'sudo dnf install' in install_cmd:
                                    cmd = ['sudo', 'dnf', 'install', '-y', dep]
                                else:
                                    print(f"   Cannot auto-install {dep}: {install_cmd}")
                                    continue
                                
                                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                                if result.returncode == 0:
                                    print(f"   ✅ Successfully installed {dep}")
                                    fixed_issues += 1
                                else:
                                    print(f"   ❌ Failed to install {dep}: {result.stderr}")
                            except Exception as e:
                                print(f"   ❌ Error installing {dep}: {e}")
                
                # Fix configuration issues
                config_path = Path.home() / '.config' / 'hyprrice' / 'config.yaml'
                if not config_path.exists():
                    print("   Creating default configuration...")
                    try:
                        from .config import Config
                        config = Config()
                        config.save()
                        print("   ✅ Default configuration created")
                        fixed_issues += 1
                    except Exception as e:
                        print(f"   ❌ Failed to create configuration: {e}")
                
                # Fix plugin directory
                plugins_dir = Path.home() / '.hyprrice' / 'plugins'
                if not plugins_dir.exists():
                    print("   Creating plugins directory...")
                    try:
                        plugins_dir.mkdir(parents=True, exist_ok=True)
                        print("   ✅ Plugins directory created")
                        fixed_issues += 1
                    except Exception as e:
                        print(f"   ❌ Failed to create plugins directory: {e}")
                
                # Fix backup directory
                backup_dir = Path.home() / '.hyprrice' / 'backups'
                if not backup_dir.exists():
                    print("   Creating backup directory...")
                    try:
                        backup_dir.mkdir(parents=True, exist_ok=True)
                        print("   ✅ Backup directory created")
                        fixed_issues += 1
                    except Exception as e:
                        print(f"   ❌ Failed to create backup directory: {e}")
                
                if fixed_issues > 0:
                    print(f"   🎉 Fixed {fixed_issues} issue(s)!")
                    print("   Run 'hyprrice doctor' again to verify fixes.")
                    if backup_name:
                        print(f"   🔄 To rollback: 'hyprrice doctor --rollback'")
                        # Store rollback info in a simple marker file
                        rollback_info = {
                            "backup_name": backup_name,
                            "timestamp": datetime.now().isoformat(),
                            "fixed_issues": fixed_issues
                        }
                        try:
                            rollback_file = Path.home() / '.hyprrice' / 'last_doctor_fix.json'
                            rollback_file.parent.mkdir(parents=True, exist_ok=True)
                            with open(rollback_file, 'w') as f:
                                json.dump(rollback_info, f, indent=2)
                        except Exception as e:
                            print(f"   ⚠️  Warning: Could not save rollback info: {e}")
                else:
                    print("   ℹ️  No issues could be automatically fixed.")
            return 1
            
    except Exception as e:
        print(f"Error during system check: {e}")
        return 1


def cmd_doctor_rollback(args: argparse.Namespace) -> int:
    """Rollback the last doctor --fix operation."""
    try:
        print("🔄 HyprRice Doctor Rollback")
        print("=" * 50)
        
        # Check for rollback info file
        rollback_file = Path.home() / '.hyprrice' / 'last_doctor_fix.json'
        if not rollback_file.exists():
            print("❌ No rollback information found.")
            print("   Only available after running 'hyprrice doctor --fix'")
            return 1
        
        # Load rollback info
        try:
            with open(rollback_file, 'r') as f:
                rollback_info = json.load(f)
        except Exception as e:
            print(f"❌ Error reading rollback info: {e}")
            return 1
        
        backup_name = rollback_info.get('backup_name')
        timestamp = rollback_info.get('timestamp')
        fixed_issues = rollback_info.get('fixed_issues', 0)
        
        if not backup_name:
            print("❌ Invalid rollback information: missing backup name")
            return 1
        
        print(f"📋 Last fix operation:")
        print(f"   Date: {timestamp}")
        print(f"   Issues fixed: {fixed_issues}")
        print(f"   Backup: {backup_name}")
        
        # Confirm rollback
        if not args.json:
            response = input("\n📋 Do you want to rollback? [y/N]: ")
            if response.lower() not in ['y', 'yes']:
                print("Rollback cancelled.")
                return 0
        
        # Perform rollback
        try:
            config = Config.load()
            backup_manager = BackupManager(config, compression_enabled=True)
            
            # Find the actual backup file
            backup_dir = Path.home() / '.hyprrice' / 'backups'
            backup_files = list(backup_dir.glob('hyprrice_backup_*.json*'))
            
            if not backup_files:
                print("❌ No backup files found in backup directory")
                return 1
            
            # Find the most recent backup (closest match to our timestamp)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            latest_backup = backup_files[0]
            
            print(f"🔄 Restoring from: {latest_backup.name}")
            
            success = backup_manager.restore_backup(latest_backup.name)
            if success:
                print("✅ Rollback completed successfully!")
                
                # Remove rollback info file
                try:
                    rollback_file.unlink()
                    print("📝 Rollback info cleared")
                except Exception as e:
                    print(f"⚠️  Warning: Could not clear rollback info: {e}")
                
                # Reload Hyprland if running
                try:
                    import subprocess
                    subprocess.run(['hyprctl', 'reload'], capture_output=True, timeout=10)
                    print("🔄 Hyprland configuration reloaded")
                except Exception as e:
                    print(f"ℹ️  Hyprland reload skipped: {e}")
                
                return 0
            else:
                print("❌ Rollback failed")
                return 1
        
        except Exception as e:
            print(f"❌ Error during rollback: {e}")
            return 1
    
    except Exception as e:
        print(f"Error during rollback: {e}")
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
            enabled = plugin_manager.list_loaded_plugins()
            
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


def cmd_autoconfig(args: argparse.Namespace) -> int:
    """Run intelligent autoconfiguration."""
    try:
        from .autoconfig import run_autoconfig
        
        print("🔧 HyprRice Autoconfiguration")
        print("=" * 40)
        
        # Run autoconfig
        result = run_autoconfig(
            profile=args.profile,
            interactive=args.interactive,
            backup=not args.no_backup
        )
        
        if args.json:
            # Output JSON result
            import json
            from dataclasses import asdict
            
            # Convert result to dict and handle enums
            result_dict = asdict(result)
            if result_dict.get('profile_applied'):
                result_dict['profile_applied'] = result_dict['profile_applied'].value
            
            print(json.dumps(result_dict, indent=2))
            return 0 if result.success else 1
        
        # Output human-readable result
        if result.success:
            print("✅ Autoconfiguration completed successfully!")
            print(f"📊 Profile applied: {result.profile_applied.value}")
            print(f"⚡ Performance impact: {result.performance_impact}")
            
            if result.optimizations_applied:
                print("\n🔧 Optimizations applied:")
                for opt in result.optimizations_applied:
                    print(f"  • {opt}")
            
            if result.recommendations:
                print("\n💡 Recommendations:")
                for rec in result.recommendations:
                    print(f"  • {rec}")
            
            if result.backup_created:
                print(f"\n💾 Backup created: {result.backup_path}")
            
            print("\n🎉 Your HyprRice configuration has been optimized!")
            return 0
        else:
            print("❌ Autoconfiguration failed!")
            if result.warnings:
                print("\n⚠️  Warnings:")
                for warning in result.warnings:
                    print(f"  • {warning}")
            return 1
            
    except ImportError as e:
        print(f"Error: Could not import autoconfig module: {e}")
        return 1
    except Exception as e:
        print(f"Error during autoconfiguration: {e}")
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
        'autoconfig': cmd_autoconfig,
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
