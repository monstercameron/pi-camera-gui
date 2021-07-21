import pygame

def Gui(settings):
    pygame.init()
    screen = pygame.display.set_mode((settings["display"]["height"], settings["display"]["width"]))

    pygame.display.set_caption(settings["display"]["caption"])
    clock = pygame.time.Clock()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                print(event.key)
        pygame.display.flip()
        clock.tick(60)