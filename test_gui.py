#!/usr/bin/env python3
"""
Test script to debug the QApplication issue.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_import():
    """Test importing the package."""
    print("Testing package import...")
    try:
        import hyprrice
        print("✓ Package import successful")
        return True
    except Exception as e:
        print(f"✗ Package import failed: {e}")
        return False

def test_cli_import():
    """Test importing the CLI module."""
    print("Testing CLI import...")
    try:
        from hyprrice.cli import main
        print("✓ CLI import successful")
        return True
    except Exception as e:
        print(f"✗ CLI import failed: {e}")
        return False

def test_gui_creation():
    """Test creating the GUI."""
    print("Testing GUI creation...")
    try:
        from hyprrice.cli import _create_gui_app
        app, window = _create_gui_app()
        print("✓ GUI creation successful")
        return True
    except Exception as e:
        print(f"✗ GUI creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=== HyprRice GUI Debug Test ===\n")
    
    success = True
    success &= test_import()
    success &= test_cli_import()
    success &= test_gui_creation()
    
    print(f"\n=== Test Results ===")
    if success:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
