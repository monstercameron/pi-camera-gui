import pygame
from typing import Dict, Any, List, Optional

class MenuController:
    @staticmethod
    def handle_event(pygame_mod, event, menu_pos: List[int], menus: Dict[str, Any], camera: Optional[Any] = None, menu_active: bool = True, quick_menu_pos: Optional[List[int]] = None, callbacks: Optional[Dict[str, Any]] = None, action: Optional[str] = None):
        """
        Handles input events for menu navigation and value updates.
        menu_pos: [menu_index, submenu_index, option_index, level]
        """
        if action == "back":
            # If menu is active, back goes up a level
            if menu_active:
                MenuController._navigate(-1, menu_pos, menus, callbacks)
            else:
                # Post a QUIT event instead of calling quit() directly
                # This allows the main loop to handle the exit gracefully
                pygame_mod.event.post(pygame_mod.event.Event(pygame_mod.QUIT))
            return

        # Navigation / Value Change
        if menu_active:
            if action == "up":
                MenuController._handle_vertical_input(1, menu_pos, menus, camera, callbacks)
            elif action == "down":
                MenuController._handle_vertical_input(-1, menu_pos, menus, camera, callbacks)
            elif action == "right":
                MenuController._navigate(1, menu_pos, menus, callbacks)
            elif action == "left":
                MenuController._navigate(-1, menu_pos, menus, callbacks)
            elif action == "enter":
                MenuController._handle_enter(menu_pos, menus, camera, callbacks)
        elif quick_menu_pos is not None and camera is not None:
            # Quick Menu Logic (when main menu is inactive)
            if action == "right":
                # Cycle to next stat (5 stats: Mode, ISO, Shutter, AWB, Exposure)
                quick_menu_pos[0] = (quick_menu_pos[0] + 1) % 5
            elif action == "left":
                # Cycle to prev stat
                quick_menu_pos[0] = (quick_menu_pos[0] - 1) % 5
            elif action == "up":
                # Increase value (or next item)
                MenuController._handle_quick_value_change(1, quick_menu_pos[0], menus, camera)
            elif action == "down":
                # Decrease value (or prev item)
                MenuController._handle_quick_value_change(-1, quick_menu_pos[0], menus, camera)

        # Camera specific controls (e.g. Capture)
        if camera is not None:
            # Assuming camera has a controls method. 
            # Ideally this should be decoupled, but keeping for compatibility.
            if hasattr(camera, 'controls'):
                if event and event.type == pygame_mod.KEYDOWN:
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
    def _navigate(direction: int, menu_pos: List[int], menus: Dict[str, Any], callbacks: Optional[Dict[str, Any]] = None):
        if direction > 0:
            # Go deeper
            
            # Check for Top Level Action (e.g. Gallery)
            if menu_pos[3] == 0:
                try:
                    current_menu = menus["menus"][menu_pos[0]]
                    if current_menu.get("name") == "gallery":
                        if callbacks and "open_gallery" in callbacks:
                            callbacks["open_gallery"]()
                            # Close menu after opening gallery?
                            if "close_menu" in callbacks:
                                callbacks["close_menu"]()
                        return
                except (KeyError, IndexError):
                    pass

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
                
                menu_pos[menu_pos[3]] = 0 # Reset current level index
                menu_pos[3] -= 1
            elif menu_pos[3] == 0:
                # Close menu if at top level
                if callbacks and "close_menu" in callbacks:
                    callbacks["close_menu"]()

    @staticmethod
    def _handle_enter(menu_pos: List[int], menus: Dict[str, Any], camera: Any, callbacks: Optional[Dict[str, Any]] = None):
        # Check for Top Level Action (e.g. Gallery)
        if menu_pos[3] == 0:
            try:
                current_menu = menus["menus"][menu_pos[0]]
                if current_menu.get("name") == "gallery":
                    if callbacks and "open_gallery" in callbacks:
                        callbacks["open_gallery"]()
                        if "close_menu" in callbacks:
                            callbacks["close_menu"]()
                    return
            except (KeyError, IndexError):
                pass

        # If not at leaf level (Level 2), Enter acts like Right (Go Deeper)
        if menu_pos[3] < 2:
            MenuController._navigate(1, menu_pos, menus, callbacks)
            return

        # If at Level 2, Enter selects the current item
        if menu_pos[3] == 2:
            try:
                option = menus["menus"][menu_pos[0]]["options"][menu_pos[1]]
                # print(f"DEBUG: Option found: {option}")
                
                if option["type"] == "list":
                    selected_item = option["options"][menu_pos[2]]
                    # print(f"DEBUG: Selected item: {selected_item}")
                    
                    if isinstance(selected_item, dict) and "value" in selected_item:
                        selected_value = selected_item["value"]
                    else:
                        selected_value = selected_item
                    
                    if option["value"] != selected_value:
                        option["value"] = selected_value
                        MenuController._apply_setting(camera, option, callbacks)
                    
                    # Go back after selection
                    MenuController._navigate(-1, menu_pos, menus, callbacks)
                
                elif option["type"] == "range":
                    # Range values are updated live, but maybe we want to confirm?
                    # For now, just go back.
                    MenuController._navigate(-1, menu_pos, menus, callbacks)
                    
            except (KeyError, IndexError):
                pass

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
            # Previous item (UP)
            if current_index > 0:
                menu_pos[menu_pos[3]] -= 1
            else:
                menu_pos[menu_pos[3]] = limit - 1 # Loop to bottom
        else:
            # Next item (DOWN)
            if current_index < limit - 1:
                menu_pos[menu_pos[3]] += 1
            else:
                menu_pos[menu_pos[3]] = 0 # Loop to top

        # For list type, we just update the index. Selection happens on Enter.
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
        stat_names = ["mode", "iso", "shutter", "awb", "exposure"]
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

        # Handle Gallery Action
        if name == "open_gallery" and value == "yes":
            if callbacks and "open_gallery" in callbacks:
                print("Opening gallery...")
                callbacks["open_gallery"]()
                option["value"] = "no"
            return

        if camera:
            directory = camera.directory()
            if name in directory:
                print(f"Applying setting: {name} = {value}")
                directory[name](value=value)
