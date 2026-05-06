"""
Caso de uso: Ejecutar backup, restauración y validación.
"""

import threading
import queue
from datetime import datetime
from domain.models import BackupRecord, BackupStatus, ConnectionConfig
from application.services.connection_service import ConnectionService
from application.services.validation_service import ValidationService
from infrastructure.logger import SafeBridgeLogger


class BackupProcess:
    """Clase que orquesta el backup en un hilo separado."""

    def __init__(self, config: ConnectionConfig, db_name: str, output_path: str, logger: SafeBridgeLogger):
        self.config = config
        self.db_name = db_name
        self.output_path = output_path
        self.logger = logger
        self.queue = queue.Queue()
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        try:
            connector = ConnectionService.get_connector(self.config)
            self.logger.info(f"Iniciando backup de {self.db_name} -> {self.output_path}")
            connector.backup(self.db_name, self.output_path)
            self.logger.info("Backup generado correctamente.")

            # Validación automática
            self.logger.info("Iniciando validación automática...")
            temp_db = f"tmp_val_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            ValidationService.validate_backup(connector, self.output_path, temp_db, self.logger)
            self.logger.info("Validación completada con éxito. Base temporal eliminada.")
            self.queue.put(("success", "Backup y validación exitosos."))
        except Exception as e:
            self.logger.error(f"Error en el proceso: {str(e)}")
            self.queue.put(("error", str(e)))