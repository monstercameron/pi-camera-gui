import copy
from deepdiff import DeepDiff


def cameraControls(pygame, event, menuPos, menus, camera=None):

    # storing old menu to diff check for changes
    menuOptionsDiff = [copy.deepcopy(menus)]

    # if event.type == pygame.KEYDOWN:
    keys = pygame.key.get_pressed()
    # print(event.key)
    # print(
    #     f"pos: {menuPos} || menu len: {menuLimits(menuPos, menus)} || type: {menuOptionType(menuPos, menus)}")
    # if event.key == pygame.K_UP:
    if keys[pygame.K_UP]:
        # print("up")
        if menuOptionType(menuPos, menus) == "list":
            menuOptionUpdateListValue(1, menuPos, menus, menuOptionsDiff)
        elif menuOptionType(menuPos, menus) == "range":
            menuOptionUpdateRangeValue(1, menuPos, menus, menuOptionsDiff)

    # elif event.key == pygame.K_DOWN:
    elif keys[pygame.K_DOWN]:
        # print("down")
        if menuOptionType(menuPos, menus) == "list":
            menuOptionUpdateListValue(-1, menuPos, menus, menuOptionsDiff)
        elif menuOptionType(menuPos, menus) == "range":
            menuOptionUpdateRangeValue(-1, menuPos, menus, menuOptionsDiff)

    # elif event.key == pygame.K_RIGHT:
    elif keys[pygame.K_RIGHT]:
        # print("right")
        menuOptionSelector(1, menuPos)

    # elif event.key == pygame.K_LEFT:
    elif keys[pygame.K_LEFT]:
        # print("left")
        menuOptionSelector(-1, menuPos)
    # print("Len of diff arr -> ",len(menuOptionsDiff))
    print("Diff? -> ", menuOptionsDiffer(menuOptionsDiff))
    menuOptionsApplyCameraSettings(camera, menuPos, menus, menuOptionsDiff)


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


def menuOptionUpdateRangeValue(direction, menuPosArr, menus, menuDiffArr):
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
    menuDiffArr.insert(0, menus)


def menuOptionUpdateListValue(direction, menuPosArr, menus, menuDiffArr):
    if direction > 0:
        if menuPosArr[menuPosArr[3]] >= 1:
            menuPosArr[menuPosArr[3]] = menuPosArr[menuPosArr[3]] - 1
    else:
        if menuPosArr[menuPosArr[3]] >= menuLimits(menuPosArr, menus)-1:
            menuPosArr[menuPosArr[3]] = 0
        else:
            menuPosArr[menuPosArr[3]] = menuPosArr[menuPosArr[3]] + 1

    # update value based on menu position
    if menuPosArr[2] > 0:
        menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]["value"] = \
            menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]
                                                     ]["options"][menuPosArr[2]]
        menuDiffArr.insert(0, menus)


def menuOptionsApplyCameraSettings(camera, menuPosArr, menus, menuDiffArr):
    diff = menuOptionsDiffer(menuDiffArr)

    if diff != -1 and menuPosArr[3] == 2 and camera is not None and "values_changed" in diff:
        menuOptionName = menus["menus"][menuPosArr[0]
                                        ]["options"][menuPosArr[1]]["name"]

        directory = camera.directory()

        if menuOptionName in directory:
            directory[menuOptionName](value=
                diff['values_changed'][list(diff['values_changed'].keys())[0]]["new_value"])

            print('changes applied')
        # print("new value drill down", diff['values_changed'][list(diff['values_changed'].keys())[0]])
        # {'values_changed': {"root['menus'][0]['options'][1]['value']": {'new_value': 28, 'old_value': 18}}}
    else:
        print('no changes applied')


def menuOptionsDiffer(menuDiffArr):
    if len(menuDiffArr) > 1:
        return DeepDiff(menuDiffArr[0], menuDiffArr[1], ignore_order=True)
    else:
        return -1
