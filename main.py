from settings import *
from gui import *
from controls import *
from buttons import *


if __name__ == '__main__':
    #  opening settins and menu files
    settings = jsonToSettings(openSettings(settingsFile))
    menus = jsonToSettings(openSettings(menusFile))
    dcimFolderChecker(settings)

    if settings["mode"]["dev"]:
        Gui(cameraControls, menus, settings, Buttons)
    else:
        from camera import Camera
        Gui(cameraControls, menus, settings, Buttons,
            camera=(Camera(menus, settings)))

    # save settings and menus
    saveSettings(settingsFile, settings)
    saveSettings(menusFile, menus)
