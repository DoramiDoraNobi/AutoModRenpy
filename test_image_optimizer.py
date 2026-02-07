import unittest
import os
import shutil
import tempfile
from src.image_optimizer import ImageOptimizer

class TestImageOptimizer(unittest.TestCase):

    def setUp(self):
        self.optimizer = ImageOptimizer()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_resolution_gui_init(self):
        gui_rpy = os.path.join(self.temp_dir, 'gui.rpy')
        with open(gui_rpy, 'w') as f:
            f.write("gui.init(1920, 1080)")

        w, h = self.optimizer._get_current_resolution(self.temp_dir)
        self.assertEqual(w, 1920)
        self.assertEqual(h, 1080)

    def test_resolution_gui_init_spaces(self):
        gui_rpy = os.path.join(self.temp_dir, 'gui.rpy')
        with open(gui_rpy, 'w') as f:
            f.write("gui.init ( 1280 , 720 )")

        w, h = self.optimizer._get_current_resolution(self.temp_dir)
        self.assertEqual(w, 1280)
        self.assertEqual(h, 720)

    def test_resolution_config_screen(self):
        options_rpy = os.path.join(self.temp_dir, 'options.rpy')
        with open(options_rpy, 'w') as f:
            f.write("define config.screen_width = 800\ndefine config.screen_height = 600")

        w, h = self.optimizer._get_current_resolution(self.temp_dir)
        self.assertEqual(w, 800)
        self.assertEqual(h, 600)

    def test_resolution_config_screen_legacy(self):
        options_rpy = os.path.join(self.temp_dir, 'options.rpy')
        with open(options_rpy, 'w') as f:
            f.write("config.screen_width = 1024\nconfig.screen_height = 768")

        w, h = self.optimizer._get_current_resolution(self.temp_dir)
        self.assertEqual(w, 1024)
        self.assertEqual(h, 768)

    def test_resolution_not_found(self):
        w, h = self.optimizer._get_current_resolution(self.temp_dir)
        self.assertIsNone(w)
        self.assertIsNone(h)

if __name__ == '__main__':
    unittest.main()
