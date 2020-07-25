import copy
import shutil
from functions import *
pcDevMode = True

App = {"alive": True, "exposure": 'auto', 'exposure_mode_value': ['off', 'auto', 'night', 'nightpreview', 'backlight', 'spotlight', 'sports', 'snow', 'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks'], 'count': 0, 'directory': 'images/',
       'name_scheme': 'photo_', 'image_format': 'jpeg', 'image_format_values': ['jpeg', 'png', 'gif', 'bmp', 'yuv', 'rgb', 'rgba', 'bgr', 'bgra'], 'shutter_speed': 8000, 'shutter_range': (100, 32000), 'iso': 800, 'iso_range': (1, 1600), 'awb': 'auto',
       'awb_mode': ['off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'], 'metering_key': 'SPOT', 'metering_value': {'SPOT': {'value': 10},  'AVERAGE': {'value': 25}, 'BACKLIT': {'value': 30}}, 'disk_space': (shutil.disk_usage("/")[2] // (2**30)), 'image_compress': 'FINE',
       'image_resolution': (4056, 3040), 'image_resolution_aspect': 'full censor', 'image_resolution_aspect_values': {'16:9': [(1280, 720), (1920, 1080), (2560, 1440), (3840, 2160)], '4:3': [(1280, 960), (2048, 1536), (4000, 3000)], '5:4': [
           (1280, 1024), (2560, 2048), (3830, 3064)], '1:1': [(1000, 1000), (2000, 2000), (3000, 3000)], 'full censor': [(4056, 3040)]}, 'menu_hilite': 0, 'menu_select': None, 'camera_mode_options': ['SINGLE', 'BURST'],
       'camera_mode': 'SINGLE', 'image_dr_compress': 'high', 'image_dr_compress_value': ['off', 'low', 'medium', 'high'],
       'window_size': (0, 0, 1280, 720), 'image_file_path': lambda: f"{App[IMAGE_DIRECTORY]}/{App[IMAGE_NAME_SCHEME]}{App[IMAGE_COUNT]}.{App[IMAGE_FORMAT]}"}

DEFAULT = copy.deepcopy(App)
DEFAULT_WINDOW_SIZE = 'window_size'
ALIVE = 'alive'
EXPOSURE = 'exposure'
EXPOSURE_MODE_VALUE = 'exposure_mode_value'
IMAGE_COUNT = 'count'
IMAGE_DIRECTORY = 'directory'
IMAGE_NAME_SCHEME = 'name_scheme'
IMAGE_FORMAT = 'image_format'
IMAGE_FORMAT_VALUES = 'image_format_values'
IMAGE_COMPRESSION = 'image_compress'
IMAGE_RESOLUTION = 'image_resolution'
IMAGE_RESOLUTION_ASPECT = 'image_resolution_aspect'
IMAGE_RESOLUTION_ASPECT_VALUES = 'image_resolution_aspect_values'
IMAGE_DR_COMPRESSION = 'image_dr_compress'
IMAGE_DR_COMPRESSION_VALUES = 'image_dr_compress_value'
IMAGE_FILE_PATH = 'image_file_path'
CAMERA_CAPTURE_MODE = 'camera_mode'
CAMERA_CAPTURE_MODE_VALUES = 'camera_mode_options'
SHUTTER_SPEED = 'shutter_speed'
SHUTTER_RANGE = 'shutter_range'
ISO = 'iso'
ISO_RANGE = 'iso_range'
AWB = 'awb'
AWB_MODE_VALUES = 'awb_mode'
METERING_MODE = 'metering_key'
METERING_MODE_VALUES = 'metering_value'
DISK_SPACE = 'disk_space'
MENU_HILITE = 'menu_hilite'
MENU_SELECT = 'menu_select'

# create a list of all the text on the GUI
textList = {}
textList['stats'] = lambda: f"{int(howManyPhotos(App[DISK_SPACE], App[IMAGE_RESOLUTION]))} Photos {App[DISK_SPACE]}GB {int(product(App[IMAGE_RESOLUTION])/1000000)}MP {App[IMAGE_FORMAT]} {App[IMAGE_COMPRESSION]}".upper()
textList[IMAGE_RESOLUTION_ASPECT] = lambda: f"Aspect Ratio {App[IMAGE_RESOLUTION_ASPECT]}".upper(
)
textList[IMAGE_RESOLUTION_ASPECT_VALUES] = lambda: f"resolution {App[IMAGE_RESOLUTION]}".upper(
)
textList[IMAGE_FORMAT] = lambda: f"format {App[IMAGE_FORMAT]}".upper()
textList[CAMERA_CAPTURE_MODE] = lambda: f"{App[CAMERA_CAPTURE_MODE]} MODE".upper(
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
            App[ISO] = adjustByFactor2(2, App[ISO], App[ISO_RANGE])
        elif direction == 'left':
            App[ISO] = adjustByFactor2(-2, App[ISO], App[ISO_RANGE])
        if not pcDevMode:
            camera.iso = App[ISO]
    elif key == AWB:
        if direction == 'right':
            App[AWB] = traverseList(App[AWB], 'next', App[AWB_MODE_VALUES])
        elif direction == 'left':
            App[AWB] = traverseList(App[AWB], 'previous', App[AWB_MODE_VALUES])
        if not pcDevMode:
            camera.awb_mode = App[AWB]
    elif key == SHUTTER_SPEED:
        if direction == 'right':
            App[SHUTTER_SPEED] = adjustByFactor2(
                2, App[SHUTTER_SPEED], App[SHUTTER_RANGE])
        elif direction == 'left':
            App[SHUTTER_SPEED] = adjustByFactor2(-2,
                                                 App[SHUTTER_SPEED], App[SHUTTER_RANGE])
        if not pcDevMode:
            camera.shutter_speed = App[SHUTTER_SPEED]
    elif key == CAMERA_CAPTURE_MODE:
        if direction == 'right':
            App[CAMERA_CAPTURE_MODE] = traverseList(
                App[CAMERA_CAPTURE_MODE], 'next', App[CAMERA_CAPTURE_MODE_VALUES])
        elif direction == 'left':
            App[CAMERA_CAPTURE_MODE] = traverseList(
                App[CAMERA_CAPTURE_MODE], 'previous', App[CAMERA_CAPTURE_MODE_VALUES])
    elif key == METERING_MODE:
        if direction == 'right':
            App[METERING_MODE] = traverseList(
                App[METERING_MODE], 'next', list(App[METERING_MODE_VALUES].keys()))
        elif direction == 'left':
            App[METERING_MODE] = traverseList(
                App[METERING_MODE], 'previous', list(App[METERING_MODE_VALUES].keys()))
    elif key == EXPOSURE:
        if direction == 'right':
            App[EXPOSURE] = traverseList(
                App[EXPOSURE], 'next', App[EXPOSURE_MODE_VALUE])
        elif direction == 'left':
            App[EXPOSURE] = traverseList(
                App[EXPOSURE], 'previous', App[EXPOSURE_MODE_VALUE])
        if not pcDevMode:
            camera.exposure_mode = App[EXPOSURE]
    elif key == IMAGE_DR_COMPRESSION:
        if direction == 'right':
            App[IMAGE_DR_COMPRESSION] = traverseList(
                App[IMAGE_DR_COMPRESSION], 'next', App[IMAGE_DR_COMPRESSION_VALUES])
        elif direction == 'left':
            App[IMAGE_DR_COMPRESSION] = traverseList(
                App[IMAGE_DR_COMPRESSION], 'previous', App[IMAGE_DR_COMPRESSION_VALUES])
    elif key == IMAGE_RESOLUTION_ASPECT:
        if direction == 'right':
            App[IMAGE_RESOLUTION_ASPECT] = traverseList(
                App[IMAGE_RESOLUTION_ASPECT], 'next', list(App[IMAGE_RESOLUTION_ASPECT_VALUES]))
        elif direction == 'left':
            App[IMAGE_RESOLUTION_ASPECT] = traverseList(
                App[IMAGE_RESOLUTION_ASPECT], 'previous', list(App[IMAGE_RESOLUTION_ASPECT_VALUES]))
    elif key == IMAGE_RESOLUTION_ASPECT_VALUES:
        if not App[IMAGE_RESOLUTION] in App[IMAGE_RESOLUTION_ASPECT_VALUES][App[IMAGE_RESOLUTION_ASPECT]]:
            App[IMAGE_RESOLUTION] = App[IMAGE_RESOLUTION_ASPECT_VALUES][App[IMAGE_RESOLUTION_ASPECT]][-1]
        if direction == 'right':
            App[IMAGE_RESOLUTION] = traverseList(
                App[IMAGE_RESOLUTION], 'next', App[IMAGE_RESOLUTION_ASPECT_VALUES][App[IMAGE_RESOLUTION_ASPECT]])
        elif direction == 'left':
            App[IMAGE_RESOLUTION] = traverseList(
                App[IMAGE_RESOLUTION], 'previous', App[IMAGE_RESOLUTION_ASPECT_VALUES][App[IMAGE_RESOLUTION_ASPECT]])
    elif key == IMAGE_FORMAT:
        if direction == 'right':
            App[IMAGE_FORMAT] = traverseList(
                App[IMAGE_FORMAT], 'next', App[IMAGE_FORMAT_VALUES])
        elif direction == 'left':
            App[IMAGE_FORMAT] = traverseList(
                App[IMAGE_FORMAT], 'previous', App[IMAGE_FORMAT_VALUES])
