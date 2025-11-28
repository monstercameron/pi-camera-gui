import pygame
import sys
from typing import Dict, Any, List, Optional, Callable

from src.ui.layout_parser import LayoutParser

class GUI:
    def __init__(self, settings: Dict[str, Any], menus: Dict[str, Any], camera: Optional[Any] = None):
        self.settings = settings
        self.menus = menus
        self.camera = camera
        self.menu_positions = [0, 0, 0, 0]  # menu_index, submenu_index, option_index, level
        
        pygame.init()
        self.width = settings["display"]["width"]
        self.height = settings["display"]["height"]
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(settings["display"]["caption"])
        
        self.layer = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        self.font = pygame.font.Font('freesansbold.ttf', settings["display"]["fontsize"])
        self.stats_font = pygame.font.Font('freesansbold.ttf', 10)
        self.clock = pygame.time.Clock()
        
        # Enable key repeat for fast scrolling (delay=300ms, interval=50ms)
        pygame.key.set_repeat(300, 50)
        
        self.running = True
        
        # Initialize Layout Parser
        try:
            self.layout = LayoutParser()
            print("Layout parser initialized")
        except Exception as e:
            print(f"Failed to initialize layout parser: {e}")
            self.layout = None

    def run(self, controls_callback: Callable, buttons_class: Any):
        # Check video driver
        driver = pygame.display.get_driver()
        print(f"Video Driver: {driver}")
        if driver == 'dummy':
            print("WARNING: Running with 'dummy' video driver. No window will be visible.")

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
                
                # Toggle Menu Visibility (Dev / Menu Key)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.settings["display"]["showmenu"] = not self.settings["display"]["showmenu"]
                    continue # Consume event to prevent capture/other actions

                # Pass event to controls
                controls_callback(pygame, event, self.menu_positions, self.menus, camera=self.camera)

            # Render Menu
            if self.settings["display"]["showmenu"]:
                self._render_menu()

            # Render Stats / Overlay
            if self.camera:
                self._render_camera_overlay()
            else:
                self.screen.blit(self.layer, (0, 0))

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

        # Render Level 0 (Main Menu)
        self._render_container("level_0", self.menus["menus"], self.menu_positions[0])

        # Render Level 1 (Submenu)
        if 0 <= current_menu_index < len(self.menus["menus"]):
            submenu_items = self.menus["menus"][current_menu_index].get("options", [])
            if self.menu_positions[3] > 0: # If level > 0
                self._render_container("level_1", submenu_items, self.menu_positions[1])

            # Render Level 2 (Options/Values)
            if self.menu_positions[3] > 1: # If level > 1
                current_submenu_index = self.menu_positions[1]
                if 0 <= current_submenu_index < len(submenu_items):
                    option = submenu_items[current_submenu_index]
                    # Construct a list for the value selector
                    value_items = []
                    if option["type"] == "list":
                        value_items = []
                        for opt in option["options"]:
                            if isinstance(opt, dict):
                                # New structure: opt is already a dict with displayname/value
                                value_items.append(opt)
                            else:
                                # Old structure: opt is a value string/int
                                value_items.append({"name": str(opt), "displayname": str(opt), "value": opt})
                        
                        # Highlight the current selection (menu_positions[2])
                        # But wait, menu_positions[2] is the index in the options list
                        self._render_container("level_2", value_items, self.menu_positions[2])
                    elif option["type"] == "range":
                        # For range, just show the value
                        # Pass min/max/step context for slider rendering
                        value_items = [{
                            "name": str(option["value"]), 
                            "is_range": True,
                            "value": option["value"],
                            "min": option["options"]["min"],
                            "max": option["options"]["max"]
                        }]
                        self._render_container("level_2", value_items, 0)

    def _render_container(self, container_id: str, items: List[Dict[str, Any]], selected_index: int):
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
        
        bg_color = self._parse_color(container.get("bg_color", "#00000000"))
        selected_color = self._parse_color(container.get("selected_color", "#FFFFFF"))
        unselected_color = self._parse_color(container.get("unselected_color", "#AAAAAA"))
        
        font_size = int(container.get("font_size", "20"))
        item_height = int(container.get("item_height", "30"))
        padding = int(container.get("padding", "5"))
        orientation = container.get("orientation", "vertical")

        # Draw background
        pygame.draw.rect(self.layer, bg_color, (x, y, w, h))

        # Setup font (Use cached font if possible, or create new one)
        # Creating a new font every frame is expensive and can cause issues
        # Ideally we should cache these in __init__ or a resource manager
        # For now, let's use self.font if size matches, or create a temporary one
        if font_size == self.settings["display"]["fontsize"]:
            font = self.font
        else:
            # Simple cache for other sizes could be added here
            font = pygame.font.Font('freesansbold.ttf', font_size)

        # Draw items
        current_x = x + padding
        current_y = y + padding
        
        # Define clipping rect for the container to handle scrolling text
        container_rect = pygame.Rect(x, y, w, h)
        self.layer.set_clip(container_rect)

        for i, item in enumerate(items):
            is_selected = (i == selected_index)
            color = selected_color if is_selected else unselected_color
            
            # Draw Selection Box
            if is_selected and orientation == "vertical":
                selection_rect = pygame.Rect(x, current_y + (i * item_height), w, item_height)
                # Draw a semi-transparent box or inverted color box
                # Using a slightly lighter background for selection
                pygame.draw.rect(self.layer, (255, 255, 255, 50), selection_rect)
                # Optional: Draw a border
                pygame.draw.rect(self.layer, selected_color, selection_rect, 1)

            # Prepare Text
            name_text = str(item.get("displayname", item.get("name", ""))).upper()
            
            # Append Value if available (for Level 1 items usually)
            if "value" in item:
                val = str(item["value"])
                # Truncate if too long
                if len(val) > 10: val = val[:8] + ".."
                name_text += f" : {val}"

            text_surf = font.render(name_text, True, color)
            text_rect = text_surf.get_rect()
            
            # Position text
            if orientation == "vertical":
                dest_y = current_y + (i * item_height)
                # Center vertically in the item slot
                dest_y += (item_height - text_rect.height) // 2
                
                # Handle Scrolling for overflow
                max_width = w - (padding * 2) - 25 # -25 for chevron space
                overflow = text_rect.width - max_width
                
                if overflow > 0 and is_selected:
                    # Scroll Logic: Pause Start -> Scroll -> Pause End -> Reset
                    scroll_speed = 0.05 # pixels per ms
                    pause_time = 1000 # ms
                    
                    # Calculate total cycle time
                    scroll_time = overflow / scroll_speed
                    total_cycle_time = scroll_time + (pause_time * 2)
                    
                    current_time = pygame.time.get_ticks() % total_cycle_time
                    
                    offset = 0
                    if current_time < pause_time:
                        # Pause at start
                        offset = 0
                    elif current_time < (pause_time + scroll_time):
                        # Scrolling
                        offset = (current_time - pause_time) * scroll_speed
                    else:
                        # Pause at end (before snap back)
                        offset = overflow
                        
                    draw_x = current_x - offset
                    
                    self.layer.blit(text_surf, (draw_x, dest_y))
                else:
                    self.layer.blit(text_surf, (current_x, dest_y))

                # Draw Chevron if item has sub-options (Draw AFTER text for Z-order)
                if "options" in item:
                    chevron_surf = font.render(">", True, color)
                    chevron_rect = chevron_surf.get_rect(midright=(x + w - 10, dest_y + text_rect.height // 2))
                    # Draw a small background behind chevron to ensure legibility if text scrolls under
                    chevron_bg_rect = chevron_rect.inflate(5, 5)
                    pygame.draw.rect(self.layer, bg_color, chevron_bg_rect) # Use container bg color
                    self.layer.blit(chevron_surf, chevron_rect)

            else: # horizontal
                # Simple horizontal layout
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
            bar_y = y + padding + item_height + 10 # Below the text
            bar_w = w - (padding * 2)
            bar_h = 10
            
            # Background track
            pygame.draw.rect(self.layer, unselected_color, (bar_x, bar_y, bar_w, bar_h))
            
            # Calculate handle position
            if max_val > min_val:
                pct = (val - min_val) / (max_val - min_val)
            else:
                pct = 0
            
            handle_w = 20
            handle_x = bar_x + (pct * (bar_w - handle_w))
            
            # Handle
            pygame.draw.rect(self.layer, selected_color, (handle_x, bar_y - 5, handle_w, bar_h + 10))

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
                priority_stats = ["iso", "shutter", "awb", "exposure"]
                
                for key in priority_stats:
                    if key in directory:
                        value = str(directory[key]())
                        
                        # Try to load icon
                        icon_path = f"src/ui/icons/{key}.svg"
                        try:
                            # Pygame 2.0+ supports SVG loading if SDL_image is built with it
                            # If not, this might fail or return empty. 
                            # Fallback: Draw text label if icon fails or is not supported well
                            icon = pygame.image.load(icon_path)
                            icon = pygame.transform.scale(icon, (24, 24)) # Scale icon
                            icon_rect = icon.get_rect(midleft=(current_x, center_y))
                            self.layer.blit(icon, icon_rect)
                            current_x += 30
                        except (pygame.error, FileNotFoundError):
                            # Fallback to text label
                            label_surf = font.render(key.upper(), True, (200, 200, 200))
                            label_rect = label_surf.get_rect(midleft=(current_x, center_y))
                            self.layer.blit(label_surf, label_rect)
                            current_x += label_rect.width + 5

                        # Draw Value
                        val_surf = font.render(value, True, color)
                        val_rect = val_surf.get_rect(midleft=(current_x, center_y))
                        self.layer.blit(val_surf, val_rect)
                        
                        current_x += val_rect.width + 20 # Spacing between items

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

    def _cleanup(self):
        if self.camera:
            self.camera.stopPreview()
            self.camera.closeCamera()
        pygame.quit()
        # sys.exit() # Removed to allow clean exit from run.py
