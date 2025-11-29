import pygame
import sys
import os
from typing import Dict, Any, List, Optional, Callable

from src.ui.layout_parser import LayoutParser
from src.ui.gallery import Gallery

class GUI:
    def __init__(self, settings: Dict[str, Any], menus: Dict[str, Any], camera: Optional[Any] = None):
        self.settings = settings
        self.menus = menus
        self.camera = camera
        self.menu_positions = [0, 0, 0, 0]  # menu_index, submenu_index, option_index, level
        self.quick_menu_pos = [0] # Selected index for quick stats menu
        
        pygame.init()
        
        self.gallery = Gallery(settings)
        
        self.width = settings["display"]["width"]
        self.height = settings["display"]["height"]
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(settings["display"]["caption"])
        
        self.layer = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        self.font = pygame.font.Font('freesansbold.ttf', settings["display"]["fontsize"])
        self.stats_font = pygame.font.Font('freesansbold.ttf', 10)
        self.clock = pygame.time.Clock()
        
        # Animation State
        self.last_level = 0
        self.transition_start = 0
        self.transition_from = 0
        self.transition_to = 0
        self.transition_duration = self.settings["display"].get("animation_duration", 250) # ms
        
        # Flash Effect State
        self.flash_start_time = 0
        self.flash_duration = 25 # ms

        # Timer & Timelapse State
        self.timer_active = False
        self.timer_start_time = 0
        self.timer_duration = 0
        
        self.timelapse_active = False
        self.next_capture_time = 0
        self.timelapse_end_time = 0
        self.timelapse_count = 0

        # Enable key repeat for fast scrolling (delay=300ms, interval=50ms)
        pygame.key.set_repeat(300, 50)
        
        self.running = True
        
        # Cache
        self._icon_cache: Dict[str, Any] = {}
        
        # Initialize Layout Parser
        try:
            self.layout = LayoutParser(theme_config=settings.get("theme", {}))
            print("Layout parser initialized")
        except Exception as e:
            print(f"Failed to initialize layout parser: {e}")
            self.layout = None

    def run(self, controls_callback: Callable, buttons_class: Any):
        # Check video driver
        driver = pygame.display.get_driver()
        print(f"Video Driver: {driver}")
        if driver == 'rpi' or driver == 'null':
            print(f"WARNING: Running with '{driver}' video driver. No window will be visible.")
            # Ensure path exists but do not override settings
            if "files" in self.settings and "path" in self.settings["files"]:
                path_to_check = self.settings["files"]["path"]
                if not os.path.exists(path_to_check):
                    try:
                        os.makedirs(path_to_check)
                    except OSError:
                        pass

        # Initial draw to show window immediately
        self.screen.fill((0, 0, 0))
        try:
            loading_font = pygame.font.Font('freesansbold.ttf', 24)
            text = loading_font.render("Initializing Camera...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(text, text_rect)
        except Exception:
            pass # Font might fail if not found, ignore for loading screen
        pygame.display.flip()

        if self.camera:
            print("Starting camera preview...")
            self.camera.startPreview()
            print("Camera preview started.")

        # Initialize buttons
        buttons = buttons_class(self.settings)
        
        frame_count = 0

        while self.running:
            self.layer.fill((0, 0, 0, 0))  # Clear layer
            
            # Check for layout updates every 60 frames (approx 1 sec)
            frame_count += 1
            if frame_count % 60 == 0:
                if self.layout:
                    self.layout.check_for_updates()
            
            # Handle hardware buttons
            buttons.listen(pygame)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                action = self._get_action_from_event(event)

                if action == "quit":
                    self.running = False
                    continue

                # Gallery Events
                if self.gallery.active:
                    self.gallery.handle_event(event, action)
                    continue
                
                # Toggle Menu Visibility (Enter Key)
                if action == "enter":
                    if not self.settings["display"]["showmenu"]:
                        self.settings["display"]["showmenu"] = True
                        continue
                    # If menu is active, pass Enter to controls for selection

                # Take Photo (Shutter)
                if action == "shutter":
                    if self.camera:
                        # Cancel active modes
                        if self.timer_active:
                            self.timer_active = False
                            print("Timer cancelled")
                            continue
                        if self.timelapse_active:
                            self.timelapse_active = False
                            if hasattr(self.camera, 'stop_timelapse_session'):
                                self.camera.stop_timelapse_session()
                            print("Timelapse cancelled")
                            continue

                        # Check settings
                        timer_delay = 0
                        if hasattr(self.camera, 'timer'):
                            timer_delay = self.camera.timer()
                        
                        timelapse_interval = 0
                        if hasattr(self.camera, 'timelapse_interval'):
                            timelapse_interval = self.camera.timelapse_interval()

                        if timer_delay > 0:
                            self.timer_active = True
                            self.timer_duration = timer_delay
                            self.timer_start_time = pygame.time.get_ticks()
                        elif timelapse_interval > 0:
                            self.timelapse_active = True
                            self.timelapse_count = 0
                            self.next_capture_time = pygame.time.get_ticks()
                            
                            # Start Session
                            if hasattr(self.camera, 'start_timelapse_session'):
                                self.camera.start_timelapse_session()
                            
                            duration = 0
                            if hasattr(self.camera, 'timelapse_duration'):
                                duration = self.camera.timelapse_duration()
                            
                            if duration > 0:
                                self.timelapse_end_time = pygame.time.get_ticks() + (duration * 60 * 1000)
                            else:
                                self.timelapse_end_time = 0
                        else:
                            self.camera.captureImage()
                            self.flash_start_time = pygame.time.get_ticks()
                    continue

                # Pass event to controls
                controls_callback(pygame, event, self.menu_positions, self.menus, camera=self.camera, menu_active=self.settings["display"]["showmenu"], quick_menu_pos=self.quick_menu_pos, action=action)

            # Detect Level Change for Animation
            current_level = self.menu_positions[3]
            if current_level != self.last_level:
                self.transition_from = self.last_level
                self.transition_to = current_level
                self.transition_start = pygame.time.get_ticks()
                self.last_level = current_level

            # Render Gallery
            if self.gallery.active:
                self.gallery.render(self.screen)
                pygame.display.flip()
                self.clock.tick(30)
                continue

            # Render Menu
            if self.settings["display"]["showmenu"]:
                self._render_menu()

            # Render Stats / Overlay
            if self.camera:
                self._render_camera_overlay()
            else:
                self.screen.blit(self.layer, (0, 0))

            # Render Flash Effect
            if pygame.time.get_ticks() - self.flash_start_time < self.flash_duration:
                self.screen.fill((255, 255, 255))

            # Handle Timer Logic & Rendering
            if self.timer_active:
                now = pygame.time.get_ticks()
                elapsed = (now - self.timer_start_time) / 1000.0
                remaining = self.timer_duration - elapsed
                
                if remaining <= 0:
                    self.camera.captureImage()
                    self.flash_start_time = pygame.time.get_ticks()
                    self.timer_active = False
                    
                    # Check for chained timelapse
                    timelapse_interval = 0
                    if hasattr(self.camera, 'timelapse_interval'):
                        timelapse_interval = self.camera.timelapse_interval()
                        
                    if timelapse_interval > 0:
                        self.timelapse_active = True
                        self.timelapse_count = 1
                        self.next_capture_time = pygame.time.get_ticks() + (timelapse_interval * 1000)
                        
                        # Start Session
                        if hasattr(self.camera, 'start_timelapse_session'):
                            self.camera.start_timelapse_session()
                        
                        duration = 0
                        if hasattr(self.camera, 'timelapse_duration'):
                            duration = self.camera.timelapse_duration()
                        
                        if duration > 0:
                            self.timelapse_end_time = pygame.time.get_ticks() + (duration * 60 * 1000)
                        else:
                            self.timelapse_end_time = 0
                else:
                    # Render Countdown
                    count_text = str(int(remaining) + 1)
                    # Big Font
                    big_font = pygame.font.Font('freesansbold.ttf', 120)
                    text_surf = big_font.render(count_text, True, (255, 255, 255))
                    text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
                    
                    # Shadow
                    shadow_surf = big_font.render(count_text, True, (0, 0, 0))
                    shadow_rect = shadow_surf.get_rect(center=(self.width // 2 + 4, self.height // 2 + 4))
                    
                    self.screen.blit(shadow_surf, shadow_rect)
                    self.screen.blit(text_surf, text_rect)

            # Handle Timelapse Logic & Rendering
            if self.timelapse_active:
                now = pygame.time.get_ticks()
                if now >= self.next_capture_time:
                    self.camera.captureImage()
                    self.flash_start_time = pygame.time.get_ticks()
                    self.timelapse_count += 1
                    
                    interval = self.camera.timelapse_interval()
                    self.next_capture_time = now + (interval * 1000)
                    
                    if self.timelapse_end_time > 0 and now >= self.timelapse_end_time:
                        self.timelapse_active = False
                        if hasattr(self.camera, 'stop_timelapse_session'):
                            self.camera.stop_timelapse_session()
                
                # Render Timelapse Status Icon/Text
                status_text = f"TL: {self.timelapse_count}"
                tl_surf = self.stats_font.render(status_text, True, (255, 50, 50))
                self.screen.blit(tl_surf, (10, 10))

            pygame.display.flip()
            self.clock.tick(self.settings["display"]["refreshrate"])

        self._cleanup()

    def _render_menu(self):
        # Determine background based on camera overlay
        if self.camera is None:
            self.layer.fill((255, 255, 255, 255))
        
        # Determine current menu name and load layout
        current_menu_index = self.menu_positions[0]
        if 0 <= current_menu_index < len(self.menus["menus"]):
            current_menu_name = self.menus["menus"][current_menu_index]["name"]
            if self.layout:
                self.layout.load_layout(current_menu_name)

        # Dynamic Layout Calculation with Animation
        current_level = self.menu_positions[3]
        
        # Calculate Animation Progress
        now = pygame.time.get_ticks()
        if now - self.transition_start < self.transition_duration:
            t = (now - self.transition_start) / self.transition_duration
            # Simple ease-out
            t = 1 - (1 - t) * (1 - t)
        else:
            t = 1.0

        # Helper to get target width for a column at a specific level state
        def get_target_width(col_idx, level_state):
            collapsed_width = 60
            # Level 0 (Main Menu)
            if col_idx == 0:
                # Collapses if level > 0
                return collapsed_width if level_state > 0 else 200
            # Level 1 (Submenu)
            elif col_idx == 1:
                # Hidden if level < 1
                if level_state < 1: return 0
                # Collapses if level > 1
                return collapsed_width if level_state > 1 else 260
            # Level 2 (Options)
            elif col_idx == 2:
                # Hidden if level < 2
                if level_state < 2: return 0
                return 260
            return 0

        # Interpolate Widths
        w0_start = get_target_width(0, self.transition_from)
        w0_end = get_target_width(0, self.transition_to)
        l0_width = int(w0_start + (w0_end - w0_start) * t)

        w1_start = get_target_width(1, self.transition_from)
        w1_end = get_target_width(1, self.transition_to)
        l1_width = int(w1_start + (w1_end - w1_start) * t)
        
        # Determine collapsed state for rendering content
        # We use the target state (current_level) to decide content mode immediately
        l0_collapsed = (current_level > 0)
        l1_collapsed = (current_level > 1)

        x_cursor = 0

        # --- Level 0 (Main Menu) ---
        # Try to get width from layout if not collapsed (for target calculation reference)
        # But for animation we use our calculated l0_width
        
        self._render_container("level_0", self.menus["menus"], self.menu_positions[0], 
                               override_x=x_cursor, override_width=l0_width, collapsed=l0_collapsed)
        x_cursor += l0_width

        # --- Level 1 (Submenu) ---
        if 0 <= current_menu_index < len(self.menus["menus"]):
            submenu_items = self.menus["menus"][current_menu_index].get("options", [])
            
            # Only render if width > 0
            if l1_width > 0:
                self._render_container("level_1", submenu_items, self.menu_positions[1],
                                       override_x=x_cursor, override_width=l1_width, collapsed=l1_collapsed)
                x_cursor += l1_width

                # --- Level 2 (Options/Values) ---
                # Level 2 width is just remaining space or standard?
                # We didn't animate Level 2 width explicitly in previous code, it just appeared.
                # Let's animate it too.
                w2_start = get_target_width(2, self.transition_from)
                w2_end = get_target_width(2, self.transition_to)
                l2_width = int(w2_start + (w2_end - w2_start) * t)

                if l2_width > 0:
                    current_submenu_index = self.menu_positions[1]
                    if 0 <= current_submenu_index < len(submenu_items):
                        option = submenu_items[current_submenu_index]
                        
                        # Get current value for "Old : New" display
                        current_val = option.get("_original_value", option.get("value", None))

                        value_items = []
                        if option["type"] == "list":
                            value_items = []
                            for opt in option["options"]:
                                if isinstance(opt, dict):
                                    value_items.append(opt)
                                else:
                                    value_items.append({"name": str(opt), "displayname": str(opt), "value": opt})
                            
                            self._render_container("level_2", value_items, self.menu_positions[2],
                                                   override_x=x_cursor, override_width=l2_width, current_value=current_val)
                        elif option["type"] == "range":
                            value_items = [{
                                "name": str(option["value"]), 
                                "is_range": True,
                                "value": option["value"],
                                "min": option["options"]["min"],
                                "max": option["options"]["max"]
                            }]
                            self._render_container("level_2", value_items, 0, override_x=x_cursor, override_width=l2_width, current_value=current_val)

    def _render_container(self, container_id: str, items: List[Dict[str, Any]], selected_index: int, 
                          override_x: Optional[int] = None, override_width: Optional[int] = None, 
                          collapsed: bool = False, current_value: Any = None):
        if not self.layout:
            return

        container = self.layout.get_element_by_id(container_id)
        if not container:
            return

        # Parse container attributes
        x = self._parse_dimension(container.get("x", "0"), self.width)
        y = self._parse_dimension(container.get("y", "0"), self.height)
        w = self._parse_dimension(container.get("width", "100"), self.width)
        h = self._parse_dimension(container.get("height", "100"), self.height)
        
        # Apply overrides
        if override_x is not None: x = override_x
        if override_width is not None: w = override_width
        
        bg_color = self._parse_color(container.get("bg_color", "#00000000"))
        selected_color = self._parse_color(container.get("selected_color", "#FFFFFF"))
        unselected_color = self._parse_color(container.get("unselected_color", "#AAAAAA"))
        selection_bg_color = self._parse_color(container.get("selection_bg_color", "#FFFFFF33"))
        
        font_size = int(container.get("font_size", "20"))
        item_height = int(container.get("item_height", "30"))
        padding = int(container.get("padding", "5"))
        orientation = container.get("orientation", "vertical")

        # Draw background
        pygame.draw.rect(self.layer, bg_color, (x, y, w, h))

        # Setup font
        if font_size == self.settings["display"]["fontsize"]:
            font = self.font
        else:
            font = pygame.font.Font('freesansbold.ttf', font_size)

        # Draw items
        current_x = x + padding
        current_y = y + padding
        
        # Define clipping rect
        container_rect = pygame.Rect(x, y, w, h)
        self.layer.set_clip(container_rect)

        for i, item in enumerate(items):
            is_selected = (i == selected_index)
            color = selected_color if is_selected else unselected_color
            
            # Draw Selection Box
            if is_selected and orientation == "vertical":
                selection_rect = pygame.Rect(x, current_y + (i * item_height), w, item_height)
                pygame.draw.rect(self.layer, selection_bg_color, selection_rect)
                # pygame.draw.rect(self.layer, selected_color, selection_rect, 1)

            # Prepare Text
            display_name = str(item.get("displayname", item.get("name", ""))).title()
            
            if collapsed:
                # Collapsed Mode: Try to load icon, fallback to first letter
                icon_loaded = False
                
                # Determine icon filename from item name
                # Normalize: lowercase, replace spaces with underscores
                raw_name = str(item.get("name", "")).lower().replace(" ", "_")
                
                # Icon Aliases
                icon_aliases = {
                    "exposurecomp": "exposure"
                }
                if raw_name in icon_aliases:
                    raw_name = icon_aliases[raw_name]

                icon_path = f"src/ui/icons/{raw_name}.svg"
                
                # Check Cache
                if icon_path in self._icon_cache:
                    icon = self._icon_cache[icon_path]
                    if icon:
                        # Center icon
                        icon_rect = icon.get_rect(center=(x + w//2, current_y + (i * item_height) + item_height//2))
                        self.layer.blit(icon, icon_rect)
                        icon_loaded = True
                elif os.path.exists(icon_path):
                    try:
                        icon = pygame.image.load(icon_path)
                        # Scale icon to fit within item_height (with some padding)
                        icon_size = int(item_height * 0.7)
                        icon = pygame.transform.scale(icon, (icon_size, icon_size))
                        
                        # Cache it
                        self._icon_cache[icon_path] = icon
                        
                        # Center icon
                        icon_rect = icon.get_rect(center=(x + w//2, current_y + (i * item_height) + item_height//2))
                        self.layer.blit(icon, icon_rect)
                        icon_loaded = True
                    except Exception as e:
                        print(f"Failed to load icon {icon_path}: {e}")
                        self._icon_cache[icon_path] = None # Cache failure to avoid retry
                else:
                    self._icon_cache[icon_path] = None
                
                if not icon_loaded:
                    short_name = display_name[0] if display_name else "?"
                    text_surf = font.render(short_name, True, color)
                    text_rect = text_surf.get_rect(center=(x + w//2, current_y + (i * item_height) + item_height//2))
                    self.layer.blit(text_surf, text_rect)
            else:
                # Normal Mode
                
                # Try to load icon for normal mode too
                icon_width = 0
                raw_name = str(item.get("name", "")).lower().replace(" ", "_")
                
                # Icon Aliases
                icon_aliases = {
                    "exposurecomp": "exposure"
                }
                if raw_name in icon_aliases:
                    raw_name = icon_aliases[raw_name]

                icon_path = f"src/ui/icons/{raw_name}.svg"
                
                # Check Cache
                if icon_path in self._icon_cache:
                    icon = self._icon_cache[icon_path]
                    if icon:
                        icon_y = current_y + (i * item_height) + (item_height - icon.get_height()) // 2
                        self.layer.blit(icon, (current_x, icon_y))
                        icon_width = icon.get_width() + 10
                elif os.path.exists(icon_path):
                    try:
                        icon = pygame.image.load(icon_path)
                        icon_size = int(item_height * 0.6)
                        icon = pygame.transform.scale(icon, (icon_size, icon_size))
                        self._icon_cache[icon_path] = icon
                        
                        # Position icon to the left of text
                        icon_y = current_y + (i * item_height) + (item_height - icon_size) // 2
                        self.layer.blit(icon, (current_x, icon_y))
                        icon_width = icon_size + 10 # Add spacing
                    except Exception:
                        self._icon_cache[icon_path] = None
                else:
                    self._icon_cache[icon_path] = None

                name_text = display_name

                # Handle Level 2 Logic
                if container_id == "level_2":
                    if item.get("is_range"):
                         # Slider: Old : New
                         candidate_val = str(item.get("value", ""))
                         if current_value is not None:
                             name_text = f"{current_value} : {candidate_val}"
                         else:
                             name_text = candidate_val
                    else:
                         # List: Asterisk for old value
                         # Check if this item's value matches current_value
                         # item["value"] might be int or string, current_value same.
                         if current_value is not None and str(item.get("value")) == str(current_value):
                             name_text += " *"

                text_surf = font.render(name_text, True, color)
                text_rect = text_surf.get_rect()
                
                # Position text
                if orientation == "vertical":
                    dest_y = current_y + (i * item_height)
                    dest_y += (item_height - text_rect.height) // 2
                    
                    # Handle Scrolling
                    max_width = w - (padding * 2) - 25 - icon_width
                    overflow = text_rect.width - max_width
                    
                    draw_x = current_x + icon_width
                    
                    if overflow > 0 and is_selected:
                        scroll_speed = 0.05
                        pause_time = 1000
                        scroll_time = overflow / scroll_speed
                        total_cycle_time = scroll_time + (pause_time * 2)
                        current_time = pygame.time.get_ticks() % total_cycle_time
                        
                        offset = 0
                        if current_time < pause_time: offset = 0
                        elif current_time < (pause_time + scroll_time): offset = (current_time - pause_time) * scroll_speed
                        else: offset = overflow
                            
                        draw_x -= offset
                        self.layer.blit(text_surf, (draw_x, dest_y))
                    else:
                        self.layer.blit(text_surf, (draw_x, dest_y))

                    # Draw Chevron
                    if "options" in item:
                        chevron_surf = font.render(">", True, color)
                        chevron_rect = chevron_surf.get_rect(midright=(x + w - 10, dest_y + text_rect.height // 2))
                        chevron_bg_rect = chevron_rect.inflate(5, 5)
                        pygame.draw.rect(self.layer, bg_color, chevron_bg_rect)
                        self.layer.blit(chevron_surf, chevron_rect)

                else: # horizontal
                    self.layer.blit(text_surf, (current_x, current_y))
                    current_x += text_rect.width + int(container.get("item_spacing", "20"))
        
        # Reset clip
        self.layer.set_clip(None)
        
        # Render Slider for Range Types (Level 2)
        if container_id == "level_2" and len(items) == 1 and items[0].get("is_range"):
            item = items[0]
            val = item["value"]
            min_val = item["min"]
            max_val = item["max"]
            
            # Draw Slider Bar
            bar_x = x + padding
            bar_y = y + padding + item_height + 10
            bar_w = w - (padding * 2)
            bar_h = 10
            
            pygame.draw.rect(self.layer, unselected_color, (bar_x, bar_y, bar_w, bar_h))
            
            if max_val > min_val:
                pct = (val - min_val) / (max_val - min_val)
            else:
                pct = 0
            
            handle_w = 20
            handle_x = bar_x + (pct * (bar_w - handle_w))
            
            pygame.draw.rect(self.layer, selected_color, (handle_x, bar_y - 5, handle_w, bar_h + 10))

            # Draw Min/Max
            min_surf = font.render(str(min_val), True, unselected_color)
            max_surf = font.render(str(max_val), True, unselected_color)
            
            # Position Min/Max below slider
            self.layer.blit(min_surf, (bar_x, bar_y + 20))
            self.layer.blit(max_surf, (bar_x + bar_w - max_surf.get_width(), bar_y + 20))

    def _parse_dimension(self, value: str, total_size: int) -> int:
        value = str(value)
        if value.endswith("%"):
            return int(total_size * float(value.strip("%")) / 100)
        if value == "center":
            return total_size // 2
        if value == "right" or value == "bottom":
            return total_size # Needs context of object size to be useful, simplified here
        return int(value)

    def _parse_color(self, hex_string: str) -> tuple:
        hex_string = hex_string.lstrip('#')
        if len(hex_string) == 6:
            return tuple(int(hex_string[i:i+2], 16) for i in (0, 2, 4))
        elif len(hex_string) == 8:
            return tuple(int(hex_string[i:i+2], 16) for i in (0, 2, 4, 6))
        return (255, 255, 255)

    def _render_camera_overlay(self):
        # Stats
        directory = self.camera.directory()
        
        # Use stats container from layout
        if self.layout:
            container = self.layout.get_element_by_id("stats")
            if container:
                x = self._parse_dimension(container.get("x", "0"), self.width)
                y = self._parse_dimension(container.get("y", "0"), self.height)
                w = self._parse_dimension(container.get("width", "100%"), self.width)
                h = self._parse_dimension(container.get("height", "30"), self.height)
                bg_color = self._parse_color(container.get("bg_color", "#00000088"))
                font_size = int(container.get("font_size", "12"))
                color = self._parse_color(container.get("color", "#FFFFFF"))
                
                # Draw background
                pygame.draw.rect(self.layer, bg_color, (x, y, w, h))
                
                # Draw stats with icons
                current_x = x + 20
                center_y = y + h // 2
                font = pygame.font.Font('freesansbold.ttf', font_size)
                
                # Define priority stats to show
                left_stats = ["mode", "iso", "shutter", "awb", "exposure"]
                right_stats = ["resolution", "filesize", "remaining"]
                
                # Render Left Stats
                for i, key in enumerate(left_stats):
                    if key in directory:
                        start_x = current_x
                        value = str(directory[key]())
                        
                        # Try to load icon
                        icon_path = f"src/ui/icons/{key}.svg"
                        
                        # Check Cache
                        icon_drawn = False
                        if icon_path in self._icon_cache:
                            icon = self._icon_cache[icon_path]
                            if icon:
                                icon_rect = icon.get_rect(midleft=(current_x, center_y))
                                self.layer.blit(icon, icon_rect)
                                current_x += 30
                                icon_drawn = True
                        elif os.path.exists(icon_path):
                            try:
                                icon = pygame.image.load(icon_path)
                                icon = pygame.transform.scale(icon, (24, 24))
                                self._icon_cache[icon_path] = icon
                                
                                icon_rect = icon.get_rect(midleft=(current_x, center_y))
                                self.layer.blit(icon, icon_rect)
                                current_x += 30
                                icon_drawn = True
                            except (pygame.error, FileNotFoundError):
                                self._icon_cache[icon_path] = None
                        else:
                            self._icon_cache[icon_path] = None
                            
                        if not icon_drawn:
                            label_surf = font.render(key.upper(), True, (200, 200, 200))
                            label_rect = label_surf.get_rect(midleft=(current_x, center_y))
                            self.layer.blit(label_surf, label_rect)
                            current_x += label_rect.width + 5

                        # Draw Value
                        val_surf = font.render(value, True, color)
                        val_rect = val_surf.get_rect(midleft=(current_x, center_y))
                        self.layer.blit(val_surf, val_rect)
                        
                        # Draw Selection Box if active
                        if not self.settings["display"]["showmenu"] and i == self.quick_menu_pos[0]:
                            end_x = current_x + val_rect.width
                            selection_rect = pygame.Rect(start_x - 5, y + 2, (end_x - start_x) + 10, h - 4)
                            s = pygame.Surface((selection_rect.width, selection_rect.height), pygame.SRCALPHA)
                            s.fill((255, 255, 255, 50))
                            self.layer.blit(s, selection_rect.topleft)
                            pygame.draw.rect(self.layer, (255, 255, 255), selection_rect, 1)

                        current_x += val_rect.width + 20

                # Render Right Stats (Right Justified)
                current_x = x + w - 20
                for key in reversed(right_stats):
                    if key in directory:
                        value = str(directory[key]())
                        
                        # Calculate width first to position correctly
                        val_surf = font.render(value, True, color)
                        val_width = val_surf.get_width()
                        
                        icon_width = 30 # Standard icon width + padding
                        
                        # Position: [Icon] [Value] | <-- current_x
                        # So we move current_x back by (icon + value + spacing)
                        
                        item_width = icon_width + val_width
                        draw_x = current_x - item_width
                        
                        # Draw Icon
                        icon_path = f"src/ui/icons/{key}.svg"
                        
                        # Check Cache
                        if icon_path in self._icon_cache:
                            icon = self._icon_cache[icon_path]
                            if icon:
                                icon_rect = icon.get_rect(midleft=(draw_x, center_y))
                                self.layer.blit(icon, icon_rect)
                        elif os.path.exists(icon_path):
                            try:
                                icon = pygame.image.load(icon_path)
                                icon = pygame.transform.scale(icon, (24, 24))
                                self._icon_cache[icon_path] = icon
                                
                                icon_rect = icon.get_rect(midleft=(draw_x, center_y))
                                self.layer.blit(icon, icon_rect)
                            except (pygame.error, FileNotFoundError):
                                self._icon_cache[icon_path] = None
                        else:
                            self._icon_cache[icon_path] = None

                        # Draw Value
                        val_rect = val_surf.get_rect(midleft=(draw_x + 30, center_y))
                        self.layer.blit(val_surf, val_rect)
                        
                        current_x -= (item_width + 20) # Move left for next item

                # Delegate rendering to camera
                self.camera.render(self.layer, self.screen)
                return

        # Fallback if no layout
        stats_details = " ".join([f"{k}:{v()}" for k, v in directory.items()])
        stats_surf = self._generate_text(stats_details, (255, 255, 255), (0, 0, 0), font=self.stats_font)
        stats_rect = stats_surf.get_rect()
        pos = (self.width / 2 - stats_rect.width / 2, self.height - stats_rect.height)
        self.layer.blit(stats_surf, pos)

        # Delegate rendering to camera
        self.camera.render(self.layer, self.screen)

    def _generate_text(self, text: str, fg: tuple, bg: tuple, font=None):
        if font is None:
            font = self.font
        return font.render(str(text).upper(), False, fg, bg)

    def _get_action_from_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
            
        controls = self.settings.get("controls", {})
        for action, config in controls.items():
            key_name = config.get("key")
            # Resolve key
            if isinstance(key_name, int):
                target_key = key_name
            else:
                target_key = getattr(pygame, key_name, None)
                
            if event.key == target_key:
                return action
        return None

    def _cleanup(self):
        if self.camera:
            self.camera.stopPreview()
            self.camera.closeCamera()
        pygame.quit()
        # sys.exit() # Removed to allow clean exit from run.py
