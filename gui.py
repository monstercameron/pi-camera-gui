import pygame

def Gui(controls, menus, settings, Buttons, camera=None):
    pygame.init()
    screen = pygame.display.set_mode(
        (settings["display"]["width"], settings["display"]["height"]))
    screen.fill((0, 0, 0))
    pygame.display.set_caption(settings["display"]["caption"])

    layer = pygame.Surface(
        (settings["display"]["width"], settings["display"]["height"]), pygame.SRCALPHA)
    layer.fill((255, 255, 255, 255))

    font = pygame.font.Font(
        'freesansbold.ttf', settings["display"]["fontsize"])
    statsFont = pygame.font.Font(
        'freesansbold.ttf', settings["display"]["fontsize"])

    clock = pygame.time.Clock()

    # take photo button

    menuPositions = [0, 0, 0, 0]  # menu, submenu, option, level

    #  start the picamera preview
    if camera is not None:
        camera.startPreview()

    # setting up the buttons
    buttons = Buttons(settings)

    firstLoop = True
    done = False
    while not done:

        buttons.listen(pygame)

        if settings["display"]["showmenu"]:
            menu(pygame, layer, font, menuPositions,
                 menus, settings, camera=camera)
                 
        for event in pygame.event.get():
            controls(pygame, event, menuPositions, menus, camera=camera)
            if event.type == pygame.QUIT:
                done = True

        if camera is not None:
            statsFont = pygame.font.Font(
                'freesansbold.ttf', 10)
            
            statsDetails = " ".join(
                map(lambda x: f"{x}:{camera.directory()[x]()}", list(camera.directory().keys())))
            stats = textGenerator(statsFont, statsDetails,
                                  (255, 255, 255), (0, 0, 0))
            statsRect = textToRect(stats)

            layer.blit(stats, (settings["display"]["width"]/2-statsRect.width/2,\
                 settings["display"]["height"]-statsRect.height))
            pygamesScreenRaw = pygame.image.tostring(layer, 'RGBA')

            if firstLoop:
                o = camera.getCamera().add_overlay(
                    pygamesScreenRaw,
                    size=(settings["display"]["width"],
                          settings["display"]["height"]),
                    fullscreen=False,
                    window=(110, 110, settings["display"]["width"], settings["display"]["height"]))
                o.alpha = 255
                o.layer = 3
                firstLoop = not firstLoop
            else:
                o.update(pygamesScreenRaw)
        else:
            # print(menuPositions)
            screen.blit(layer, (0, 0))

        pygame.display.flip()

        clock.tick(settings["display"]["refreshrate"])
    if camera is not None:
        camera.stopPreview()
        camera.closeCamera()

    pygame.quit()
    exit()


def textGenerator(font, text, foreground, background,):
    text = font.render(text.upper(), False, foreground, background)
    return text


def textToRect(text):
    textRect = text.get_rect()
    textRect.center = (textRect.width // 2, textRect.height // 2)
    return textRect


def menu(pygame, surface, font, menuPos, menus, settings, camera=None):
    if camera is None:
        surface.fill((255, 255, 255, 255))
    else:
        surface.fill((0, 0, 0, 0))

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
                             (250, padding+textRect.height*count))

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
                                 (350 + padding + subTextRect.width, padding+subTextRect.height*count))
                # break
        # break
