import sqlite3
import os
from typing import Any, Optional

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
            # Store everything as string for simplicity, or handle types
            cursor.execute('''
                INSERT OR REPLACE INTO menu_settings (key, value)
                VALUES (?, ?)
            ''', (key, str(value)))
            if commit:
                self.conn.commit()
        except Exception as e:
            print(f"Error setting setting {key}: {e}")

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
            self.conn.commit()
            print("Settings reset to defaults.")
        except Exception as e:
            print(f"Error resetting settings: {e}")
