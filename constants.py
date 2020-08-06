from functions import *
import shutil
import copy

# App state
App = {}

# Image settings
App['imageIterator'] = {'value': 0,
                        'message': lambda: f"{App['imageIterator']['value']} photos added"}

App['imageDirectory'] = {'value': 'images/',
                         'message': lambda: f"{App['imageDirectory']['value']} image directory"}

App['imageName'] = {'value': 'picamera_',
                    'message': lambda: f"{App['imageName']['value']} image naming"}

App['imageQuality'] = {'value': 100,
                       'values': (1, 100),
                       'message': lambda: f"{App['imageQuality']['value']} image quality"}

App['imageSaturation'] = {'value': 0,
                          'values': (-100, 100),
                          'message': lambda: f"{App['imageSaturation']['value']} image saturation"}

App['imageSharpness'] = {'value': 0,
                         'values': (-100, 100),
                         'message': lambda: f"{App['imageSharpness']['value']} image sharpness"}

App['imageDenoise'] = {"value": True,
                       "values": [True, False],
                       'message': lambda: f"{App['imageDenoise']['value']} image denoise"}

App['imageFormat'] = {'value': 'jpeg',
                      'values': ['jpeg', 'png', 'gif', 'bmp', 'yuv', 'rgb', 'rgba', 'bgr', 'bgra'],
                      'message': lambda: f"{App['imageFormat']['value']} image format"}

App['imageEffect'] = {'value': 'none',
                      'values': ['none', 'negative', 'solarize', 'sketch', 'denoise', 'emboss', 'oilpaint', 'hatch', 'gpen', 'pastel',
                                 'watercolor', 'film', 'blur', 'saturation', 'colorswap', 'washedout', 'posterise', 'colorpoint',
                                 'colorbalance', 'cartoon', 'deinterlace1', 'deinterlace2'],
                      'message': lambda: f"{App['imageFormat']['value']} image format"}

App['imageAspectRatio'] = {'value': 'full censor',
                           'values': {'16:9': [(1280, 720), (1920, 1080), (2560, 1440), (3840, 2160)], '4:3': [(1280, 960), (2048, 1536), (4000, 3000)], '5:4': [
                               (1280, 1024), (2560, 2048), (3830, 3064)], '1:1': [(1000, 1000), (2000, 2000), (3000, 3000)], 'full censor': [(4056, 3040)]},
                           'message': lambda: f"{App['imageAspectRatio']['value']} image aspect"}

App['imageResolution'] = {'value': (4056, 3040),
                          'values': lambda: App['imageAspectRatio']['values'][App['imageAspectRatio']['value']],
                          'message': lambda: f"{App['imageResolution']['value']} image resolution"}

App['imageFilePath'] = lambda: f"{App['imageDirectory']['value']}/{App['imageName']['value']}{App['imageIterator']['value']}.{App['imageFormat']['value']}"

# Camera settings
App['exposureMode'] = {'value': 'auto',
                       'values': ['off', 'auto', 'night', 'nightpreview', 'backlight', 'spotlight', 'sports', 'snow', 'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks'],
                       'message': lambda: f"{App['exposureMode']['value']} image exposure mode"}

App['exposureCompensation'] = {'value': 0,
                               'values': (-25, 25),
                               'message': lambda: f"{App['exposureCompensation']['value']} image exposure compensation"}

App['contrast'] = {'value': 0,
                   'values': (-100, 100),
                   'message': lambda: f"{App['contrast']['value']} image contrast"}

App['brightness'] = {'value': 0,
                   'values': (-100, 100),
                   'message': lambda: f"{App['brightness']['value']} image brightness"}

App['wb'] = {'value': 'auto',
             'values': ['off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'],
             'message': lambda: f"{App['wb']['value']} white balance"}

App['meteringMode'] = {'value': 'spot',
                       'values': {'spot': {'value': 10},  'average': {'value': 25}, 'backlit': {'value': 30}},
                       'message': lambda: f"{App['meteringMode']['value']} metering mode"}

App['shutterSpeed'] = {'value': 8000,
                       'values': (100, 32000),
                       'message': lambda: f"{App['shutterSpeed']['value']} shutter speed"}

App['iso'] = {'value': 800,
              'values': (1, 1600),
              'message': lambda: f"{App['iso']['value']} iso"}

App['captureSpeed'] = {'value': 'single',
                       'values': ['single', 'continous'],
                       'message': lambda: f"{App['captureSpeed']['value']} capture mode"}

App['dynamicRangeCompression'] = {'value': 'high',
                                  'values': ['off', 'low', 'medium', 'high'],
                                  'message': lambda: f"{App['dynamicRangeCompression']['value']} drc"}

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
    ''], 'message': lambda: f"{int(howManyPhotos(App['diskSize']['value'], App['imageResolution']['value']))} Photos {App['diskSize']['value']}GB {int(product(App['imageResolution']['value'])/1000000)}MP {App['imageFormat']['value']} {App['imageQuality']['value']}"}
# Menus
App['menus'] = {'photo': {'auto': [], 'manual': [], 'settings': []},
                'video': {'auto': [], 'manual': [], 'settings': []}}


App['menus']['photo']['auto'] = ['stats', 'mode', 'menu']
App['menus']['photo']['manual'] = ['stats', 'mode',
                                   'menu', 'iso', 'wb', 'meteringMode', 'shutterSpeed']
App['menus']['photo']['settings'] = ['stats', 'mode', 'menu',
                                     'dynamicRangeCompression', 'imageFormat', 'imageAspectRatio', 'imageResolution', 'imageQuality']

DEFAULT = copy.deepcopy(App)

devMode = True
camera = {}
if not devMode:
    import picamera
    camera['camera'] = picamera.PiCamera()
    camera['camera'].shutter_speed = App['shutterSpeed']['value']
    camera['camera'].iso = App['iso']['value']
    camera['start'] = lambda: camera['camera'].start_preview(
        fullscreen=App['isFullscreen']['value'], window=App['window']['value'])
    camera['stop'] = lambda: camera['camera'].stop_preview()
    camera['close'] = lambda: camera['camera'].close()
    App['camera'] = {"iso": camera['camera'].iso,
                     "wb": camera['camera'].awb_mode,
                     "dynamicRangeCompression": camera['camera'].drc_strength,
                     "exposureMode": camera['camera'].exposure_mode,
                     "exposureCompensation": camera['camera'].exposure_compensation,
                     "shutterSpeed": camera['camera'].shutter_mode,
                     "imageDenoise": camera['camera'].image_denoise,
                     "meteringMode": camera['camera'].meter_mode,
                     "imageResolution": camera['camera'].resolution,
                     }
