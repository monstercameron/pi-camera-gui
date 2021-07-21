from settings import settings, menus, jsonToSettings, openSettings
from gui import *
from controls import *
from camera import *

if __name__ == '__main__':
    settings = jsonToSettings(openSettings(settings))
    menus = jsonToSettings(openSettings(menus))
    # print(settings, menus)
    Gui(cameraControls, menus, settings)
