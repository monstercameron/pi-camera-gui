from settings import *
from gui import *
from controls import *
from buttons import *
from camera import get_camera


if __name__ == '__main__':
    #  opening settins and menu files
    settings = jsonToSettings(openSettings(settingsFile))
    menus = jsonToSettings(openSettings(menusFile))
    dcimFolderChecker(settings)

    # Initialize camera (Real or Mock based on availability)
    camera = get_camera(menus, settings)
    
    Gui(cameraControls, menus, settings, Buttons, camera=camera)

    # save settings and menus
    saveSettings(settingsFile, settings)
    saveSettings(menusFile, menus)
