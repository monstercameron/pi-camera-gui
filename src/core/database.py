import sqlite3
import os
from typing import Any, Optional, Dict, List

class DatabaseManager:
    def __init__(self, db_path: str = 'home/config/settings.db'):
        self.db_path = db_path
        self._ensure_dir()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def _ensure_dir(self):
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                print(f"Error creating database directory {directory}: {e}")

    def _init_db(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            # New table for mode-specific settings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mode_settings (
                    mode TEXT,
                    key TEXT,
                    value TEXT,
                    PRIMARY KEY (mode, key)
                )
            ''')
            self.conn.commit()
        except Exception as e:
            print(f"Database initialization error: {e}")

    def get_setting(self, key: str) -> Optional[str]:
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT value FROM menu_settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting setting {key}: {e}")
            return None

    def set_setting(self, key: str, value: Any, commit: bool = True):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO menu_settings (key, value)
                VALUES (?, ?)
            ''', (key, str(value)))
            if commit:
                self.conn.commit()
        except Exception as e:
            print(f"Error setting setting {key}: {e}")

    def get_mode_setting(self, mode: str, key: str) -> Optional[str]:
        """Get a setting value for a specific camera mode."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT value FROM mode_settings WHERE mode = ? AND key = ?', (mode, key))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting mode setting {mode}.{key}: {e}")
            return None

    def set_mode_setting(self, mode: str, key: str, value: Any, commit: bool = True):
        """Set a setting value for a specific camera mode."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO mode_settings (mode, key, value)
                VALUES (?, ?, ?)
            ''', (mode, key, str(value)))
            if commit:
                self.conn.commit()
        except Exception as e:
            print(f"Error setting mode setting {mode}.{key}: {e}")

    def get_all_mode_settings(self, mode: str) -> Dict[str, str]:
        """Get all settings for a specific camera mode."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT key, value FROM mode_settings WHERE mode = ?', (mode,))
            results = cursor.fetchall()
            return {row[0]: row[1] for row in results}
        except Exception as e:
            print(f"Error getting all mode settings for {mode}: {e}")
            return {}

    def save_mode_settings(self, mode: str, settings: Dict[str, Any]):
        """Save multiple settings for a mode at once."""
        try:
            cursor = self.conn.cursor()
            for key, value in settings.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO mode_settings (mode, key, value)
                    VALUES (?, ?, ?)
                ''', (mode, key, str(value)))
            self.conn.commit()
        except Exception as e:
            print(f"Error saving mode settings for {mode}: {e}")

    def commit(self):
        """Manually commit changes to the database."""
        if self.conn:
            try:
                self.conn.commit()
            except Exception as e:
                print(f"Error committing changes: {e}")

    def reset_settings(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM menu_settings')
            cursor.execute('DELETE FROM mode_settings')
            self.conn.commit()
            print("Settings reset to defaults.")
        except Exception as e:
            print(f"Error resetting settings: {e}")
