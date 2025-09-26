"""
Performance tests for HyprRice components
"""

import unittest
import tempfile
import os
import sys
import time
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hyprrice.config import Config
from hyprrice.history import HistoryManager, BackupManager
from hyprrice.gui.theme_manager import ThemeManager


class TestConfigPerformance(unittest.TestCase):
    """Test configuration system performance."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.config.paths.config_dir = self.temp_dir
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_config_save_performance(self):
        """Test configuration save performance."""
        # Modify config with many values
        for i in range(100):
            setattr(self.config.general, f'custom_field_{i}', f'value_{i}')
        
        # Measure save time
        start_time = time.time()
        config_path = os.path.join(self.temp_dir, "perf_config.yaml")
        self.config.save(config_path)
        save_time = time.time() - start_time
        
        # Should complete within reasonable time (1 second)
        self.assertLess(save_time, 1.0)
        self.assertTrue(os.path.exists(config_path))
    
    def test_config_load_performance(self):
        """Test configuration load performance."""
        # Create a large config file
        config_path = os.path.join(self.temp_dir, "large_config.yaml")
        
        # Add many custom fields
        for i in range(100):
            setattr(self.config.general, f'custom_field_{i}', f'value_{i}')
        
        self.config.save(config_path)
        
        # Measure load time
        start_time = time.time()
        loaded_config = Config.load(config_path)
        load_time = time.time() - start_time
        
        # Should complete within reasonable time (1 second)
        self.assertLess(load_time, 1.0)
        self.assertIsNotNone(loaded_config)
    
    def test_config_validation_performance(self):
        """Test configuration validation performance."""
        # Create config with many values
        for i in range(1000):
            setattr(self.config.general, f'custom_field_{i}', f'value_{i}')
        
        # Measure validation time
        start_time = time.time()
        result = self.config.validate()
        validation_time = time.time() - start_time
        
        # Should complete within reasonable time (0.5 seconds)
        self.assertLess(validation_time, 0.5)
        self.assertTrue(result)
    
    def test_config_serialization_performance(self):
        """Test configuration serialization performance."""
        # Add many values
        for i in range(500):
            setattr(self.config.general, f'custom_field_{i}', f'value_{i}')
        
        # Measure serialization time
        start_time = time.time()
        config_dict = self.config._to_dict()
        serialization_time = time.time() - start_time
        
        # Should complete within reasonable time (0.5 seconds)
        self.assertLess(serialization_time, 0.5)
        self.assertIsInstance(config_dict, dict)
        
        # Measure deserialization time
        start_time = time.time()
        new_config = Config()
        new_config._from_dict(config_dict)
        deserialization_time = time.time() - start_time
        
        # Should complete within reasonable time (0.5 seconds)
        self.assertLess(deserialization_time, 0.5)


class TestHistoryPerformance(unittest.TestCase):
    """Test history system performance."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.history_manager = HistoryManager(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_large_history_performance(self):
        """Test performance with large history."""
        from hyprrice.history import ConfigChangeCommand
        
        # Create many history entries
        start_time = time.time()
        
        for i in range(1000):
            old_state = self.config._to_dict()
            setattr(self.config.general, f'field_{i}', f'value_{i}')
            new_state = self.config._to_dict()
            
            command = ConfigChangeCommand(self.config, old_state, new_state)
            self.history_manager.execute(command)
        
        creation_time = time.time() - start_time
        
        # Should complete within reasonable time (5 seconds)
        self.assertLess(creation_time, 5.0)
        self.assertEqual(len(self.history_manager._undo_stack), 1000)
    
    def test_undo_redo_performance(self):
        """Test undo/redo performance with large history."""
        from hyprrice.history import ConfigChangeCommand
        
        # Create history entries
        for i in range(100):
            old_state = self.config._to_dict()
            setattr(self.config.general, f'field_{i}', f'value_{i}')
            new_state = self.config._to_dict()
            
            command = ConfigChangeCommand(self.config, old_state, new_state)
            self.history_manager.execute(command)
        
        # Measure undo performance
        start_time = time.time()
        for i in range(50):
            self.history_manager.undo()
        undo_time = time.time() - start_time
        
        # Should complete within reasonable time (1 second)
        self.assertLess(undo_time, 1.0)
        
        # Measure redo performance
        start_time = time.time()
        for i in range(50):
            self.history_manager.redo()
        redo_time = time.time() - start_time
        
        # Should complete within reasonable time (1 second)
        self.assertLess(redo_time, 1.0)
    
    def test_history_cleanup_performance(self):
        """Test history cleanup performance."""
        from hyprrice.history import ConfigChangeCommand
        
        # Set small max history
        self.history_manager.max_history = 10
        
        # Create many entries (should trigger cleanup)
        start_time = time.time()
        
        for i in range(1000):
            old_state = self.config._to_dict()
            setattr(self.config.general, f'field_{i}', f'value_{i}')
            new_state = self.config._to_dict()
            
            command = ConfigChangeCommand(self.config, old_state, new_state)
            self.history_manager.execute(command)
        
        cleanup_time = time.time() - start_time
        
        # Should complete within reasonable time (3 seconds)
        self.assertLess(cleanup_time, 3.0)
        self.assertEqual(len(self.history_manager._undo_stack), 10)


class TestBackupPerformance(unittest.TestCase):
    """Test backup system performance."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.backup_manager = BackupManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_backup_creation_performance(self):
        """Test backup creation performance."""
        # Create large config
        for i in range(1000):
            setattr(self.config.general, f'custom_field_{i}', f'value_{i}')
        
        # Measure backup creation time
        start_time = time.time()
        backup_path = self.backup_manager.create_backup(self.config, "Performance test backup")
        backup_time = time.time() - start_time
        
        # Should complete within reasonable time (2 seconds)
        self.assertLess(backup_time, 2.0)
        self.assertIsNotNone(backup_path)
        self.assertTrue(os.path.exists(backup_path))
    
    def test_backup_restoration_performance(self):
        """Test backup restoration performance."""
        # Create large config and backup
        for i in range(1000):
            setattr(self.config.general, f'custom_field_{i}', f'value_{i}')
        
        backup_path = self.backup_manager.create_backup(self.config, "Restoration test backup")
        
        # Measure restoration time
        start_time = time.time()
        result = self.backup_manager.restore_backup(backup_path)
        restoration_time = time.time() - start_time
        
        # Should complete within reasonable time (1 second)
        self.assertLess(restoration_time, 1.0)
        self.assertTrue(result)
    
    def test_backup_listing_performance(self):
        """Test backup listing performance."""
        # Create many backups
        start_time = time.time()
        
        for i in range(100):
            for j in range(10):
                setattr(self.config.general, f'field_{i}_{j}', f'value_{i}_{j}')
            self.backup_manager.create_backup(self.config, f"Backup {i}")
        
        creation_time = time.time() - start_time
        
        # Should complete within reasonable time (10 seconds)
        self.assertLess(creation_time, 10.0)
        
        # Measure listing time
        start_time = time.time()
        backups = self.backup_manager.list_backups()
        listing_time = time.time() - start_time
        
        # Should complete within reasonable time (1 second)
        self.assertLess(listing_time, 1.0)
        self.assertEqual(len(backups), 100)
    
    def test_backup_cleanup_performance(self):
        """Test backup cleanup performance."""
        # Set small max backups
        self.backup_manager.max_backups = 5
        
        # Create many backups (should trigger cleanup)
        start_time = time.time()
        
        for i in range(100):
            for j in range(10):
                setattr(self.config.general, f'field_{i}_{j}', f'value_{i}_{j}')
            self.backup_manager.create_backup(self.config, f"Backup {i}")
        
        cleanup_time = time.time() - start_time
        
        # Should complete within reasonable time (8 seconds)
        self.assertLess(cleanup_time, 8.0)
        
        # Should only have max_backups
        backups = self.backup_manager.list_backups()
        self.assertEqual(len(backups), 5)


class TestThemeManagerPerformance(unittest.TestCase):
    """Test theme manager performance."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.theme_manager = ThemeManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_theme_application_performance(self):
        """Test theme application performance."""
        # Create large config
        for i in range(1000):
            setattr(self.config.general, f'custom_field_{i}', f'value_{i}')
        
        # Measure theme application time
        start_time = time.time()
        result = self.theme_manager.apply_theme("minimal", self.config)
        application_time = time.time() - start_time
        
        # Should complete within reasonable time (1 second)
        self.assertLess(application_time, 1.0)
        self.assertTrue(result)
    
    def test_theme_export_performance(self):
        """Test theme export performance."""
        # Create large config
        for i in range(1000):
            setattr(self.config.general, f'custom_field_{i}', f'value_{i}')
        
        # Measure theme export time
        start_time = time.time()
        export_path = os.path.join(self.temp_dir, "large_theme.hyprrice")
        result = self.theme_manager.export_theme(self.config, export_path)
        export_time = time.time() - start_time
        
        # Should complete within reasonable time (1 second)
        self.assertLess(export_time, 1.0)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(export_path))
    
    def test_theme_import_performance(self):
        """Test theme import performance."""
        # Create and export large theme
        for i in range(1000):
            setattr(self.config.general, f'custom_field_{i}', f'value_{i}')
        
        export_path = os.path.join(self.temp_dir, "large_theme.hyprrice")
        self.theme_manager.export_theme(self.config, export_path)
        
        # Measure theme import time
        start_time = time.time()
        result = self.theme_manager.import_theme(export_path)
        import_time = time.time() - start_time
        
        # Should complete within reasonable time (1 second)
        self.assertLess(import_time, 1.0)
        self.assertTrue(result)
    
    def test_theme_listing_performance(self):
        """Test theme listing performance."""
        # Create many themes
        start_time = time.time()
        
        for i in range(100):
            for j in range(10):
                setattr(self.config.general, f'field_{i}_{j}', f'value_{i}_{j}')
            
            theme_name = f"theme_{i}"
            self.theme_manager.save_theme(theme_name, self.config, f"Theme {i}")
        
        creation_time = time.time() - start_time
        
        # Should complete within reasonable time (5 seconds)
        self.assertLess(creation_time, 5.0)
        
        # Measure listing time
        start_time = time.time()
        themes = self.theme_manager.list_themes()
        listing_time = time.time() - start_time
        
        # Should complete within reasonable time (0.5 seconds)
        self.assertLess(listing_time, 0.5)
        self.assertGreaterEqual(len(themes), 100)


class TestMemoryUsage(unittest.TestCase):
    """Test memory usage of components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_config_memory_usage(self):
        """Test configuration memory usage."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create large config
        for i in range(10000):
            setattr(self.config.general, f'custom_field_{i}', f'value_{i}')
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        self.assertLess(memory_increase, 100 * 1024 * 1024)
    
    def test_history_memory_usage(self):
        """Test history system memory usage."""
        import psutil
        import os
        from hyprrice.history import HistoryManager, ConfigChangeCommand
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        history_manager = HistoryManager(self.config)
        
        # Create many history entries
        for i in range(1000):
            old_state = self.config._to_dict()
            setattr(self.config.general, f'field_{i}', f'value_{i}')
            new_state = self.config._to_dict()
            
            command = ConfigChangeCommand(self.config, old_state, new_state)
            history_manager.execute(command)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        self.assertLess(memory_increase, 50 * 1024 * 1024)


if __name__ == '__main__':
    unittest.main()
