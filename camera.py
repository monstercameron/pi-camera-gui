import picamera
from os import path
from datetime import datetime


class Camera:
    def __init__(self, menus, settings):
        self.camera = picamera.PiCamera()
        self.menus = menus
        self.settings = settings
        self.resolution = (4000, 3000)
        self.autoMode()

    def autoMode(self):
        self.camera.exposure_mode = 'auto'
        self.camera.shutter_speed = 0
        self.camera.iso = 0

    def getCamera(self):
        return self.camera

    def startPreview(self):
        self.camera.start_preview(
            fullscreen=self.settings["display"]["fullscreen"],
            window=(110, 110, self.settings["display"]["width"], self.settings["display"]["height"]))

    def stopPreview(self):
        self.camera.stop_preview()

    def closeCamera(self):
        self.camera.close()

    def exposure(self, value=None):
        if value is not None:
            self.camera.exposure_mode = value
        return self.camera.exposure_mode

    def shutterSpeed(self, value=None):
        if value is not None:
            self.camera.shutter_speed = value
        return self.camera.shutter_speed

    def iso(self, value=None):
        # print(f"{value} => {self.camera.iso}")
        if value is not None:
            self.camera.iso = value
        return self.camera.iso

    def whiteBalance(self, value=None):
        # print(f"{value} => {self.camera.iso}")
        if value is not None:
            self.camera.awb_mode = value
        return self.camera.awb_mode

    def sharpness(self, value=None):
        if value is not None:
            self.camera.sharpness = value
        return self.camera.sharpness

    def imgDenoise(self, value=None):
        if value is not None:
            self.camera.image_denoise = value
        return self.camera.image_denoise

    def imgEffect(self, value=None):
        if value is not None:
            self.camera.image_effect = value
        return self.camera.image_effect

    def drcStrength(self, value=None):
        if value is not None:
            self.camera.drc_strength = value
        return self.camera.drc_strength

    def contrast(self, value=None):
        if value is not None:
            self.camera.contrast = value
        return self.camera.contrast

    def saturation(self, value=None):
        if value is not None:
            self.camera.saturation = value
        return self.camera.saturation

    def brightness(self, value=None):
        if value is not None:
            self.camera.brightness = value
        return self.camera.brightness

    def resolutionGetSet(self, value=None):
        if value is not None:
            strToTuple = tuple(map(int, value.split(',')))
            self.resolution = strToTuple
        return self.resolution

    def captureImage(self):
        self.camera.resolution = self.resolution

        try:
            dateAndTime = datetime.now().strftime('%Y-%m-%d')
            fileNumber = 1
            file = f'{self.settings["files"]["path"]}/{self.settings["files"]["template"].format(dateAndTime, str(fileNumber))}.{self.settings["files"]["extension"]}'

            while path.exists(file):
                fileNumber = fileNumber + 1
                file = f'{self.settings["files"]["path"]}/{self.settings["files"]["template"].format(dateAndTime, str(fileNumber))}.{self.settings["files"]["extension"]}'

            # file = incrementPhotoIfExists(filePath, interator)
            file = f'{self.settings["files"]["path"]}/{self.settings["files"]["template"].format(dateAndTime, str(fileNumber))}.{self.settings["files"]["extension"]}'
            self.camera.capture(file)
            print('Camera capture success:' + file)
        except Exception as e:
            print('Camera capture error')
            print(e)

        self.camera.resolution = (
            self.settings["display"]["width"], self.settings["display"]["height"])

    def captureVideo(self):
        pass

    def controls(self, pygame, key):
        if key == pygame.K_RETURN:
            self.captureImage()

    def directory(self):
        return {
            "exposure": self.exposure,
            "shutter": self.shutterSpeed,
            "iso": self.iso,
            "awb": self.whiteBalance,
            "sharpness":self.sharpness,
            "imagedenoise":self.imgDenoise,
            "imageeffect":self.imgEffect,
            "dynamicrangecompression":self.drcStrength,
            "contrast":self.contrast,
            "saturation":self.saturation,
            "brightness":self.brightness,
            "resolution":self.resolutionGetSet
        }
