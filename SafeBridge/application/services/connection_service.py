"""
Caso de uso: Probar conexión y conectar.
"""

from domain.models import ConnectionConfig, EngineType
from infrastructure.connectors import (
    MySQLConnector,
    PostgreSQLConnector,
    SQLServerConnector,
    OracleConnector,
    SQLiteConnector
)


class ConnectionService:
    @staticmethod
    def get_connector(config: ConnectionConfig):
        """Devuelve el conector adecuado según el motor."""
        mapping = {
            EngineType.MYSQL: MySQLConnector,
            EngineType.POSTGRESQL: PostgreSQLConnector,
            EngineType.SQLSERVER: SQLServerConnector,
            EngineType.ORACLE: OracleConnector,
            EngineType.SQLITE: SQLiteConnector,
        }
        connector_class = mapping.get(config.engine)
        if not connector_class:
            raise ValueError(f"Motor no soportado: {config.engine}")
        return connector_class(config)

    @staticmethod
    def test_connection(config: ConnectionConfig) -> str:
        """Prueba la conexión y devuelve mensaje de éxito o error."""
        connector = ConnectionService.get_connector(config)
        try:
            connector.test_connection()
            return "Conexión exitosa"
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def get_databases_list(config: ConnectionConfig) -> list[str]:
        """Obtiene la lista de bases de datos usando el conector."""
        connector = ConnectionService.get_connector(config)
        return connector.get_databases()