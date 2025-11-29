import pygame
import os
import math
import threading
from typing import List, Optional, Set
from PIL import Image, ExifTags

class Gallery:
    # Buffer size: keep ±25 images loaded around current position
    BUFFER_SIZE = 25
    
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
        self._cache_lock = threading.Lock()
        self._loading_indices: Set[int] = set()  # Track which indices are being loaded
        self.font = pygame.font.Font("freesansbold.ttf", 20)
        self.meta_font = pygame.font.Font("freesansbold.ttf", 16)
        self.active = False
        
        # Display dimensions for scaling (set on first render)
        self._display_size = None
        
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
            # Start loading buffer around current position
            self._update_buffer()

    def exit(self):
        self.active = False
        # Clear cache to free RAM
        with self._cache_lock:
            self.image_cache.clear()
        self._loading_indices.clear()

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

    def handle_event(self, event, action=None, auto_collapse=False):
        if not self.active: return

        if action == "left":
            if self.files and not self.animating:
                # Auto-collapse: exit when at first image
                if auto_collapse and self.current_index == 0:
                    self.exit()
                    return
                # Wrap around or stay at boundary
                new_index = (self.current_index - 1) % len(self.files)
                if new_index != self.current_index:
                    self.target_index = new_index
                    self.direction = -1
                    self.animating = True
                    self.transition_start = pygame.time.get_ticks()
                    # Update buffer for new position
                    self._update_buffer(new_index)
        elif action == "right":
            if self.files and not self.animating:
                # Auto-collapse: exit when at last image
                if auto_collapse and self.current_index == len(self.files) - 1:
                    self.exit()
                    return
                # Wrap around or stay at boundary
                new_index = (self.current_index + 1) % len(self.files)
                if new_index != self.current_index:
                    self.target_index = new_index
                    self.direction = 1
                    self.animating = True
                    self.transition_start = pygame.time.get_ticks()
                    # Update buffer for new position
                    self._update_buffer(new_index)
        elif action == "up":
            self.show_metadata = True
        elif action == "down":
            self.show_metadata = False
        elif action == "back" or action == "enter":
            self.exit()

    def _get_buffer_indices(self, center_index: int = None) -> Set[int]:
        """Get the set of indices that should be in the buffer."""
        if center_index is None:
            center_index = self.current_index
        
        if not self.files:
            return set()
        
        indices = set()
        total = len(self.files)
        
        for offset in range(-self.BUFFER_SIZE, self.BUFFER_SIZE + 1):
            idx = center_index + offset
            # Clamp to valid range (no wrapping for buffer)
            if 0 <= idx < total:
                indices.add(idx)
        
        return indices

    def _update_buffer(self, new_center: int = None):
        """Update the image buffer: load new images, unload distant ones."""
        if not self.files:
            return
            
        if new_center is None:
            new_center = self.current_index
        
        desired_indices = self._get_buffer_indices(new_center)
        
        # Unload images outside the buffer
        with self._cache_lock:
            current_cached = set()
            for filepath in list(self.image_cache.keys()):
                filename = os.path.basename(filepath)
                if filename in self.files:
                    idx = self.files.index(filename)
                    current_cached.add(idx)
                    if idx not in desired_indices:
                        del self.image_cache[filepath]
        
        # Load missing images in background
        for idx in desired_indices:
            if idx not in current_cached and idx not in self._loading_indices:
                self._load_image_async(idx)

    def _load_image_async(self, index: int):
        """Load an image in a background thread."""
        if index < 0 or index >= len(self.files):
            return
        
        self._loading_indices.add(index)
        
        def load():
            try:
                filename = self.files[index]
                filepath = os.path.join(self.path, filename)
                
                if not os.path.exists(filepath):
                    return
                
                # Load and scale image
                img = pygame.image.load(filepath)
                
                # Use stored display size or default
                if self._display_size:
                    sw, sh = self._display_size
                else:
                    sw, sh = 480, 320  # Default fallback
                
                iw, ih = img.get_size()
                scale = min(sw/iw, sh/ih)
                new_size = (int(iw*scale), int(ih*scale))
                img = pygame.transform.scale(img, new_size)
                
                with self._cache_lock:
                    self.image_cache[filepath] = img
            except Exception as e:
                print(f"Error loading {self.files[index]}: {e}")
            finally:
                self._loading_indices.discard(index)
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()

    def render(self, surface):
        if not self.active: return
        
        # Store display size for async loading
        self._display_size = surface.get_size()

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
        
        # Thread-safe cache access
        with self._cache_lock:
            img = self.image_cache.get(filepath)
        
        # Check if image is currently being loaded
        file_index = self.files.index(filename) if filename in self.files else -1
        is_loading = file_index in self._loading_indices
        
        # If not in cache and not loading, show loading indicator and trigger async load
        if img is None:
            if is_loading:
                # Show loading spinner/indicator
                self._draw_loading_indicator(surface, x_offset)
                return
            else:
                # Try synchronous load as fallback (blocks but ensures display)
                try:
                    if os.path.exists(filepath):
                        img = pygame.image.load(filepath)
                        # Scale to fit
                        sw, sh = surface.get_size()
                        iw, ih = img.get_size()
                        scale = min(sw/iw, sh/ih)
                        new_size = (int(iw*scale), int(ih*scale))
                        img = pygame.transform.scale(img, new_size)
                        with self._cache_lock:
                            self.image_cache[filepath] = img
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
                    return

        if img:
            rect = img.get_rect(center=surface.get_rect().center)
            rect.x += x_offset
            surface.blit(img, rect)

    def _draw_loading_indicator(self, surface, x_offset):
        """Draw a loading spinner when image is being loaded asynchronously."""
        width, height = surface.get_size()
        center_x = width // 2 + x_offset
        center_y = height // 2
        
        # Animated spinner using time
        angle = (pygame.time.get_ticks() // 50) % 360
        
        # Draw spinning arc segments
        radius = 30
        for i in range(8):
            segment_angle = angle + i * 45
            alpha = 255 - (i * 28)  # Fade trail
            
            # Calculate segment position
            import math
            rad = math.radians(segment_angle)
            x = center_x + int(radius * math.cos(rad))
            y = center_y + int(radius * math.sin(rad))
            
            # Draw dot
            color = (255, 255, 255, max(50, alpha))
            pygame.draw.circle(surface, color[:3], (x, y), 4)
        
        # Draw "Loading..." text
        loading_text = self.font.render("Loading...", True, (200, 200, 200))
        text_rect = loading_text.get_rect(center=(center_x, center_y + 50))
        surface.blit(loading_text, text_rect)

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

