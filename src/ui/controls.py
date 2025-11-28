import pygame
from typing import Dict, Any, List, Optional

class MenuController:
    @staticmethod
    def handle_event(pygame_mod, event, menu_pos: List[int], menus: Dict[str, Any], camera: Optional[Any] = None, menu_active: bool = True, quick_menu_pos: Optional[List[int]] = None, callbacks: Optional[Dict[str, Any]] = None):
        """
        Handles input events for menu navigation and value updates.
        menu_pos: [menu_index, submenu_index, option_index, level]
        """
        if event.type == pygame_mod.KEYDOWN:
            if event.key == pygame_mod.K_ESCAPE:
                # Post a QUIT event instead of calling quit() directly
                # This allows the main loop to handle the exit gracefully
                pygame_mod.event.post(pygame_mod.event.Event(pygame_mod.QUIT))
                return

            # Navigation / Value Change
            if menu_active:
                if event.key == pygame_mod.K_UP:
                    MenuController._handle_vertical_input(1, menu_pos, menus, camera, callbacks)
                elif event.key == pygame_mod.K_DOWN:
                    MenuController._handle_vertical_input(-1, menu_pos, menus, camera, callbacks)
                elif event.key == pygame_mod.K_RIGHT:
                    MenuController._navigate(1, menu_pos, menus)
                elif event.key == pygame_mod.K_LEFT:
                    MenuController._navigate(-1, menu_pos, menus)
            elif quick_menu_pos is not None and camera is not None:
                # Quick Menu Logic (when main menu is inactive)
                if event.key == pygame_mod.K_RIGHT:
                    # Cycle to next stat (4 stats: ISO, Shutter, AWB, Exposure)
                    quick_menu_pos[0] = (quick_menu_pos[0] + 1) % 4
                elif event.key == pygame_mod.K_LEFT:
                    # Cycle to prev stat
                    quick_menu_pos[0] = (quick_menu_pos[0] - 1) % 4
                elif event.key == pygame_mod.K_UP:
                    # Increase value (or next item)
                    MenuController._handle_quick_value_change(1, quick_menu_pos[0], menus, camera)
                elif event.key == pygame_mod.K_DOWN:
                    # Decrease value (or prev item)
                    MenuController._handle_quick_value_change(-1, quick_menu_pos[0], menus, camera)

            # Camera specific controls (e.g. Capture)
            if camera is not None:
                # Assuming camera has a controls method. 
                # Ideally this should be decoupled, but keeping for compatibility.
                if hasattr(camera, 'controls'):
                    camera.controls(pygame_mod, event.key)

    @staticmethod
    def _handle_vertical_input(direction: int, menu_pos: List[int], menus: Dict[str, Any], camera: Optional[Any], callbacks: Optional[Dict[str, Any]] = None):
        option_type = MenuController._get_option_type(menu_pos, menus)
        
        changed_option = None
        
        if option_type == "list":
            changed_option = MenuController._update_list_value(direction, menu_pos, menus)
        elif option_type == "range":
            changed_option = MenuController._update_range_value(direction, menu_pos, menus)

        if changed_option:
            MenuController._apply_setting(camera, changed_option, callbacks)

    @staticmethod
    def _navigate(direction: int, menu_pos: List[int], menus: Dict[str, Any]):
        if direction > 0:
            # Go deeper
            if menu_pos[3] <= 1:
                # If entering Level 2 (Value Selection), save the original value for reference
                if menu_pos[3] == 1:
                    try:
                        option = menus["menus"][menu_pos[0]]["options"][menu_pos[1]]
                        if "value" in option:
                            option["_original_value"] = option["value"]
                    except (KeyError, IndexError):
                        pass
                
                menu_pos[3] += 1
        else:
            # Go back
            if menu_pos[3] >= 1:
                # If leaving Level 2, we could clean up _original_value, but it's harmless to keep
                # or we can keep it until next entry.
                
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
                selected_item = option["options"][menu_pos[2]]
                
                if isinstance(selected_item, dict) and "value" in selected_item:
                    selected_value = selected_item["value"]
                else:
                    selected_value = selected_item
                
                if option["value"] != selected_value:
                    option["value"] = selected_value
                    return option
            except (KeyError, IndexError):
                pass
        return None

    @staticmethod
    def _find_menu_item(menus: Dict[str, Any], name: str) -> Optional[Dict[str, Any]]:
        for menu in menus["menus"]:
            for option in menu["options"]:
                if option["name"] == name:
                    return option
        return None

    @staticmethod
    def _handle_quick_value_change(direction: int, stat_index: int, menus: Dict[str, Any], camera: Any):
        stat_names = ["iso", "shutter", "awb", "exposure"]
        stat_name = stat_names[stat_index]
        
        option = MenuController._find_menu_item(menus, stat_name)
        if not option:
            return

        if option["type"] == "range":
            current_val = option["value"]
            step = option["options"]["step"]
            min_val = option["options"]["min"]
            max_val = option["options"]["max"]
            
            new_val = current_val
            if direction > 0: # UP
                if current_val < max_val: new_val += step
            else: # DOWN
                if current_val > min_val: new_val -= step
            
            if new_val != current_val:
                option["value"] = new_val
                MenuController._apply_setting(camera, option)

        elif option["type"] == "list":
            current_val = option["value"]
            options_list = option["options"]
            
            current_idx = -1
            for i, item in enumerate(options_list):
                val = item["value"] if isinstance(item, dict) else item
                if val == current_val:
                    current_idx = i
                    break
            
            if current_idx != -1:
                new_idx = current_idx
                if direction > 0: # UP -> Next item
                    if new_idx < len(options_list) - 1:
                        new_idx += 1
                    else:
                        new_idx = 0 # Loop
                else: # DOWN -> Prev item
                    if new_idx > 0:
                        new_idx -= 1
                    else:
                        new_idx = len(options_list) - 1 # Loop
                
                new_item = options_list[new_idx]
                new_val = new_item["value"] if isinstance(new_item, dict) else new_item
                
                if new_val != current_val:
                    option["value"] = new_val
                    MenuController._apply_setting(camera, option)

    @staticmethod
    def _apply_setting(camera: Any, option: Dict[str, Any], callbacks: Optional[Dict[str, Any]] = None):
        name = option["name"]
        value = option["value"]
        
        # Handle Reset Action
        if name == "reset_settings" and value == "yes":
            if callbacks and "reset" in callbacks:
                print("Resetting settings...")
                callbacks["reset"]()
                # Reset the option value back to "no" so it doesn't stay on "yes"
                option["value"] = "no"
            return

        if camera:
            directory = camera.directory()
            if name in directory:
                print(f"Applying setting: {name} = {value}")
                directory[name](value=value)
