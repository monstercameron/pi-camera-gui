import unittest
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch
import sys

# Mock dependencies
sys.modules['picamera'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['pygame.camera'] = MagicMock()

from src.hardware.camera import MockCamera, CameraBase

class TestCameraBase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.settings = {
            "files": {
                "path": self.test_dir,
                "template": "img_{}_{}"
            },
            "display": {"width": 100, "height": 100, "fullscreen": False}
        }
        self.menus = {}
        
        # Instantiate MockCamera to test Base methods
        self.camera = MockCamera(self.menus, self.settings)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_filename_generation(self):
        # First file
        name1 = self.camera._get_next_filename("jpg")
        self.assertTrue(name1.endswith("_1.jpg"))
        
        # Create it
        with open(name1, 'w') as f: f.write("test")
        
        # Second file
        name2 = self.camera._get_next_filename("jpg")
        self.assertTrue(name2.endswith("_2.jpg"))

    def test_filename_continuity_different_ext(self):
        # Create file 1 as png
        # We need to match the date format in the code: datetime.now().strftime('%Y-%m-%d')
        from datetime import datetime
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        file1 = os.path.join(self.test_dir, f"img_{date_str}_1.png")
        with open(file1, 'w') as f: f.write("test")
        
        # Next file should be 2, even if we ask for jpg
        name2 = self.camera._get_next_filename("jpg")
        self.assertIn("_2.jpg", name2)

    def test_disk_space_calculation(self):
        # Mock shutil.disk_usage
        with patch('shutil.disk_usage') as mock_usage:
            mock_usage.return_value = (1000, 500, 500 * 1024 * 1024) # 500MB free
            
            space = self.camera.get_disk_space()
            self.assertEqual(space, "500MB")

class TestMockCamera(unittest.TestCase):
    def setUp(self):
        self.settings = {
            "files": {"path": "tmp", "template": "{}"},
            "display": {"width": 100, "height": 100}
        }
        self.camera = MockCamera({}, self.settings)

    def test_options_discovery(self):
        opts = self.camera.get_supported_options("awb")
        self.assertIsInstance(opts, list)
        self.assertIn("auto", opts)

    def test_set_get_resolution(self):
        self.camera.resolution_get_set("1920,1080")
        self.assertEqual(self.camera.resolution, (1920, 1080))

    def test_capture_calls_encoder(self):
        # Mock the thread pool
        self.camera.encoder_pool = MagicMock()
        
        self.camera.captureImage()
        
        # Verify submit was called
        self.assertTrue(self.camera.encoder_pool.submit.called)

if __name__ == '__main__':
    unittest.main()
