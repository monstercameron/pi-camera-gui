try:
    import picamera
except ImportError:
    picamera = None

try:
    import pygame.camera
    pygame.camera.init()
except ImportError:
    pass

from os import path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, Callable
from abc import ABC, abstractmethod
from src.core.config import config
import pygame

class CameraBase(ABC):
    def __init__(self, menus: Dict[str, Any], settings: Dict[str, Any]):
        self.menus = menus
        self.settings = settings
        self.resolution: Tuple[int, int] = (4000, 3000)
        self.has_hardware_overlay: bool = False

    @abstractmethod
    def startPreview(self): pass

    @abstractmethod
    def stopPreview(self): pass

    @abstractmethod
    def closeCamera(self): pass
    
    @abstractmethod
    def getCamera(self): pass

    @abstractmethod
    def captureImage(self): pass

    @abstractmethod
    def controls(self, pygame_mod, key): pass

    @abstractmethod
    def directory(self) -> Dict[str, Callable]: pass
    
    @abstractmethod
    def render(self, overlay_surface: pygame.Surface, display_surface: pygame.Surface): pass


class RealCamera(CameraBase):
    def __init__(self, menus: Dict[str, Any], settings: Dict[str, Any]):
        super().__init__(menus, settings)
        if picamera is None:
            raise ImportError("picamera module not found")
        self.camera = picamera.PiCamera()
        self.has_hardware_overlay = True
        self.overlay = None
        self._auto_mode()

    def _auto_mode(self):
        self.camera.exposure_mode = 'auto'
        self.camera.shutter_speed = 0
        self.camera.iso = 0

    def getCamera(self):
        return self.camera

    def render(self, overlay_surface: pygame.Surface, display_surface: pygame.Surface):
        # Hardware Overlay Handling
        # Convert Pygame surface to raw bytes
        pygames_screen_raw = pygame.image.tostring(overlay_surface, 'RGBA')
        width, height = overlay_surface.get_size()
        
        if self.overlay is None:
            # Create overlay
            try:
                self.overlay = self.camera.add_overlay(
                    pygames_screen_raw,
                    size=(width, height),
                    layer=3,
                    alpha=255,
                    fullscreen=False,
                    window=(0, 0, width, height)
                )
            except Exception as e:
                print(f"Error creating overlay: {e}")
        else:
            # Update overlay
            try:
                self.overlay.update(pygames_screen_raw)
            except Exception as e:
                print(f"Error updating overlay: {e}")

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

    def shutter_speed(self, value=None):
        if value is not None:
            self.camera.shutter_speed = value
        return self.camera.shutter_speed

    def iso(self, value=None):
        if value is not None:
            self.camera.iso = value
        return self.camera.iso

    def white_balance(self, value=None):
        if value is not None:
            self.camera.awb_mode = value
        return self.camera.awb_mode

    def sharpness(self, value=None):
        if value is not None:
            self.camera.sharpness = value
        return self.camera.sharpness

    def img_denoise(self, value=None):
        if value is not None:
            self.camera.image_denoise = value
        return self.camera.image_denoise

    def img_effect(self, value=None):
        if value is not None:
            self.camera.image_effect = value
        return self.camera.image_effect

    def drc_strength(self, value=None):
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

    def resolution_get_set(self, value=None):
        if value is not None:
            str_to_tuple = tuple(map(int, value.split(',')))
            self.resolution = str_to_tuple
        return self.resolution

    def captureImage(self):
        self.camera.resolution = self.resolution

        try:
            date_and_time = datetime.now().strftime('%Y-%m-%d')
            file_number = 1
            file_path = self.settings["files"]["path"]
            template = self.settings["files"]["template"]
            extension = self.settings["files"]["extension"]
            
            file_name = f'{file_path}/{template.format(date_and_time, str(file_number))}.{extension}'

            while path.exists(file_name):
                file_number += 1
                file_name = f'{file_path}/{template.format(date_and_time, str(file_number))}.{extension}'

            self.camera.capture(file_name)
            print('Camera capture success:' + file_name)
        except Exception as e:
            print('Camera capture error')
            print(e)

        self.camera.resolution = (
            self.settings["display"]["width"], self.settings["display"]["height"])

    def controls(self, pygame_mod, key):
        if key == pygame_mod.K_RETURN:
            self.captureImage()

    def directory(self) -> Dict[str, Callable]:
        return {
            "exposure": self.exposure,
            "shutter": self.shutter_speed,
            "iso": self.iso,
            "awb": self.white_balance,
            "sharpness": self.sharpness,
            "imagedenoise": self.img_denoise,
            "imageeffect": self.img_effect,
            "dynamicrangecompression": self.drc_strength,
            "contrast": self.contrast,
            "saturation": self.saturation,
            "brightness": self.brightness,
            "resolution": self.resolution_get_set
        }


class MockCamera(CameraBase):
    def __init__(self, menus: Dict[str, Any], settings: Dict[str, Any]):
        super().__init__(menus, settings)
        self.has_hardware_overlay = False
        self.webcam = None
        self.is_previewing = False
        
        # Mock state
        self._exposure_mode = 'auto'
        self._shutter_speed = 0
        self._iso = 0
        self._awb_mode = 'auto'
        self._sharpness = 0
        self._image_denoise = False
        self._image_effect = 'none'
        self._drc_strength = 'off'
        self._contrast = 0
        self._saturation = 0
        self._brightness = 50

    def getCamera(self):
        return None

    def startPreview(self):
        print("MockCamera: startPreview")
        self.is_previewing = True
        try:
            cameras = pygame.camera.list_cameras()
            if cameras:
                self.webcam = pygame.camera.Camera(cameras[0])
                self.webcam.start()
                print(f"MockCamera: Webcam started on {cameras[0]}")
            else:
                print("MockCamera: No webcam found")
        except Exception as e:
            print(f"MockCamera: Error starting webcam: {e}")

    def stopPreview(self):
        print("MockCamera: stopPreview")
        self.is_previewing = False
        if self.webcam:
            self.webcam.stop()
            self.webcam = None

    def closeCamera(self):
        print("MockCamera: closeCamera")
        self.stopPreview()

    def render(self, overlay_surface: pygame.Surface, display_surface: pygame.Surface):
        # Render Webcam Feed
        if self.is_previewing and self.webcam:
            try:
                frame = self.webcam.get_image()
                if frame:
                    # Calculate aspect ratio scaling
                    frame_rect = frame.get_rect()
                    display_rect = display_surface.get_rect()
                    
                    # Calculate scale factor to fit within display while maintaining aspect ratio
                    scale_w = display_rect.width / frame_rect.width
                    scale_h = display_rect.height / frame_rect.height
                    scale = min(scale_w, scale_h)
                    
                    new_width = int(frame_rect.width * scale)
                    new_height = int(frame_rect.height * scale)
                    
                    scaled_frame = pygame.transform.scale(frame, (new_width, new_height))
                    
                    # Center the frame
                    dest_rect = scaled_frame.get_rect(center=display_rect.center)
                    
                    # Clear background (black bars)
                    display_surface.fill((0, 0, 0))
                    
                    # Blit scaled frame
                    display_surface.blit(scaled_frame, dest_rect)
            except Exception:
                pass
        
        # Render Menu Layer on top
        display_surface.blit(overlay_surface, (0, 0))

    def exposure(self, value=None):
        if value is not None:
            self._exposure_mode = value
            print(f"MockCamera: Set exposure to {value}")
        return self._exposure_mode

    def shutter_speed(self, value=None):
        if value is not None:
            self._shutter_speed = value
            print(f"MockCamera: Set shutter speed to {value}")
        return self._shutter_speed

    def iso(self, value=None):
        if value is not None:
            self._iso = value
            print(f"MockCamera: Set ISO to {value}")
        return self._iso

    def white_balance(self, value=None):
        if value is not None:
            self._awb_mode = value
            print(f"MockCamera: Set AWB to {value}")
        return self._awb_mode

    def sharpness(self, value=None):
        if value is not None:
            self._sharpness = value
            print(f"MockCamera: Set sharpness to {value}")
        return self._sharpness

    def img_denoise(self, value=None):
        if value is not None:
            self._image_denoise = value
            print(f"MockCamera: Set denoise to {value}")
        return self._image_denoise

    def img_effect(self, value=None):
        if value is not None:
            self._image_effect = value
            print(f"MockCamera: Set effect to {value}")
        return self._image_effect

    def drc_strength(self, value=None):
        if value is not None:
            self._drc_strength = value
            print(f"MockCamera: Set DRC to {value}")
        return self._drc_strength

    def contrast(self, value=None):
        if value is not None:
            self._contrast = value
            print(f"MockCamera: Set contrast to {value}")
        return self._contrast

    def saturation(self, value=None):
        if value is not None:
            self._saturation = value
            print(f"MockCamera: Set saturation to {value}")
        return self._saturation

    def brightness(self, value=None):
        if value is not None:
            self._brightness = value
            print(f"MockCamera: Set brightness to {value}")
        return self._brightness

    def resolution_get_set(self, value=None):
        if value is not None:
            str_to_tuple = tuple(map(int, value.split(',')))
            self.resolution = str_to_tuple
            print(f"MockCamera: Set resolution to {self.resolution}")
        return self.resolution

    def captureImage(self):
        print(f"MockCamera: *CLICK* Image captured at {self.resolution}")

    def controls(self, pygame_mod, key):
        if key == pygame_mod.K_RETURN:
            self.captureImage()

    def directory(self) -> Dict[str, Callable]:
        return {
            "exposure": self.exposure,
            "shutter": self.shutter_speed,
            "iso": self.iso,
            "awb": self.white_balance,
            "sharpness": self.sharpness,
            "imagedenoise": self.img_denoise,
            "imageeffect": self.img_effect,
            "dynamicrangecompression": self.drc_strength,
            "contrast": self.contrast,
            "saturation": self.saturation,
            "brightness": self.brightness,
            "resolution": self.resolution_get_set
        }

def get_camera(menus: Dict[str, Any], settings: Dict[str, Any]) -> CameraBase:
    if config.USE_MOCK_CAMERA:
        print("Using MockCamera (Configured or Auto-detected)")
        return MockCamera(menus, settings)
    else:
        return RealCamera(menus, settings)
