from functions import *
import shutil
import copy

# App state
App = {}

# Image settings
App['imageIterator'] = {
    'value': 0, 'message': lambda: f"{App['imageIterator']['value']} photos added"}

App['imageDirectory'] = {'value': 'images/',
                         'message': lambda: f"{App['imageDirectory']['value']} image directory"}

App['imageName'] = {'value': 'picamera_',
                    'message': lambda: f"{App['imageName']['value']} image naming"}

App['imageQuality'] = {'value': 100, 'values': (
    1, 100), 'message': lambda: f"{App['imageQuality']['value']} image quality"}

App['imageFormat'] = {'value': 'jpeg', 'values': [
    'jpeg', 'png', 'gif', 'bmp', 'yuv', 'rgb', 'rgba', 'bgr', 'bgra']}

App['imageResolution'] = {'value': (
    4056, 3040), 'message': lambda: f"{App['imageResolution']['value']} image resolution"}

App['imageAspectRatio'] = {'value': 'full censor', 'values': {'16:9': [(1280, 720), (1920, 1080), (2560, 1440), (3840, 2160)], '4:3': [(1280, 960), (2048, 1536), (4000, 3000)], '5:4': [
    (1280, 1024), (2560, 2048), (3830, 3064)], '1:1': [(1000, 1000), (2000, 2000), (3000, 3000)], 'full censor': [(4056, 3040)]}, 'message': lambda: f"{App['imageAspectRatio']['value']} image aspect"}

App['imageFilePath'] = lambda: f"{App['imageDirectory']['value']}/{App['imageName']['value']}{App['imageIterator']['value']}.{App['imageFormat']['value']}"

# Camera settings
App['exposure'] = {'value': 'auto', 'values': ['off', 'auto', 'night', 'nightpreview', 'backlight',
                                               'spotlight', 'sports', 'snow', 'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks'], 'message': lambda: f"{App['exposure']['value']} image exposure"}
App['wb'] = {'value': 'auto', 'values': ['off', 'auto', 'sunlight', 'cloudy',
                                         'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'], 'message': lambda: f"{App['wb']['value']} whtie balance"}
App['meteringMode'] = {'value': 'spot', 'values': {
    'spot': {'value': 10},  'average': {'value': 25}, 'backlit': {'value': 30}}, 'message': lambda: f"{App['meteringMode']['value']} metering mdoe"}
App['shutterSpeed'] = {'value': 8000, 'values': (
    100, 32000), 'message': lambda: f"{App['shutterSpeed']['value']} shutter speed"}
App['iso'] = {'value': 800, 'values': (
    1, 1600), 'message': lambda: f"{App['iso']['value']} iso"}
App['captureSpeed'] = {'value': 'single', 'values': [
    'single', 'continous'], 'message': lambda: f"{App['captureSpeed']['value']} capture mode"}
App['dynamicRangeCompression'] = {
    'value': 'high', 'values': ['off', 'low', 'medium', 'high'], 'message': lambda: f"{App['dynamicRangeCompression']['value']} drc"}

# App settings
App['alive'] = {'value': True}
App['font'] = {'value': 24}
App['fontColor'] = {'value': 24}
App['fontColor'] = {'value': [(255, 255, 255), (0, 0, 0, 125), (0, 0, 0)]}
App['padding'] = {'value': 20}
App['window'] = {'value': (0, 0, 1280, 720)}
App['isFullscreen'] = {'value': True}
App['fullscreen'] = {'value': (1280, 720)}
App['diskSize'] = {'value': shutil.disk_usage("/")[2] // (2**30)}
App['diskSpace'] = {'value': shutil.disk_usage("/")[2] // (2**30)}
App['mode'] = {'value': 'photo', 'values': ['photo', 'video']}
App['menu'] = {'value': 'auto', 'values': ['auto', 'manual', 'settings']}
App['menuHighlight'] = {'value': ''}
App['stats'] = {'values': [
    ''], 'value': lambda: f"{int(howManyPhotos(App['diskSize']['value'], App['imageResolution']['value']))} Photos {App['diskSize']['value']}GB {int(product(App['imageResolution']['value'])/1000000)}MP {App['imageFormat']['value']} {App['imageQuality']['value']}"}
# Menus
App['menus'] = {'photo': {'auto': [], 'manual': [], 'settings': []},
                'video': {'auto': [], 'manual': [], 'settings': []}}

stats = ('stats', App['stats']['value'])
main = ('mode', lambda: f"{App['mode']['value']} mode")
sub = ('menu', lambda: f"{App['menu']['value']} mode")
iso = ('iso', lambda: f"{App['iso']['value']} iso")
# sub = ('menu', lambda: f"{App['menu']['value']} mode")
# sub = ('menu', lambda: f"{App['menu']['value']} mode")
# sub = ('menu', lambda: f"{App['menu']['value']} mode")

App['menus']['photo']['auto'] = [stats, main, sub]
App['menus']['photo']['manual'] = [stats, main, sub, iso]
App['menus']['photo']['settings'] = [stats, main, sub]

DEFAULT = copy.deepcopy(App)

devMode = True
camera = None
if not devMode:
    import picamera
    camera = picamera.PiCamera()
    camera.shutter_speed = App['shutterSpeed']['value']
    camera.iso = App['ISO']['value']
