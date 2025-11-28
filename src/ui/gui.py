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
        
        self.running = True
        
        # Initialize Layout Parser
        try:
            self.layout = LayoutParser()
            print("Layout parser initialized")
        except Exception as e:
            print(f"Failed to initialize layout parser: {e}")
            self.layout = None

    def run(self, controls_callback: Callable, buttons_class: Any):
        if self.camera:
            self.camera.startPreview()

        # Initialize buttons
        buttons = buttons_class(self.settings)

        while self.running:
            self.layer.fill((0, 0, 0, 0))  # Clear layer
            
            # Handle hardware buttons
            buttons.listen(pygame)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
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
        
        highlighted = (255, 255, 255)
        normal = (0, 0, 0)
        
        # Determine current menu name and load layout
        current_menu_index = self.menu_positions[0]
        if 0 <= current_menu_index < len(self.menus["menus"]):
            current_menu_name = self.menus["menus"][current_menu_index]["name"]
            if self.layout:
                self.layout.load_layout(current_menu_name)
        
        # Use layout if available
        start_x = self.settings["display"]["padding"]
        start_y = self.settings["display"]["padding"]
        
        if self.layout:
            menu_area = self.layout.get_element_by_id("menu_area")
            if menu_area:
                # Parse x/y from layout (simple implementation)
                try:
                    start_x = int(menu_area.get("x", start_x))
                    start_y = int(menu_area.get("y", start_y))
                except ValueError:
                    pass # Keep defaults if parsing fails

        padding = self.settings["display"]["padding"]

        for i, menu_item in enumerate(self.menus["menus"]):
            is_selected_menu = (i == self.menu_positions[0])
            fg = highlighted if is_selected_menu else normal
            bg = normal if is_selected_menu else highlighted

            text_surf = self._generate_text(menu_item["name"], fg, bg)
            text_rect = text_surf.get_rect()
            self.layer.blit(text_surf, (start_x, start_y + text_rect.height * i))

            # Render Submenu
            if "options" in menu_item and is_selected_menu and self.menu_positions[3] > 0:
                self._render_submenu(menu_item["options"], start_y)

    def _render_submenu(self, options: List[Dict[str, Any]], padding: int):
        highlighted = (255, 255, 255)
        normal = (0, 0, 0)
        
        for j, option in enumerate(options):
            is_selected_option = (j == self.menu_positions[1])
            fg = highlighted if is_selected_option and self.menu_positions[3] > 0 else normal
            bg = normal if is_selected_option and self.menu_positions[3] > 0 else highlighted

            text_surf = self._generate_text(option["name"], fg, bg)
            text_rect = text_surf.get_rect()
            self.layer.blit(text_surf, (250, padding + text_rect.height * j))

            # Render Option Value
            if "options" in option and is_selected_option and self.menu_positions[3] > 1:
                self._render_option_value(option, padding, j, text_rect)

    def _render_option_value(self, option: Dict[str, Any], padding: int, index: int, parent_rect: pygame.Rect):
        highlighted = (255, 255, 255)
        normal = (0, 0, 0)
        fg = highlighted
        bg = normal
        
        display_text = "loading..."
        if option["type"] == "list":
            # option["value"] is the current value
            # option["options"] is the list of possible values
            # menu_positions[2] is the index in the list? 
            # Wait, the original code used menuPos[2] to index option["options"]
            # But option["value"] seems to be the stored value.
            # Let's trust the original logic for now:
            # text = f'{option["value"]} --> {option["options"][menuPos[2]]}'
            try:
                current_selection = option["options"][self.menu_positions[2]]
                display_text = f'{option["value"]} --> {current_selection}'
            except (IndexError, KeyError):
                display_text = str(option["value"])

        elif option["type"] == "range":
            display_text = str(option["value"])

        text_surf = self._generate_text(display_text, fg, bg)
        self.layer.blit(text_surf, (350 + padding + parent_rect.width, padding + parent_rect.height * index))

    def _render_camera_overlay(self):
        # Stats
        directory = self.camera.directory()
        stats_details = " ".join([f"{k}:{v()}" for k, v in directory.items()])
        
        stats_surf = self._generate_text(stats_details, (255, 255, 255), (0, 0, 0), font=self.stats_font)
        stats_rect = stats_surf.get_rect()
        
        # Center bottom
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
        sys.exit()
