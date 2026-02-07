import unittest
import os
import shutil
import tempfile
from src.image_optimizer import ImageOptimizer

class TestImageOptimizerResolution(unittest.TestCase):

    def setUp(self):
        self.optimizer = ImageOptimizer()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_manual_resolution_valid(self):
        # Create a dummy image
        img_path = os.path.join(self.temp_dir, 'test.png')
        # We can't easily create a real image without PIL dependencies in test env (wait, pillow is installed)
        # But we can check the logic flow by mocking _get_current_resolution to fail

        # Override _get_current_resolution to return None
        self.optimizer._get_current_resolution = lambda x: (None, None)

        # This should fail without manual res
        result = self.optimizer.resize_images(self.temp_dir, target_height=720)
        self.assertFalse(result)

        # This should pass logic check (though image resizing loop won't find images)
        # Wait, if no images, it returns True (count=0)
        result = self.optimizer.resize_images(self.temp_dir, target_height=720, manual_resolution="1920x1080")
        self.assertTrue(result)

    def test_manual_resolution_invalid(self):
        result = self.optimizer.resize_images(self.temp_dir, target_height=720, manual_resolution="invalid")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
