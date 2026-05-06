"""
Clase base abstracta para conectores de bases de datos.
Define la interfaz común.
"""

from abc import ABC, abstractmethod
from typing import List


class DatabaseConnector(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def test_connection(self) -> bool:
        """Prueba la conectividad. Lanza excepción si falla."""
        pass

    @abstractmethod
    def get_databases(self) -> List[str]:
        """Devuelve lista de bases de datos disponibles."""
        pass

    @abstractmethod
    def backup(self, database: str, output_path: str) -> bool:
        """Genera backup de la base de datos en la ruta especificada."""
        pass

    @abstractmethod
    def restore(self, backup_file: str, temp_db: str) -> bool:
        """Restaura un backup en una base de datos temporal."""
        pass

    @abstractmethod
    def create_temp_database(self, temp_db: str) -> bool:
        """Crea una base de datos temporal para pruebas."""
        pass

    @abstractmethod
    def drop_database(self, temp_db: str) -> bool:
        """Elimina la base de datos temporal."""
        pass

    @abstractmethod
    def verify_tables(self, temp_db: str) -> bool:
        """Verifica que la base temporal contenga tablas (estructura básica)."""
        pass