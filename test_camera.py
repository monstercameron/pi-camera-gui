import pygame
import pygame.camera

pygame.init()
pygame.camera.init()

cameras = pygame.camera.list_cameras()
print(f"Cameras found: {cameras}")

if cameras:
    cam = pygame.camera.Camera(cameras[0])
    cam.start()
    img = cam.get_image()
    print(f"Captured image size: {img.get_size()}")
    cam.stop()
else:
    print("No cameras found.")
