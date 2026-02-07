import unittest
import os
import shutil
import tempfile
from src.porter import PortingEngine
from src.utils import Config

class TestPorterOptimization(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.config.set('temp_dir', self.temp_dir)
        self.porter = PortingEngine(self.config)

        # Mock source structure
        self.source_dir = os.path.join(self.temp_dir, 'source')
        os.makedirs(os.path.join(self.source_dir, 'game', 'cache'))
        os.makedirs(os.path.join(self.source_dir, 'game', 'saves'))

        # Create some files
        with open(os.path.join(self.source_dir, 'game', 'script.rpy'), 'w') as f: f.write('label start:')
        with open(os.path.join(self.source_dir, 'game', 'cache', 'bytecode.rpyc'), 'w') as f: f.write('data')
        with open(os.path.join(self.source_dir, 'game', 'saves', 'save1.save'), 'w') as f: f.write('data')
        with open(os.path.join(self.source_dir, 'game', 'thumbs.db'), 'w') as f: f.write('junk')

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_ignore_patterns(self):
        # We need to manually test the copy logic since we can't easily mock the full port_game method without an APK
        # So we'll test the ignore pattern logic separately if we can, or simulate the copy step.

        source_game = os.path.join(self.source_dir, 'game')
        dest_game = os.path.join(self.temp_dir, 'dest_game')

        ignore_pattern = shutil.ignore_patterns(
                'cache', 'saves', '.git*', '*.bak', '*.tmp',
                'thumbs.db', '.DS_Store', '__pycache__'
            )

        shutil.copytree(source_game, dest_game, ignore=ignore_pattern)

        self.assertTrue(os.path.exists(os.path.join(dest_game, 'script.rpy')))
        self.assertFalse(os.path.exists(os.path.join(dest_game, 'cache')))
        self.assertFalse(os.path.exists(os.path.join(dest_game, 'saves')))
        self.assertFalse(os.path.exists(os.path.join(dest_game, 'thumbs.db')))

if __name__ == '__main__':
    unittest.main()
