import pygame


def Gui(controls, menus, settings):
    pygame.init()
    screen = pygame.display.set_mode(
        (settings["display"]["height"], settings["display"]["width"]))
    screen.fill((0, 0, 0))
    pygame.display.set_caption(settings["display"]["caption"])

    layer = pygame.Surface(
        (settings["display"]["height"], settings["display"]["width"]), pygame.SRCALPHA)
    layer.fill((255, 255, 255, 255))

    font = pygame.font.Font(
        'freesansbold.ttf', settings["display"]["fontsize"])

    clock = pygame.time.Clock()

    menuPositions = []

    done = False
    while not done:
        for event in pygame.event.get():
            controls(pygame, event, menuPositions, settings)
            if event.type == pygame.QUIT:
                done = True

        menu(pygame, layer, font, menus, settings)

        screen.blit(layer, (0, 0))
        pygame.display.flip()
        clock.tick(settings["display"]["refreshrate"])
    pygame.quit()


def textGenerator(font, text, foreground, background,):
    text = font.render(text, False, foreground, background)
    return text


def textToRect(text):
    textRect = text.get_rect()
    textRect.center = (textRect.width // 2, textRect.height // 2)
    return textRect


def menu(pygame, surface, font, menus, settings):
    highlighted = (255, 255, 255)
    normal = (0, 0, 0)
    for count, menu in enumerate(menus["menus"]):

        foreground = normal
        background = highlighted
        if count == 1:
            foreground = highlighted
            background = normal

        text = textGenerator(font, menu["name"], foreground, background)
        textRect = textToRect(text)
        padding = settings["display"]["padding"]

        # saving menu bitmap to layer
        surface.blit(text, (padding, padding+textRect.height*count))
