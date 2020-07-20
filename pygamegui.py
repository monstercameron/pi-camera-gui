import picamera
import time
import sys
from pynput.keyboard import Key, Listener
from PIL import Image
from constants import *
from controls import *
import pygame
from numpy import savetxt
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)
pygame.init()
clock = pygame.time.Clock()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
App[IMAGE_DIRECTORY] = 'images'
camera = picamera.PiCamera()
camera.shutter_speed = App[SHUTTER_SPEED]
camera.iso = App[ISO]


def load_image(image):
    # Load the arbitrarily sized image
    img = Image.open(f"images/{image}")
    # Create an image padded to the required size with
    # mode 'RGB'
    pad = Image.new('RGBA', (
        ((img.size[0] + 31) // 32) * 32,
        ((img.size[1] + 15) // 16) * 16,
    ))
    # Paste the original image into the padded one
    pad.paste(img, (0, 0))
    return [img, pad]


def preview():
    print('Pi Camera Gui Started')
    camera.resolution = (1280, 720)
    print('Starting preview')
    camera.start_preview(fullscreen=True, window=DEFAULT_WINDOW_SIZE)
    image = load_image('overlay.png')
    o = camera.add_overlay(image[1].tobytes(), size=image[1].size)
    o.alpha = 255
    o.layer = 3
    # camera.capture('images/test.jpg')
    # time.sleep(5)


def text_overlay():
    text = f"Shutter speed:{camera.shutter_speed} | ISO:{camera.iso} | WB:{camera.awb_mode}"
    camera.annotate_text = text


def keyboard_press(key):
    try:
        if hasattr(key, 'char'):
            if key.char == '1':
                print("option 1")
            elif key.char == '2':
                print("option 2")
            elif key.char == '2':
                print("option 2")
            elif key.char == '2':
                print("option 2")
            elif key.char == '2':
                print("option 2")
            elif key.char == '2':
                print("option 2")
            elif key.char == '2':
                print("option 2")
            elif key.char == 'a':
                camera.awb_mode = save_to_app(
                    App, AWB, traverse_list(App[AWB], 'next', AWB_MODES))
            elif key.char == 'A':
                camera.awb_mode = save_to_app(
                    App, AWB, traverse_list(App[AWB], 'previous', AWB_MODES))
            elif key.char == '0':
                print(camera.shutter_speed)
            elif key.char == 'e':
                camera.shutter_speed = adjust_by_factor(App,
                                                        2, SHUTTER_SPEED, SHUTTER_MINMAX)
            elif key.char == 'E':
                camera.shutter_speed = adjust_by_factor(App,
                                                        -2, SHUTTER_SPEED, SHUTTER_MINMAX)
            elif key.char == 'i':
                camera.iso = adjust_by_factor(App, 2, ISO, ISO_MINMAX)
            elif key.char == 'I':
                camera.iso = adjust_by_factor(App, -2, ISO, ISO_MINMAX)
            elif key == Key.enter:
                take_photo()
            else:
                print('Pressed:  ', key.char)
        else:
            if key == Key.enter:
                take_photo()
            if key == Key.esc:
                exit()
    except AttributeError:
        print('special key {0} pressed'.format(
            key))


def keyboard_release(key):
    print('released:  ', key)
    if key == 'q':
        print('xxx')
    elif key == 'w':
        print('sss')
    else:
        print('No key pressed')


def take_photo():
    print('take_photo()')
    try:
        file = f"{App[IMAGE_DIRECTORY]}/{App[IMAGE_NAME_SCHEME]}{App[IMAGE_COUNT]}.{App[IMAGE_FORMAT]}"
        print('Taking photo: ', file)
        camera.annotate_text = ''
        camera.capture(file)
        print('took photo', file)
    except:
        print('error')


def main():
    # listens for keypresses in a non blocking way
    # listener = Listener(on_press=keyboard_press, on_release=keyboard_release)
    # listener = Listener(on_press=keyboard_press)
    # listener.start()
    # preview()

    print('Pi Camera Gui Started')
    camera.resolution = (1280, 720)
    print('Starting preview')
    camera.start_preview(fullscreen=False, window=DEFAULT_WINDOW_SIZE)
    # can be a splash screen?
    image = load_image('overlay.png')
    # o = camera.add_overlay(pygame.image.tostring(
    #     screen, 'RGBA'), size=(1280, 720))
    # o = camera.add_overlay(image[1].tobytes(), size=image[1].size)
    dd = 50

    firstLoop = True

    o = None

    while App[ALIVE]:
        text_overlay()
        for event in pygame.event.get():
            # Did the user hit a key?
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop the loop.
                if event.key == K_ESCAPE:
                    App[ALIVE] = False

            # Did the user click the window close button? If so, stop the loop.
            elif event.type == QUIT:
                App[ALIVE] = False

        screen.fill((0, 255, 0))
        surf = pygame.Surface((dd, 50))
        dd = dd + 1

        surf.fill((255, 0, 0))
        rect = surf.get_rect()
        screen.blit(surf, (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

        ss = pygame.Surface((1280, 720), pygame.SRCALPHA)
        ss.blit(screen, (1280, 720))
        ss.set_colorkey((0, 255, 0))

        pygamesScreenRaw = pygame.image.tostring(ss, 'RGBA')

        if firstLoop:
            o = camera.add_overlay(pygamesScreenRaw, size=(
                1280, 720), fullscreen=False, window=DEFAULT_WINDOW_SIZE)
            o.alpha = 255
            o.layer = 3
            firstLoop = not firstLoop
        else:
            o.update(pygamesScreenRaw)
        # pygame.display.flip()
        clock.tick(305)
        # App[ALIVE] = False


if __name__ == "__main__":
    main()
