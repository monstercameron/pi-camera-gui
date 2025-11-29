import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
import os

class LayoutParser:
    def __init__(self, theme_config: Dict[str, Any] = None, layout_dir: str = "src/ui/layouts"):
        self.layout_dir = layout_dir
        self.theme_config = theme_config or {}
        self.layouts: Dict[str, Any] = {}
        self.file_timestamps: Dict[str, float] = {}
        self.current_layout_name = "default"
        self._id_cache: Dict[str, Dict[str, Any]] = {}  # Cache for get_element_by_id
        self._config_cache: Dict[str, Dict[str, Any]] = {}  # Cache for layout config
        self._load_layout("default")
    
    def get_theme_value(self, category: str, key: str, default: Any = None) -> Any:
        """Get a value from the theme config (colors or sizes)."""
        if category in self.theme_config and key in self.theme_config[category]:
            return self.theme_config[category][key]
        return default

    def load_layout(self, layout_name: str):
        """Loads a specific layout file if not already loaded."""
        # Normalize name (replace spaces with underscores, lowercase)
        normalized_name = layout_name.lower().replace(" ", "_")
        
        if normalized_name not in self.layouts:
            if not self._load_layout(normalized_name):
                # Fallback to default if specific layout not found
                self.current_layout_name = "default"
                return

        self.current_layout_name = normalized_name

    def _load_layout(self, name: str) -> bool:
        filename = f"{name}.xml"
        path = os.path.join(self.layout_dir, filename)
        
        if not os.path.exists(path):
            print(f"Error loading layout {name}: {os.strerror(2)}: '{path}'")
            return False
            
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            self.layouts[name] = root
            self.file_timestamps[name] = os.path.getmtime(path)
            
            # Initialize caches for this layout
            if name not in self._id_cache:
                self._id_cache[name] = {}
            if name not in self._config_cache:
                self._config_cache[name] = {}
            
            # Parse config element
            config_elem = root.find('config')
            if config_elem is not None:
                self._parse_config(name, config_elem)
            
            # Populate ID cache for containers
            for elem in root.iter():
                eid = elem.get('id')
                if eid:
                    self._id_cache[name][eid] = self._parse_attributes(elem.attrib)
            
            print(f"Loaded layout: {name}")
            return True
        except Exception as e:
            print(f"Error loading layout {name}: {e}")
            return False

    def _parse_config(self, layout_name: str, config_elem):
        """Parse the config element and cache layout-specific settings.
        Uses theme_config values as defaults, XML values override."""
        config = {}
        
        # Get defaults from theme config
        sizes = self.theme_config.get("sizes", {})
        default_widths = {
            'level_0': sizes.get('level_0_width', 200),
            'level_1': sizes.get('level_1_width', 260),
            'level_2': sizes.get('level_2_width', 260),
            'collapsed': sizes.get('collapsed_width', 60)
        }
        
        # Parse widths - XML overrides theme defaults
        widths_elem = config_elem.find('widths')
        if widths_elem is not None:
            config['widths'] = {
                'level_0': int(widths_elem.get('level_0', default_widths['level_0'])),
                'level_1': int(widths_elem.get('level_1', default_widths['level_1'])),
                'level_2': int(widths_elem.get('level_2', default_widths['level_2'])),
                'collapsed': int(widths_elem.get('collapsed', default_widths['collapsed']))
            }
        else:
            config['widths'] = default_widths
        
        # Parse animation - use display.animation_duration as default
        display_config = self.theme_config.get("display", {}) if "display" not in self.theme_config else {}
        # Check parent settings for animation_duration
        default_animation = 100
        if isinstance(self.theme_config, dict):
            # Theme config might be the full settings dict
            if "display" in self.theme_config:
                default_animation = self.theme_config["display"].get("animation_duration", 100)
        
        anim_elem = config_elem.find('animation')
        if anim_elem is not None:
            config['animation'] = {
                'duration': int(anim_elem.get('duration', default_animation))
            }
        else:
            config['animation'] = {'duration': default_animation}
        
        self._config_cache[layout_name] = config

    def _parse_attributes(self, attribs: Dict[str, str]) -> Dict[str, Any]:
        """Parse and convert attribute values to appropriate types.
        Resolves @variable references from theme_config."""
        parsed = {}
        for key, value in attribs.items():
            # Resolve @variable references
            if isinstance(value, str) and value.startswith("@"):
                var_name = value[1:]
                resolved = None
                # Search in colors
                if "colors" in self.theme_config and var_name in self.theme_config["colors"]:
                    resolved = self.theme_config["colors"][var_name]
                # Search in sizes
                elif "sizes" in self.theme_config and var_name in self.theme_config["sizes"]:
                    resolved = self.theme_config["sizes"][var_name]
                # Search in theme root
                elif "theme" in self.theme_config:
                    theme = self.theme_config["theme"]
                    if "colors" in theme and var_name in theme["colors"]:
                        resolved = theme["colors"][var_name]
                    elif "sizes" in theme and var_name in theme["sizes"]:
                        resolved = theme["sizes"][var_name]
                
                if resolved is not None:
                    parsed[key] = resolved
                else:
                    # Keep original if not found
                    parsed[key] = self._parse_value(value)
            else:
                parsed[key] = self._parse_value(value)
        return parsed

    def _parse_value(self, value: str) -> Any:
        """Convert string value to appropriate type."""
        if value is None:
            return None
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Percentage - keep as string for later parsing
        if value.endswith('%'):
            return value
        
        # Return as string
        return value

    def get_config(self) -> Dict[str, Any]:
        """Get the config for the current layout."""
        if self.current_layout_name in self._config_cache:
            return self._config_cache[self.current_layout_name]
        
        # Return defaults from theme config
        sizes = self.theme_config.get("sizes", {})
        return {
            'widths': {
                'level_0': sizes.get('level_0_width', 200),
                'level_1': sizes.get('level_1_width', 260),
                'level_2': sizes.get('level_2_width', 260),
                'collapsed': sizes.get('collapsed_width', 60)
            },
            'animation': {'duration': self.theme_config.get("display", {}).get("animation_duration", 100)}
        }

    def get_widths(self) -> Dict[str, int]:
        """Get the width configuration for the current layout."""
        config = self.get_config()
        return config.get('widths', {
            'level_0': self.get_theme_value('sizes', 'level_0_width', 200),
            'level_1': self.get_theme_value('sizes', 'level_1_width', 260),
            'level_2': self.get_theme_value('sizes', 'level_2_width', 260),
            'collapsed': self.get_theme_value('sizes', 'collapsed_width', 60)
        })

    def get_animation_duration(self) -> int:
        """Get the animation duration for the current layout."""
        config = self.get_config()
        return config.get('animation', {}).get('duration', 100)

    def get_element_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        """
        Finds an element by ID in the CURRENT layout and returns its attributes.
        """
        # Check cache first
        if self.current_layout_name in self._id_cache:
            if element_id in self._id_cache[self.current_layout_name]:
                return self._id_cache[self.current_layout_name][element_id]
        
        # Fallback to iteration (shouldn't happen if cache is working correctly)
        root = self.layouts.get(self.current_layout_name)
        if root is None:
            return None
            
        for elem in root.iter():
            if elem.get('id') == element_id:
                return self._parse_attributes(elem.attrib)
        return None

    def _resolve_variables(self, attribs: Dict[str, str]) -> Dict[str, Any]:
        """
        Resolves variable references (starting with @) using the theme config.
        Deprecated: Use direct values in XML instead.
        """
        resolved = {}
        for key, value in attribs.items():
            if isinstance(value, str) and value.startswith("@"):
                var_name = value[1:]
                # Search in colors and sizes
                found = False
                if "colors" in self.theme_config and var_name in self.theme_config["colors"]:
                    resolved[key] = self.theme_config["colors"][var_name]
                    found = True
                elif "sizes" in self.theme_config and var_name in self.theme_config["sizes"]:
                    resolved[key] = self.theme_config["sizes"][var_name]
                    found = True
                
                if not found:
                    print(f"Warning: Theme variable '{var_name}' not found.")
                    resolved[key] = value  # Keep original if not found
            else:
                resolved[key] = value
        return resolved

    def check_for_updates(self):
        """Checks if the current layout file has changed and reloads it."""
        name = self.current_layout_name
        filename = f"{name}.xml"
        path = os.path.join(self.layout_dir, filename)
        
        if os.path.exists(path):
            try:
                current_mtime = os.path.getmtime(path)
                last_mtime = self.file_timestamps.get(name, 0)
                
                if current_mtime > last_mtime:
                    print(f"Reloading layout: {name}")
                    self._load_layout(name)
            except OSError:
                pass

    def get_layout_structure(self) -> Dict[str, Any]:
        """
        Returns a simplified dictionary representation of the current layout.
        """
        root = self.layouts.get(self.current_layout_name)
        if root is None:
            return {}
        return self._parse_element(root)

    def _parse_element(self, element) -> Dict[str, Any]:
        data = {
            "tag": element.tag,
            "attrib": element.attrib,
            "children": [self._parse_element(child) for child in element]
        }
        return data
