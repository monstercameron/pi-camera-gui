# Import the pygame module
import pygame
from functions import *

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

# Initialize pygame
pygame.init()

# Define constants for the screen width and height
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# create a font object.
# 1st parameter is the font file
# which is present in pygame.
# 2nd parameter is size of the font
font = pygame.font.Font('freesansbold.ttf', 32)

# create a text suface object,
# on which text is drawn on it.
textColor = (255, 255, 255)
highlighted = (0, 0, 0)

# test values
values = {}
values['diskSpace'] = 1000 # MBs
values['format'] = 'jpg'
values['stillCompression'] = 'fine'

# create a list of all the text on the GUI
textList = {}
textList.append(('quality', f""))


layer = pygame.Surface((1280, 720))  # , pygame.SRCALPHA)

# Variable to keep the main loop running
running = True

# Main loop
while running:
    # Look at every event in the queue
    for event in pygame.event.get():
        # Did the user hit a key?
        if event.type == KEYDOWN:
            # Was it the Escape key? If so, stop the loop.
            if event.key == K_ESCAPE:
                running = False

        # Did the user click the window close button? If so, stop the loop.
        elif event.type == QUIT:
            running = False

    screen.fill((255, 255, 255))

    # draw rect
    rect = pygame.draw.rect(
        layer, blue, ((SCREEN_WIDTH//2, SCREEN_HEIGHT//2), (50, 50)), 1)

    screen.blit(layer, (0, 0))

    screen.blit(text, ((SCREEN_WIDTH//2)-(textRect.width//2), 0))

    pygame.display.flip()
