import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
import os

class LayoutParser:
    def __init__(self, layout_dir: str = "src/ui/layouts"):
        self.layout_dir = layout_dir
        self.layouts: Dict[str, Any] = {}
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
                return elem.attrib
        return None

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
