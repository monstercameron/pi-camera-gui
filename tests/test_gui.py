import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock pygame
sys.modules['pygame'] = MagicMock()
import pygame

from src.ui.gui import GUI

class TestGUI(unittest.TestCase):
    def setUp(self):
        self.settings = {
            "display": {
                "width": 800,
                "height": 480,
                "caption": "Test",
                "fontsize": 20,
                "showmenu": True,
                "refreshrate": 60
            },
            "theme": {}
        }
        self.menus = {"menus": []}
        
        # Mock pygame.display.set_mode
        pygame.display.set_mode = MagicMock()
        
        self.gui = GUI(self.settings, self.menus)

    def test_parse_dimension_pixels(self):
        val = self.gui._parse_dimension("100", 1000)
        self.assertEqual(val, 100)

    def test_parse_dimension_percent(self):
        val = self.gui._parse_dimension("50%", 1000)
        self.assertEqual(val, 500)

    def test_parse_dimension_center(self):
        val = self.gui._parse_dimension("center", 1000)
        self.assertEqual(val, 500)

    def test_parse_color_hex6(self):
        val = self.gui._parse_color("#FF0000")
        self.assertEqual(val, (255, 0, 0))

    def test_parse_color_hex8(self):
        val = self.gui._parse_color("#FF000080")
        self.assertEqual(val, (255, 0, 0, 128))

    def test_parse_color_no_hash(self):
        val = self.gui._parse_color("00FF00")
        self.assertEqual(val, (0, 255, 0))

if __name__ == '__main__':
    unittest.main()
