from src.core.settings import SettingsManager
from src.ui.gui import GUI
from src.ui.controls import MenuController
from src.hardware.buttons import Buttons
from src.hardware.camera import get_camera
import sys

def populate_menu_options(menus, camera):
    """
    Dynamically populates menu options based on camera capabilities.
    """
    for menu in menus["menus"]:
        if "options" in menu:
            for option in menu["options"]:
                if option["type"] == "list":
                    key = option["name"]
                    supported_options = camera.get_supported_options(key)
                    
                    if supported_options:
                        print(f"Discovered options for {key}: {len(supported_options)} items")
                        new_options = []
                        for opt_val in supported_options:
                            # Create display name (Capitalize first letter)
                            display_name = str(opt_val).replace('_', ' ').title()
                            
                            # Handle special cases if needed
                            if display_name.lower() == "off": display_name = "Off"
                            
                            new_options.append({
                                "value": opt_val,
                                "displayname": display_name
                            })
                        
                        # Update the option list
                        option["options"] = new_options
                        
                        # Ensure current value is valid
                        if option["value"] not in supported_options:
                            if supported_options:
                                option["value"] = supported_options[0]

def apply_settings_to_camera(menus, camera):
    """
    Applies all settings from the menu structure to the camera.
    """
    directory = camera.directory()
    print("Applying initial settings to camera...")
    
    for menu in menus["menus"]:
        if "options" in menu:
            for option in menu["options"]:
                key = option.get("name")
                value = option.get("value")
                
                if key and value is not None and key in directory:
                    try:
                        # print(f"  Setting {key} -> {value}")
                        directory[key](value=value)
                    except Exception as e:
                        print(f"  Failed to set {key}: {e}")

if __name__ == '__main__':
    # Initialize settings manager
    settings_manager = SettingsManager()
    settings, menus = settings_manager.load()

    # Initialize camera (Real or Mock based on availability)
    camera = get_camera(menus, settings)
    
    # Auto-discover options
    populate_menu_options(menus, camera)
    
    # Apply loaded settings to camera
    apply_settings_to_camera(menus, camera)
    
    # Initialize GUI
    gui = GUI(settings, menus, camera)
    
    # Define callbacks
    callbacks = {
        "reset": lambda: settings_manager.reset(),
        "open_gallery": lambda: gui.gallery.enter(),
        "close_menu": lambda: settings["display"].update({"showmenu": False})
    }

    # Wrap handle_event to include callbacks
    def controls_handler(pygame_mod, event, menu_pos, menus, camera=None, menu_active=True, quick_menu_pos=None, action=None):
        MenuController.handle_event(pygame_mod, event, menu_pos, menus, camera, menu_active, quick_menu_pos, callbacks, action)
    
    try:
        print("Starting GUI...")
        # Run the GUI
        gui.run(controls_handler, Buttons)
        print("GUI exited normally.")
    except KeyboardInterrupt:
        print("GUI interrupted by user.")
        pass
    except Exception as e:
        print(f"Error running GUI: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Saving settings...")
        # Save settings and menus on exit
        settings_manager.save()
        print("Exiting application.")
        # sys.exit() # Removed to prevent masking exit codes or errors
