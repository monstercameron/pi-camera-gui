import pygame
from typing import Dict, Any, List, Optional

class MenuController:
    @staticmethod
    def handle_event(pygame_mod, event, menu_pos: List[int], menus: Dict[str, Any], camera: Optional[Any] = None):
        """
        Handles input events for menu navigation and value updates.
        menu_pos: [menu_index, submenu_index, option_index, level]
        """
        if event.type == pygame_mod.KEYDOWN:
            if event.key == pygame_mod.K_ESCAPE:
                pygame_mod.quit()
                return

            # Navigation / Value Change
            if event.key == pygame_mod.K_UP:
                MenuController._handle_vertical_input(1, menu_pos, menus, camera)
            elif event.key == pygame_mod.K_DOWN:
                MenuController._handle_vertical_input(-1, menu_pos, menus, camera)
            elif event.key == pygame_mod.K_RIGHT:
                MenuController._navigate(1, menu_pos)
            elif event.key == pygame_mod.K_LEFT:
                MenuController._navigate(-1, menu_pos)

            # Camera specific controls (e.g. Capture)
            if camera is not None:
                # Assuming camera has a controls method. 
                # Ideally this should be decoupled, but keeping for compatibility.
                if hasattr(camera, 'controls'):
                    camera.controls(pygame_mod, event.key)

    @staticmethod
    def _handle_vertical_input(direction: int, menu_pos: List[int], menus: Dict[str, Any], camera: Optional[Any]):
        option_type = MenuController._get_option_type(menu_pos, menus)
        
        changed_option = None
        
        if option_type == "list":
            changed_option = MenuController._update_list_value(direction, menu_pos, menus)
        elif option_type == "range":
            changed_option = MenuController._update_range_value(direction, menu_pos, menus)

        if changed_option and camera:
            MenuController._apply_setting(camera, changed_option)

    @staticmethod
    def _navigate(direction: int, menu_pos: List[int]):
        if direction > 0:
            # Go deeper
            if menu_pos[3] <= 1:
                menu_pos[3] += 1
        else:
            # Go back
            if menu_pos[3] >= 1:
                menu_pos[menu_pos[3]] = 0 # Reset current level index
                menu_pos[3] -= 1

    @staticmethod
    def _get_option_type(menu_pos: List[int], menus: Dict[str, Any]) -> str:
        try:
            if menu_pos[3] == 1:
                return menus["menus"][menu_pos[0]]["type"]
            elif menu_pos[3] == 2:
                return menus["menus"][menu_pos[0]]["options"][menu_pos[1]]["type"]
        except (KeyError, IndexError):
            pass
        return "list"

    @staticmethod
    def _get_menu_limits(menu_pos: List[int], menus: Dict[str, Any]) -> int:
        try:
            if menu_pos[3] == 0:
                return len(menus["menus"])
            elif menu_pos[3] == 1:
                return len(menus["menus"][menu_pos[0]]["options"])
            elif menu_pos[3] == 2:
                return len(menus["menus"][menu_pos[0]]["options"][menu_pos[1]]["options"])
        except (KeyError, IndexError):
            pass
        return 0

    @staticmethod
    def _update_range_value(direction: int, menu_pos: List[int], menus: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            option = menus["menus"][menu_pos[0]]["options"][menu_pos[1]]
            current_val = option["value"]
            step = option["options"]["step"]
            min_val = option["options"]["min"]
            max_val = option["options"]["max"]

            new_val = current_val
            if direction > 0:
                if current_val < max_val:
                    new_val += step
            else:
                if current_val > min_val:
                    new_val -= step
            
            if new_val != current_val:
                option["value"] = new_val
                return option
        except (KeyError, IndexError):
            pass
        return None

    @staticmethod
    def _update_list_value(direction: int, menu_pos: List[int], menus: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Update index
        limit = MenuController._get_menu_limits(menu_pos, menus)
        current_index = menu_pos[menu_pos[3]]
        
        if direction > 0:
            # Previous item (Up key usually means up in list, which is lower index? 
            # Original code: direction 1 (UP) -> index - 1. So UP key = Previous Item.
            if current_index >= 1:
                menu_pos[menu_pos[3]] -= 1
        else:
            # Next item
            if current_index < limit - 1:
                menu_pos[menu_pos[3]] += 1
            else:
                menu_pos[menu_pos[3]] = 0 # Loop back to start? Original code did this.

        # Update value in menu structure if we are at the value selection level (level 2 usually?)
        # Original code: if menuPosArr[2] > 0: ... wait, menuPos[2] is option index.
        # If we are selecting a value from a list, we are at level 2?
        # Let's check original logic:
        # if menuPosArr[2] > 0: ...
        # Actually, for a list type, the "value" is selected by the index at menuPos[2].
        
        if menu_pos[3] == 2: # We are selecting a value
            try:
                option = menus["menus"][menu_pos[0]]["options"][menu_pos[1]]
                selected_value = option["options"][menu_pos[2]]
                
                if option["value"] != selected_value:
                    option["value"] = selected_value
                    return option
            except (KeyError, IndexError):
                pass
        return None

    @staticmethod
    def _apply_setting(camera: Any, option: Dict[str, Any]):
        directory = camera.directory()
        name = option["name"]
        value = option["value"]
        
        if name in directory:
            print(f"Applying setting: {name} = {value}")
            directory[name](value=value)
