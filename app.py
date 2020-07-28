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
from os import path, mkdir
from functions import *
from constants import App, camera, devMode

clock = None
screen = None
font = None
textColor = None
textBackground = None
highlightedTextColor = None
highlighted = None
padding = None
layer = None
firstLoop = None
o = None
startCamera = None
stopCamera = None
closeCamera = None


def init():
    # check if path exists
    if not path.exists(App['imageDirectory']['value']):
        mkdir(App['imageDirectory']['value'])

    # Import pygame.locals for easier access to key coordinates
    # Updated to conform to flake8 and black standards

    # Initialize pygame
    pygame.init()
    global clock
    clock = pygame.time.Clock()

    # Create the screen object
    # The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
    global screen
    screen = pygame.display.set_mode(
        (App['fullscreen']['value'][0], App['fullscreen']['value'][1]))

    # create a font object.
    # 1st parameter is the font file
    # which is present in pygame.
    # 2nd parameter is size of the font
    global font
    font = pygame.font.Font('freesansbold.ttf', App['font']['value'])

    # create a text suface object,
    # on which text is drawn on it.
    global textColor
    global textBackground
    global highlightedTextColor
    global highlighted
    textColor = App['fontColor']['value'][0]
    textBackground = App['fontColor']['value'][1]
    highlightedTextColor = App['fontColor']['value'][2]
    highlighted = App['fontColor']['value'][0]

    global padding
    padding = App['padding']['value']

    # creates transparent surface to blit all other surfaces to
    global layer
    layer = pygame.Surface(
        (App['fullscreen']['value'][0], App['fullscreen']['value'][1]), pygame.SRCALPHA)

    # Variable to keep the main loop running
    global firstLoop
    firstLoop = True

    # starting the camera preview
    global startCamera
    global stopCamera
    global closeCamera
    def startCamera(): return camera.start_preview(
        fullscreen=App['isFullscreen']['value'], window=App['window']['value'])

    def stopCamera(): return camera.stop_preview()
    def closeCamera(): return camera.close()
    if not devMode:
        startCamera()


def main():
    # Main loop
    while App['alive']['value']:
        # current menu
        aList = App['menus'][App['mode']['value']][App['menu']['value']]
        # Look at every event in the queue
        for event in pygame.event.get():
            # Did the user hit a key?
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop the loop.
                if event.key == K_ESCAPE:
                    App['alive']['value'] = False

                if event.key == K_RETURN:
                    if not devMode:
                        camera.resolution = App['imageResolution']['value']
                        takePhoto(
                            camera, App['imageFilePath'], App['imageIterator'])
                        camera.resolution = (
                            App['fullscreen']['value'][0], App['fullscreen']['value'][1])

                if event.key == K_UP:
                    App['menuHighlight']['value'] = incrementAndCycleTuples(
                        -1, App['menuHighlight']['value'], aList, (0, len(aList)))

                if event.key == K_DOWN:
                    App['menuHighlight']['value'] = incrementAndCycleTuples(
                        1, App['menuHighlight']['value'], aList, (0, len(aList)))

                if event.key == K_LEFT:
                    try:
                        if type(App[App['menuHighlight']['value']]['values']).__name__ == 'list':
                            App[App['menuHighlight']['value']]['value'] = traverseList2(
                                App[App['menuHighlight']['value']]['value'], 'next', App[App['menuHighlight']['value']]['values'])
                        elif type(App[App['menuHighlight']['value']]['values']).__name__ == 'tuple':
                            App[App['menuHighlight']['value']]['value'] = adjustByFactor2(
                                -2, App[App['menuHighlight']['value']]['value'], App[App['menuHighlight']['value']]['values'])
                    except:
                        pass
                if event.key == K_RIGHT:
                    try:
                        if type(App[App['menuHighlight']['value']]['values']).__name__ == 'list':
                            App[App['menuHighlight']['value']]['value'] = traverseList2(
                                App[App['menuHighlight']['value']]['value'], 'previous', App[App['menuHighlight']['value']]['values'])
                        elif type(App[App['menuHighlight']['value']]['values']).__name__ == 'tuple':
                            App[App['menuHighlight']['value']]['value'] = adjustByFactor2(
                                2, App[App['menuHighlight']['value']]['value'], App[App['menuHighlight']['value']]['values'])
                    except:
                        pass
            # Did the user click the window close button? If so, stop the loop.
            elif event.type == QUIT:
                App['alive']['value'] = False

        # makes the GUI repr white
        screen.fill((0, 0, 0))
        layer.fill((0, 0, 0, 0))

        # drawing menu options
        menuIdx = 0
        for key in App['menus'][App['mode']['value']][App['menu']['value']]:
            background = textBackground
            currentTextColor = textColor

            if App['menuHighlight']['value'] == '':
                App['menuHighlight']['value'] = key[0]
            if App['menuHighlight']['value'] == key[0]:
                background = highlighted
                currentTextColor = highlightedTextColor

            text = textGen(font, key[1]().upper(),
                           currentTextColor, background)
            rect = textRectify(text)
            layer.blit(text, ((App['fullscreen']['value'][0] - rect.width - App['padding']['value'], rect.height*(menuIdx) + App['padding']['value']),
                              (rect.width, rect.height)))
            menuIdx = menuIdx + 1

            # draw metering area
        meterWidth = App['fullscreen']['value'][0]//100 * \
            App['meteringMode']['values'][App['meteringMode']['value']]['value']
        rect = pygame.draw.rect(
            layer, (128, 128, 128), ((App['fullscreen']['value'][0]//2-(meterWidth//2), App['fullscreen']['value'][1]//2-(meterWidth//2)), (meterWidth, meterWidth)), 3)

        if not devMode:
            pygamesScreenRaw = pygame.image.tostring(layer, 'RGBA')
            global firstLoop
            if firstLoop:
                o = camera.add_overlay(pygamesScreenRaw, size=(
                    1280, 720), fullscreen=False, window=App['window']['value'])
                o.alpha = 255
                o.layer = 3
                firstLoop = not firstLoop
            else:
                o.update(pygamesScreenRaw)
        elif devMode:
            screen.blit(layer, (0, 0))
            pygame.display.flip()

        clock.tick(15)

    if not devMode:
        stopCamera()
        closeCamera()


if __name__ == "__main__":
    init()
    main()
