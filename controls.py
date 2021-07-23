def cameraControls(pygame, event, menuPos, menus, camera=None):
    if event.type == pygame.KEYDOWN:
        # print(event.key)
        print(
            f"pos: {menuPos} || menu len: {menuLimits(menuPos, menus)} || type: {menuOptionType(menuPos, menus)}")
        if event.key == pygame.K_UP:
            # print("up")
            if menuOptionType(menuPos, menus) == "list":
                menuOptionUpdateListValue(1, menuPos, menus)
            elif menuOptionType(menuPos, menus) == "range":
                menuOptionUpdateRangeValue(1, menuPos, menus)

        elif event.key == pygame.K_DOWN:
            # print("down")
            if menuOptionType(menuPos, menus) == "list":
                menuOptionUpdateListValue(-1, menuPos, menus)
            elif menuOptionType(menuPos, menus) == "range":
                menuOptionUpdateRangeValue(-1, menuPos, menus)

        elif event.key == pygame.K_RIGHT:
            # print("right")
            menuOptionSelector(1, menuPos)

        elif event.key == pygame.K_LEFT:
            # print("left")
            menuOptionSelector(-1, menuPos)


def menuLimits(menuPosArr, menus):
    # print(menus)
    try:
        if menuPosArr[3] == 0:
            return len(menus["menus"])
        elif menuPosArr[3] == 1:
            return len(menus["menus"][menuPosArr[1]]["options"])
        elif menuPosArr[3] == 2:
            return len(menus["menus"][menuPosArr[1]]["options"][menuPosArr[2]]["options"])
    except:
        print("Out of range")
    return 0


def menuOptionType(menuPosArr, menus):
    if menuPosArr[3] == 1:
        return menus["menus"][menuPosArr[0]]["type"]
    else:
        return menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]["type"]


def menuOptionSelector(direction, menuPosArr):
    if direction > 0:
        if menuPosArr[3] <= 1:
            menuPosArr[3] = menuPosArr[3] + 1
    else:
        if menuPosArr[3] >= 1:
            menuPosArr[menuPosArr[3]] = 0
            menuPosArr[3] = menuPosArr[3] - 1


def menuOptionUpdateRangeValue(direction, menuPosArr, menus):
    if direction > 0:
        if menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]["value"] < menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]["options"]["max"]:
            menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]["value"] = \
                menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]["value"] +\
                menus["menus"][menuPosArr[0]
                               ]["options"][menuPosArr[1]]["options"]["step"]
    else:
        if menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]["value"] > menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]["options"]["min"]:
            menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]["value"] = \
                menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]["value"] -\
                menus["menus"][menuPosArr[0]
                               ]["options"][menuPosArr[1]]["options"]["step"]


def menuOptionUpdateListValue(direction, menuPosArr, menus):
    if direction > 0:
        if menuPosArr[menuPosArr[3]] >= 1:
            menuPosArr[menuPosArr[3]] = menuPosArr[menuPosArr[3]] - 1
        print('over here')
    else:
        if menuPosArr[menuPosArr[3]] >= menuLimits(menuPosArr, menus)-1:
            menuPosArr[menuPosArr[3]] = 0
            print('here')
        else:
            menuPosArr[menuPosArr[3]] = menuPosArr[menuPosArr[3]] + 1
            print('there')

    # update value based on menu position
    if menuPosArr[2] > 0:
        menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]["value"] = \
            menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]
                                                     ]["options"][menuPosArr[2]]
