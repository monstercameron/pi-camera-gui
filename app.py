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
from constants import App, camera, devMode, applyChanges

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
        (App['fullscreen']['value'][0], App['fullscreen']['value'][1]), pygame.FULLSCREEN)

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
    if not devMode:
        camera['start']()


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
                        camera['camera'].resolution = App['imageResolution']['value']
                        takePhoto(
                            camera['camera'], App['imageFilePath'](), App['imageIterator'])
                        camera['camera'].resolution = (
                            App['fullscreen']['value'][0], App['fullscreen']['value'][1])

                if event.key == K_UP:
                    App['menuHighlight']['value'] = aList[incrementAndCycle(
                        -1, aList.index(App['menuHighlight']['value']), (0, len(aList)))]

                if event.key == K_DOWN:
                    App['menuHighlight']['value'] = aList[incrementAndCycle(
                        1, aList.index(App['menuHighlight']['value']), (0, len(aList)))]

                if event.key == K_LEFT:
                    try:
                        aType = type(
                            App[App['menuHighlight']['value']]['values']).__name__
                        menuValue = App[App['menuHighlight']['value']]['value']
                        menuValues = App[App['menuHighlight']
                                         ['value']]['values']
                        if aType == 'list':
                            App[App['menuHighlight']['value']]['value'] = traverseList2(
                                menuValue, 'previous', menuValues)
                        elif aType == 'tuple':
                            App[App['menuHighlight']['value']]['value'] = adjustByFactor2(
                                -2, menuValue, menuValues)
                        elif aType == 'dict':
                            App[App['menuHighlight']['value']]['value'] = traverseList2(
                                menuValue, 'previous', list(menuValues.keys()))
                        elif aType == 'function':
                            App[App['menuHighlight']['value']]['value'] = traverseList2(
                                menuValue, 'previous', menuValues())
                    except ValueError:
                        App[App['menuHighlight']['value']]['value'] = menuValues()[
                            0]
                    except:
                        pass
                    finally:
                        applyChanges(App, App['camera'])
                if event.key == K_RIGHT:
                    try:
                        aType = type(
                            App[App['menuHighlight']['value']]['values']).__name__
                        menuValue = App[App['menuHighlight']['value']]['value']
                        menuValues = App[App['menuHighlight']
                                         ['value']]['values']
                        if aType == 'list':
                            App[App['menuHighlight']['value']]['value'] = traverseList2(
                                menuValue, 'next', menuValues)
                        elif aType == 'tuple':
                            App[App['menuHighlight']['value']]['value'] = adjustByFactor2(
                                2, menuValue, menuValues)
                        elif aType == 'dict':
                            App[App['menuHighlight']['value']]['value'] = traverseList2(
                                menuValue, 'next', list(menuValues.keys()))
                        elif aType == 'function':
                            App[App['menuHighlight']['value']]['value'] = traverseList2(
                                menuValue, 'next', menuValues())
                    except ValueError:
                        App[App['menuHighlight']['value']]['value'] = menuValues()[
                            0]
                    except:
                        #print(menuValue)
                        pass
                    finally:
                        applyChanges(App, App['camera'])
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
                App['menuHighlight']['value'] = key

            if App['menuHighlight']['value'] == key:
                currentTextColor = highlightedTextColor
                background = highlighted

            message = ''
            if 'message' in App[key]:
                message = App[key]['message']()
            elif 'value' in App[key]:
                message = f"{key} {App[key]['value']}"
            else:
                message = key

            text = textGen(font, message.upper(),
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
                o = camera['camera'].add_overlay(pygamesScreenRaw, size=(
                    1280, 720), fullscreen=False, window=App['window']['value'])
                o.alpha = 255
                o.layer = 3
                firstLoop = not firstLoop
            else:
                o.update(pygamesScreenRaw)
        elif devMode:
            screen.blit(layer, (0, 0))
            pygame.display.flip()

        clock.tick(5)

    if not devMode:
        camera['stop']()
        camera['close']()


if __name__ == "__main__":
    init()
    main()
