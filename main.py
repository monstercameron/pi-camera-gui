from settings import settingsFile, menusFile, jsonToSettings, openSettings, saveSettings
from gui import *
from controls import *
from camera import *

if __name__ == '__main__':
    #  opening settins and menu files
    settings = jsonToSettings(openSettings(settingsFile))
    menus = jsonToSettings(openSettings(menusFile))

    Gui(cameraControls, menus, settings)

    # save settings and menus
    saveSettings(settingsFile, settings)
    saveSettings(menusFile, menus)
