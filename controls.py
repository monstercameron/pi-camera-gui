def cameraControls(pygame, event, menuPos, menus):
    if event.type == pygame.KEYDOWN:
        # print(event.key)
        if event.key == pygame.K_UP:
            # print("up")
            if menuPos[menuPos[3]] >= 1:
                menuPos[menuPos[3]] = menuPos[menuPos[3]] - 1

        elif event.key == pygame.K_DOWN:
            # print("down")
            # print("menupos-->",menuPos[3], " | menu lenght-->",menuLimits(menuPos, menus))
            menuPos[menuPos[3]] = menuPos[menuPos[3]] + 1
            if menuPos[menuPos[3]] > menuLimits(menuPos, menus):
                menuPos[menuPos[3]] = 0

        elif event.key == pygame.K_RIGHT:
            # print("right")
            if menuPos[3] <= 1:
                menuPos[3] = menuPos[3] + 1

        elif event.key == pygame.K_LEFT:
            # print("left")
            if menuPos[3] >= 1:
                menuPos[3] = menuPos[3] - 1


def menuLimits(menuPosArr, menus):
    # print(menus)
    try:
        if "menus" in menus:
            # print(menus["menus"])
            if "options" in menus["menus"][menuPosArr[0]]:
                # print(menus["menus"][menuPosArr[0]]["options"])
                if [menuPosArr[3]] == 0:
                    return len(menus["menus"][menuPosArr[0]]["options"])
                if "options" in menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]:
                    # print(menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]])
                    if [menuPosArr[3] == 1]:
                        return len(menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]])
                    if "options" in menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]:
                        # print(len(menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]["options"])-1)
                        if [menuPosArr[3] == 2]:
                            return len(menus["menus"][menuPosArr[0]]["options"][menuPosArr[1]]["options"])
    except:
        print("Out of range")
    return 0
