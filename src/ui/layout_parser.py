import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
import os

class LayoutParser:
    def __init__(self, theme_config: Dict[str, Any] = None, layout_dir: str = "src/ui/layouts"):
        self.layout_dir = layout_dir
        self.theme_config = theme_config or {}
        self.main_layout = None  # The unified main.xml root
        self.file_timestamp = 0
        self.current_mode_name = "default"
        self._id_cache: Dict[str, Dict[str, Any]] = {}  # Cache per mode
        self._config_cache: Dict[str, Dict[str, Any]] = {}  # Cache per mode
        self._style_cache: Dict[str, Any] = {}  # Global styles from main.xml
        self._animation_cache: Dict[str, Any] = {}  # Global animations
        self._template_cache: Dict[str, Any] = {}  # Templates for reuse
        self._behavior_cache: Dict[str, Dict[str, Any]] = {}  # Behavior config per mode
        
        # For backwards compatibility - track "old" layouts too
        self.layouts: Dict[str, Any] = {}
        self.file_timestamps: Dict[str, float] = {}
        self.current_layout_name = "default"
        
        # Try to load unified main.xml first, fallback to individual files
        self._load_main_layout()
    
    def _load_main_layout(self) -> bool:
        """Load the unified main.xml layout file."""
        path = os.path.join(self.layout_dir, "main.xml")
        
        if not os.path.exists(path):
            # Fallback to loading default.xml
            self._load_layout("default")
            return False
        
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            self.main_layout = root
            self.file_timestamp = os.path.getmtime(path)
            
            # Parse global style element
            style_elem = root.find('style')
            if style_elem is not None:
                self._parse_global_style(style_elem)
            
            # Parse templates
            for template_elem in root.findall('template'):
                template_id = template_elem.get('id')
                if template_id:
                    self._template_cache[template_id] = template_elem
            
            # Parse global config (fallback defaults)
            config_elem = root.find('config')
            if config_elem is not None:
                self._parse_config_for_mode("default", config_elem)
            
            # Parse each mode
            for mode_elem in root.findall('mode'):
                mode_name = mode_elem.get('name')
                if mode_name:
                    self._parse_mode(mode_name, mode_elem)
            
            print(f"Loaded unified layout: main.xml")
            return True
        except Exception as e:
            print(f"Error loading main.xml: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to loading default.xml
            self._load_layout("default")
            return False

    def _parse_global_style(self, style_elem):
        """Parse global style element for variables and animations."""
        # Parse var elements
        for var_elem in style_elem.findall('var'):
            var_name = var_elem.get('name')
            var_value = var_elem.get('value')
            if var_name and var_value:
                if var_value.startswith('@'):
                    resolved = self._resolve_theme_variable(var_value[1:])
                    if resolved is not None:
                        self._style_cache[var_name] = resolved
                    else:
                        self._style_cache[var_name] = var_value
                else:
                    self._style_cache[var_name] = self._parse_value(var_value)
        
        # Parse animation elements
        for anim_elem in style_elem.findall('animation'):
            anim_name = anim_elem.get('name')
            if anim_name:
                duration = anim_elem.get('duration', '100')
                if isinstance(duration, str) and duration.startswith('@'):
                    resolved = self._resolve_theme_variable(duration[1:])
                    duration = resolved if resolved is not None else 100
                else:
                    duration = self._parse_value(duration)
                
                self._animation_cache[anim_name] = {
                    'duration': int(duration) if duration else 100,
                    'easing': anim_elem.get('easing', 'linear')
                }

    def _parse_mode(self, mode_name: str, mode_elem):
        """Parse a mode element and cache its containers."""
        # Initialize caches for this mode
        self._id_cache[mode_name] = {}
        
        # Parse mode-specific config
        config_elem = mode_elem.find('config')
        if config_elem is not None:
            self._parse_config_for_mode(mode_name, config_elem)
            
            # Parse behavior element
            behavior_elem = config_elem.find('behavior')
            if behavior_elem is not None:
                self._behavior_cache[mode_name] = self._parse_attributes(behavior_elem.attrib, mode_name)
        
        # Parse containers
        for container_elem in mode_elem.findall('container'):
            eid = container_elem.get('id')
            if eid:
                self._id_cache[mode_name][eid] = self._parse_attributes(container_elem.attrib, mode_name)
        
        # Handle <use template="..."> elements - copy template containers
        for use_elem in mode_elem.findall('use'):
            template_name = use_elem.get('template')
            if template_name and template_name in self._template_cache:
                template = self._template_cache[template_name]
                for container_elem in template.findall('container'):
                    eid = container_elem.get('id')
                    if eid:
                        self._id_cache[mode_name][eid] = self._parse_attributes(container_elem.attrib, mode_name)

    def _parse_config_for_mode(self, mode_name: str, config_elem):
        """Parse config element for a specific mode."""
        config = {}
        
        # Get defaults from theme config
        sizes = self.theme_config.get("theme", {}).get("sizes", {})
        if not sizes:
            sizes = self.theme_config.get("sizes", {})
        default_widths = {
            'level_0': sizes.get('level_0_width', 200),
            'level_1': sizes.get('level_1_width', 260),
            'level_2': sizes.get('level_2_width', 260),
            'collapsed': sizes.get('collapsed_width', 60)
        }
        
        widths_elem = config_elem.find('widths')
        if widths_elem is not None:
            config['widths'] = {}
            for key in ['level_0', 'level_1', 'level_2', 'collapsed']:
                val = widths_elem.get(key, str(default_widths.get(key, 200)))
                if isinstance(val, str) and val.startswith('@'):
                    resolved = self._resolve_theme_variable(val[1:])
                    config['widths'][key] = int(resolved) if resolved is not None else default_widths.get(key, 200)
                else:
                    config['widths'][key] = int(val)
        else:
            config['widths'] = default_widths
        
        # Animation
        default_animation = 100
        if "display" in self.theme_config:
            default_animation = self.theme_config["display"].get("animation_duration", 100)
        
        anim_elem = config_elem.find('animation')
        if anim_elem is not None:
            duration_val = anim_elem.get('duration', str(default_animation))
            if isinstance(duration_val, str) and duration_val.startswith('@'):
                resolved = self._resolve_theme_variable(duration_val[1:])
                duration = int(resolved) if resolved is not None else default_animation
            else:
                duration = int(duration_val)
            config['animation'] = {'duration': duration}
        else:
            config['animation'] = {'duration': default_animation}
        
        self._config_cache[mode_name] = config

    def get_theme_value(self, category: str, key: str, default: Any = None) -> Any:
        """Get a value from the theme config (colors or sizes)."""
        if category in self.theme_config and key in self.theme_config[category]:
            return self.theme_config[category][key]
        return default

    def _resolve_theme_variable(self, var_name: str) -> Any:
        """Resolve a @variable reference from theme_config."""
        # Search in theme.colors (nested structure from settings)
        if "theme" in self.theme_config:
            theme = self.theme_config["theme"]
            if "colors" in theme and var_name in theme["colors"]:
                return theme["colors"][var_name]
            if "sizes" in theme and var_name in theme["sizes"]:
                return theme["sizes"][var_name]
        # Search in top-level colors (if theme_config is just the theme dict)
        if "colors" in self.theme_config and var_name in self.theme_config["colors"]:
            return self.theme_config["colors"][var_name]
        # Search in top-level sizes
        if "sizes" in self.theme_config and var_name in self.theme_config["sizes"]:
            return self.theme_config["sizes"][var_name]
        # Search in display (for animation_duration etc)
        if "display" in self.theme_config and var_name in self.theme_config["display"]:
            return self.theme_config["display"][var_name]
        return None

    def load_layout(self, layout_name: str):
        """Switch to a specific mode/layout."""
        normalized_name = layout_name.lower().replace(" ", "_")
        
        # If using unified layout and mode exists
        if self.main_layout is not None and normalized_name in self._id_cache:
            self.current_mode_name = normalized_name
            self.current_layout_name = normalized_name
            return
        
        # Fallback to loading individual file (backwards compat)
        if normalized_name not in self.layouts:
            if not self._load_layout(normalized_name):
                self.current_layout_name = "default"
                self.current_mode_name = "default"
                return
        
        self.current_layout_name = normalized_name
        self.current_mode_name = normalized_name

    def _load_layout(self, name: str) -> bool:
        """Load an individual layout file (backwards compatibility)."""
        filename = f"{name}.xml"
        path = os.path.join(self.layout_dir, filename)
        
        if not os.path.exists(path):
            return False
            
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            self.layouts[name] = root
            self.file_timestamps[name] = os.path.getmtime(path)
            
            # Initialize caches
            if name not in self._id_cache:
                self._id_cache[name] = {}
            if name not in self._config_cache:
                self._config_cache[name] = {}
            
            # Parse style
            style_elem = root.find('style')
            if style_elem is not None:
                self._parse_global_style(style_elem)
            
            # Parse config
            config_elem = root.find('config')
            if config_elem is not None:
                self._parse_config_for_mode(name, config_elem)
            
            # Cache containers
            for elem in root.iter():
                eid = elem.get('id')
                if eid:
                    self._id_cache[name][eid] = self._parse_attributes(elem.attrib, name)
            
            print(f"Loaded layout: {name}")
            return True
        except Exception as e:
            print(f"Error loading layout {name}: {e}")
            return False

    def _parse_attributes(self, attribs: Dict[str, str], mode_name: str = None) -> Dict[str, Any]:
        """Parse and convert attribute values to appropriate types."""
        parsed = {}
        
        for key, value in attribs.items():
            if isinstance(value, str) and value.startswith("@"):
                var_name = value[1:]
                resolved = None
                
                # Check global style cache first
                if var_name in self._style_cache:
                    resolved = self._style_cache[var_name]
                else:
                    resolved = self._resolve_theme_variable(var_name)
                
                if resolved is not None:
                    parsed[key] = resolved
                else:
                    parsed[key] = self._parse_value(value)
            else:
                parsed[key] = self._parse_value(value)
        return parsed

    def _parse_value(self, value: str) -> Any:
        """Convert string value to appropriate type."""
        if value is None:
            return None
        
        # Boolean values
        if isinstance(value, str):
            if value.lower() == 'true':
                return True
            if value.lower() == 'false':
                return False
        
        try:
            return int(value)
        except ValueError:
            pass
        
        try:
            return float(value)
        except ValueError:
            pass
        
        if value.endswith('%'):
            return value
        
        return value

    def get_config(self) -> Dict[str, Any]:
        """Get the config for the current mode."""
        mode = self.current_mode_name
        if mode in self._config_cache:
            return self._config_cache[mode]
        
        # Fallback to default
        if "default" in self._config_cache:
            return self._config_cache["default"]
        
        sizes = self.theme_config.get("theme", {}).get("sizes", {})
        return {
            'widths': {
                'level_0': sizes.get('level_0_width', 200),
                'level_1': sizes.get('level_1_width', 260),
                'level_2': sizes.get('level_2_width', 260),
                'collapsed': sizes.get('collapsed_width', 60)
            },
            'animation': {'duration': self.theme_config.get("display", {}).get("animation_duration", 100)}
        }

    def get_behavior(self) -> Dict[str, Any]:
        """Get behavior config for current mode."""
        return self._behavior_cache.get(self.current_mode_name, {})

    def get_animation(self, name: str) -> Dict[str, Any]:
        """Get animation config by name."""
        if name in self._animation_cache:
            return self._animation_cache[name]
        return {
            'duration': self.get_animation_duration(),
            'easing': 'linear'
        }

    def get_widths(self) -> Dict[str, int]:
        """Get the width configuration for the current mode."""
        config = self.get_config()
        return config.get('widths', {
            'level_0': 200, 'level_1': 260, 'level_2': 260, 'collapsed': 60
        })

    def get_animation_duration(self) -> int:
        """Get the animation duration for the current mode."""
        config = self.get_config()
        return config.get('animation', {}).get('duration', 100)

    def get_element_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        """Find an element by ID in the current mode."""
        mode = self.current_mode_name
        
        # Check mode-specific cache
        if mode in self._id_cache and element_id in self._id_cache[mode]:
            return self._id_cache[mode][element_id]
        
        # Fallback to default mode
        if "default" in self._id_cache and element_id in self._id_cache["default"]:
            return self._id_cache["default"][element_id]
        
        return None

    def check_for_updates(self):
        """Check if main.xml has changed and reload."""
        path = os.path.join(self.layout_dir, "main.xml")
        
        if os.path.exists(path):
            try:
                current_mtime = os.path.getmtime(path)
                if current_mtime > self.file_timestamp:
                    print("Reloading main.xml")
                    self._load_main_layout()
            except OSError:
                pass

    def get_layout_structure(self) -> Dict[str, Any]:
        """Returns a simplified dictionary representation of the layout."""
        if self.main_layout is not None:
            return self._parse_element(self.main_layout)
        return {}
