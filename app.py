import picamera
import time
import sys
from pynput.keyboard import Key, Listener
from constants import *
from controls import *

# setup
App[IMAGE_DIRECTORY] = 'images'
camera = picamera.PiCamera()
camera.shutter_speed = App[SHUTTER_SPEED]
camera.iso = App[ISO]


def preview():
    print('Pi Camera Gui Started')
    camera.resolution = (960, 540)
    print('Starting preview')
    camera.start_preview(fullscreen=False, window=DEFAULT_WINDOW_SIZE)
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
        camera.capture(file)
        print('took photo', file)
    except:
        print('error')


def main():
    print('Hajime!')

    # listens for keypresses in a non blocking way
    # listener = Listener(on_press=keyboard_press, on_release=keyboard_release)
    listener = Listener(on_press=keyboard_press)
    listener.start()
    preview()
    while App[ALIVE]:
        text_overlay()
    # camera.stop_preview()
    # exit


if __name__ == "__main__":
    main()
