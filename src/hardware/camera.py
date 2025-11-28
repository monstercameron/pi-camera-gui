try:
    import picamera
except ImportError:
    picamera = None

try:
    import pygame.camera
    pygame.camera.init()
except ImportError:
    pass

import os
from os import path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, Callable
from abc import ABC, abstractmethod
from src.core.config import config
import pygame
import shutil
import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor
try:
    from PIL import Image
except ImportError:
    Image = None

def generate_exif_bytes(metadata=None):
    """Generates EXIF bytes with rich metadata."""
    if not Image:
        return None
    
    try:
        # Create a dummy image to generate EXIF structure
        # We can't just create bytes directly easily without using Pillow's machinery
        # or we can use a minimal image.
        img = Image.new('RGB', (1, 1))
        exif = img.getexif()
        
        # Standard EXIF
        exif[0x010f] = "Raspberry Pi"             # Make
        exif[0x0110] = "PiCamera"                 # Model
        exif[0x0131] = "PiCameraGUI"              # Software
        exif[0x013b] = "PiCamera User"            # Artist
        exif[0x8298] = "Copyright (c) 2025"       # Copyright
        exif[0x010e] = "Captured with PiCameraGUI" # ImageDescription
        
        # DateTime
        dt_str = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
        exif[0x9003] = dt_str                     # DateTimeOriginal
        exif[0x9004] = dt_str                     # DateTimeDigitized
        exif[0x0132] = dt_str                     # DateTime

        # Camera Tech Specs (Static/Mock for now)
        exif[0xA405] = 35                         # FocalLengthIn35mmFilm
        exif[0x829D] = (28, 10)                   # FNumber (f/2.8)
        exif[0x920A] = (304, 100)                 # FocalLength (3.04mm)
        exif[0x9205] = (28, 10)                   # MaxApertureValue (f/2.8)
        exif[0x9207] = 5                          # MeteringMode (Pattern)
        exif[0x9209] = 0                          # Flash (No Flash)
        
        # Extended Tech Specs
        exif[0x920B] = (100, 1)                   # FlashEnergy
        exif[0xA433] = "Raspberry Pi"             # LensMake
        exif[0xA434] = "PiCamera Module v2"       # LensModel
        exif[0xA431] = "0000000000"               # BodySerialNumber
        exif[0x9000] = b"0232"                    # ExifVersion
        exif[0xA404] = (0, 1)                     # DigitalZoomRatio
        exif[0x0106] = 2                          # PhotometricInterpretation (RGB)
        
        # Dynamic/Default Settings
        exif[0xA408] = 0                          # Contrast (Normal)
        exif[0x9203] = (50, 100)                  # BrightnessValue
        exif[0x9208] = 0                          # LightSource (Unknown)
        exif[0x8822] = 2                          # ExposureProgram (Normal)
        exif[0xA409] = 0                          # Saturation (Normal)
        exif[0xA40A] = 0                          # Sharpness (Normal)
        exif[0xA403] = 0                          # WhiteBalance (Auto)

        # Windows XP Tags (UCS-2 encoded)
        def encode_xp(text):
            return text.encode('utf-16le') + b'\x00\x00'

        exif[0x9c9b] = encode_xp("PiCamera Capture")      # XPTitle
        exif[0x9c9c] = encode_xp("Created with PiCameraGUI") # XPComment
        exif[0x9c9d] = encode_xp("PiCamera User")         # XPAuthor
        exif[0x9c9e] = encode_xp("picamera;gui;python")   # XPKeywords
        exif[0x9c9f] = encode_xp("Photography")           # XPSubject

        if metadata:
            if 'iso' in metadata:
                # 0x8827: ISO
                exif[0x8827] = int(metadata['iso'])
            
            if 'shutter_speed' in metadata:
                # 0x829a: ExposureTime (Rational)
                # Shutter speed is in microseconds
                ss = int(metadata['shutter_speed'])
                if ss > 0:
                    # Convert to seconds fraction (approx)
                    exif[0x829a] = (ss, 1000000)

        return exif.tobytes()
    except Exception as e:
        print(f"Error generating EXIF: {e}")
        return None

def add_exif_to_file_task(file_name, metadata=None):
    """Adds rich EXIF metadata to an existing image file."""
    try:
        if Image:
            print(f"Adding EXIF to: {file_name}")
            img = Image.open(file_name)
            exif_bytes = generate_exif_bytes(metadata)
            
            if exif_bytes:
                # We must save the image to write the EXIF.
                # This might re-encode JPEGs.
                # To minimize loss, we can try to use the same quality if known, or high quality.
                # But Pillow doesn't easily let us 'copy' the compressed stream with new headers.
                # For now, we accept re-encoding as the cost of rich metadata on RPi without complex libraries.
                img.save(file_name, exif=exif_bytes, quality=95) 
                print(f"EXIF added to: {file_name}")
        else:
            print("Pillow not installed, cannot add EXIF.")
    except Exception as e:
        print(f"Error adding EXIF to file: {e}")

def software_encode_task(file_name, data, resolution, fmt, quality, metadata=None):
    try:
        if Image:
            print(f"Software encoding: {file_name} ({fmt})")
            # Create image from raw RGB
            img = Image.frombytes('RGB', resolution, data)
            
            # Save
            # Map format to Pillow format
            pil_fmt = fmt.upper()
            if pil_fmt == 'JPG': pil_fmt = 'JPEG'
            
            # Save params
            params = {}
            if pil_fmt == 'JPEG':
                params['quality'] = quality
            elif pil_fmt == 'PNG':
                params['compress_level'] = 6 # Default
            
            # Add Metadata (EXIF)
            # Pillow supports EXIF for JPEG, PNG, WebP, TIFF
            if pil_fmt in ['JPEG', 'PNG', 'WEBP', 'TIFF']:
                exif_bytes = generate_exif_bytes(metadata)
                if exif_bytes:
                    params['exif'] = exif_bytes

            img.save(file_name, format=pil_fmt, **params)
            print(f"Software encode success: {file_name}")
        else:
            print("Pillow not installed, cannot encode in software.")
    except Exception as e:
        print(f"Software encode error: {e}")

class CameraBase(ABC):
    def __init__(self, menus: Dict[str, Any], settings: Dict[str, Any]):
        self.menus = menus
        self.settings = settings
        self.resolution: Tuple[int, int] = (4000, 3000)
        self.has_hardware_overlay: bool = False
        self.image_format: str = "jpeg"
        self.image_quality: int = 85
        
        # Encoder Thread Pool
        # Optimize for RPi 4 (4 cores) or scalable
        workers = os.cpu_count() or 4
        self.encoder_pool = ThreadPoolExecutor(max_workers=workers)

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

    @abstractmethod
    def get_supported_options(self, key: str) -> Optional[list]: pass

    def get_disk_space(self) -> str:
        try:
            path_to_check = self.settings["files"]["path"]
            if not path.exists(path_to_check):
                return "N/A"
            total, used, free = shutil.disk_usage(path_to_check)
            return f"{free // (1024 * 1024)}MB"
        except Exception:
            return "N/A"

    def get_estimated_size(self) -> str:
        # Rough estimation
        w, h = self.resolution
        pixels = w * h
        
        if self.image_format == "jpeg":
            # Approx 1/10 compression at 85 quality
            # Adjust for quality
            compression = 0.1 * (self.image_quality / 85.0)
            bytes_size = pixels * 3 * compression
        elif self.image_format in ["raw", "bmp"]:
            bytes_size = pixels * 3
        elif self.image_format == "png":
            bytes_size = pixels * 3 * 0.5 # Approx
        else:
            bytes_size = pixels * 3 * 0.2 # Generic
            
        mb_size = bytes_size / (1024 * 1024)
        return f"{mb_size:.2f}MB"

    def get_remaining_photos(self) -> str:
        try:
            path_to_check = self.settings["files"]["path"]
            if not path.exists(path_to_check):
                return "0"
            total, used, free = shutil.disk_usage(path_to_check)
            
            # Parse estimated size
            est_str = self.get_estimated_size()
            est_mb = float(est_str.replace("MB", ""))
            if est_mb == 0: est_mb = 0.01 # Avoid div by zero
            
            return str(int((free // (1024 * 1024)) / est_mb))
        except Exception:
            return "0"

    def _get_next_filename(self, extension):
        date_and_time = datetime.now().strftime('%Y-%m-%d')
        file_number = 1
        file_path = self.settings["files"]["path"]
        template = self.settings["files"]["template"]
        
        # List of extensions to check for continuity
        checked_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp']
        
        while True:
            # Check if this file number exists with ANY extension
            exists = False
            for ext in checked_extensions:
                check_name = f'{file_path}/{template.format(date_and_time, str(file_number))}.{ext}'
                if path.exists(check_name):
                    exists = True
                    break
            
            if exists:
                file_number += 1
            else:
                # Found a free number
                break
                
        return f'{file_path}/{template.format(date_and_time, str(file_number))}.{extension}'

    def set_image_format(self, value=None):
        if value is not None:
            self.image_format = value
            print(f"Image format set to {value}")
        return self.image_format

    def set_image_quality(self, value=None):
        if value is not None:
            self.image_quality = value
            print(f"Image quality set to {value}")
        return self.image_quality

    def _save_image_task(self, file_name, data, fmt, quality, resolution):
        try:
            print(f"Encoding image: {file_name} ({fmt}, Q={quality})")
            if Image:
                # Assuming data is RGB bytes or similar if we captured to stream
                # For now, if we use PiCamera capture to file, this task is just metadata/post-process
                # But if we captured to stream, we save here.
                
                # If data is None, it means we already saved via hardware (e.g. JPEG)
                pass
            else:
                print("Pillow not installed, cannot encode in software.")
        except Exception as e:
            print(f"Error saving image: {e}")


class RealCamera(CameraBase):
    def __init__(self, menus: Dict[str, Any], settings: Dict[str, Any]):
        super().__init__(menus, settings)
        if picamera is None:
            raise ImportError("picamera module not found")
        self.camera = picamera.PiCamera()
        self.has_hardware_overlay = True
        self.overlay = None
        
        # Capture Queue for sequential hardware access
        self.capture_queue = queue.Queue()
        self.capture_worker = threading.Thread(target=self._capture_queue_worker, daemon=True)
        self.capture_worker.start()
        
        self._auto_mode()

    def get_supported_options(self, key: str) -> Optional[list]:
        try:
            if key == "awb":
                return list(picamera.PiCamera.AWB_MODES.keys())
            elif key == "exposure":
                return list(picamera.PiCamera.EXPOSURE_MODES.keys())
            elif key == "imageeffect":
                return list(picamera.PiCamera.IMAGE_EFFECTS.keys())
            elif key == "metering":
                return list(picamera.PiCamera.METER_MODES.keys())
            elif key == "dynamicRangeCompression":
                return list(picamera.PiCamera.DRC_STRENGTHS.keys())
        except AttributeError:
            pass
        return None

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

    def _capture_queue_worker(self):
        while True:
            try:
                args = self.capture_queue.get()
                self._execute_capture(*args)
                self.capture_queue.task_done()
            except Exception as e:
                print(f"Capture worker error: {e}")

    def _execute_capture(self, file_name, resolution, fmt, quality):
        try:
            # If format is supported by PiCamera hardware/firmware, use it directly
            # PiCamera supports: jpeg, png, gif, bmp, yuv, rgb, rgba, bgr, bgra
            # However, only JPEG is hardware accelerated.
            
            # If user wants to use software encoder (e.g. for better PNG compression or unsupported formats),
            # we should capture to stream and offload.
            
            # For now, we stick to PiCamera's capture for simplicity unless it's a format we want to handle manually.
            # But the user asked for "n remaining encoder threads".
            
            # Let's implement a hybrid approach:
            # 1. If JPEG, use PiCamera (fastest).
            # 2. If others, capture RGB to stream, then submit to encoder pool.
            
            if fmt == 'jpeg':
                print(f"Starting hardware capture: {file_name} (jpeg, Q={quality})")
                # PiCamera quality is 1-100
                self.camera.capture(file_name, format='jpeg', quality=quality)
                print('Camera capture success:' + file_name)
                
                # Post-process to add rich EXIF metadata
                metadata = {
                    'iso': self.iso(),
                    'shutter_speed': self.shutter_speed(),
                    'awb': self.white_balance(),
                    'exposure': self.exposure()
                }
                self.encoder_pool.submit(add_exif_to_file_task, file_name, metadata)
            else:
                # Capture to stream (RGB)
                import io
                stream = io.BytesIO()
                print(f"Capturing raw RGB for software encoding...")
                self.camera.capture(stream, format='rgb')
                stream.seek(0)
                
                # Offload encoding
                # We need to read the stream content to pass to thread safely? 
                # Or just pass the stream.
                data = stream.read()
                
                # Gather Metadata
                metadata = {
                    'iso': self.iso(),
                    'shutter_speed': self.shutter_speed(),
                    'awb': self.white_balance(),
                    'exposure': self.exposure()
                }
                
                self.encoder_pool.submit(software_encode_task, file_name, data, resolution, fmt, quality, metadata)
                
        except Exception as e:
            print('Camera capture error')
            print(e)

    def captureImage(self):
        self.camera.resolution = self.resolution

        try:
            extension = self.image_format # Use selected format
            # Map format to extension if needed (e.g. jpeg -> jpg)
            if extension == 'jpeg': extension = 'jpg'
            
            file_name = self._get_next_filename(extension)

            # Ensure directory exists
            file_dir = os.path.dirname(file_name)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)

            # Queue capture request
            self.capture_queue.put((file_name, self.resolution, self.image_format, self.image_quality))
            
        except Exception as e:
            print('Camera capture setup error')
            print(e)

        # Reset resolution for preview (if needed, usually preview uses different res)
        # self.camera.resolution = (self.settings["display"]["width"], self.settings["display"]["height"])

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
            "resolution": self.resolution_get_set,
            "imageformat": self.set_image_format,
            "quality": self.set_image_quality,
            "filesize": self.get_estimated_size,
            "remaining": self.get_remaining_photos
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
                self.webcam_device = cameras[0]
                print(f"MockCamera: Requesting resolution {self.resolution}")
                self.webcam = pygame.camera.Camera(self.webcam_device, self.resolution)
                self.webcam.start()
                print(f"MockCamera: Webcam started on {self.webcam_device} at {self.webcam.get_size()}")
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
            if self.is_previewing:
                self.stopPreview()
                self.startPreview()
        return self.resolution

    def captureImage(self):
        print(f"MockCamera: *CLICK* Image captured at {self.resolution} in {self.image_format}")
        
        # Determine filename
        extension = self.image_format
        if extension == 'jpeg': extension = 'jpg'
        
        file_name = self._get_next_filename(extension)

        # Ensure directory exists
        file_dir = os.path.dirname(file_name)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        # Capture Data
        data = None
        capture_res = self.resolution

        if self.webcam:
            try:
                surf = self.webcam.get_image()
                data = pygame.image.tostring(surf, 'RGB')
                capture_res = surf.get_size()
            except Exception as e:
                print(f"MockCamera: Webcam capture error: {e}")
        
        if data is None:
            # Generate dummy blue image
            if Image:
                img = Image.new('RGB', self.resolution, color=(100, 150, 200))
                data = img.tobytes()
                capture_res = self.resolution

        if data:
             # Gather Metadata
             metadata = {
                 'iso': self.iso(),
                 'shutter_speed': self.shutter_speed(),
                 'awb': self.white_balance(),
                 'exposure': self.exposure()
             }
             self.encoder_pool.submit(software_encode_task, file_name, data, capture_res, self.image_format, self.image_quality, metadata)

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
            "resolution": self.resolution_get_set,
            "imageformat": self.set_image_format,
            "quality": self.set_image_quality,
            "filesize": self.get_estimated_size,
            "remaining": self.get_remaining_photos
        }

    def get_supported_options(self, key: str) -> Optional[list]:
        if key == "awb":
            return ["off", "auto", "sunlight", "cloudy", "shade", "tungsten", "fluorescent", "incandescent", "flash", "horizon"]
        elif key == "exposure":
            return ["off", "auto", "night", "nightpreview", "backlight", "spotlight", "sports", "snow", "beach", "verylong", "fixedfps", "antishake", "fireworks"]
        elif key == "imageeffect":
            return ["none", "negative", "solarize", "sketch", "denoise", "emboss", "oilpaint", "hatch", "gpen", "pastel", "watercolor", "film", "blur", "saturation", "colorswap", "washedout", "posterise", "colorpoint", "colorbalance", "cartoon", "deinterlace1", "deinterlace2"]
        elif key == "dynamicRangeCompression":
            return ["off", "low", "medium", "high"]
        return None


def get_camera(menus: Dict[str, Any], settings: Dict[str, Any]) -> CameraBase:
    if config.USE_MOCK_CAMERA:
        print("Using MockCamera (Configured or Auto-detected)")
        return MockCamera(menus, settings)
    else:
        return RealCamera(menus, settings)
