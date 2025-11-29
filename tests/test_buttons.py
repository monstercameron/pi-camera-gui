import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock pygame
sys.modules['pygame'] = MagicMock()
import pygame

from src.hardware.buttons import Buttons, MockButton

class TestButtons(unittest.TestCase):
    def setUp(self):
        self.settings = {
            "controls": {
                "btn1": {"key": 1, "pin": 17},
                "btn2": {"key": 2, "pin": 27}
            }
        }

    def test_initialization(self):
        buttons = Buttons(self.settings)
        self.assertIn("btn1", buttons.buttons)
        self.assertIn("btn2", buttons.buttons)
        self.assertIsInstance(buttons.buttons["btn1"]["button"], MockButton)

    def test_listen_posts_event(self):
        buttons = Buttons(self.settings)
        
        # Simulate button press
        buttons.buttons["btn1"]["button"].is_pressed = True
        
        # Mock pygame methods
        pygame.event.post = MagicMock()
        pygame.event.Event = MagicMock()
        pygame.time.get_ticks = MagicMock(return_value=1000)
        
        # Run listen once
        buttons.listen(pygame)
            
        # Verify Event creation
        pygame.event.Event.assert_called_with(pygame.KEYDOWN, key=1)
        
        # Verify event posted
        pygame.event.post.assert_called()
        expected_event = pygame.event.Event.return_value
        pygame.event.post.assert_called_with(expected_event)

    def test_listen_debounce(self):
        buttons = Buttons(self.settings)
        buttons.buttons["btn1"]["button"].is_pressed = True
        
        pygame.event.post = MagicMock()
        pygame.time.get_ticks = MagicMock()
        
        # First press at t=1000
        pygame.time.get_ticks.return_value = 1000
        buttons.listen(pygame)
        pygame.event.post.assert_called_once()
        
        pygame.event.post.reset_mock()
        
        # Second check at t=1100 (100ms later, < initial delay 300ms)
        pygame.time.get_ticks.return_value = 1100
        buttons.listen(pygame)
        pygame.event.post.assert_not_called()
        
        # Third check at t=1350 (350ms later, > initial delay 300ms)
        pygame.time.get_ticks.return_value = 1350
        buttons.listen(pygame)
        pygame.event.post.assert_called_once()
        
        pygame.event.post.reset_mock()
        
        # Fourth check at t=1360 (10ms later, < repeat interval 50ms)
        pygame.time.get_ticks.return_value = 1360
        buttons.listen(pygame)
        pygame.event.post.assert_not_called()
        
        # Fifth check at t=1410 (60ms later, > repeat interval 50ms)
        pygame.time.get_ticks.return_value = 1410
        buttons.listen(pygame)
        pygame.event.post.assert_called_once()

if __name__ == '__main__':
    unittest.main()
