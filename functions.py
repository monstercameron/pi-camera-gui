from os import path


def textGen(font, text, foreground, background,):
    text = font.render(text, False, foreground, background)
    return text


def textRectify(text):
    textRect = text.get_rect()
    textRect.center = (textRect.width // 2, textRect.height // 2)
    return textRect


def product(tuple):
    """Calculates the product of a tuple"""
    prod = 1
    for x in tuple:
        prod = prod * x
    return prod


def takePhoto(camera, app, fileFn, image_count_key):
    try:
        file = incrementPhotoIfExists(app, fileFn, image_count_key)
        camera.capture(file, quality=100)
    except:
        print('error')


def incrementPhotoIfExists(app, fileFn, image_count_key):
    while path.exists(app[fileFn]()):
        app[image_count_key] = app[image_count_key] + 1
    return app[fileFn]()
