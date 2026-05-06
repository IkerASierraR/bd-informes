"""
Caso de uso: Validación de backups (restauración temporal y verificación).
"""

from infrastructure.logger import SafeBridgeLogger


class ValidationService:
    @staticmethod
    def validate_backup(connector, backup_file: str, temp_db: str, logger: SafeBridgeLogger):
        logger.info(f"Creando base de datos temporal '{temp_db}'...")
        connector.create_temp_database(temp_db)
        try:
            logger.info(f"Restaurando backup en '{temp_db}'...")
            connector.restore(backup_file, temp_db)
            logger.info("Verificando existencia de tablas...")
            if not connector.verify_tables(temp_db):
                raise RuntimeError("No se encontraron tablas en la restauración.")
        finally:
            logger.info(f"Eliminando base de datos temporal '{temp_db}'...")
            connector.drop_database(temp_db)