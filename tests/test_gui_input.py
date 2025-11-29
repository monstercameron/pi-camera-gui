import unittest
from unittest.mock import MagicMock, patch
import pygame
# We need to mock pygame.display.set_mode BEFORE importing GUI if it calls it in __init__
# But GUI imports pygame inside.
# Let's patch pygame.display.set_mode in the test file before creating GUI instance.

from src.ui.gui import GUI

class TestGUIInput(unittest.TestCase):
    @patch('pygame.display.set_mode')
    def setUp(self, mock_set_mode):
        self.settings = {
            "display": {"width": 800, "height": 600, "caption": "Test", "fontsize": 20},
            "controls": {
                "up": {"key": "K_UP", "pin": 21},
                "enter": {"key": "K_RETURN", "pin": 19},
                "back": {"key": "K_BACKSPACE", "pin": 6},
                "quit": {"key": "K_ESCAPE", "pin": None}
            }
        }
        self.menus = {"menus": []}
        self.gui = GUI(self.settings, self.menus)

    def test_get_action_from_event(self):
        # Test UP
        event_up = MagicMock()
        event_up.type = pygame.KEYDOWN
        event_up.key = pygame.K_UP
        self.assertEqual(self.gui._get_action_from_event(event_up), "up")

        # Test ENTER
        event_enter = MagicMock()
        event_enter.type = pygame.KEYDOWN
        event_enter.key = pygame.K_RETURN
        self.assertEqual(self.gui._get_action_from_event(event_enter), "enter")

        # Test BACK
        event_back = MagicMock()
        event_back.type = pygame.KEYDOWN
        event_back.key = pygame.K_BACKSPACE
        self.assertEqual(self.gui._get_action_from_event(event_back), "back")

        # Test QUIT
        event_quit = MagicMock()
        event_quit.type = pygame.KEYDOWN
        event_quit.key = pygame.K_ESCAPE
        self.assertEqual(self.gui._get_action_from_event(event_quit), "quit")

        # Test Unmapped
        event_space = MagicMock()
        event_space.type = pygame.KEYDOWN
        event_space.key = pygame.K_SPACE
        self.assertIsNone(self.gui._get_action_from_event(event_space))

if __name__ == '__main__':
    unittest.main()
