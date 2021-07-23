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

    menuPositions = [0, 0, 0, 0]  # menu, submenu, option, level

    done = False
    while not done:
        if settings["display"]["showmenu"]:
            menu(pygame, layer, font, menuPositions, menus, settings)
        for event in pygame.event.get():
            controls(pygame, event, menuPositions, menus)
            if event.type == pygame.QUIT:
                done = True

        # print(menuPositions)
        screen.blit(layer, (0, 0))
        pygame.display.flip()
        clock.tick(settings["display"]["refreshrate"])
    pygame.quit()


def textGenerator(font, text, foreground, background,):
    text = font.render(text.upper(), False, foreground, background)
    return text


def textToRect(text):
    textRect = text.get_rect()
    textRect.center = (textRect.width // 2, textRect.height // 2)
    return textRect


def menu(pygame, surface, font, menuPos, menus, settings):
    surface.fill((255, 255, 255, 255))
    highlighted = (255, 255, 255)
    normal = (0, 0, 0)

    for count, menu in enumerate(menus["menus"]):
        superCount = count

        foreground = normal
        background = highlighted
        if count == menuPos[0]:
            foreground = highlighted
            background = normal

        text = textGenerator(font, menu["name"], foreground, background)
        textRect = textToRect(text)
        superTextRect = textRect
        padding = settings["display"]["padding"]

        # saving menu bitmap to layer
        surface.blit(text, (padding, padding+textRect.height*count))

        # drawing sub menu bitmap to screen
        if "options" in menu and superCount == menuPos[0] and menuPos[3] > 0:
            for count, option in enumerate(menu["options"]):
                foreground = normal
                background = highlighted
                if count == menuPos[1] and menuPos[3] > 0:
                    foreground = highlighted
                    background = normal

                text = textGenerator(
                    font, option["name"], foreground, background)
                textRect = textToRect(text)
                subTextRect = textRect
                surface.blit(text,
                             (100, padding+textRect.height*count))

                # drawing sub menu options bitmap to screen
                if "options" in option and count == menuPos[1] and menuPos[3] > 1:
                    foreground = highlighted
                    background = normal
                    text = textGenerator(
                        font, "loading...", foreground, background)
                    # print(option["type"])

                    # check option type
                    if option["type"] == "list":
                        text = textGenerator(
                            font, f'''{option["value"]} --> {option["options"][menuPos[2]]}''', foreground, background)
                    elif option["type"] == "range":
                        text = textGenerator(
                            font, str(option["value"]), foreground, background)

                    textRect = textToRect(text)
                    surface.blit(text,
                                 (100 + padding + subTextRect.width, padding+subTextRect.height*count))
                # break
        # break
