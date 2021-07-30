from time import sleep
from gpiozero import Button

# testing gpio and timing logic.
button = Button(16)

count = 0
pressed = False
while True:
    if button.is_pressed and not pressed:
        print('xrk999' + str(count))
        count = count + 1
        pressed = not pressed
        sleep(.25)
    else:
        pressed = not pressed

