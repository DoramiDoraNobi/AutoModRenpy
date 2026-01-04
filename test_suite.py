"""
Test Suite for AutoModRenpy
Basic tests to verify components are working
"""
import unittest
import os
import sys
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils import Config, Logger, Cache
from src.script_validator import ScriptValidator, ValidationIssue
from src.mod_processor import ModProcessor, ConflictStrategy, ModFile
from src.backup_manager import BackupManager


class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def test_config_loading(self):
        """Test config loading"""
        config = Config('config.json')
        self.assertIsNotNone(config.get('version'))
        self.assertEqual(config.get('app_name'), 'AutoModRenpy')
    
    def test_logger(self):
        """Test logger functionality"""
        logger = Logger(verbose=False)
        logger.info("Test message")
        logger.warning("Test warning")
        logger.error("Test error")
        logger.success("Test success")
        # Should not raise exceptions
        self.assertTrue(True)
    
    def test_cache(self):
        """Test cache functionality"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            cache_file = f.name
        
        try:
            cache = Cache(cache_file, max_entries=5)
            
            # Test set and get
            cache.set('key1', 'value1')
            self.assertEqual(cache.get('key1'), 'value1')
            
            # Test max entries
            for i in range(10):
                cache.set(f'key{i}', f'value{i}')
            
            # Should only keep last 5
            self.assertLessEqual(len(cache.cache), 5)
            
            # Test clear
            cache.clear()
            self.assertEqual(len(cache.cache), 0)
        
        finally:
            if os.path.exists(cache_file):
                os.remove(cache_file)


class TestScriptValidator(unittest.TestCase):
    """Test script validator"""
    
    def setUp(self):
        self.validator = ScriptValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_valid_script(self):
        """Test validation of valid script"""
        script_content = """# Valid Renpy script
label start:
    "Hello World"
    jump next_scene

label next_scene:
    "This is the next scene"
    return
"""
        script_path = os.path.join(self.temp_dir, 'test.rpy')
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        is_valid, issues = self.validator.validate_script(script_path)
        self.assertTrue(is_valid)
    
    def test_indentation_error(self):
        """Test detection of indentation errors"""
        script_content = """label start:
  "Wrong indentation (2 spaces)"
    "Correct indentation (4 spaces)"
"""
        script_path = os.path.join(self.temp_dir, 'test_indent.rpy')
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        is_valid, issues = self.validator.validate_script(script_path)
        # Should have warnings about indentation
        self.assertTrue(any('indent' in str(issue).lower() for issue in issues))
    
    def test_missing_colon(self):
        """Test detection of missing colon"""
        script_content = """label start
    "Missing colon above"
"""
        script_path = os.path.join(self.temp_dir, 'test_colon.rpy')
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        is_valid, issues = self.validator.validate_script(script_path)
        # Should detect error
        self.assertFalse(is_valid)


class TestModProcessor(unittest.TestCase):
    """Test mod processor"""
    
    def setUp(self):
        self.config = Config('config.json')
        self.processor = ModProcessor(self.config)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_detect_game_subfolder(self):
        """Test detection of game/ subfolder"""
        # Create mod with game subfolder
        mod_dir = os.path.join(self.temp_dir, 'test_mod')
        game_dir = os.path.join(mod_dir, 'game')
        os.makedirs(game_dir)
        
        has_game, detected_path = self.processor.detect_mod_structure(mod_dir)
        self.assertTrue(has_game)
        self.assertEqual(detected_path, game_dir)
    
    def test_detect_no_subfolder(self):
        """Test detection when no game/ subfolder"""
        mod_dir = os.path.join(self.temp_dir, 'test_mod_no_game')
        os.makedirs(mod_dir)
        
        has_game, detected_path = self.processor.detect_mod_structure(mod_dir)
        self.assertFalse(has_game)
        self.assertEqual(detected_path, mod_dir)
    
    def test_conflict_strategy_new_file(self):
        """Test new file conflict strategy"""
        mod_file = ModFile('source.rpy', 'game/script.rpy', is_script=True)
        mod_file.conflicts = True
        
        new_path = self.processor.apply_conflict_strategy(
            mod_file,
            ConflictStrategy.NEW_FILE,
            mod_priority=1
        )
        
        # Should create z01_script.rpy
        self.assertIn('z01_', new_path)
    
    def test_conflict_strategy_skip(self):
        """Test skip conflict strategy"""
        mod_file = ModFile('source.rpy', 'game/script.rpy', is_script=True)
        mod_file.conflicts = True
        
        new_path = self.processor.apply_conflict_strategy(
            mod_file,
            ConflictStrategy.SKIP,
            mod_priority=1
        )
        
        # Should return empty path
        self.assertEqual(new_path, "")


class TestBackupManager(unittest.TestCase):
    """Test backup manager"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backup_dir = os.path.join(self.temp_dir, 'backups')
        self.manager = BackupManager(self.backup_dir)
        
        # Create test APK
        self.test_apk = os.path.join(self.temp_dir, 'test.apk')
        with open(self.test_apk, 'wb') as f:
            f.write(b'Test APK content')
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_create_backup(self):
        """Test backup creation"""
        entry = self.manager.create_backup(
            self.test_apk,
            game_name="Test Game",
            notes="Test backup"
        )
        
        self.assertIsNotNone(entry)
        self.assertTrue(os.path.exists(entry.backup_path))
        self.assertEqual(entry.game_name, "Test Game")
    
    def test_restore_backup(self):
        """Test backup restoration"""
        # Create backup
        entry = self.manager.create_backup(self.test_apk, "Test")
        
        # Restore to new location
        restore_path = os.path.join(self.temp_dir, 'restored.apk')
        success = self.manager.restore_backup(entry, restore_path)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(restore_path))
    
    def test_delete_backup(self):
        """Test backup deletion"""
        entry = self.manager.create_backup(self.test_apk, "Test")
        backup_path = entry.backup_path
        
        success = self.manager.delete_backup(entry)
        
        self.assertTrue(success)
        self.assertFalse(os.path.exists(backup_path))
    
    def test_cleanup_old_backups(self):
        """Test cleanup of old backups"""
        # Create multiple backups
        for i in range(10):
            self.manager.create_backup(self.test_apk, "Test Game", f"Backup {i}")
        
        # Cleanup (keep only 3)
        deleted = self.manager.cleanup_old_backups(max_backups_per_game=3)
        
        self.assertGreater(deleted, 0)
        self.assertLessEqual(len(self.manager.get_all_backups()), 3)


def run_tests():
    """Run all tests"""
    print("="*60)
    print("AutoModRenpy Test Suite")
    print("="*60)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestScriptValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestModProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestBackupManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("="*60)
    if result.wasSuccessful():
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
