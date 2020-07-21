# Import the pygame module
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    K_RETURN,
    QUIT,
)
import pygame
import time
from functions import *
from constants import *
import shutil
import picamera

total, used, free = shutil.disk_usage("/")
# print("Total: %d GiB" % (total // (2**30)))
# print("Used: %d GiB" % (used // (2**30)))
# print("Free: %d GiB" % (free // (2**30)))
App[DISK_SPACE] = free // (2**30)


camera = picamera.PiCamera()
camera.shutter_speed = App[SHUTTER_SPEED]
camera.iso = App[ISO]

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards

# Initialize pygame
pygame.init()
clock = pygame.time.Clock()

# Define constants for the screen width and height
SCREEN_WIDTH = App[DEFAULT_WINDOW_SIZE][2]
SCREEN_HEIGHT = App[DEFAULT_WINDOW_SIZE][3]

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# create a font object.
# 1st parameter is the font file
# which is present in pygame.
# 2nd parameter is size of the font
font = pygame.font.Font('freesansbold.ttf', 24)

# create a text suface object,
# on which text is drawn on it.
textColor = (255, 255, 255)
highlightedTextColor = (0, 0, 0)
highlighted = (255, 255, 255)
padding = 20

# create a list of all the text on the GUI
textList = {}
textList['file'] = lambda: f"{int(App[DISK_SPACE]//0.00025)}|{App[DISK_SPACE]}GB {product(App[IMAGE_RESOLUTION])//1000000}MP {App[IMAGE_FORMAT]} {App[IMAGE_COMPRESSION]}"
textList[CAMERA_CAPTURE_MODE] = lambda: f"{App[CAMERA_CAPTURE_MODE_VALUES][App[CAMERA_CAPTURE_MODE]]} MODE"
textList[METERING_MODE] = lambda: f"{App[METERING_MODE]} METERING"
textList[AWB] = lambda: f"{App[AWB].upper()} WB"
textList[IMAGE_DR_COMPRESSION] = lambda: f"DRC {App[IMAGE_DR_COMPRESSION].upper()}"
textList[EXPOSURE] = lambda: f"EXPOSURE {App[EXPOSURE].upper()}"
textList[ISO] = lambda: f"{App[ISO]} ISO"


# creates transparent surface to blit all other surfaces to
layer = pygame.Surface((1280, 720), pygame.SRCALPHA)

# Variable to keep the main loop running
running = True
firstLoop = True

# startingthe camera preview
camera.start_preview(fullscreen=False, window=App[DEFAULT_WINDOW_SIZE])

# initializing overlay variable
o = None

# Main loop
while running:
    # Look at every event in the queue
    for event in pygame.event.get():
        # Did the user hit a key?
        if event.type == KEYDOWN:
            # Was it the Escape key? If so, stop the loop.
            if event.key == K_ESCAPE:
                running = False
            # Was it the Escape key? If so, stop the loop.
            if event.key == K_RETURN:
                # pass
                takePhoto(camera, App, IMAGE_FILE_PATH, IMAGE_COUNT)
        # Did the user click the window close button? If so, stop the loop.
        elif event.type == QUIT:
            running = False

    # makes the GUI repr white
    screen.fill((0, 0, 0))
    layer.fill((0, 0, 0, 0))

    # blitting all text onto layer
    for key in textList:
        background = None
        currentTextColor = textColor
        currentIndex = list(textList.keys()).index(key)
        if currentIndex == 0:
            background = highlighted
            currentTextColor = highlightedTextColor
            nextItemHpos = 0
        text = textGen(font, textList[key](), currentTextColor, background)
        rect = textRectify(text)
        nextItemHpos = rect.height*(currentIndex)
        if currentIndex == 0:
            nextItemHpos = 0
        layer.blit(text, ((SCREEN_WIDTH - rect.width - padding, rect.height*(currentIndex) + padding),
                          (rect.width, rect.height)))

    # draw metering area
    meterWidth = SCREEN_WIDTH//100 * \
        App[METERING_MODE_VALUES][App[METERING_MODE]]['value']
    rect = pygame.draw.rect(
        layer, (128, 128, 128), ((SCREEN_WIDTH//2-(meterWidth//2), SCREEN_HEIGHT//2-(meterWidth//2)), (meterWidth, meterWidth)), 3)

    #  test updating a value
    App[DISK_SPACE] = App[DISK_SPACE] + 1
    print(App[DISK_SPACE])

    pygamesScreenRaw = pygame.image.tostring(layer, 'RGBA')
    if firstLoop:
        o = camera.add_overlay(pygamesScreenRaw, size=(
            1280, 720), fullscreen=False, window=App[DEFAULT_WINDOW_SIZE])
        o.alpha = 255
        o.layer = 3
        firstLoop = not firstLoop
    else:
        o.update(pygamesScreenRaw)

    screen.blit(layer, (0, 0))
    pygame.display.flip()
    clock.tick(15)
