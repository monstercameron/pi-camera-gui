from settings import *
from gui import *
from controls import *
from camera import *

if __name__ == '__main__':
    settings = jsonToSettings(openSettings())
    print(type(settings))

    Gui(settings)