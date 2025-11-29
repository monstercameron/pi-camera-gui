import os
import importlib.util

def is_module_available(name):
    return importlib.util.find_spec(name) is not None

class Config:
    def __init__(self):
        self._MOCK_CAMERA = os.getenv('MOCK_CAMERA')
        self._MOCK_GPIO = os.getenv('MOCK_GPIO')

    @property
    def USE_MOCK_CAMERA(self):
        if self._MOCK_CAMERA is not None:
            return self._MOCK_CAMERA.lower() == 'true'
        return not is_module_available('picamera')

    @property
    def USE_MOCK_GPIO(self):
        if self._MOCK_GPIO is not None:
            return self._MOCK_GPIO.lower() == 'true'
        if os.name == 'nt':
            return True
        return not is_module_available('gpiozero')

config = Config()
