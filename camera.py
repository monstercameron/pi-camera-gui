import picamera

class Camera:
    def __init__(self, menus, settings):
        self.camera = picamera.PiCamera()
        self.menus = menus
        self.settings = settings

    def startPreview():
        self.camera.start_preview(
            fullscreen=self.settings["display"]["fullscreen"], \
                window=(0,0,self.settings["display"]["height"],self.settings["display"]["width"]))

    def stopPreview():
        self.camera.stop_preview()

    def closeCamera(cameraClass):
        self.camera.close()

    def captureImage(settings):
        pass

    def captureVideo(settings):
        pass