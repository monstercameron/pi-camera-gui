def textGen(font, text, foreground, background,):
    text = font.render(text, False, foreground, background)
    return text

def textRectify(text):
    textRect = text.get_rect()
    textRect.center = (textRect.width // 2, textRect.height // 2)
    return textRect