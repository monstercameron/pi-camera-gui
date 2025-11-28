import sqlite3
import os
from typing import Any, Optional

class DatabaseManager:
    def __init__(self, db_path: str = 'home/config/settings.db'):
        self.db_path = db_path
        self._ensure_dir()
        self._init_db()

    def _ensure_dir(self):
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                print(f"Error creating database directory {directory}: {e}")

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS menu_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            print(f"Database initialization error: {e}")

    def get_setting(self, key: str) -> Optional[str]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM menu_settings WHERE key = ?', (key,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error getting setting {key}: {e}")
            return None

    def set_setting(self, key: str, value: Any):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Store everything as string for simplicity, or handle types
                cursor.execute('''
                    INSERT OR REPLACE INTO menu_settings (key, value)
                    VALUES (?, ?)
                ''', (key, str(value)))
                conn.commit()
        except Exception as e:
            print(f"Error setting setting {key}: {e}")

    def reset_settings(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM menu_settings')
                conn.commit()
            print("Settings reset to defaults.")
        except Exception as e:
            print(f"Error resetting settings: {e}")
