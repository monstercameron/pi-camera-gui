"""
Test to simulate the actual pygame event loop and identify resolution cycling.
This mimics what happens in gui.py's run() method.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()

from src.core.settings import SettingsManager
from src.ui.controls import MenuController
from src.ui.layout_parser import LayoutParser


def test_event_simulation():
    """Simulate the event loop to see if spurious events are generated."""
    
    # Load settings
    settings_manager = SettingsManager()
    settings, menus = settings_manager.load()
    
    # Track resolution changes
    resolution_changes = []
    current_resolution = (1920, 1080)
    
    class MockCamera:
        def __init__(self):
            self.resolution = (1920, 1080)
            self.is_previewing = False
            
        def resolution_get_set(self, value=None):
            if value is not None:
                str_to_tuple = tuple(map(int, value.split(',')))
                resolution_changes.append(value)
                self.resolution = str_to_tuple
                print(f"  [RESOLUTION CHANGE #{len(resolution_changes)}] -> {value}")
                
                # Simulate what MockCamera does: stop/start preview
                if self.is_previewing:
                    print("    stopPreview()")
                    self.is_previewing = False
                    print("    startPreview()")
                    self.is_previewing = True
                    
            return f"{self.resolution[0]},{self.resolution[1]}"
        
        def directory(self):
            return {
                "resolution": self.resolution_get_set,
                "iso": lambda v=None: 100,
                "shutter": lambda v=None: 8000,
                "awb": lambda v=None: "auto",
                "exposure": lambda v=None: "auto",
                "exposurecomp": lambda v=None: 0,
                "mode": lambda: "Single",
            }
        
        def startPreview(self):
            self.is_previewing = True
            
        def stopPreview(self):
            self.is_previewing = False
    
    camera = MockCamera()
    camera.startPreview()
    
    # Create layout parser
    layout = LayoutParser(theme_config=settings)
    
    # Settings for quick menu mode (menu hidden)
    settings["display"]["showmenu"] = False
    settings["mode"] = {"cameramode": "auto"}
    
    quick_menu_pos = [0]  # Start at first stat
    menu_pos = [0, 0, 0, 0]
    
    # Get quick stats
    quick_stats = MenuController._get_quick_stats(menu_pos, menus, settings, camera, layout)
    print(f"\nQuick stats: {quick_stats}")
    print(f"Resolution is at index: {quick_stats.index('resolution') if 'resolution' in quick_stats else 'NOT IN LIST'}")
    
    # Simulate: User navigates to resolution and presses UP multiple times
    if 'resolution' in quick_stats:
        resolution_index = quick_stats.index('resolution')
        quick_menu_pos[0] = resolution_index
        print(f"\nSimulating: User at resolution (index {resolution_index})")
        
        print("\n--- Simulating 10 UP key presses ---")
        for i in range(10):
            print(f"\nFrame {i+1}: Processing UP key")
            
            # This is what happens in the event loop
            MenuController._handle_quick_value_change(
                direction=1,  # UP
                stat_index=quick_menu_pos[0],
                menus=menus,
                camera=camera,
                settings=settings,
                settings_manager=None,
                layout=layout
            )
            
            # Check for runaway
            if len(resolution_changes) > 15:
                print("\n!!! RUNAWAY DETECTED - TOO MANY CHANGES !!!")
                break
        
        print(f"\n--- Summary ---")
        print(f"Total resolution changes: {len(resolution_changes)}")
        print(f"Changes: {resolution_changes}")
        
        # Verify: should have exactly 10 changes (or less if values wrapped)
        # But NOT more than 10
        if len(resolution_changes) > 10:
            print("\n!!! BUG: More resolution changes than key presses !!!")
            return False
    else:
        print("Resolution not in quick stats - checking why...")
        
        # Check what stats are available
        directory = camera.directory()
        print(f"Camera directory keys: {list(directory.keys())}")
        
    return True


def test_key_repeat_behavior():
    """Test pygame key repeat to see if it generates events correctly."""
    print("\n\n=== Testing pygame key repeat ===")
    
    pygame.key.set_repeat(300, 50)  # Same as gui.py
    
    # Create a small display
    screen = pygame.display.set_mode((100, 100))
    
    # Manually inject a KEYDOWN event
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    pygame.event.post(event)
    
    # Process events
    events = pygame.event.get()
    print(f"Events after posting 1 KEYDOWN: {len(events)}")
    for e in events:
        print(f"  Event: {e}")
    
    # Post multiple events quickly
    for _ in range(5):
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        pygame.event.post(event)
    
    events = pygame.event.get()
    print(f"\nEvents after posting 5 KEYDOWNs: {len(events)}")
    
    pygame.quit()


def test_find_resolution_menu_item():
    """Debug: Find where resolution is in the menus."""
    settings_manager = SettingsManager()
    settings, menus = settings_manager.load()
    
    print("\n\n=== Finding resolution in menus ===")
    
    for menu_idx, menu in enumerate(menus["menus"]):
        if "options" not in menu:
            continue
        for opt_idx, option in enumerate(menu["options"]):
            if option.get("name") == "resolution":
                print(f"Found resolution at menu[{menu_idx}] ({menu['name']}), option[{opt_idx}]")
                print(f"  Value: {option.get('value')}")
                print(f"  Options: {[o['value'] for o in option.get('options', [])]}")


if __name__ == '__main__':
    print("=" * 60)
    print("RESOLUTION LOOP DIAGNOSTIC TEST")
    print("=" * 60)
    
    test_find_resolution_menu_item()
    
    print("\n" + "=" * 60)
    success = test_event_simulation()
    
    print("\n" + "=" * 60)
    if success:
        print("TEST PASSED: No infinite loop detected in simulation")
    else:
        print("TEST FAILED: Infinite loop or excessive changes detected")
