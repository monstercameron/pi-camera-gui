import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Mock pygame before importing Gallery
sys.modules['pygame'] = MagicMock()
import pygame

# Configure pygame mock
pygame.time.get_ticks = MagicMock(return_value=0)
pygame.font.Font = MagicMock(return_value=MagicMock())

from src.ui.gallery import Gallery

class TestGallery(unittest.TestCase):
    def setUp(self):
        self.settings = {
            "files": {"path": "test/path"},
            "display": {"fontsize": 20}
        }
        
        self.gallery = Gallery(self.settings)
        # Mock buffer update to avoid side effects in basic tests
        self.gallery._update_buffer = MagicMock()

    @patch('os.path.exists')
    @patch('os.listdir')
    def test_refresh_files(self, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ["image1.jpg", "image2.png", "text.txt", "image3.BMP"]
        
        self.gallery.refresh_files()
        
        self.assertEqual(len(self.gallery.files), 3)
        self.assertIn("image1.jpg", self.gallery.files)
        self.assertIn("image2.png", self.gallery.files)
        self.assertIn("image3.BMP", self.gallery.files)
        self.assertNotIn("text.txt", self.gallery.files)

    @patch('os.path.exists')
    def test_refresh_files_no_path(self, mock_exists):
        mock_exists.return_value = False
        self.gallery.refresh_files()
        self.assertEqual(self.gallery.files, [])

    @patch('src.ui.gallery.Image')
    @patch('os.path.getsize')
    @patch('os.path.exists')
    def test_get_image_metadata(self, mock_exists, mock_getsize, mock_image):
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024 * 2.5 # 2.5 MB
        
        # Mock Image object
        mock_img_instance = MagicMock()
        mock_img_instance.width = 1920
        mock_img_instance.height = 1080
        mock_img_instance._getexif.return_value = {
            36867: "2025:11:28 12:00:00", # DateTimeOriginal
            306: "2025:11:28 12:00:00"    # DateTime
        }
        
        # Context manager mock
        mock_image.open.return_value.__enter__.return_value = mock_img_instance
        
        metadata = self.gallery._get_image_metadata("test.jpg")
        
        self.assertEqual(metadata["File"], "test.jpg")
        self.assertEqual(metadata["Size"], "2.5 MB")
        self.assertEqual(metadata["Resolution"], "1920x1080")
        self.assertEqual(metadata["Date"], "2025:11:28 12:00:00")

    @patch('src.ui.gallery.Image')
    @patch('os.path.getsize')
    @patch('os.path.exists')
    def test_get_image_metadata_no_exif(self, mock_exists, mock_getsize, mock_image):
        mock_exists.return_value = True
        mock_getsize.return_value = 500 # 500 B
        
        mock_img_instance = MagicMock()
        mock_img_instance.width = 800
        mock_img_instance.height = 600
        mock_img_instance._getexif.return_value = None
        
        mock_image.open.return_value.__enter__.return_value = mock_img_instance
        
        metadata = self.gallery._get_image_metadata("test.png")
        
        self.assertEqual(metadata["Size"], "500 B")
        self.assertEqual(metadata["Resolution"], "800x600")
        self.assertEqual(metadata["Date"], "Unknown")

    def test_navigation(self):
        self.gallery.files = ["1.jpg", "2.jpg", "3.jpg"]
        self.gallery.active = True
        self.gallery.current_index = 0
        
        # Test Right
        self.gallery.handle_event(None, action="right")
        self.assertTrue(self.gallery.animating)
        self.assertEqual(self.gallery.target_index, 1)
        self.assertEqual(self.gallery.direction, 1)
        
        # Reset
        self.gallery.animating = False
        self.gallery.current_index = 1
        
        # Test Left
        self.gallery.handle_event(None, action="left")
        self.assertTrue(self.gallery.animating)
        self.assertEqual(self.gallery.target_index, 0)
        self.assertEqual(self.gallery.direction, -1)

if __name__ == '__main__':
    unittest.main()
