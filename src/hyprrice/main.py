#!/usr/bin/env python3
"""
Main entry point for HyprRice application
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from .config import Config
from .gui import HyprRiceGUI
from .utils import setup_logging, check_dependencies, create_directories
from .exceptions import HyprRiceError


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="HyprRice - Comprehensive Hyprland Ecosystem Ricing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hyprrice                    # Launch GUI
  hyprrice --debug           # Launch with debug logging
  hyprrice --check-deps      # Check system dependencies
  hyprrice --config /path/to/config.yaml  # Use custom config
        """
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check system dependencies and exit"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to custom configuration file"
    )
    
    parser.add_argument(
        "--theme",
        type=str,
        choices=["dark", "light", "auto"],
        default="auto",
        help="GUI theme (default: auto)"
    )
    
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Disable automatic backups"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="HyprRice %(prog)s 1.0.0"
    )
    
    return parser.parse_args()


def check_system_requirements() -> bool:
    """Check if system meets requirements."""
    logger = logging.getLogger(__name__)
    
    # Check if running on Linux
    if sys.platform != "linux":
        logger.error("HyprRice only supports Linux systems")
        return False
    
    # Check if running on Wayland
    wayland_display = "WAYLAND_DISPLAY" in os.environ
    if not wayland_display:
        logger.warning("Not running on Wayland. Some features may not work correctly.")
    
    # Check if Hyprland is available
    hyprctl_path = Path("/usr/bin/hyprctl")
    if not hyprctl_path.exists():
        logger.error("hyprctl not found. Please install Hyprland.")
        return False
    
    return True


def main() -> int:
    """Main application entry point."""
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting HyprRice...")
        
        # Check system requirements
        if not check_system_requirements():
            return 1
        
        # Check dependencies if requested
        if args.check_deps:
            deps_ok = check_dependencies()
            return 0 if deps_ok else 1
        
        # Create necessary directories
        create_directories()
        
        # Load configuration
        config = Config(config_path=args.config)
        
        # Disable backups if requested
        if args.no_backup:
            config.general.auto_backup = False
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("HyprRice")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("HyprRice")
        
        # Set application style
        if args.theme != "auto":
            config.gui.theme = args.theme
        
        # Create and show main window
        window = HyprRiceGUI(config)
        window.show()
        
        logger.info("HyprRice GUI started successfully")
        
        # Run application
        return app.exec_()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except HyprRiceError as e:
        logger.error(f"HyprRice error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import os
    sys.exit(main()) 