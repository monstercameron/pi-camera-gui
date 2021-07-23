from settings import settingsFile, menusFile, jsonToSettings, openSettings, saveSettings
from gui import *
from controls import *


if __name__ == '__main__':
    #  opening settins and menu files
    settings = jsonToSettings(openSettings(settingsFile))
    menus = jsonToSettings(openSettings(menusFile))

    if settings["mode"]["dev"]:
        Gui(cameraControls, menus, settings)
    else:
        from camera import Camera
        Gui(cameraControls, menus, settings,
            camera=(Camera(menus, settings)))

    # save settings and menus
    saveSettings(settingsFile, settings)
    saveSettings(menusFile, menus)
