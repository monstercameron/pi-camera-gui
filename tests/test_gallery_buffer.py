"""
Unit and component tests for Gallery buffer system.
Tests the ±25 image sliding buffer that manages RAM usage.
"""
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os
import threading
import time

# Mock pygame before importing Gallery
sys.modules['pygame'] = MagicMock()
import pygame

# Configure pygame mock
pygame.time.get_ticks = MagicMock(return_value=0)
pygame.font.Font = MagicMock(return_value=MagicMock())


class TestGalleryBufferIndices(unittest.TestCase):
    """Unit tests for buffer index calculation."""
    
    def setUp(self):
        self.settings = {
            "files": {"path": "test/path"},
            "display": {"fontsize": 20}
        }
        from src.ui.gallery import Gallery
        self.gallery = Gallery(self.settings)
    
    def test_buffer_indices_at_start(self):
        """Buffer at index 0 should include indices 0 to BUFFER_SIZE."""
        self.gallery.files = [f"{i}.jpg" for i in range(100)]
        self.gallery.current_index = 0
        
        indices = self.gallery._get_buffer_indices(0)
        
        # Should include 0 to 25 (26 items)
        self.assertEqual(len(indices), self.gallery.BUFFER_SIZE + 1)
        self.assertIn(0, indices)
        self.assertIn(25, indices)
        self.assertNotIn(-1, indices)  # No negative indices
        self.assertNotIn(26, indices)
    
    def test_buffer_indices_at_end(self):
        """Buffer at last index should include last BUFFER_SIZE items."""
        self.gallery.files = [f"{i}.jpg" for i in range(100)]
        self.gallery.current_index = 99
        
        indices = self.gallery._get_buffer_indices(99)
        
        # Should include 74 to 99 (26 items)
        self.assertEqual(len(indices), self.gallery.BUFFER_SIZE + 1)
        self.assertIn(99, indices)
        self.assertIn(74, indices)
        self.assertNotIn(100, indices)  # No out-of-bounds
    
    def test_buffer_indices_in_middle(self):
        """Buffer in middle should include ±BUFFER_SIZE items."""
        self.gallery.files = [f"{i}.jpg" for i in range(100)]
        self.gallery.current_index = 50
        
        indices = self.gallery._get_buffer_indices(50)
        
        # Should include 25 to 75 (51 items)
        expected_count = 2 * self.gallery.BUFFER_SIZE + 1
        self.assertEqual(len(indices), expected_count)
        self.assertIn(50, indices)
        self.assertIn(25, indices)
        self.assertIn(75, indices)
    
    def test_buffer_indices_small_gallery(self):
        """Buffer with fewer files than buffer size should include all."""
        self.gallery.files = [f"{i}.jpg" for i in range(10)]
        self.gallery.current_index = 5
        
        indices = self.gallery._get_buffer_indices(5)
        
        # Should include all 10 items
        self.assertEqual(len(indices), 10)
        for i in range(10):
            self.assertIn(i, indices)
    
    def test_buffer_indices_empty_gallery(self):
        """Empty gallery should return empty set."""
        self.gallery.files = []
        
        indices = self.gallery._get_buffer_indices(0)
        
        self.assertEqual(len(indices), 0)
    
    def test_buffer_indices_single_image(self):
        """Single image gallery should return only index 0."""
        self.gallery.files = ["only.jpg"]
        self.gallery.current_index = 0
        
        indices = self.gallery._get_buffer_indices(0)
        
        self.assertEqual(indices, {0})


class TestGalleryBufferUpdate(unittest.TestCase):
    """Unit tests for buffer update logic."""
    
    def setUp(self):
        self.settings = {
            "files": {"path": "test/path"},
            "display": {"fontsize": 20}
        }
        from src.ui.gallery import Gallery
        self.gallery = Gallery(self.settings)
        self.gallery._load_image_async = MagicMock()  # Mock async loading
    
    def test_update_buffer_loads_missing_images(self):
        """Should trigger async load for images not in cache."""
        self.gallery.files = [f"{i}.jpg" for i in range(100)]
        self.gallery.current_index = 50
        self.gallery.image_cache = {}  # Empty cache
        
        self.gallery._update_buffer(50)
        
        # Should have called _load_image_async for all buffer indices
        expected_calls = 2 * self.gallery.BUFFER_SIZE + 1
        self.assertEqual(self.gallery._load_image_async.call_count, expected_calls)
    
    def test_update_buffer_skips_cached_images(self):
        """Should not reload images already in cache."""
        self.gallery.files = [f"{i}.jpg" for i in range(100)]
        self.gallery.current_index = 50
        
        # Pre-populate cache with some images
        for i in range(45, 56):
            filepath = os.path.join(self.gallery.path, f"{i}.jpg")
            self.gallery.image_cache[filepath] = MagicMock()
        
        self.gallery._update_buffer(50)
        
        # Should only load images NOT in cache
        # Buffer is 25-75 (51 images), 11 already cached (45-55)
        expected_calls = 51 - 11
        self.assertEqual(self.gallery._load_image_async.call_count, expected_calls)
    
    def test_update_buffer_unloads_distant_images(self):
        """Should remove images outside new buffer window."""
        self.gallery.files = [f"{i}.jpg" for i in range(100)]
        
        # Cache has images from old position (around index 10)
        for i in range(0, 20):
            filepath = os.path.join(self.gallery.path, f"{i}.jpg")
            self.gallery.image_cache[filepath] = MagicMock()
        
        # Move to new position (index 80)
        self.gallery._update_buffer(80)
        
        # Old images (0-19) should be removed as they're outside 55-99 range
        for i in range(0, 20):
            filepath = os.path.join(self.gallery.path, f"{i}.jpg")
            self.assertNotIn(filepath, self.gallery.image_cache)
    
    def test_update_buffer_skips_loading_indices(self):
        """Should not re-trigger load for images already being loaded."""
        self.gallery.files = [f"{i}.jpg" for i in range(100)]
        self.gallery.current_index = 50
        self.gallery.image_cache = {}
        
        # Mark some indices as currently loading
        self.gallery._loading_indices = {48, 49, 50, 51, 52}
        
        self.gallery._update_buffer(50)
        
        # Should not attempt to load indices that are already loading
        for call in self.gallery._load_image_async.call_args_list:
            idx = call[0][0]
            self.assertNotIn(idx, {48, 49, 50, 51, 52})


class TestGalleryNavigation(unittest.TestCase):
    """Tests for navigation with buffer updates."""
    
    def setUp(self):
        self.settings = {
            "files": {"path": "test/path"},
            "display": {"fontsize": 20}
        }
        from src.ui.gallery import Gallery
        self.gallery = Gallery(self.settings)
        self.gallery._update_buffer = MagicMock()
        pygame.time.get_ticks.return_value = 1000
    
    def test_navigate_right_updates_buffer(self):
        """Moving right should update buffer for new position."""
        self.gallery.files = [f"{i}.jpg" for i in range(100)]
        self.gallery.active = True
        self.gallery.current_index = 50
        self.gallery.animating = False
        
        self.gallery.handle_event(None, action="right")
        
        self.gallery._update_buffer.assert_called_once_with(51)
    
    def test_navigate_left_updates_buffer(self):
        """Moving left should update buffer for new position."""
        self.gallery.files = [f"{i}.jpg" for i in range(100)]
        self.gallery.active = True
        self.gallery.current_index = 50
        self.gallery.animating = False
        
        self.gallery.handle_event(None, action="left")
        
        self.gallery._update_buffer.assert_called_once_with(49)
    
    def test_navigate_during_animation_blocked(self):
        """Should not navigate or update buffer while animating."""
        self.gallery.files = [f"{i}.jpg" for i in range(100)]
        self.gallery.active = True
        self.gallery.current_index = 50
        self.gallery.animating = True  # Animation in progress
        
        self.gallery.handle_event(None, action="right")
        
        self.gallery._update_buffer.assert_not_called()
    
    def test_wrap_around_right(self):
        """Navigating right at end should wrap to beginning."""
        self.gallery.files = [f"{i}.jpg" for i in range(10)]
        self.gallery.active = True
        self.gallery.current_index = 9
        self.gallery.animating = False
        
        self.gallery.handle_event(None, action="right")
        
        self.assertEqual(self.gallery.target_index, 0)
        self.gallery._update_buffer.assert_called_once_with(0)
    
    def test_wrap_around_left(self):
        """Navigating left at beginning should wrap to end."""
        self.gallery.files = [f"{i}.jpg" for i in range(10)]
        self.gallery.active = True
        self.gallery.current_index = 0
        self.gallery.animating = False
        
        self.gallery.handle_event(None, action="left")
        
        self.assertEqual(self.gallery.target_index, 9)
        self.gallery._update_buffer.assert_called_once_with(9)


class TestGalleryEnterExit(unittest.TestCase):
    """Tests for gallery enter/exit with buffer management."""
    
    def setUp(self):
        self.settings = {
            "files": {"path": "test/path"},
            "display": {"fontsize": 20}
        }
        from src.ui.gallery import Gallery
        self.gallery = Gallery(self.settings)
    
    @patch('os.path.exists')
    @patch('os.listdir')
    def test_enter_initializes_buffer(self, mock_listdir, mock_exists):
        """Entering gallery should start loading buffer around newest image."""
        mock_exists.return_value = True
        mock_listdir.return_value = [f"{i}.jpg" for i in range(50)]
        
        with patch.object(self.gallery, '_update_buffer') as mock_update:
            self.gallery.enter()
            
            mock_update.assert_called_once()
            self.assertEqual(self.gallery.current_index, 49)  # Newest
    
    def test_exit_clears_cache(self):
        """Exiting gallery should clear image cache to free RAM."""
        self.gallery.image_cache = {
            "path/1.jpg": MagicMock(),
            "path/2.jpg": MagicMock(),
            "path/3.jpg": MagicMock(),
        }
        self.gallery._loading_indices = {1, 2, 3}
        self.gallery.active = True
        
        self.gallery.exit()
        
        self.assertEqual(len(self.gallery.image_cache), 0)
        self.assertEqual(len(self.gallery._loading_indices), 0)
        self.assertFalse(self.gallery.active)


class TestGalleryLoadingIndicator(unittest.TestCase):
    """Tests for loading indicator when buffer is outrun."""
    
    def setUp(self):
        self.settings = {
            "files": {"path": "test/path"},
            "display": {"fontsize": 20}
        }
        from src.ui.gallery import Gallery
        self.gallery = Gallery(self.settings)
    
    def test_draw_image_shows_loading_when_async_loading(self):
        """Should show loading indicator when image is being loaded async."""
        self.gallery.files = ["test.jpg"]
        self.gallery._loading_indices = {0}  # Image is being loaded
        self.gallery.image_cache = {}  # Not in cache yet
        
        surface = MagicMock()
        surface.get_size.return_value = (480, 320)
        
        with patch.object(self.gallery, '_draw_loading_indicator') as mock_loading:
            self.gallery._draw_image(surface, "test.jpg", 0)
            
            mock_loading.assert_called_once_with(surface, 0)
    
    @patch('os.path.exists')
    def test_draw_image_sync_fallback_when_not_loading(self, mock_exists):
        """Should do sync load when not in cache and not async loading."""
        mock_exists.return_value = True
        self.gallery.files = ["test.jpg"]
        self.gallery._loading_indices = set()  # Not loading
        self.gallery.image_cache = {}  # Not cached
        
        # Mock pygame image loading
        mock_img = MagicMock()
        mock_img.get_size.return_value = (800, 600)
        mock_img.get_rect.return_value = MagicMock(center=(0, 0))
        pygame.image.load.return_value = mock_img
        pygame.transform.scale.return_value = mock_img
        
        surface = MagicMock()
        surface.get_size.return_value = (480, 320)
        surface.get_rect.return_value = MagicMock(center=(240, 160))
        
        self.gallery._draw_image(surface, "test.jpg", 0)
        
        # Should have loaded synchronously
        pygame.image.load.assert_called()


class TestGalleryThreadSafety(unittest.TestCase):
    """Tests for thread-safe cache access."""
    
    def setUp(self):
        self.settings = {
            "files": {"path": "test/path"},
            "display": {"fontsize": 20}
        }
        from src.ui.gallery import Gallery
        self.gallery = Gallery(self.settings)
    
    def test_cache_lock_exists(self):
        """Gallery should have a threading lock for cache access."""
        self.assertIsInstance(self.gallery._cache_lock, type(threading.Lock()))
    
    def test_loading_indices_tracking(self):
        """Should track which indices are being loaded."""
        self.assertIsInstance(self.gallery._loading_indices, set)
    
    def test_concurrent_buffer_updates(self):
        """Simulate concurrent buffer updates don't cause race conditions."""
        self.gallery.files = [f"{i}.jpg" for i in range(100)]
        self.gallery._load_image_async = MagicMock()
        
        errors = []
        
        def update_buffer_thread(center):
            try:
                for _ in range(10):
                    self.gallery._update_buffer(center)
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=update_buffer_thread, args=(25,)),
            threading.Thread(target=update_buffer_thread, args=(50,)),
            threading.Thread(target=update_buffer_thread, args=(75,)),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0, f"Thread errors: {errors}")


class TestGalleryBufferSize(unittest.TestCase):
    """Tests for buffer size constant."""
    
    def setUp(self):
        self.settings = {
            "files": {"path": "test/path"},
            "display": {"fontsize": 20}
        }
        from src.ui.gallery import Gallery
        self.gallery = Gallery(self.settings)
    
    def test_buffer_size_is_25(self):
        """Buffer size should be 25 (±25 images)."""
        self.assertEqual(self.gallery.BUFFER_SIZE, 25)
    
    def test_max_cached_images(self):
        """Maximum cached images should be 51 (25 + 1 + 25)."""
        self.gallery.files = [f"{i}.jpg" for i in range(1000)]
        
        indices = self.gallery._get_buffer_indices(500)
        
        # In the middle, we get full buffer: 500-25 to 500+25 = 51 images
        self.assertEqual(len(indices), 51)


if __name__ == '__main__':
    unittest.main()
