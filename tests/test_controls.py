import unittest
from unittest.mock import MagicMock
from src.ui.controls import MenuController

class TestMenuController(unittest.TestCase):
    def setUp(self):
        self.pygame_mod = MagicMock()
        self.menus = {
            "menus": [
                {
                    "name": "main",
                    "type": "list",
                    "options": [
                        {"name": "sub1", "type": "list", "value": 0, "options": [{"name": "opt1", "value": 1}]},
                        {"name": "open_gallery", "type": "action", "value": "no"}
                    ]
                },
                {
                    "name": "settings",
                    "type": "list",
                    "options": []
                }
            ]
        }
        self.camera = MagicMock()
        # Mock directory
        self.camera.directory.return_value = {}
        
        self.callbacks = {"open_gallery": MagicMock(), "close_menu": MagicMock()}

    def test_navigate_menus(self):
        menu_pos = [0, 0, 0, 0] # Level 0
        
        # Down -> Index 1 (Settings)
        MenuController.handle_event(self.pygame_mod, None, menu_pos, self.menus, action="down")
        self.assertEqual(menu_pos[0], 1)
        
        # Up -> Index 0 (Main)
        MenuController.handle_event(self.pygame_mod, None, menu_pos, self.menus, action="up")
        self.assertEqual(menu_pos[0], 0)

    def test_enter_submenu(self):
        menu_pos = [0, 0, 0, 0]
        # Right -> Level 1
        MenuController.handle_event(self.pygame_mod, None, menu_pos, self.menus, action="right")
        self.assertEqual(menu_pos[3], 1)
        
        # Back -> Level 0
        MenuController.handle_event(self.pygame_mod, None, menu_pos, self.menus, action="back")
        self.assertEqual(menu_pos[3], 0)

    def test_select_value(self):
        menu_pos = [0, 0, 0, 1] # Level 1 (Submenu), Item 0 (sub1)
        # Enter -> Level 2 (Options)
        MenuController.handle_event(self.pygame_mod, None, menu_pos, self.menus, action="enter")
        self.assertEqual(menu_pos[3], 2)
        
        # Enter again -> Select value (and go back to Level 1)
        MenuController.handle_event(self.pygame_mod, None, menu_pos, self.menus, self.camera, action="enter")
        self.assertEqual(menu_pos[3], 1)

    def test_gallery_action(self):
        # Navigate to gallery item (index 1 in submenu of menu 0)
        menu_pos = [0, 1, 0, 1] # Menu 0, Option 1 ("open_gallery"), Level 1
        
        # Enter on gallery option
        # Note: In controls.py, we check for name == "open_gallery" and value == "yes"
        # But here value is "no". The controller sets it to "yes" if we select it?
        # Wait, controls.py logic for list/action:
        # If type is list (which it is by default if not range), it selects the item.
        # If the item is an action (like open_gallery), it usually has options "yes"/"no" or similar?
        # In my mock, "open_gallery" has no "options" list, so it might fail or be treated as leaf.
        # Let's fix the mock to match reality.
        # Usually actions are lists with ["no", "yes"] options.
        
        self.menus["menus"][0]["options"][1]["type"] = "list"
        self.menus["menus"][0]["options"][1]["options"] = [{"name": "no", "value": "no"}, {"name": "yes", "value": "yes"}]
        
        # We are at Level 1. Enter -> Level 2 (Select Yes/No)
        MenuController.handle_event(self.pygame_mod, None, menu_pos, self.menus, action="enter")
        self.assertEqual(menu_pos[3], 2)
        
        # Now at Level 2. We need to select "yes" (index 1).
        # Currently index is 0 ("no").
        menu_pos[2] = 1 # Manually set to "yes" index for test
        
        # Enter to confirm "yes"
        MenuController.handle_event(self.pygame_mod, None, menu_pos, self.menus, self.camera, callbacks=self.callbacks, action="enter")
        
        # Should trigger open_gallery callback
        self.callbacks["open_gallery"].assert_called()

if __name__ == '__main__':
    unittest.main()
