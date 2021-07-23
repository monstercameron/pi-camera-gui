import picamera


class Camera:
    def __init__(self, menus, settings):
        self.camera = picamera.PiCamera()
        self.menus = menus
        self.settings = settings
        self.setCameraDefaults()

    def setCameraDefaults(self):
        self.exposure('off')
        self.iso(100)
        # self.shutterSpeed()

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
        print(f"{value} => {self.camera.iso}")
        if value is not None:
            self.camera.iso = value
        return self.camera.iso

    def captureImage(settings):
        pass

    def captureVideo(settings):
        pass

    def directory(self):
        return {
            "exposure": self.exposure,
            "shutter": self.shutterSpeed,
            "iso": self.iso
        }
