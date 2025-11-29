import json
from os import path, makedirs
from typing import Dict, Any, Tuple, List
from src.core.database import DatabaseManager

class SettingsManager:
    # Camera settings that should be reset to "auto" when switching to auto mode
    AUTO_MODE_DEFAULTS = {
        "shutter": 0,         # 0 = auto shutter
        "iso": 0,             # 0 = auto ISO
        "awb": "auto",        # Auto white balance
        "exposure": "auto",   # Auto exposure mode
        "exposurecomp": 0,    # Neutral exposure compensation
        "saturation": 0,      # Neutral saturation
        "brightness": 50,     # Default brightness
        "contrast": 0,        # Neutral contrast
        "sharpness": 0,       # Neutral sharpness
    }
    
    # Settings that are mode-specific (saved per mode)
    MODE_SPECIFIC_SETTINGS = [
        "shutter", "iso", "awb", "exposure", "exposurecomp",
        "saturation", "brightness", "contrast", "sharpness",
        "imageeffect"
    ]

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

    def save_mode_settings(self, mode: str, menus: Dict[str, Any]):
        """Save current mode-specific camera settings to the database."""
        settings_to_save = {}
        
        for setting_name in self.MODE_SPECIFIC_SETTINGS:
            option = self._find_option_in_menus(menus, setting_name)
            if option and 'value' in option:
                settings_to_save[setting_name] = option['value']
        
        if settings_to_save:
            self.db.save_mode_settings(mode, settings_to_save)
            print(f"Saved settings for mode '{mode}': {settings_to_save}")

    def load_mode_settings(self, mode: str, menus: Dict[str, Any], camera: Any = None):
        """Load mode-specific settings from the database and apply to menus and camera."""
        if mode == "auto":
            # Auto mode uses predefined defaults
            settings_to_apply = self.AUTO_MODE_DEFAULTS.copy()
            print(f"Loading AUTO mode defaults: {settings_to_apply}")
        else:
            # Load from DB for other modes
            settings_to_apply = self.db.get_all_mode_settings(mode)
            # Convert types back from strings
            settings_to_apply = self._convert_db_settings(settings_to_apply)
            print(f"Loaded settings for mode '{mode}': {settings_to_apply}")
        
        # Apply to menus
        for setting_name, value in settings_to_apply.items():
            option = self._find_option_in_menus(menus, setting_name)
            if option:
                option['value'] = value
                # Apply to camera
                if camera:
                    directory = camera.directory()
                    if setting_name in directory:
                        print(f"Applying {setting_name} = {value}")
                        directory[setting_name](value=value)
    
    def _convert_db_settings(self, settings: Dict[str, str]) -> Dict[str, Any]:
        """Convert string values from DB to appropriate types."""
        converted = {}
        for key, value in settings.items():
            # Try int first
            try:
                converted[key] = int(value)
                continue
            except ValueError:
                pass
            # Try float
            try:
                converted[key] = float(value)
                continue
            except ValueError:
                pass
            # Keep as string
            converted[key] = value
        return converted
    
    def _find_option_in_menus(self, menus: Dict[str, Any], setting_name: str) -> Dict[str, Any]:
        """Find an option by name in the menus structure (searches nested groups)."""
        if 'menus' not in menus:
            return None
            
        def search_options(options: List[Dict]) -> Dict[str, Any]:
            for option in options:
                if option.get('name') == setting_name:
                    return option
                # Search in nested options (groups)
                if 'options' in option and isinstance(option['options'], list):
                    # Check if it's a group (options is a list of dicts with 'name')
                    if option['options'] and isinstance(option['options'][0], dict) and 'name' in option['options'][0]:
                        found = search_options(option['options'])
                        if found:
                            return found
            return None
        
        for page in menus['menus']:
            if 'options' in page:
                found = search_options(page['options'])
                if found:
                    return found
        
        return None

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
