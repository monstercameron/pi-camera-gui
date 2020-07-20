# Import the pygame module
import pygame
from numpy import savetxt

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
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Variable to keep the main loop running
running = True

writeOnce = True

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

    # screen.fill((0, 255, 0, 255))

    surf = pygame.Surface((50, 50))
    surf.fill((255, 0, 0))
    rect = surf.get_rect()
    screen.blit(surf, (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

    if writeOnce:
        # image = pygame.image.tostring(screen, 'RGBA')
        # print(image)
        writeOnce = not writeOnce

    pygame.display.flip()
