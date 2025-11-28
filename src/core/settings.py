import json
from os import path, makedirs
from typing import Dict, Any, Tuple

class SettingsManager:
    def __init__(self, settings_file: str = 'src/core/camerasettings.json', menus_file: str = 'src/core/menusettings.json'):
        self.settings_file = settings_file
        self.menus_file = menus_file
        self.settings: Dict[str, Any] = {}
        self.menus: Dict[str, Any] = {}

    def load(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        self.settings = self._open_settings(self.settings_file)
        self.menus = self._open_settings(self.menus_file)
        self._ensure_dcim_folder(self.settings)
        return self.settings, self.menus

    def save(self):
        self._save_settings(self.settings_file, self.settings)
        self._save_settings(self.menus_file, self.menus)

    def _save_settings(self, file_path: str, data: Dict[str, Any]):
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving settings to {file_path}: {e}")

    def _open_settings(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error opening settings from {file_path}: {e}")
            return {}

    def _ensure_dcim_folder(self, settings: Dict[str, Any]):
        try:
            if 'files' in settings and 'path' in settings['files']:
                folder_path = settings['files']['path']
                if not path.exists(folder_path):
                    makedirs(folder_path)
                    print(f"Created DCIM folder: {folder_path}")
        except Exception as e:
            print(f"Error checking DCIM folder: {e}")
