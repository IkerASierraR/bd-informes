"""
Modelos de dominio (entidades y objetos de valor).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EngineType(Enum):
    MYSQL = "MySQL"
    POSTGRESQL = "PostgreSQL"
    SQLSERVER = "SQL Server"
    ORACLE = "Oracle"
    SQLITE = "SQLite"


class BackupStatus(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    VALIDATED = "VALIDATED"


@dataclass
class ConnectionConfig:
    engine: EngineType
    host: str
    port: int
    user: str
    password: str = field(repr=False)
    database: str = ""       # para SQLite es la ruta del archivo
    service_name: str = ""   # Oracle SID o Service Name


@dataclass
class BackupRecord:
    id: int = 0
    database: str = ""
    engine: str = ""
    file_path: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    status: BackupStatus = BackupStatus.SUCCESS
    detail: str = ""