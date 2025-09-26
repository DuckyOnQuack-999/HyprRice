#!/usr/bin/env python3
"""
Test runner for HyprRice test suite
"""

import sys
import os
import unittest
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def discover_tests(test_dir=None):
    """Discover all test files in the test directory."""
    if test_dir is None:
        test_dir = os.path.dirname(__file__)
    
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    return suite


def run_tests(verbosity=2, test_pattern=None, test_file=None):
    """Run the test suite."""
    # Create test suite
    if test_file:
        # Run specific test file
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(test_file)
    elif test_pattern:
        # Run tests matching pattern
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(test_pattern)
    else:
        # Run all tests
        suite = discover_tests()
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description='Run HyprRice test suite')
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true', 
        help='Verbose output'
    )
    parser.add_argument(
        '-q', '--quiet', 
        action='store_true', 
        help='Quiet output'
    )
    parser.add_argument(
        '-f', '--file', 
        help='Run specific test file (e.g., test_config)'
    )
    parser.add_argument(
        '-p', '--pattern', 
        help='Run tests matching pattern (e.g., TestConfig)'
    )
    parser.add_argument(
        '--coverage', 
        action='store_true', 
        help='Run with coverage reporting'
    )
    parser.add_argument(
        '--performance', 
        action='store_true', 
        help='Run performance tests only'
    )
    parser.add_argument(
        '--unit', 
        action='store_true', 
        help='Run unit tests only'
    )
    parser.add_argument(
        '--integration', 
        action='store_true', 
        help='Run integration tests only'
    )
    
    args = parser.parse_args()
    
    # Set verbosity
    if args.verbose:
        verbosity = 2
    elif args.quiet:
        verbosity = 0
    else:
        verbosity = 1
    
    # Determine test pattern
    test_pattern = None
    test_file = None
    
    if args.file:
        test_file = args.file
    elif args.pattern:
        test_pattern = args.pattern
    elif args.performance:
        test_pattern = 'test_performance'
    elif args.unit:
        test_pattern = 'test_config test_utils test_plugin_manager'
    elif args.integration:
        test_pattern = 'test_integration'
    
    # Run tests
    try:
        success = run_tests(verbosity, test_pattern, test_file)
        
        if success:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()








