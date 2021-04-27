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


def takePhoto(camera, filePath, interator):
    try:
        file = incrementPhotoIfExists(filePath, interator)
        camera.capture(file)
    except:
        print('error')


def incrementPhotoIfExists(filePath, interator):
    while path.exists(filePath):
        interator['value'] = interator['value'] + 1
    return filePath


def adjustByIncrement(app, increment, property, min_max):
    if increment > 0:
        updated_value = app[property] + increment
        print(property, ": ", app[property])

        if updated_value > min_max[1]:
            app[property] = min_max[1]
            return app[property]
        else:
            app[property] = updated_value
            return app[property]
    elif increment < 0:
        updated_value = app[property] - abs(increment)
        print(property, ": ", app[property])

        if updated_value < min_max[0]:
            app[property] = min_max[0]
            return min_max[0]
        else:
            app[property] = updated_value
            return app[property]
    else:
        print('Error')


def adjustByFactor(app, factor, property, min_max):
    if factor > 0:
        updated_value = app[property] * factor
        # print(property, ": ", app[property])

        if updated_value > min_max[1]:
            app[property] = min_max[1]
            return app[property]
        else:
            app[property] = updated_value
            return app[property]
    elif factor < 0:
        updated_value = app[property] // abs(factor)
        # print(property, ": ", app[property])

        if updated_value < min_max[0]:
            app[property] = min_max[0]
            return min_max[0]
        else:
            app[property] = updated_value
            return app[property]
    else:
        print('Error')


def adjustByFactor2(multiply, value, range):
    # print(multiply, value, range)
    if multiply > 0:
        updated_value = value * multiply
        if updated_value >= range[1]:
            return range[1]
        else:
            return updated_value
    elif multiply < 0:
        updated_value = value // abs(multiply)
        if updated_value <= range[0]:
            return range[0]
        else:
            return updated_value
    else:
        print('Error')


def traverseList2(current, direction, list):
    if direction == 'next':
        index = list.index(current)
        if index + 1 > len(list) - 1:
            index = 0
            return list[index]
        else:
            return list[index+1]
    elif direction == 'previous':
        index = list.index(current)
        if index - 1 < 0:
            index = len(list)-1
            return list[index]
        else:
            return list[index-1]


def traverseList2(current, direction, list):
    if direction == 'next':
        index = list.index(current)
        if index + 1 > len(list) - 1:
            index = 0
            return list[index]
        else:
            return list[index+1]
    elif direction == 'previous':
        index = list.index(current)
        if index - 1 < 0:
            index = len(list)-1
            return list[index]
        else:
            return list[index-1]


def incrementAndCycle(step, current, minMax):
    nextStep = current + step
    if current + step >= minMax[1]:
        return nextStep - minMax[1]
    elif current + step < minMax[0]:
        return minMax[1] - nextStep - 2
    else:
        return nextStep


def incrementAndCycleTuples(step, current, aList, minMax):
    currentIdx = 0
    for key in aList:
        if current == key[0]:
            break
        currentIdx = currentIdx + 1
    nextStep = currentIdx + step
    if nextStep < minMax[0]:
        val = minMax[1] + nextStep
        return aList[val][0]
    if nextStep >= minMax[1]:
        val = nextStep - minMax[1]
        return aList[val][0]
    else:
        return aList[nextStep][0]


def save_to_app(app, property, value):
    app[property] = value
    return app[property]


def howManyPhotos(storageGB, resoltuion):
    storageMB = storageGB * 1024
    imageMB = product(resoltuion) * 8 / 1024 / 1024 / 8
    return storageMB / imageMB
