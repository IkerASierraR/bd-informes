"""
Sistema de logging con soporte para archivo y terminal en tiempo real.
"""

import logging
import os
from datetime import datetime
from typing import Callable


class SafeBridgeLogger:
    def __init__(self, log_dir: str = "logs", terminal_callback: Callable = None):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, f"safebridge_{datetime.now().strftime('%Y%m%d')}.log")

        self.logger = logging.getLogger("SafeBridge")
        self.logger.setLevel(logging.DEBUG)

        # Handler para archivo
        fh = logging.FileHandler(self.log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # Callback para terminal en UI
        self.terminal_callback = terminal_callback

    def log(self, level: str, message: str):
        getattr(self.logger, level.lower())(message)
        if self.terminal_callback:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.terminal_callback(f"[{timestamp}] {level.upper()}: {message}")

    def info(self, msg): self.log("INFO", msg)
    def error(self, msg): self.log("ERROR", msg)
    def debug(self, msg): self.log("DEBUG", msg)
    def warning(self, msg): self.log("WARNING", msg)