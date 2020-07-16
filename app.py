import picamera
import time
import sys
from pynput.keyboard import Key, Listener
from constants import *

# setup
App[IMAGE_DIRECTORY] = 'images'
camera = picamera.PiCamera()

def gui():
    print('Pi Camera Gui Started')
    camera.resolution = (960,540)
    # print('Starting preview')
    # camera.start_preview()
    # camera.capture('images/test.jpg')
    # time.sleep(5)


def keyboard_press(key):
    try:
        if hasattr(key, 'char'):
            if key.char == 'q':
                print('xxx')
            elif key.char == 'w':
                print('sss')
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
        camera.capture(f"{App[IMAGE_DIRECTORY]}/{App[IMAGE_NAME_SCHEME]}{App[IMAGE_COUNT]}")
        print('took photo')
    except:
        print('error')


def adjust_exposure(exposure_offset):
    App[EXPOSURE] = App[EXPOSURE] + exposure_offset


def main():
    print('Hajime!')

    # listens for keypresses in a non blocking way
    # listener = Listener(on_press=keyboard_press, on_release=keyboard_release)
    listener = Listener(on_press=keyboard_press)
    listener.start()
    # gui()
    while App[ALIVE]:
        pass
    # camera.stop_preview()
    # exit


if __name__ == "__main__":
    main()
