import sqlite3
import shutil
import os
from .base_connector import DatabaseConnector


class SQLiteConnector(DatabaseConnector):
    def __init__(self, config):
        super().__init__(config)
        # En SQLite, host es la ruta del archivo
        self.db_path = config.host

    def test_connection(self):
        if not os.path.isfile(self.db_path):
            raise FileNotFoundError(f"No se encuentra {self.db_path}")
        conn = sqlite3.connect(self.db_path)
        conn.close()
        return True

    def get_databases(self):
        # En SQLite solo hay una "base de datos", el archivo mismo
        return [os.path.splitext(os.path.basename(self.db_path))[0]]

    def backup(self, database, output_path):
        shutil.copy2(self.db_path, output_path)
        return True

    def restore(self, backup_file, temp_db):
        # Para validación, copiamos a un archivo temporal
        temp_path = os.path.join(os.path.dirname(backup_file), f"{temp_db}.db")
        shutil.copy2(backup_file, temp_path)
        self._temp_restore_path = temp_path
        return True

    def create_temp_database(self, temp_db):
        # No es necesario crear; restaurar ya copia
        return True

    def drop_database(self, temp_db):
        if hasattr(self, '_temp_restore_path') and os.path.exists(self._temp_restore_path):
            os.remove(self._temp_restore_path)
        return True

    def verify_tables(self, temp_db):
        temp_path = getattr(self, '_temp_restore_path', None)
        if not temp_path:
            return False
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        return len(tables) > 0