#!/usr/bin/env python3
"""
Wrapper script for HyprRice GUI that ensures QApplication is initialized first.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for GUI wrapper."""
    try:
        # Import and run the CLI
        from hyprrice.cli import main
        sys.exit(main())
    except Exception as e:
        print(f"Error launching HyprRice GUI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
