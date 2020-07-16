import picamera
import time
from pynput.keyboard import Key, Listener
import sys

alive = True
# camera = picamera.PiCamera()


def gui():
    print('Pi Camera Gui Started')

    # camera.resolution = (960,540)

    # print('Starting preview')
    # camera.start_preview()

    # camera.capture('images/test.jpg')

    # time.sleep(5)


def keyboard_press(key):
    print('Pressed:  ',key)
    

def keyboard_release(key):
    print('released:  ',key)
    # sys.exit(0)


def main():
    print('Hajime!')

    # listens for keypresses in a non blocking way
    listener = Listener(on_press=keyboard_press, on_release=keyboard_release)
    listener.start()

    while True:
        pass
        # while alive:
        #     gui()

        # print('Ending preview')
        # camera.stop_preview()


if __name__ == "__main__":
    main()
