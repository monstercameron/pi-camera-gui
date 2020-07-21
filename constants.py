
from functions import *
import shutil

App = {"alive": True, "exposure": 'auto', 'exposure_mode_value': ['off', 'auto', 'night', 'nightpreview', 'backlight', 'spotlight', 'sports', 'snow', 'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks'], 'count': 0, 'directory': 'images/',
       'name_scheme': 'photo_', 'image_format': 'jpeg', 'shutter_speed': 400, 'shutter_range': (100, 32000), 'iso': 50, 'iso_range': (0, 1600), 'awb': 'auto',
       'awb_mode': ['off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'], 'metering_key': 'SPOT', 'metering_value': {'SPOT': {'value': 10},  'AVERAGE': {'value': 25}, 'BACKLIT': {'value': 30}}, 'disk_space': (shutil.disk_usage("/")[2] // (2**30)), 'image_compress': 'FINE',
       'image_resolution': (4056, 3040), 'menu_hilite': 0, 'menu_select': None, 'camera_mode_options': ['SINGLE', 'BURST'],
       'camera_mode': 0, 'image_dr_compress': 'high', 'image_dr_compress_value': ['off', 'low', 'medium', 'high'],
       'window_size': (0, 0, 1280, 720), 'image_file_path': lambda: f"{App[IMAGE_DIRECTORY]}/{App[IMAGE_NAME_SCHEME]}{App[IMAGE_COUNT]}.{App[IMAGE_FORMAT]}"}

ALIVE = 'alive'
EXPOSURE = 'exposure'
EXPOSURE_MODE_VALUE = 'exposure_mode_value'
IMAGE_COUNT = 'count'
IMAGE_DIRECTORY = 'directory'
IMAGE_NAME_SCHEME = 'name_scheme'
IMAGE_FORMAT = 'image_format'
IMAGE_COMPRESSION = 'image_compress'
IMAGE_RESOLUTION = 'image_resolution'
IMAGE_DR_COMPRESSION = 'image_dr_compress'
IMAGE_DR_COMPRESSION_VALUES = 'image_dr_compress_value'
IMAGE_FILE_PATH = 'image_file_path'
CAMERA_CAPTURE_MODE = 'camera_mode'
CAMERA_CAPTURE_MODE_VALUES = 'camera_mode_options'
SHUTTER_SPEED = 'shutter_speed'
SHUTTER_RANGE = 'shutter_range'
ISO = 'iso'
ISO_RANGE = 'iso_range'
DEFAULT_WINDOW_SIZE = 'window_size'
AWB = 'awb'
AWB_MODE_VALUES = 'awb_mode'
METERING_MODE = 'metering_key'
METERING_MODE_VALUES = 'metering_value'
DISK_SPACE = 'disk_space'
MENU_HILITE = 'menu_hilite'
MENU_SELECT = 'menu_select'

# create a list of all the text on the GUI
textList = {}
textList['stats'] = lambda: f"{int(App[DISK_SPACE]//0.00025)}|{App[DISK_SPACE]}GB {product(App[IMAGE_RESOLUTION])//1000000}MP {App[IMAGE_FORMAT]} {App[IMAGE_COMPRESSION]}".upper()
textList[CAMERA_CAPTURE_MODE] = lambda: f"{App[CAMERA_CAPTURE_MODE_VALUES][App[CAMERA_CAPTURE_MODE]]} MODE".upper(
)
textList[METERING_MODE] = lambda: f"{App[METERING_MODE]} METERING".upper()
textList[AWB] = lambda: f"{App[AWB]} WB".upper()
textList[IMAGE_DR_COMPRESSION] = lambda: f"DRC {App[IMAGE_DR_COMPRESSION]}".upper(
)
textList[EXPOSURE] = lambda: f"EXPOSURE {App[EXPOSURE]}".upper()
textList[ISO] = lambda: f"{App[ISO]} ISO"
textList[SHUTTER_SPEED] = lambda: f"{App[SHUTTER_SPEED]} shutter".upper()


def menuActions(camera, key, direction):
    if key == ISO:
        if direction == 'right':
            adjustByFactor(App, 2, ISO, App[ISO_RANGE])
            # camera.iso = adjustByFactor(App, 2, App[ISO], App[ISO_RANGE])
        elif direction == 'left':
            adjustByFactor(App, -2, ISO, App[ISO_RANGE])
            # camera.iso = adjustByFactor(App, -2, App[ISO], App[ISO_RANGE])
