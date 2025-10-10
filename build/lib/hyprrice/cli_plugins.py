"""
CLI commands for plugin management and modular configuration

Provides command-line interface for managing Hyprbars, Hyprexpo, Glow, and Blur Shaders.
"""

import argparse
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from .config import Config
from .hyprland.modular_config import ModularConfigGenerator
from .exceptions import HyprRiceError


def cmd_plugins(args: argparse.Namespace) -> int:
    """Handle plugin-related commands."""
    try:
        config = Config.load()
        
        if args.subcommand == "list":
            return _list_plugins(config, args)
        elif args.subcommand == "enable":
            return _enable_plugin(config, args)
        elif args.subcommand == "disable":
            return _disable_plugin(config, args)
        elif args.subcommand == "status":
            return _plugin_status(config, args)
        elif args.subcommand == "generate":
            return _generate_modular_configs(config, args)
        elif args.subcommand == "apply":
            return _apply_theme(config, args)
        else:
            print(f"Unknown plugin subcommand: {args.subcommand}")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _list_plugins(config: Config, args: argparse.Namespace) -> int:
    """List available plugins and their status."""
    plugins = {
        "hyprbars": {
            "name": "Hyprbars",
            "description": "Titlebars with window control buttons",
            "enabled": config.hyprland.hyprbars_enabled,
            "config": {
                "height": config.hyprland.hyprbars_height,
                "buttons_size": config.hyprland.hyprbars_buttons_size,
                "buttons_gap": config.hyprland.hyprbars_buttons_gap,
                "buttons_color": config.hyprland.hyprbars_buttons_color,
                "buttons_hover_color": config.hyprland.hyprbars_buttons_hover_color,
                "title_color": config.hyprland.hyprbars_title_color,
                "title_font": config.hyprland.hyprbars_title_font,
                "title_size": config.hyprland.hyprbars_title_size
            }
        },
        "hyprexpo": {
            "name": "Hyprexpo",
            "description": "Workspace exposure and effects plugin",
            "enabled": config.hyprland.hyprexpo_enabled,
            "config": {
                "workspace_method": config.hyprland.hyprexpo_workspace_method,
                "workspace_gaps": config.hyprland.hyprexpo_workspace_gaps,
                "workspace_rounding": config.hyprland.hyprexpo_workspace_rounding,
                "workspace_shadow": config.hyprland.hyprexpo_workspace_shadow,
                "workspace_shadow_color": config.hyprland.hyprexpo_workspace_shadow_color,
                "workspace_shadow_size": config.hyprland.hyprexpo_workspace_shadow_size,
                "workspace_shadow_offset": config.hyprland.hyprexpo_workspace_shadow_offset
            }
        },
        "glow": {
            "name": "Glow Effects",
            "description": "Glow effects via shadows",
            "enabled": config.hyprland.glow_enabled,
            "config": {
                "color": config.hyprland.glow_color,
                "size": config.hyprland.glow_size,
                "offset": config.hyprland.glow_offset,
                "opacity": config.hyprland.glow_opacity,
                "blur": config.hyprland.glow_blur
            }
        },
        "blur_shaders": {
            "name": "Blur Shaders",
            "description": "Advanced blur shader effects",
            "enabled": config.hyprland.blur_shaders_enabled,
            "config": {
                "type": config.hyprland.blur_shader_type,
                "passes": config.hyprland.blur_shader_passes,
                "size": config.hyprland.blur_shader_size,
                "noise": config.hyprland.blur_shader_noise,
                "contrast": config.hyprland.blur_shader_contrast,
                "brightness": config.hyprland.blur_shader_brightness,
                "vibrancy": config.hyprland.blur_shader_vibrancy,
                "vibrancy_darkness": config.hyprland.blur_shader_vibrancy_darkness
            }
        }
    }
    
    if args.json:
        print(json.dumps(plugins, indent=2))
    else:
        print("🔌 Available Plugins")
        print("=" * 50)
        
        for plugin_id, plugin_info in plugins.items():
            status = "✅ Enabled" if plugin_info["enabled"] else "❌ Disabled"
            print(f"\n{plugin_info['name']} ({plugin_id})")
            print(f"  Status: {status}")
            print(f"  Description: {plugin_info['description']}")
            
            if args.verbose:
                print("  Configuration:")
                for key, value in plugin_info["config"].items():
                    print(f"    {key}: {value}")
    
    return 0


def _enable_plugin(config: Config, args: argparse.Namespace) -> int:
    """Enable a plugin."""
    plugin = args.plugin.lower()
    
    if plugin == "hyprbars":
        config.hyprland.hyprbars_enabled = True
        print("✅ Hyprbars enabled")
    elif plugin == "hyprexpo":
        config.hyprland.hyprexpo_enabled = True
        print("✅ Hyprexpo enabled")
    elif plugin == "glow":
        config.hyprland.glow_enabled = True
        print("✅ Glow effects enabled")
    elif plugin == "blur_shaders":
        config.hyprland.blur_shaders_enabled = True
        print("✅ Blur shaders enabled")
    else:
        print(f"❌ Unknown plugin: {plugin}")
        return 1
    
    # Save configuration
    config.save()
    
    # Generate modular configs if requested
    if args.generate:
        return _generate_modular_configs(config, args)
    
    return 0


def _disable_plugin(config: Config, args: argparse.Namespace) -> int:
    """Disable a plugin."""
    plugin = args.plugin.lower()
    
    if plugin == "hyprbars":
        config.hyprland.hyprbars_enabled = False
        print("❌ Hyprbars disabled")
    elif plugin == "hyprexpo":
        config.hyprland.hyprexpo_enabled = False
        print("❌ Hyprexpo disabled")
    elif plugin == "glow":
        config.hyprland.glow_enabled = False
        print("❌ Glow effects disabled")
    elif plugin == "blur_shaders":
        config.hyprland.blur_shaders_enabled = False
        print("❌ Blur shaders disabled")
    else:
        print(f"❌ Unknown plugin: {plugin}")
        return 1
    
    # Save configuration
    config.save()
    
    # Generate modular configs if requested
    if args.generate:
        return _generate_modular_configs(config, args)
    
    return 0


def _plugin_status(config: Config, args: argparse.Namespace) -> int:
    """Show plugin status."""
    plugin = args.plugin.lower()
    
    if plugin == "hyprbars":
        enabled = config.hyprland.hyprbars_enabled
        print(f"Hyprbars: {'✅ Enabled' if enabled else '❌ Disabled'}")
    elif plugin == "hyprexpo":
        enabled = config.hyprland.hyprexpo_enabled
        print(f"Hyprexpo: {'✅ Enabled' if enabled else '❌ Disabled'}")
    elif plugin == "glow":
        enabled = config.hyprland.glow_enabled
        print(f"Glow effects: {'✅ Enabled' if enabled else '❌ Disabled'}")
    elif plugin == "blur_shaders":
        enabled = config.hyprland.blur_shaders_enabled
        print(f"Blur shaders: {'✅ Enabled' if enabled else '❌ Disabled'}")
    else:
        print(f"❌ Unknown plugin: {plugin}")
        return 1
    
    return 0


def _generate_modular_configs(config: Config, args: argparse.Namespace) -> int:
    """Generate modular configuration files."""
    try:
        generator = ModularConfigGenerator(config)
        configs = generator.generate_all_configs()
        
        if args.json:
            result = {
                "success": True,
                "generated_files": list(configs.keys()),
                "hyprland_dir": str(generator.hypr_dir)
            }
            print(json.dumps(result, indent=2))
        else:
            print("🔧 Generated Modular Configuration Files")
            print("=" * 50)
            for filename in configs.keys():
                print(f"✅ {filename}")
            print(f"\n📁 Configuration directory: {generator.hypr_dir}")
        
        # Reload Hyprland if requested
        if args.reload:
            if generator.reload_hyprland():
                print("🔄 Hyprland configuration reloaded successfully")
            else:
                print("⚠️  Failed to reload Hyprland configuration")
                return 1
        
        return 0
        
    except Exception as e:
        if args.json:
            result = {
                "success": False,
                "error": str(e)
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Failed to generate modular configs: {e}")
        return 1


def _apply_theme(config: Config, args: argparse.Namespace) -> int:
    """Apply a theme configuration."""
    try:
        generator = ModularConfigGenerator(config)
        
        if args.theme == "palevioletred":
            theme_configs = generator.generate_palevioletred_theme()
        else:
            print(f"❌ Unknown theme: {args.theme}")
            return 1
        
        if generator.apply_theme(theme_configs):
            if args.json:
                result = {
                    "success": True,
                    "theme": args.theme,
                    "applied_files": [k for k in theme_configs.keys() if k != 'theme_info']
                }
                print(json.dumps(result, indent=2))
            else:
                print(f"🎨 Applied theme: {args.theme}")
                print("Applied files:")
                for filename in theme_configs.keys():
                    if filename != 'theme_info':
                        print(f"  ✅ {filename}")
            
            # Reload Hyprland if requested
            if args.reload:
                if generator.reload_hyprland():
                    print("🔄 Hyprland configuration reloaded successfully")
                else:
                    print("⚠️  Failed to reload Hyprland configuration")
                    return 1
            
            return 0
        else:
            if args.json:
                result = {
                    "success": False,
                    "error": "Failed to apply theme"
                }
                print(json.dumps(result, indent=2))
            else:
                print("❌ Failed to apply theme")
            return 1
            
    except Exception as e:
        if args.json:
            result = {
                "success": False,
                "error": str(e)
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Failed to apply theme: {e}")
        return 1


def build_plugin_parser(subparsers):
    """Build the plugin command parser."""
    plugin_parser = subparsers.add_parser(
        'plugins',
        help='Manage Hyprland plugins and modular configuration'
    )
    
    plugin_subparsers = plugin_parser.add_subparsers(
        dest='subcommand',
        help='Plugin subcommands'
    )
    
    # List plugins
    list_parser = plugin_subparsers.add_parser(
        'list',
        help='List available plugins and their status'
    )
    list_parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    list_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed configuration'
    )
    
    # Enable plugin
    enable_parser = plugin_subparsers.add_parser(
        'enable',
        help='Enable a plugin'
    )
    enable_parser.add_argument(
        'plugin',
        choices=['hyprbars', 'hyprexpo', 'glow', 'blur_shaders'],
        help='Plugin to enable'
    )
    enable_parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate modular configs after enabling'
    )
    
    # Disable plugin
    disable_parser = plugin_subparsers.add_parser(
        'disable',
        help='Disable a plugin'
    )
    disable_parser.add_argument(
        'plugin',
        choices=['hyprbars', 'hyprexpo', 'glow', 'blur_shaders'],
        help='Plugin to disable'
    )
    disable_parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate modular configs after disabling'
    )
    
    # Plugin status
    status_parser = plugin_subparsers.add_parser(
        'status',
        help='Show plugin status'
    )
    status_parser.add_argument(
        'plugin',
        choices=['hyprbars', 'hyprexpo', 'glow', 'blur_shaders'],
        help='Plugin to check'
    )
    
    # Generate modular configs
    generate_parser = plugin_subparsers.add_parser(
        'generate',
        help='Generate modular configuration files'
    )
    generate_parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    generate_parser.add_argument(
        '--reload',
        action='store_true',
        help='Reload Hyprland configuration after generating'
    )
    
    # Apply theme
    apply_parser = plugin_subparsers.add_parser(
        'apply',
        help='Apply a theme configuration'
    )
    apply_parser.add_argument(
        'theme',
        choices=['palevioletred'],
        help='Theme to apply'
    )
    apply_parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    apply_parser.add_argument(
        '--reload',
        action='store_true',
        help='Reload Hyprland configuration after applying'
    )
    
    return plugin_parser
