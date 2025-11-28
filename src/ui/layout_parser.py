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
        self._load_layout("default")

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
            print(f"Layout file not found: {path}")
            return False
            
        try:
            tree = ET.parse(path)
            self.layouts[name] = tree.getroot()
            self.file_timestamps[name] = os.path.getmtime(path)
            print(f"Loaded layout: {name}")
            return True
        except Exception as e:
            print(f"Error loading layout {name}: {e}")
            return False

    def get_element_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        """
        Finds an element by ID in the CURRENT layout and returns its attributes.
        """
        root = self.layouts.get(self.current_layout_name)
        if not root:
            return None
            
        for elem in root.iter():
            if elem.get('id') == element_id:
                return self._resolve_variables(elem.attrib)
        return None

    def _resolve_variables(self, attribs: Dict[str, str]) -> Dict[str, Any]:
        """
        Resolves variable references (starting with @) using the theme config.
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
                    resolved[key] = value # Keep original if not found
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
        if not root:
            return {}
        return self._parse_element(root)

    def _parse_element(self, element) -> Dict[str, Any]:
        data = {
            "tag": element.tag,
            "attrib": element.attrib,
            "children": [self._parse_element(child) for child in element]
        }
        return data
