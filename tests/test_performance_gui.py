import unittest
import time
from unittest.mock import MagicMock, patch
import sys
import os
import importlib

# Mock pygame before importing it in gui
sys.modules['pygame'] = MagicMock()
import pygame

# We need to ensure we import the module fresh so it uses our mock
if 'src.ui.gui' in sys.modules:
    del sys.modules['src.ui.gui']
from src.ui.gui import GUI

class TestGUIPerformance(unittest.TestCase):
    def setUp(self):
        # Ensure pygame is mocked correctly for this test
        sys.modules['pygame'] = MagicMock()
        import pygame
        
        # Reload GUI module to ensure it uses the mocked pygame
        if 'src.ui.gui' in sys.modules:
            importlib.reload(sys.modules['src.ui.gui'])
        else:
            import src.ui.gui
        
        from src.ui.gui import GUI
        self.GUI_class = GUI

        self.settings = {
            "display": {
                "width": 800,
                "height": 480,
                "caption": "Test",
                "fontsize": 20,
                "showmenu": True,
                "refreshrate": 60
            },
            "theme": {
                "sizes": {
                    "item_height_main": "50",
                    "font_main": "24",
                    "item_height_sub": "40",
                    "font_sub": "20",
                    "font_stats": "12"
                },
                "colors": {
                    "menu_bg_level_0": "#333333",
                    "menu_bg_level_1": "#444444",
                    "menu_bg_level_2": "#555555",
                    "selected": "#FFFFFF",
                    "unselected": "#AAAAAA",
                    "unselected_dim": "#888888",
                    "selection_bg": "#FFFFFF33",
                    "stats_bg": "#000000",
                    "text_main": "#FFFFFF"
                }
            }
        }
        self.menus = {
            "menus": [
                {
                    "name": "main",
                    "type": "list",
                    "options": [
                        {"name": "opt1", "value": "val1", "type": "list", "options": ["val1"]},
                        {"name": "opt2", "value": "val2", "type": "list", "options": ["val2"]},
                        {"name": "opt3", "value": "val3", "type": "list", "options": ["val3"]},
                        {"name": "opt4", "value": "val4", "type": "list", "options": ["val4"]},
                        {"name": "opt5", "value": "val5", "type": "list", "options": ["val5"]}
                    ]
                }
            ]
        }
        
        # Mock Font and Rect Helper Classes
        class MockRect:
            def __init__(self, x=0, y=0, w=100, h=30):
                self.x = x
                self.y = y
                self.width = w
                self.height = h
            
            def inflate(self, x, y):
                return MockRect(self.x, self.y, self.width + x, self.height + y)
            
            def move(self, x, y):
                return MockRect(self.x + x, self.y + y, self.width, self.height)
                
            @property
            def topleft(self): return (self.x, self.y)
            
            @property
            def midright(self): return (self.x + self.width, self.y + self.height // 2)
            
            @property
            def midleft(self): return (self.x, self.y + self.height // 2)
            
            def __repr__(self):
                return f"MockRect({self.x}, {self.y}, {self.width}, {self.height})"

        def get_rect_side_effect(**kwargs):
            return MockRect(0, 0, 100, 30)

        # Reset mocks
        pygame.display.set_mode = MagicMock()
        
        # Mock Image
        mock_image = MagicMock()
        mock_image.get_width.return_value = 24
        mock_image.get_height.return_value = 24
        mock_image.get_rect.side_effect = get_rect_side_effect
        
        pygame.image.load = MagicMock(return_value=mock_image)
        pygame.transform.scale = MagicMock(return_value=mock_image)
        
        # Fix pygame.time.get_ticks
        pygame.time.get_ticks.return_value = 1000
        
        # Mock os.path.exists
        self.path_patcher = patch('os.path.exists')
        self.mock_exists = self.path_patcher.start()
        self.mock_exists.return_value = True
        
        # Mock Font
        mock_surface = MagicMock()
        mock_surface.get_rect.side_effect = get_rect_side_effect
        mock_surface.get_width.return_value = 100
        mock_surface.get_height.return_value = 30
        
        mock_font = MagicMock()
        mock_font.render.return_value = mock_surface
        
        pygame.font.Font.return_value = mock_font

        self.gui = self.GUI_class(self.settings, self.menus)
        # Force layout load
        if self.gui.layout:
            self.gui.layout.load_layout("default")

    def tearDown(self):
        self.path_patcher.stop()

    def test_render_performance(self):
        # Reset call count before test
        pygame.image.load.reset_mock()
        
        # Measure time to render menu 100 times
        start_time = time.time()
        for _ in range(100):
            self.gui._render_menu()
        duration = time.time() - start_time
        
        print(f"\nGUI Render Performance (100 frames): {duration:.4f}s")
        print(f"Image Load Call Count: {pygame.image.load.call_count}")
        
        # Assert that image.load was called roughly 5 times (once per item)
        # It might be slightly more if icons are loaded for other things, but definitely not 500
        self.assertLess(pygame.image.load.call_count, 20, "Image loading should be cached!")

if __name__ == '__main__':
    unittest.main()
