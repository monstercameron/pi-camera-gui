import pygame
import os
from typing import List, Optional
from PIL import Image, ExifTags

class Gallery:
    def __init__(self, settings):
        self.settings = settings
        # Ensure path exists
        if "files" in settings and "path" in settings["files"]:
            self.path = settings["files"]["path"]
        else:
            self.path = "home/dcim"
            
        self.files: List[str] = []
        self.current_index = 0
        self.image_cache = {}
        self.font = pygame.font.Font("freesansbold.ttf", 20)
        self.meta_font = pygame.font.Font("freesansbold.ttf", 16)
        self.active = False
        
        # Animation State
        self.target_index = 0
        self.transition_start = 0
        self.transition_duration = 100 # ms
        self.animating = False
        self.direction = 0 # -1 (left/prev), 1 (right/next)
        
        # Metadata State
        self.show_metadata = False

    def enter(self):
        self.active = True
        self.refresh_files()
        if self.files:
            self.current_index = len(self.files) - 1 # Start at newest
            self.target_index = self.current_index
            self.animating = False

    def exit(self):
        self.active = False
        self.image_cache.clear()

    def refresh_files(self):
        if not os.path.exists(self.path):
            self.files = []
            return
        
        valid_exts = [".jpg", ".jpeg", ".png", ".bmp"]
        try:
            self.files = sorted([
                f for f in os.listdir(self.path) 
                if os.path.splitext(f)[1].lower() in valid_exts
            ])
        except OSError:
            self.files = []

    def handle_event(self, event, action=None):
        if not self.active: return

        if action == "left":
            if self.files and not self.animating:
                new_index = (self.current_index - 1) % len(self.files)
                if new_index != self.current_index:
                    self.target_index = new_index
                    self.direction = -1
                    self.animating = True
                    self.transition_start = pygame.time.get_ticks()
        elif action == "right":
            if self.files and not self.animating:
                new_index = (self.current_index + 1) % len(self.files)
                if new_index != self.current_index:
                    self.target_index = new_index
                    self.direction = 1
                    self.animating = True
                    self.transition_start = pygame.time.get_ticks()
        elif action == "up":
            self.show_metadata = True
        elif action == "down":
            self.show_metadata = False
        elif action == "back" or action == "enter":
            self.exit()

    def render(self, surface):
        if not self.active: return

        surface.fill((0, 0, 0))

        if not self.files:
            text = self.font.render("No Images Found", True, (255, 255, 255))
            rect = text.get_rect(center=surface.get_rect().center)
            surface.blit(text, rect)
            return

        width, height = surface.get_size()
        
        # Animation Logic
        draw_offset = 0
        if self.animating:
            now = pygame.time.get_ticks()
            progress = (now - self.transition_start) / self.transition_duration
            if progress >= 1.0:
                self.animating = False
                self.current_index = self.target_index
            else:
                # Linear slide for smoothness
                if self.direction == 1: # Next
                    draw_offset = int(-width * progress)
                else: # Prev
                    draw_offset = int(width * progress)

        # Draw Primary Image (current_index)
        self._draw_image(surface, self.files[self.current_index], draw_offset)
        
        # Draw Secondary Image (target_index) if animating
        if self.animating:
            target_x = draw_offset + (width * self.direction)
            self._draw_image(surface, self.files[self.target_index], target_x)

        # Info Overlay (Top Left)
        # Show target index if animating to avoid confusion
        idx_to_show = self.target_index if self.animating else self.current_index
        filename = self.files[idx_to_show]
        info_text = f"{idx_to_show + 1}/{len(self.files)} - {filename}"
        text = self.font.render(info_text, True, (255, 255, 255))
        # Add shadow
        shadow = self.font.render(info_text, True, (0, 0, 0))
        surface.blit(shadow, (12, 12))
        surface.blit(text, (10, 10))
        
        # Metadata Overlay (Lower Thirds)
        if self.show_metadata:
            self._draw_metadata(surface, filename)

    def _draw_image(self, surface, filename, x_offset):
        filepath = os.path.join(self.path, filename)
        
        # Load Image
        if filepath not in self.image_cache:
            try:
                img = pygame.image.load(filepath)
                # Scale to fit
                sw, sh = surface.get_size()
                iw, ih = img.get_size()
                scale = min(sw/iw, sh/ih)
                new_size = (int(iw*scale), int(ih*scale))
                img = pygame.transform.scale(img, new_size)
                self.image_cache[filepath] = img
                
                # Limit cache size
                if len(self.image_cache) > 5:
                    self.image_cache.pop(next(iter(self.image_cache)))
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
                self.image_cache[filepath] = None

        img = self.image_cache.get(filepath)
        if img:
            rect = img.get_rect(center=surface.get_rect().center)
            rect.x += x_offset
            surface.blit(img, rect)

    def _draw_metadata(self, surface, filename):
        width, height = surface.get_size()
        overlay_height = 100
        
        # Semi-transparent background
        s = pygame.Surface((width, overlay_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        surface.blit(s, (0, height - overlay_height))
        
        meta = self._get_image_metadata(filename)
        
        y = height - overlay_height + 10
        x = 20
        
        lines = [
            f"File: {meta['File']}",
            f"Resolution: {meta['Resolution']}",
            f"Date: {meta['Date']}",
            f"Size: {meta['Size']}"
        ]
        
        for line in lines:
            text = self.meta_font.render(line, True, (200, 200, 200))
            surface.blit(text, (x, y))
            y += 20

    def _get_image_metadata(self, filename):
        filepath = os.path.join(self.path, filename)
        metadata = {
            "File": filename,
            "Resolution": "Unknown",
            "Date": "Unknown",
            "Size": "Unknown"
        }
        
        if not os.path.exists(filepath):
            return metadata
            
        # File Size
        try:
            size_bytes = os.path.getsize(filepath)
            if size_bytes < 1024:
                metadata["Size"] = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                metadata["Size"] = f"{size_bytes / 1024:.1f} KB"
            else:
                metadata["Size"] = f"{size_bytes / (1024 * 1024):.1f} MB"
        except OSError:
            pass

        # EXIF Data
        try:
            with Image.open(filepath) as img:
                # Resolution
                metadata["Resolution"] = f"{img.width}x{img.height}"
                
                # Date
                exif = img._getexif()
                if exif:
                    for tag, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag, tag)
                        if tag_name == "DateTimeOriginal":
                            metadata["Date"] = str(value)
                            break
                        elif tag_name == "DateTime":
                            metadata["Date"] = str(value)
        except Exception as e:
            print(f"Error reading metadata for {filename}: {e}")
            
        return metadata

