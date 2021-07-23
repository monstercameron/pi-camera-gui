import picamera

class Camera:
    def __init__(self, menus, settings):
        self.camera = picamera.PiCamera()
        self.menus = menus
        self.settings = settings
        self.setCameraDefaults()

    def setCameraDefaults(self):
        self.camera.exposure_mode = 'auto'

    def getCamera(self):
        return self.camera

    def startPreview(self):
        self.camera.start_preview(
            fullscreen=self.settings["display"]["fullscreen"], \
                window=(110,110,self.settings["display"]["width"],self.settings["display"]["height"]))

    def stopPreview(self):
        self.camera.stop_preview()

    def closeCamera(self):
        self.camera.close()

    def captureImage(settings):
        pass

    def captureVideo(settings):
        pass