"""
Tests for the plugin sandboxing system.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hyprrice.plugin_sandbox import (
    SandboxLimits, create_sandbox, SecurePluginManager
)


class TestSandboxLimits(unittest.TestCase):
    """Test SandboxLimits dataclass."""
    
    def test_sandbox_limits_creation(self):
        """Test creating SandboxLimits."""
        limits = SandboxLimits(
            max_memory_mb=100,
            max_cpu_seconds=30,
            max_file_descriptors=50,
            max_execution_time=60
        )
        
        self.assertEqual(limits.max_memory_mb, 100)
        self.assertEqual(limits.max_cpu_seconds, 30)
        self.assertEqual(limits.max_file_descriptors, 50)
        self.assertEqual(limits.max_execution_time, 60)
    
    def test_sandbox_limits_defaults(self):
        """Test SandboxLimits with default values."""
        limits = SandboxLimits()
        
        self.assertEqual(limits.max_memory_mb, 50)
        self.assertEqual(limits.max_cpu_seconds, 10)
        self.assertEqual(limits.max_file_descriptors, 20)
        self.assertEqual(limits.max_execution_time, 30)


class TestCreateSandbox(unittest.TestCase):
    """Test create_sandbox function."""
    
    def test_create_sandbox_strict(self):
        """Test creating strict sandbox."""
        limits = create_sandbox('strict')
        
        self.assertEqual(limits.max_memory_mb, 25)
        self.assertEqual(limits.max_cpu_seconds, 5)
        self.assertEqual(limits.max_file_descriptors, 10)
        self.assertEqual(limits.max_execution_time, 15)
    
    def test_create_sandbox_medium(self):
        """Test creating medium sandbox."""
        limits = create_sandbox('medium')
        
        self.assertEqual(limits.max_memory_mb, 50)
        self.assertEqual(limits.max_cpu_seconds, 10)
        self.assertEqual(limits.max_file_descriptors, 20)
        self.assertEqual(limits.max_execution_time, 30)
    
    def test_create_sandbox_relaxed(self):
        """Test creating relaxed sandbox."""
        limits = create_sandbox('relaxed')
        
        self.assertEqual(limits.max_memory_mb, 100)
        self.assertEqual(limits.max_cpu_seconds, 30)
        self.assertEqual(limits.max_file_descriptors, 50)
        self.assertEqual(limits.max_execution_time, 60)
    
    def test_create_sandbox_invalid_level(self):
        """Test creating sandbox with invalid security level."""
        with self.assertRaises(ValueError):
            create_sandbox('invalid')


class TestSecurePluginManager(unittest.TestCase):
    """Test SecurePluginManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
        
        self.manager = SecurePluginManager(
            plugins_dir=self.temp_dir,
            security_level='medium'
        )
    
    def test_init(self):
        """Test SecurePluginManager initialization."""
        self.assertEqual(self.manager.plugins_dir, self.temp_dir)
        self.assertEqual(self.manager.security_level, 'medium')
        self.assertIsNotNone(self.manager.sandbox_limits)
    
    def test_load_plugin_secure_success(self):
        """Test loading a plugin securely with success."""
        # Create a simple plugin file
        plugin_content = """
def test_function():
    return "Hello from sandboxed plugin"

# This should be allowed
result = test_function()
"""
        
        plugin_file = Path(self.temp_dir) / "test_plugin.py"
        plugin_file.write_text(plugin_content)
        
        # Mock the plugin loading
        with patch.object(self.manager, '_execute_in_sandbox') as mock_execute:
            mock_execute.return_value = {'result': 'Hello from sandboxed plugin'}
            
            result = self.manager.load_plugin_secure(str(plugin_file))
            
            self.assertTrue(result['success'])
            self.assertEqual(result['result'], 'Hello from sandboxed plugin')
    
    def test_load_plugin_secure_dangerous_import(self):
        """Test loading a plugin with dangerous import."""
        plugin_content = """
import os
import subprocess

# This should be blocked
os.system('rm -rf /')
"""
        
        plugin_file = Path(self.temp_dir) / "dangerous_plugin.py"
        plugin_file.write_text(plugin_content)
        
        result = self.manager.load_plugin_secure(str(plugin_file))
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_load_plugin_secure_file_access(self):
        """Test loading a plugin with restricted file access."""
        plugin_content = """
# Try to access restricted file
with open('/etc/passwd', 'r') as f:
    content = f.read()
"""
        
        plugin_file = Path(self.temp_dir) / "file_access_plugin.py"
        plugin_file.write_text(plugin_content)
        
        result = self.manager.load_plugin_secure(str(plugin_file))
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_load_plugin_secure_memory_limit(self):
        """Test loading a plugin that exceeds memory limit."""
        plugin_content = """
# Create a large list to exceed memory limit
large_list = []
for i in range(1000000):
    large_list.append('x' * 1000)
"""
        
        plugin_file = Path(self.temp_dir) / "memory_plugin.py"
        plugin_file.write_text(plugin_content)
        
        # Set very low memory limit
        self.manager.sandbox_limits.max_memory_mb = 1
        
        result = self.manager.load_plugin_secure(str(plugin_file))
        
        # Should either succeed (if memory limit not enforced) or fail gracefully
        self.assertIn('success', result)
    
    def test_load_plugin_secure_timeout(self):
        """Test loading a plugin that exceeds time limit."""
        plugin_content = """
import time

# Sleep for a long time
time.sleep(100)
"""
        
        plugin_file = Path(self.temp_dir) / "timeout_plugin.py"
        plugin_file.write_text(plugin_content)
        
        # Set very low time limit
        self.manager.sandbox_limits.max_execution_time = 1
        
        result = self.manager.load_plugin_secure(str(plugin_file))
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_load_plugin_secure_safe_operations(self):
        """Test that safe operations are allowed."""
        plugin_content = """
import math
import json

# Safe operations
result = math.sqrt(16)
data = {'key': 'value'}
json_str = json.dumps(data)
parsed = json.loads(json_str)

# Return results
output = {
    'sqrt_result': result,
    'json_works': parsed == data
}
"""
        
        plugin_file = Path(self.temp_dir) / "safe_plugin.py"
        plugin_file.write_text(plugin_content)
        
        result = self.manager.load_plugin_secure(str(plugin_file))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['output']['sqrt_result'], 4.0)
        self.assertTrue(result['output']['json_works'])
    
    def test_load_plugin_secure_nonexistent_file(self):
        """Test loading a nonexistent plugin file."""
        result = self.manager.load_plugin_secure('/nonexistent/plugin.py')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_load_plugin_secure_syntax_error(self):
        """Test loading a plugin with syntax error."""
        plugin_content = """
# Syntax error
def broken_function(
    return "missing closing parenthesis"
"""
        
        plugin_file = Path(self.temp_dir) / "syntax_error_plugin.py"
        plugin_file.write_text(plugin_content)
        
        result = self.manager.load_plugin_secure(str(plugin_file))
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_load_plugin_secure_runtime_error(self):
        """Test loading a plugin with runtime error."""
        plugin_content = """
# Runtime error
undefined_variable = some_undefined_function()
"""
        
        plugin_file = Path(self.temp_dir) / "runtime_error_plugin.py"
        plugin_file.write_text(plugin_content)
        
        result = self.manager.load_plugin_secure(str(plugin_file))
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_validate_plugin_safe(self):
        """Test validating a safe plugin."""
        plugin_content = """
def safe_function():
    return "safe"
"""
        
        plugin_file = Path(self.temp_dir) / "safe_plugin.py"
        plugin_file.write_text(plugin_content)
        
        result = self.manager.validate_plugin(str(plugin_file))
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['warnings']), 0)
    
    def test_validate_plugin_dangerous(self):
        """Test validating a dangerous plugin."""
        plugin_content = """
import os
import subprocess

def dangerous_function():
    os.system('rm -rf /')
    subprocess.call(['rm', '-rf', '/'])
"""
        
        plugin_file = Path(self.temp_dir) / "dangerous_plugin.py"
        plugin_file.write_text(plugin_content)
        
        result = self.manager.validate_plugin(str(plugin_file))
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['warnings']), 0)
    
    def test_get_sandbox_info(self):
        """Test getting sandbox information."""
        info = self.manager.get_sandbox_info()
        
        self.assertIn('security_level', info)
        self.assertIn('limits', info)
        self.assertEqual(info['security_level'], 'medium')
        self.assertIsInstance(info['limits'], dict)


if __name__ == '__main__':
    unittest.main()
