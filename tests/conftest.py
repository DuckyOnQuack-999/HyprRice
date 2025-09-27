"""
Pytest configuration and fixtures for HyprRice tests
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set Qt platform plugin for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from hyprrice.config import Config
from hyprrice.history import HistoryManager, BackupManager
from hyprrice.gui.theme_manager import ThemeManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def config(temp_dir):
    """Create a test configuration."""
    config = Config()
    config.paths.config_dir = temp_dir
    return config


@pytest.fixture
def history_manager(config):
    """Create a test history manager."""
    return HistoryManager(config)


@pytest.fixture
def backup_manager(temp_dir):
    """Create a test backup manager."""
    return BackupManager(temp_dir)


@pytest.fixture
def theme_manager(temp_dir):
    """Create a test theme manager."""
    return ThemeManager(temp_dir)


@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing."""
    return {
        'general': {
            'language': 'en',
            'live_preview': True,
            'auto_backup': True,
            'backup_retention': 10
        },
        'gui': {
            'theme': 'dark',
            'auto_save': True,
            'auto_save_interval': 30,
            'window_width': 1200,
            'window_height': 800
        },
        'hyprland': {
            'border_color': '#ffffff',
            'gaps_in': 5,
            'gaps_out': 10,
            'blur_enabled': True,
            'window_opacity': 0.9
        },
        'waybar': {
            'background_color': '#000000',
            'text_color': '#ffffff',
            'border_color': '#333333'
        },
        'rofi': {
            'background_color': '#111111',
            'text_color': '#ffffff',
            'border_color': '#444444'
        },
        'notifications': {
            'background_color': '#222222',
            'text_color': '#ffffff',
            'border_color': '#555555'
        },
        'clipboard': {
            'manager': 'cliphist',
            'history_size': 100,
            'auto_sync': True,
            'sync_interval': 30
        },
        'lockscreen': {
            'background': '~/.config/hyprlock/bg.jpg',
            'timeout': 300,
            'grace_period': 5,
            'show_clock': True,
            'show_date': True
        }
    }


@pytest.fixture
def sample_theme_data():
    """Sample theme data for testing."""
    return {
        'name': 'Test Theme',
        'description': 'A test theme for unit testing',
        'version': '1.0.0',
        'author': 'Test Author',
        'colors': {
            'primary': '#ff0000',
            'secondary': '#00ff00',
            'background': '#000000',
            'text': '#ffffff'
        },
        'hyprland': {
            'border_color': '#ff0000',
            'gaps_in': 10,
            'gaps_out': 20,
            'blur_enabled': True
        },
        'waybar': {
            'background_color': '#000000',
            'text_color': '#ffffff'
        },
        'rofi': {
            'background_color': '#111111',
            'text_color': '#ffffff'
        }
    }


@pytest.fixture
def mock_hyprctl():
    """Mock hyprctl function for testing."""
    import unittest.mock
    with unittest.mock.patch('hyprrice.utils.hyprctl') as mock:
        mock.return_value = (0, "", "")
        yield mock


@pytest.fixture
def mock_qapplication():
    """Mock QApplication for GUI tests."""
    import unittest.mock
    with unittest.mock.patch('PyQt6.QtWidgets.QApplication'):
        yield


@pytest.fixture
def mock_qmessagebox():
    """Mock QMessageBox for GUI tests."""
    import unittest.mock
    with unittest.mock.patch('PyQt6.QtWidgets.QMessageBox') as mock:
        mock.return_value.exec.return_value = None
        yield mock


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "gui: marks tests as GUI tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add markers based on test file names
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_gui" in item.nodeid:
            item.add_marker(pytest.mark.gui)
        else:
            item.add_marker(pytest.mark.unit)
        
        # Mark slow tests
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.slow)


# Test data generators
def generate_test_configs(count=5):
    """Generate multiple test configurations."""
    configs = []
    for i in range(count):
        config = Config()
        config.general.language = f"lang_{i}"
        config.hyprland.border_color = f"#ff{i:02x}00"
        config.waybar.background_color = f"#00{i:02x}00"
        configs.append(config)
    return configs


def generate_test_themes(count=3):
    """Generate multiple test themes."""
    themes = []
    for i in range(count):
        theme = {
            'name': f'Test Theme {i}',
            'description': f'Test theme number {i}',
            'version': '1.0.0',
            'colors': {
                'primary': f'#ff{i:02x}00',
                'background': f'#00{i:02x}00'
            }
        }
        themes.append(theme)
    return themes








