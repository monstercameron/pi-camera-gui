import unittest
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch
import sys

# Mock pygame before importing modules that use it
sys.modules['pygame'] = MagicMock()
import pygame

from src.ui.controls import MenuController
from src.ui.layout_parser import LayoutParser

class TestMenuController(unittest.TestCase):
    def setUp(self):
        self.menus = {
            "menus": [
                {
                    "name": "main",
                    "type": "list",
                    "options": [
                        {
                            "name": "opt1",
                            "type": "list",
                            "value": "val1",
                            "options": ["val1", "val2"]
                        },
                        {
                            "name": "opt2",
                            "type": "range",
                            "value": 10,
                            "options": {"min": 0, "max": 20, "step": 5}
                        }
                    ]
                }
            ]
        }
        # [menu_index, submenu_index, option_index, level]
        self.menu_pos = [0, 0, 0, 0]
        self.camera = MagicMock()
        self.camera.directory.return_value = {"opt1": MagicMock(), "opt2": MagicMock()}

    def test_navigation_down(self):
        # Level 0: Main Menu (only 1 item in this test structure, so down shouldn't move if limit is 1)
        # Wait, structure is menus -> [menu1]. So len is 1.
        # If I add another menu
        self.menus["menus"].append({"name": "menu2", "options": []})
        
        # Down
        MenuController._handle_vertical_input(-1, self.menu_pos, self.menus, self.camera)
        # Direction -1 (DOWN) usually increments index in this codebase logic?
        # Let's check controls.py:
        # if direction > 0: if current_index >= 1: menu_pos -= 1 (UP decreases index)
        # else: if current_index < limit - 1: menu_pos += 1 (DOWN increases index)
        
        self.assertEqual(self.menu_pos[0], 1)

    def test_navigation_enter_exit(self):
        # Enter (Right)
        MenuController._navigate(1, self.menu_pos, self.menus)
        self.assertEqual(self.menu_pos[3], 1) # Level 1
        
        # Exit (Left)
        MenuController._navigate(-1, self.menu_pos, self.menus)
        self.assertEqual(self.menu_pos[3], 0) # Level 0

    def test_value_change_list(self):
        # Navigate to opt1 (Level 1, index 0)
        self.menu_pos = [0, 0, 0, 1]
        
        # Enter to Level 2 (Value selection)
        MenuController._navigate(1, self.menu_pos, self.menus)
        self.assertEqual(self.menu_pos[3], 2)
        
        # Current value is val1 (index 0). Options: val1, val2.
        # Down (Next item) -> index 1
        MenuController._handle_vertical_input(-1, self.menu_pos, self.menus, self.camera)
        self.assertEqual(self.menu_pos[2], 1)
        
        # Check if value updated in menu structure
        self.assertEqual(self.menus["menus"][0]["options"][0]["value"], "val2")
        
        # Check if camera setting applied
        self.camera.directory.return_value["opt1"].assert_called_with(value="val2")

    def test_value_change_range(self):
        # Navigate to opt2 (Level 1, index 1)
        self.menu_pos = [0, 1, 0, 1]
        
        # Enter to Level 2 (Range slider)
        MenuController._navigate(1, self.menu_pos, self.menus)
        
        # Current 10. Min 0, Max 20, Step 5.
        # Up (Increase) -> 15
        MenuController._handle_vertical_input(1, self.menu_pos, self.menus, self.camera)
        
        self.assertEqual(self.menus["menus"][0]["options"][1]["value"], 15)
        self.camera.directory.return_value["opt2"].assert_called_with(value=15)

    def test_quick_value_change(self):
        # Setup menus with standard stats
        self.menus["menus"][0]["options"].extend([
            {"name": "iso", "type": "list", "value": 100, "options": [100, 200, 400]},
            {"name": "shutter", "type": "range", "value": 10, "options": {"min": 0, "max": 100, "step": 10}}
        ])
        
        # Update camera mock to include these settings
        self.camera.directory.return_value.update({
            "iso": MagicMock(),
            "shutter": MagicMock()
        })
        
        # ISO is index 0 in quick stats (iso, shutter, awb, exposure)
        # Increase ISO (UP)
        MenuController._handle_quick_value_change(1, 0, self.menus, self.camera)
        self.assertEqual(self.menus["menus"][0]["options"][2]["value"], 200)
        self.camera.directory.return_value["iso"].assert_called_with(value=200)
        
        # Shutter is index 1
        # Increase Shutter (UP)
        MenuController._handle_quick_value_change(1, 1, self.menus, self.camera)
        self.assertEqual(self.menus["menus"][0]["options"][3]["value"], 20)
        self.camera.directory.return_value["shutter"].assert_called_with(value=20)

    def test_apply_setting_reset(self):
        reset_callback = MagicMock()
        callbacks = {"reset": reset_callback}
        option = {"name": "reset_settings", "value": "yes"}
        
        MenuController._apply_setting(self.camera, option, callbacks)
        
        reset_callback.assert_called_once()
        self.assertEqual(option["value"], "no")

class TestLayoutParser(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.layout_file = os.path.join(self.test_dir, "default.xml")
        
        with open(self.layout_file, "w") as f:
            f.write("""
            <layout>
                <container id="test_cont" x="10" y="10" width="100" height="100" bg_color="@bg">
                </container>
            </layout>
            """)
            
        self.theme = {"colors": {"bg": "#FF0000"}}
        self.parser = LayoutParser(self.theme, self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_layout(self):
        self.assertIn("default", self.parser.layouts)

    def test_get_element(self):
        elem = self.parser.get_element_by_id("test_cont")
        self.assertIsNotNone(elem)
        self.assertEqual(elem["x"], "10")

    def test_variable_resolution(self):
        elem = self.parser.get_element_by_id("test_cont")
        self.assertEqual(elem["bg_color"], "#FF0000")

if __name__ == '__main__':
    unittest.main()
