from time import sleep
from gpiozero import Button
from os import path, makedirs

print(path.exists('/home/pi/images/'))
try:
    if not print(path.exists('/home/pi/images/dcim/picamera/')):
        makedirs('/home/pi/images/dcim/picamera/')
except Exception as e:
    print(e)
            

# testing gpio and timing logic.
# button16 = Button(16)
# button20 = Button(20)
# button21 = Button(21)
# button26 = Button(26)

# count = 0
# pressed = False
# while True:
#     if button16.is_pressed and not pressed:
#         print('pressed 16 - ' + str(count))
#         count = count + 1
#         pressed = not pressed
#         sleep(.25)
#     elif button20.is_pressed and not pressed:
#         print('pressed 20 - ' + str(count))
#         count = count + 1
#         pressed = not pressed
#         sleep(.25)
#     elif button21.is_pressed and not pressed:
#         print('pressed 21 - ' + str(count))
#         count = count + 1
#         pressed = not pressed
#         sleep(.25)
#     elif button26.is_pressed and not pressed:
#         print('pressed 26 - ' + str(count))
#         count = count + 1
#         pressed = not pressed
#         sleep(.25)
#     else:
#         pressed = not pressed

# # Simple pygame program

# # Import and initialize the pygame library
# import pygame
# pygame.init()

# # Set up the drawing window
# screen = pygame.display.set_mode([500, 500])

# # Run until the user asks to quit
# running = True
# while running:

#     # Did the user click the window close button?
#     for event in pygame.event.get():
#         if event.type == pygame.KEYDOWN:
#             print(event.key)
#         if event.type == pygame.QUIT:
#             running = False

#     # Fill the background with white
#     screen.fill((255, 255, 255))

#     # Draw a solid blue circle in the center
#     pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)

#     # Flip the display
#     pygame.display.flip()

# # Done! Time to quit.
# pygame.quit()