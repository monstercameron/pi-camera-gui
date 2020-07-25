# Import the pygame module
pcDevMode = True
if not pcDevMode:
    import picamera
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
from os import path, mkdir
from functions import *
from constants import *

clock = None
screen  = None
font = None
textColor = None
textBackground = None
highlightedTextColor = None
highlighted = None
padding = None
layer =  None
firstLoop = None
o = None
startCamera =  None
stopCamera =  None
closeCamera =  None
SCREEN_WIDTH = None
SCREEN_HEIGHT = None
camera = None


def init():
    # check if path exists
    if not path.exists(App[IMAGE_DIRECTORY]):
        mkdir(App[IMAGE_DIRECTORY])

    # Import pygame.locals for easier access to key coordinates
    # Updated to conform to flake8 and black standards

    # Initialize pygame
    pygame.init()
    global clock
    clock = pygame.time.Clock()

    # Define constants for the screen width and height
    global SCREEN_WIDTH
    SCREEN_WIDTH = App[DEFAULT_WINDOW_SIZE][2]
    global SCREEN_HEIGHT
    SCREEN_HEIGHT = App[DEFAULT_WINDOW_SIZE][3]

    # Create the screen object
    # The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
    global screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # create a font object.
    # 1st parameter is the font file
    # which is present in pygame.
    # 2nd parameter is size of the font
    global font
    font = pygame.font.Font('freesansbold.ttf', 24)

    # create a text suface object,
    # on which text is drawn on it.
    global textColor
    textColor = (255, 255, 255)
    global textBackground
    textBackground = (0, 0, 0, 125)
    global highlightedTextColor
    highlightedTextColor = (0, 0, 0)
    global highlighted
    highlighted = (255, 255, 255)
    global padding
    padding = 20

    # creates transparent surface to blit all other surfaces to
    global layer 
    layer = pygame.Surface((1280, 720), pygame.SRCALPHA)

    # Variable to keep the main loop running
    firstLoop = True

    # setting up camera
    if not pcDevMode:
        camera = picamera.PiCamera()
        camera.shutter_speed = App[SHUTTER_SPEED]
        camera.iso = App[ISO]

    # starting the camera preview
    global startCamera
    startCamera = lambda: camera.start_preview(
        fullscreen=False, window=App[DEFAULT_WINDOW_SIZE])
    global stopCamera
    stopCamera = lambda: camera.stop_preview()
    global closeCamera
    closeCamera = lambda: camera.close()

    if not pcDevMode:
        startCamera()

    # initializing overlay variable
    global o
    o = None

def main():
    # Main loop
    while App[ALIVE]:
        # get  current  menu key
        menuKey = list(textList.keys())[App[MENU_HILITE]]
        # Look at every event in the queue
        for event in pygame.event.get():
            # Did the user hit a key?
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop the loop.
                if event.key == K_ESCAPE:
                    App[ALIVE] = False
                if event.key == K_RETURN:
                    if not pcDevMode:
                        camera.resolution = App[IMAGE_RESOLUTION]
                        takePhoto(camera, App, IMAGE_FILE_PATH, IMAGE_COUNT)
                        camera.resolution = (
                            App[DEFAULT_WINDOW_SIZE][2], App[DEFAULT_WINDOW_SIZE][3])
                if event.key == K_UP:
                    App[MENU_HILITE] = incrementAndCycle(
                        -1, App[MENU_HILITE], (0, len(textList.keys())-1))
                if event.key == K_DOWN:
                    App[MENU_HILITE] = incrementAndCycle(
                        1, App[MENU_HILITE], (0, len(textList.keys())))
                if event.key == K_LEFT:
                    menuActions(camera, menuKey, 'left')
                if event.key == K_RIGHT:
                    menuActions(camera, menuKey, 'right')
            # Did the user click the window close button? If so, stop the loop.
            elif event.type == QUIT:
                App[ALIVE] = False

        # makes the GUI repr white
        # screen.fill((255, 255, 255))
        screen.fill((0, 0, 0))
        layer.fill((0, 0, 0, 0))

        # blitting all text onto layer
        for key in textList:
            background = textBackground
            currentTextColor = textColor
            currentIndex = list(textList.keys()).index(key)
            if currentIndex == App[MENU_HILITE]:
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


        if not pcDevMode:
            pygamesScreenRaw = pygame.image.tostring(layer, 'RGBA')
            if firstLoop:
                o = camera.add_overlay(pygamesScreenRaw, size=(
                    1280, 720), fullscreen=False, window=App[DEFAULT_WINDOW_SIZE])
                o.alpha = 255
                o.layer = 3
                firstLoop = not firstLoop
            else:
                o.update(pygamesScreenRaw)
        elif pcDevMode:
            screen.blit(layer, (0, 0))
            pygame.display.flip()

        clock.tick(15)

    if not pcDevMode:
        stopCamera()
        closeCamera()

if __name__ == "__main__":
    init()
    main()
