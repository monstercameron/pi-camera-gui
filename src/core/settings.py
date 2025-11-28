import json
from os import path, makedirs
from typing import Dict, Any, Tuple
from src.core.database import DatabaseManager

class SettingsManager:
    def __init__(self, settings_file: str = 'home/config/camerasettings.json', menus_file: str = 'home/config/menusettings.json'):
        self.settings_file = settings_file
        self.menus_file = menus_file
        self.settings: Dict[str, Any] = {}
        self.menus: Dict[str, Any] = {}
        self.db = DatabaseManager()

    def load(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        self.settings = self._open_settings(self.settings_file)
        self.menus = self._open_settings(self.menus_file)
        
        # Overlay DB values onto menus
        self._apply_db_values()
        
        self._ensure_dcim_folder(self.settings)
        return self.settings, self.menus

    def save(self):
        self._save_settings(self.settings_file, self.settings)
        # Save menu changes to DB instead of JSON
        self._save_menus_to_db()

    def reset(self):
        """Reset all menu settings to defaults (clears DB)"""
        self.db.reset_settings()
        # Reload defaults from JSON
        self.menus = self._open_settings(self.menus_file)
        return self.menus

    def _apply_db_values(self):
        if 'menus' not in self.menus:
            return
            
        for page in self.menus['menus']:
            if 'options' in page:
                for option in page['options']:
                    self._apply_single_setting(option)

    def _apply_single_setting(self, option):
        key = option.get('name')
        if not key: return
        
        db_value = self.db.get_setting(key)
        if db_value is not None:
            # Convert type based on current value or option type
            current_value = option.get('value')
            
            # Handle boolean
            if isinstance(current_value, bool):
                option['value'] = (str(db_value).lower() == 'true')
            # Handle int
            elif isinstance(current_value, int):
                try:
                    option['value'] = int(db_value)
                except: pass
            # Handle float
            elif isinstance(current_value, float):
                try:
                    option['value'] = float(db_value)
                except: pass
            # Handle string/default
            else:
                option['value'] = db_value

    def _save_menus_to_db(self):
        if 'menus' not in self.menus:
            return
            
        for page in self.menus['menus']:
            if 'options' in page:
                for option in page['options']:
                    key = option.get('name')
                    value = option.get('value')
                    # Only save if key exists and value is not None
                    if key and value is not None:
                        self.db.set_setting(key, value)

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
