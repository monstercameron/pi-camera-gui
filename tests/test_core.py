import unittest
import os
import shutil
import tempfile
import json
import time
from unittest.mock import patch
from src.core.database import DatabaseManager
from src.core.settings import SettingsManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test_settings.db')
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        if hasattr(self, 'db'):
            self.db.close()
        # Give the OS a moment to release the file lock
        # time.sleep(0.1) 
        try:
            shutil.rmtree(self.test_dir)
        except PermissionError:
            # Retry once if Windows is being slow
            time.sleep(0.5)
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_creates_file(self):
        self.assertTrue(os.path.exists(self.db_path))

    def test_set_get_setting(self):
        self.db.set_setting('test_key', 'test_value')
        value = self.db.get_setting('test_key')
        self.assertEqual(value, 'test_value')

    def test_get_nonexistent_setting(self):
        value = self.db.get_setting('nonexistent')
        self.assertIsNone(value)

    def test_update_setting(self):
        self.db.set_setting('key', 'value1')
        self.db.set_setting('key', 'value2')
        self.assertEqual(self.db.get_setting('key'), 'value2')

    def test_reset_settings(self):
        self.db.set_setting('key1', 'value1')
        self.db.reset_settings()
        self.assertIsNone(self.db.get_setting('key1'))

    def test_persistence(self):
        self.db.set_setting('persist', 'true')
        # Create new instance pointing to same file
        new_db = DatabaseManager(self.db_path)
        try:
            self.assertEqual(new_db.get_setting('persist'), 'true')
        finally:
            new_db.close()

    def test_performance_write(self):
        start_time = time.time()
        # Use batch commit for performance
        for i in range(1000):
            self.db.set_setting(f'key_{i}', f'value_{i}', commit=False)
        self.db.commit()
        duration = time.time() - start_time
        print(f"\nDatabase Write Performance (1000 items): {duration:.4f}s")
        # Assert it's reasonably fast (e.g., < 2 seconds for SQLite on typical hardware)
        self.assertLess(duration, 2.0)

class TestConfig(unittest.TestCase):
    def test_mock_defaults(self):
        # Mock is_module_available to avoid issues with sys.modules mocking in other tests
        with patch('src.core.config.is_module_available') as mock_avail:
            mock_avail.return_value = False # Simulate module missing
            
            from src.core.config import Config
            c = Config()
            # On Windows (where tests run), these should be True
            if os.name == 'nt':
                self.assertTrue(c.USE_MOCK_GPIO)
                # USE_MOCK_CAMERA depends on is_module_available('picamera')
                # If we return False (missing), it should be True
                self.assertTrue(c.USE_MOCK_CAMERA)

    def test_env_overrides(self):
        with patch.dict(os.environ, {'MOCK_CAMERA': 'false', 'MOCK_GPIO': 'false'}):
            from src.core.config import Config
            c = Config()
            self.assertFalse(c.USE_MOCK_CAMERA)
            self.assertFalse(c.USE_MOCK_GPIO)

class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.test_dir, 'camerasettings.json')
        self.menus_file = os.path.join(self.test_dir, 'menusettings.json')
        self.db_path = os.path.join(self.test_dir, 'settings.db')
        
        # Create placeholder config files
        with open(self.settings_file, 'w') as f:
            json.dump({"files": {"path": self.test_dir}}, f)
            
        with open(self.menus_file, 'w') as f:
            json.dump({
                "menus": [
                    {
                        "name": "test_menu",
                        "options": [
                            {"name": "opt1", "value": "default", "type": "list"},
                            {"name": "opt2", "value": 10, "type": "range"}
                        ]
                    }
                ]
            }, f)

        # Patch DatabaseManager to use test path
        # Since we can't easily patch the internal instantiation without mocking,
        # we'll rely on the fact that SettingsManager uses the default or we modify it to accept a db instance.
        # Actually, SettingsManager instantiates DatabaseManager() with default args in __init__.
        # We should modify SettingsManager to accept a db_path or db instance for better testing,
        # but for now we can monkeypatch the class or just rely on the fact that we can't easily change the path 
        # without modifying the code.
        # WAIT: SettingsManager hardcodes DatabaseManager().
        # I will modify SettingsManager in the test setup to use a custom DB path if possible, 
        # or I will mock the DatabaseManager class.
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_defaults(self):
        # We need to mock DatabaseManager to avoid writing to real home/config
        # Or we can just let it write to a temp location if we could inject it.
        # Let's use unittest.mock
        from unittest.mock import patch, MagicMock
        
        with patch('src.core.settings.DatabaseManager') as MockDB:
            mock_db_instance = MockDB.return_value
            mock_db_instance.get_setting.return_value = None # No overrides
            
            manager = SettingsManager(self.settings_file, self.menus_file)
            settings, menus = manager.load()
            
            self.assertEqual(menus['menus'][0]['options'][0]['value'], 'default')

    def test_overlay_db_values(self):
        from unittest.mock import patch
        
        with patch('src.core.settings.DatabaseManager') as MockDB:
            mock_db_instance = MockDB.return_value
            # Mock DB returning an override
            def side_effect(key):
                if key == 'opt1': return 'overridden'
                return None
            mock_db_instance.get_setting.side_effect = side_effect
            
            manager = SettingsManager(self.settings_file, self.menus_file)
            settings, menus = manager.load()
            
            self.assertEqual(menus['menus'][0]['options'][0]['value'], 'overridden')

    def test_save_updates_db(self):
        from unittest.mock import patch
        
        with patch('src.core.settings.DatabaseManager') as MockDB:
            mock_db_instance = MockDB.return_value
            
            manager = SettingsManager(self.settings_file, self.menus_file)
            manager.load()
            
            # Change a value
            manager.menus['menus'][0]['options'][0]['value'] = 'new_value'
            manager.save()
            
            # Verify set_setting was called
            mock_db_instance.set_setting.assert_any_call('opt1', 'new_value')

if __name__ == '__main__':
    unittest.main()
