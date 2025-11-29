import unittest
from unittest.mock import MagicMock
from src.ui.controls import MenuController

class TestQuickMenu(unittest.TestCase):
    def setUp(self):
        self.menus = {
            "menus": [
                {
                    "name": "settings",
                    "options": [
                        {"name": "mode", "type": "list", "value": "single", "options": ["single", "timer"]},
                        {"name": "iso", "type": "list", "value": 100, "options": [100, 200]},
                        {"name": "shutter", "type": "list", "value": 0, "options": [0, 1000]},
                        {"name": "awb", "type": "list", "value": "auto", "options": ["auto", "sun"]},
                        {"name": "exposure", "type": "list", "value": "auto", "options": ["auto", "night"]}
                    ]
                }
            ]
        }
        self.camera = MagicMock()
        self.camera.directory.return_value = {
            "mode": MagicMock(),
            "iso": MagicMock(),
            "shutter": MagicMock(),
            "awb": MagicMock(),
            "exposure": MagicMock()
        }

    def test_quick_menu_cycling(self):
        # Initial position 0
        quick_menu_pos = [0]
        
        # Move Right -> 1
        MenuController.handle_event(MagicMock(), None, [0,0,0,0], self.menus, self.camera, menu_active=False, quick_menu_pos=quick_menu_pos, action="right")
        self.assertEqual(quick_menu_pos[0], 1)
        
        # Move Right -> 2
        MenuController.handle_event(MagicMock(), None, [0,0,0,0], self.menus, self.camera, menu_active=False, quick_menu_pos=quick_menu_pos, action="right")
        self.assertEqual(quick_menu_pos[0], 2)
        
        # Move Right -> 3
        MenuController.handle_event(MagicMock(), None, [0,0,0,0], self.menus, self.camera, menu_active=False, quick_menu_pos=quick_menu_pos, action="right")
        self.assertEqual(quick_menu_pos[0], 3)
        
        # Move Right -> 4
        MenuController.handle_event(MagicMock(), None, [0,0,0,0], self.menus, self.camera, menu_active=False, quick_menu_pos=quick_menu_pos, action="right")
        self.assertEqual(quick_menu_pos[0], 4)
        
        # Move Right -> 0 (Loop)
        MenuController.handle_event(MagicMock(), None, [0,0,0,0], self.menus, self.camera, menu_active=False, quick_menu_pos=quick_menu_pos, action="right")
        self.assertEqual(quick_menu_pos[0], 0)

    def test_quick_menu_value_change_mode(self):
        # Position 0 should be Mode
        quick_menu_pos = [0]
        
        # Change Value UP
        MenuController.handle_event(MagicMock(), None, [0,0,0,0], self.menus, self.camera, menu_active=False, quick_menu_pos=quick_menu_pos, action="up")
        
        # Verify 'mode' was changed in camera
        # We need to check if _apply_setting was called for 'mode'
        # Since _apply_setting calls camera.directory()[name](value=...), we check that.
        self.camera.directory.return_value["mode"].assert_called()

    def test_quick_menu_value_change_iso(self):
        # Position 1 should be ISO
        quick_menu_pos = [1]
        
        # Change Value UP
        MenuController.handle_event(MagicMock(), None, [0,0,0,0], self.menus, self.camera, menu_active=False, quick_menu_pos=quick_menu_pos, action="up")
        
        # Verify 'iso' was changed
        self.camera.directory.return_value["iso"].assert_called()

if __name__ == '__main__':
    unittest.main()
