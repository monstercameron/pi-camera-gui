import pygame
import pygame.camera
import time

pygame.init()
pygame.camera.init()

cameras = pygame.camera.list_cameras()
if not cameras:
    print("No cameras found")
    exit()

cam_name = cameras[0]
print(f"Using camera: {cam_name}")

# Try default
cam = pygame.camera.Camera(cam_name)
cam.start()
img = cam.get_image()
print(f"Default resolution: {img.get_size()}")
cam.stop()

# Try High Res
target_res = (4000, 3000)
print(f"Requesting {target_res}...")
try:
    cam = pygame.camera.Camera(cam_name, target_res)
    cam.start()
    time.sleep(2) # Warmup
    img = cam.get_image()
    print(f"Got resolution: {img.get_size()}")
    cam.stop()
except Exception as e:
    print(f"Failed to set high res: {e}")
