from src.core.settings import SettingsManager
from src.ui.gui import GUI
from src.ui.controls import MenuController
from src.hardware.buttons import Buttons
from src.hardware.camera import get_camera
import sys

if __name__ == '__main__':
    # Initialize settings manager
    settings_manager = SettingsManager()
    settings, menus = settings_manager.load()

    # Initialize camera (Real or Mock based on availability)
    camera = get_camera(menus, settings)
    
    # Initialize GUI
    gui = GUI(settings, menus, camera)
    
    try:
        # Run the GUI
        gui.run(MenuController.handle_event, Buttons)
    except KeyboardInterrupt:
        pass
    finally:
        # Save settings and menus on exit
        settings_manager.save()
        sys.exit()
