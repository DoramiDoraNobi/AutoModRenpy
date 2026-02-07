import unittest
import os
import shutil
import tempfile
from src.android_features import AndroidFeatures

class TestAndroidFeatures(unittest.TestCase):

    def setUp(self):
        self.features = AndroidFeatures()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_inject_hotkeys(self):
        result = self.features.inject_hotkeys(self.temp_dir)
        self.assertTrue(result)

        buttons_path = os.path.join(self.temp_dir, 'android_buttons.rpy')
        self.assertTrue(os.path.exists(buttons_path))

        with open(buttons_path, 'r') as f:
            content = f.read()
            self.assertIn('screen mobile_overlay', content)
            self.assertIn('config.overlay_screens.append', content)

    def test_inject_config(self):
        result = self.features.inject_android_config(self.temp_dir)
        self.assertTrue(result)

        config_path = os.path.join(self.temp_dir, 'android_config.rpy')
        self.assertTrue(os.path.exists(config_path))

        with open(config_path, 'r') as f:
            content = f.read()
            self.assertIn('config.variants', content)

if __name__ == '__main__':
    unittest.main()
