"""
Test to identify the resolution cycling infinite loop issue.
This test simulates the startup sequence and checks for repeated resolution changes.
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, patch, MagicMock
from src.core.settings import SettingsManager
from src.ui.controls import MenuController


class ResolutionChangeTracker:
    """Tracks resolution changes to detect loops."""
    def __init__(self):
        self.changes = []
        self.resolution = (1920, 1080)
        
    def resolution_get_set(self, value=None):
        if value is not None:
            str_to_tuple = tuple(map(int, value.split(',')))
            self.changes.append(value)
            self.resolution = str_to_tuple
            print(f"Resolution changed to: {value} (total changes: {len(self.changes)})")
        return f"{self.resolution[0]},{self.resolution[1]}"


class TestResolutionLoop(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = ResolutionChangeTracker()
        
        # Create mock camera with tracking
        self.mock_camera = Mock()
        self.mock_camera.resolution_get_set = self.tracker.resolution_get_set
        self.mock_camera.directory = Mock(return_value={
            "resolution": self.tracker.resolution_get_set,
            "iso": Mock(return_value=100),
            "shutter": Mock(return_value=8000),
            "awb": Mock(return_value="auto"),
            "exposure": Mock(return_value="auto"),
            "exposurecomp": Mock(return_value=0),
        })
        
        # Load real menus
        self.settings_manager = SettingsManager()
        self.settings, self.menus = self.settings_manager.load()
        
    def test_apply_settings_to_camera_single_resolution(self):
        """Test that apply_settings_to_camera only sets resolution once per menu item."""
        from run import apply_settings_to_camera
        
        self.tracker.changes.clear()
        apply_settings_to_camera(self.menus, self.mock_camera)
        
        print(f"\nResolution changes during apply_settings_to_camera: {self.tracker.changes}")
        
        # Resolution appears in multiple menus (auto, image settings)
        # Each should only apply ONCE (the current value), not cycle through options
        for change in self.tracker.changes:
            # All changes should be the same value (the stored value)
            self.assertIn(change, ["1920,1080", "1280,720", "2560,1440", "3840,2160", "4056,3040"])
        
        # Should NOT have cycled through all values
        unique_changes = set(self.tracker.changes)
        print(f"Unique resolution values applied: {unique_changes}")
        
        # If we see ALL resolution options, that's a bug
        all_resolutions = {"1280,720", "1920,1080", "2560,1440", "3840,2160", "4056,3040"}
        if unique_changes == all_resolutions:
            self.fail("BUG: All resolution options were applied - cycling detected!")
    
    def test_quick_menu_resolution_change(self):
        """Test that quick menu only changes resolution by ONE step per input."""
        self.tracker.changes.clear()
        
        # Simulate settings with resolution in quick stats
        settings = {
            "mode": {"cameramode": "auto"},
            "display": {"showmenu": False},
        }
        
        # Find resolution option in menus
        resolution_option = None
        for menu in self.menus["menus"]:
            if "options" in menu:
                for opt in menu["options"]:
                    if opt.get("name") == "resolution":
                        resolution_option = opt
                        break
        
        self.assertIsNotNone(resolution_option, "Resolution option not found in menus")
        print(f"\nResolution option: {resolution_option['name']}, current value: {resolution_option['value']}")
        print(f"Available options: {[o['value'] for o in resolution_option['options']]}")
        
        # Simulate ONE up press on resolution
        initial_value = resolution_option["value"]
        MenuController._handle_quick_value_change(
            direction=1,  # UP
            stat_index=2,  # Assuming resolution is at index 2 in quick stats
            menus=self.menus,
            camera=self.mock_camera,
            settings=settings,
            settings_manager=None,
            layout=None
        )
        
        print(f"Changes after one UP: {self.tracker.changes}")
        
        # Should have at most ONE change
        self.assertLessEqual(len(self.tracker.changes), 1, 
                            f"Expected at most 1 resolution change, got {len(self.tracker.changes)}")
    
    def test_resolution_change_no_recursive_calls(self):
        """Test that changing resolution doesn't trigger recursive changes."""
        self.tracker.changes.clear()
        
        # Directly call the resolution setter multiple times
        # to verify it doesn't self-trigger
        self.tracker.resolution_get_set("1920,1080")
        self.tracker.resolution_get_set("2560,1440")
        
        print(f"\nDirect resolution changes: {self.tracker.changes}")
        self.assertEqual(len(self.tracker.changes), 2, "Direct calls should result in exactly 2 changes")
    
    def test_menu_position_and_option_value(self):
        """Test that menu navigation doesn't inadvertently apply settings."""
        self.tracker.changes.clear()
        
        menu_pos = [0, 0, 0, 0]  # Top level
        
        # Navigate through menus (should NOT apply settings)
        MenuController._navigate(1, menu_pos, self.menus)  # Go deeper
        MenuController._navigate(1, menu_pos, self.menus)  # Go deeper again
        
        print(f"\nResolution changes during navigation: {self.tracker.changes}")
        
        # Navigation alone should NOT change resolution
        self.assertEqual(len(self.tracker.changes), 0, 
                        "Navigation should not apply settings")
    
    def test_vertical_input_list_type_behavior(self):
        """Test that vertical input on list items only updates index, not value."""
        self.tracker.changes.clear()
        
        # Position at level 2 (value selection) for a list item
        # Find resolution's position
        menu_pos = [0, 3, 0, 2]  # auto menu, resolution option (index 3), first value, level 2
        
        # UP should change index but NOT apply (that's Enter's job for lists)
        changed = MenuController._update_list_value(1, menu_pos, self.menus)
        
        print(f"\n_update_list_value returned: {changed}")
        print(f"Resolution changes: {self.tracker.changes}")
        
        # _update_list_value should return None for lists (no immediate apply)
        self.assertIsNone(changed, "_update_list_value should return None for list navigation")


class TestMockCameraResolution(unittest.TestCase):
    """Test MockCamera's resolution behavior."""
    
    def test_mock_camera_resolution_no_loop(self):
        """Test that MockCamera.resolution_get_set doesn't cause loops."""
        from src.hardware.camera import MockCamera
        
        # Track calls
        call_count = 0
        original_stop = None
        original_start = None
        
        settings = {"files": {"path": "home/dcim", "template": "IMG_{0}_{1}"}}
        menus = {"menus": []}
        
        camera = MockCamera(menus, settings)
        
        # Patch to track calls
        stop_calls = []
        start_calls = []
        
        original_stop = camera.stopPreview
        original_start = camera.startPreview
        
        def tracking_stop():
            stop_calls.append(1)
            # Don't actually stop (no webcam in test)
            camera.is_previewing = False
            
        def tracking_start():
            start_calls.append(1)
            camera.is_previewing = True
            # Check for recursion
            if len(start_calls) > 5:
                raise RecursionError("Too many startPreview calls!")
        
        camera.stopPreview = tracking_stop
        camera.startPreview = tracking_start
        camera.is_previewing = True
        
        # Now set resolution
        camera.resolution_get_set("1920,1080")
        
        print(f"\nstopPreview calls: {len(stop_calls)}")
        print(f"startPreview calls: {len(start_calls)}")
        
        # Should be exactly 1 stop and 1 start
        self.assertEqual(len(stop_calls), 1, "Should stop preview exactly once")
        self.assertEqual(len(start_calls), 1, "Should start preview exactly once")


if __name__ == '__main__':
    unittest.main(verbosity=2)
