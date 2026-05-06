<div align="center">

# 🛡️ SafeBridge

### Orquestador Multi-Motor de Respaldos y Validación de Integridad de Bases de Datos

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CI/CD](https://img.shields.io/github/actions/workflow/status/IkerASierraR/bd-informes/ci-cd.yml?label=CI%2FCD&logo=github-actions)](https://github.com/IkerASierraR/bd-informes/actions)
[![Security](https://img.shields.io/badge/Security-Fernet%20AES--128-orange)](https://cryptography.io)
[![University](https://img.shields.io/badge/UPT-FAING--EPIS-red)](https://upt.edu.pe)

**Universidad Privada de Tacna — FAING-EPIS — Ingeniería de Sistemas**  
**Equipo:** BitCraft Solutions | **Desarrollador Principal:** Iker Alberto Sierra Ruiz

</div>

---

## 📋 Tabla de Contenidos

- [¿Qué es SafeBridge?](#-qué-es-safebridge)
- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Requisitos del Sistema](#-requisitos-del-sistema)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso de la Aplicación](#-uso-de-la-aplicación)
- [Variables de Entorno](#-variables-de-entorno)
- [Despliegue](#-despliegue)
- [Pipeline CI/CD](#-pipeline-cicd)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Contribución](#-contribución)
- [Equipo](#-equipo)
- [Licencia](#-licencia)

---

## 🛡️ ¿Qué es SafeBridge?

**SafeBridge** es una aplicación de escritorio desarrollada en Python que resuelve uno de los problemas más críticos y silenciosos en la administración de bases de datos: **los backups que nadie ha probado**.

> *"Un backup que no se ha probado no es un backup, es una esperanza."*

La mayoría de los sistemas de respaldo generan el archivo de backup y dan el proceso por terminado. SafeBridge va un paso más allá: **restaura automáticamente cada backup en una base de datos temporal (sandbox)**, verifica su integridad estructural, y descarta el entorno de prueba, todo sin afectar la base de datos de producción.

### El Problema que Resuelve

```
Situación Actual (Sin SafeBridge):
  ✅ Backup generado → ❓ ¿Es restaurable? → 🔥 Desastre = NO LO SABEMOS

Con SafeBridge:
  ✅ Backup generado → ✅ Restaurado en sandbox → ✅ Integridad verificada → ✅ VALIDADO
```

---

## ✨ Características Principales

| Característica | Descripción |
|----------------|-------------|
| 🔌 **Multi-Motor** | Soporte para SQL Server, MySQL, PostgreSQL, Oracle y SQLite |
| 🔄 **Validación Automática** | Restaura cada backup en base temporal y verifica tablas |
| 🔐 **Cifrado Fernet** | Credenciales cifradas con AES-128-CBC + HMAC-SHA256 |
| ⚡ **Proceso Asíncrono** | Backup y validación en hilo separado, UI siempre responsiva |
| 📝 **Logging Detallado** | Registro por severidad (INFO/WARNING/ERROR) con timestamps |
| 🏗️ **Clean Architecture** | Separación estricta en capas: UI, Aplicación, Dominio, Infraestructura |
| 💉 **Inyección de Dependencias** | Factory pattern para selección de conector según motor |
| 🖥️ **UI Moderna** | Interfaz CustomTkinter con soporte para tema oscuro/claro |

---

## 🏗️ Arquitectura del Sistema

SafeBridge implementa **Clean Architecture (Robert C. Martin)** con cuatro capas bien definidas:

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                    │
│         LoginWindow │ DashboardWindow │ TerminalWidget   │
├─────────────────────────────────────────────────────────┤
│                   APPLICATION LAYER                     │
│      BackupProcess │ ConnectionService │ ValidationService│
├─────────────────────────────────────────────────────────┤
│                     DOMAIN LAYER                        │
│        ConnectionConfig │ BackupRecord │ EngineType       │
├─────────────────────────────────────────────────────────┤
│                 INFRASTRUCTURE LAYER                    │
│  MySQLConnector │ PostgreSQLConnector │ SQLServerConnector│
│  OracleConnector │ SQLiteConnector │ Logger │ Security    │
└─────────────────────────────────────────────────────────┘
```

**Principio de Dependencia:** Las flechas de dependencia siempre apuntan hacia adentro. La capa de dominio no conoce nada de la infraestructura o la UI.

---

## 💻 Requisitos del Sistema

### Sistema Operativo
- Windows 10 / Windows 11 (64 bits) — **Recomendado**
- Linux Ubuntu 20.04+ / Debian 11+
- macOS 12+ (Monterey o superior)

### Python
- **Python 3.12+** (obligatorio)
- `pip` actualizado a versión 23+

### Dependencias del Sistema (según motor de BD a usar)

| Motor | Herramienta requerida | Versión | Instalación |
|-------|----------------------|---------|-------------|
| **SQL Server** | ODBC Driver 18 for SQL Server | 18.x | [Microsoft Docs](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server) |
| **SQL Server** | `sqlcmd` utility | 16+ | Incluido en ODBC Driver Tools |
| **MySQL** | `mysqldump` + `mysql` CLI | 8.0+ | Incluido en MySQL Community Server |
| **PostgreSQL** | `pg_dump` + `psql` CLI | 14+ | Incluido en PostgreSQL |
| **Oracle** | Oracle Instant Client | 21.x | [Oracle Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html) |
| **SQLite** | (ninguno externo) | — | Incluido en Python stdlib |

### Hardware Mínimo
- **CPU:** Intel Core i5 de 5.ª generación o equivalente
- **RAM:** 8 GB (16 GB recomendado para motores de BD locales)
- **Disco:** 20 GB libres (excluyendo el espacio para backups)
- **Red:** Conexión estable si se usan motores remotos

---

## 🚀 Instalación

### Método 1: Desde el Código Fuente (Desarrollo)

```bash
# 1. Clonar el repositorio
git clone https://github.com/IkerASierraR/bd-informes.git
cd bd-informes/SafeBridge

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar el entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Actualizar pip
pip install --upgrade pip

# 5. Instalar dependencias
pip install -r requirements.txt

# 6. Ejecutar la aplicación
python main.py
```

### Método 2: Ejecutable Standalone (Windows)

Descarga el instalador `SafeBridge-v1.0-Setup.exe` desde la [sección de Releases](https://github.com/IkerASierraR/bd-informes/releases/latest).

> ⚠️ **Nota:** El ejecutable incluye todas las dependencias de Python. Sin embargo, aún necesitas instalar los drivers del motor de BD que uses (ODBC Driver 18, mysqldump, pg_dump, etc.) por separado.

### Método 3: Docker (Próximamente en v2.0)

```bash
docker pull bitcraftsolutions/safebridge:latest
docker run -it -v /ruta/backups:/app/backups bitcraftsolutions/safebridge:latest
```

---

## ⚙️ Configuración

### Primer Uso

Al iniciar SafeBridge por primera vez:

1. La aplicación crea automáticamente el directorio `~/.safebridge/`.
2. Se genera la **clave Fernet** en `~/.safebridge/fernet_key.key` (guárdala en un lugar seguro).
3. El archivo de conexiones cifradas `~/.safebridge/connections.json.enc` se crea vacío.
4. Los logs se almacenan en `~/.safebridge/logs/`.

> ⚠️ **IMPORTANTE:** No elimines `fernet_key.key`. Sin esta clave, las conexiones guardadas no pueden descifrarse y deberás reconfigurarlas desde cero.

### Configuración de una Conexión Nueva

En la ventana de Login:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Motor** | Selecciona el motor de BD | `MySQL` |
| **Host** | IP o hostname del servidor | `localhost` o `192.168.1.100` |
| **Puerto** | Puerto TCP del motor | `3306` (MySQL por defecto) |
| **Usuario** | Usuario de la BD | `root` |
| **Contraseña** | Contraseña del usuario | `••••••••` |
| **Base de Datos** | BD inicial (opcional) | `produccion_db` |
| **Service Name** | Solo para Oracle | `ORCL` |

### Puertos por Defecto

| Motor | Puerto Defecto |
|-------|---------------|
| MySQL | 3306 |
| PostgreSQL | 5432 |
| SQL Server | 1433 |
| Oracle | 1521 |
| SQLite | N/A (archivo local) |

---

## 📖 Uso de la Aplicación

### 1. Configurar y Probar Conexión

```
LoginWindow → Seleccionar motor → Ingresar credenciales → "Probar Conexión" → "Guardar"
```

### 2. Ejecutar Backup con Validación

```
DashboardWindow → Seleccionar base de datos → Especificar ruta de destino → "Iniciar Backup y Validar"
```

El proceso automático es:
1. 📤 Genera el archivo de backup en la ruta especificada.
2. 🏗️ Crea base de datos temporal `tmp_val_YYYYMMDDHHMMSS`.
3. 📥 Restaura el backup en la base temporal.
4. ✅ Verifica tablas y estructura de la base restaurada.
5. 🗑️ Elimina la base temporal.
6. 📝 Registra resultado completo en el terminal widget.

### 3. Monitorear en Tiempo Real

El **Terminal Widget** en el Dashboard muestra todos los eventos del proceso con codificación de colores:
- 🟦 **INFO** — Progreso normal del proceso
- 🟡 **WARNING** — Situaciones atípicas no críticas
- 🔴 **ERROR** — Fallos que requieren atención

---

## 🌍 Variables de Entorno

SafeBridge puede configurarse mediante variables de entorno para integraciones CI/CD o despliegues automatizados:

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `SAFEBRIDGE_BACKUP_DIR` | Directorio base para almacenar backups | `~/backups/` |
| `SAFEBRIDGE_LOG_DIR` | Directorio para archivos de log | `~/.safebridge/logs/` |
| `SAFEBRIDGE_KEY_FILE` | Ruta personalizada para la clave Fernet | `~/.safebridge/fernet_key.key` |
| `SAFEBRIDGE_CONNECTIONS_FILE` | Ruta para el archivo de conexiones cifradas | `~/.safebridge/connections.json.enc` |
| `SAFEBRIDGE_LOG_LEVEL` | Nivel mínimo de logging (`INFO`/`WARNING`/`ERROR`) | `INFO` |
| `SAFEBRIDGE_RETENTION_DAYS` | Días de retención de archivos de backup | `30` |

```bash
# Ejemplo de uso en Linux/macOS
export SAFEBRIDGE_BACKUP_DIR="/mnt/nas/backups/"
export SAFEBRIDGE_LOG_LEVEL="WARNING"
python main.py
```

```powershell
# Ejemplo de uso en Windows PowerShell
$env:SAFEBRIDGE_BACKUP_DIR = "D:\backups\"
$env:SAFEBRIDGE_LOG_LEVEL = "WARNING"
python main.py
```

---

## 🚢 Despliegue

### Despliegue Local (Escritorio)

Sigue la guía de [Instalación](#-instalación) — Método 1 o Método 2.

### Despliegue en AWS con Terraform

SafeBridge incluye configuración Terraform para desplegar la infraestructura de soporte en AWS:

```bash
# Prerequisito: Terraform CLI v1.7+ y AWS CLI configurado
cd terraform/

# 1. Inicializar Terraform
terraform init

# 2. Revisar los cambios planificados
terraform plan

# 3. Aplicar la infraestructura
terraform apply

# Al finalizar el proyecto
terraform destroy
```

Los recursos desplegados incluyen:
- **EC2 t3.micro** — Servidor de BD para pruebas de restauración remota.
- **S3 Bucket** — Repositorio de backups validados con cifrado SSE y versionado.
- **Security Group** — Reglas de firewall restrictivas para los puertos de BD.
- **IAM Role** — Permisos mínimos necesarios (Principio de Mínimo Privilegio).

### Generación del Ejecutable (PyInstaller)

```bash
# Instalar PyInstaller
pip install pyinstaller

# Generar ejecutable standalone
pyinstaller --onefile --windowed --name SafeBridge \
  --add-data "assets;assets" \
  --icon assets/icon.ico \
  SafeBridge/main.py

# El ejecutable se genera en dist/SafeBridge.exe
```

---

## 🔄 Pipeline CI/CD

SafeBridge utiliza **GitHub Actions** para automatización de pruebas, análisis de seguridad y releases. Ver [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml).

**Etapas del pipeline:**
1. ✅ **Lint** — `flake8` + `pylint` para calidad de código
2. 🧪 **Tests** — Pruebas unitarias con `pytest`
3. 🔒 **Security Scan** — SonarQube + Snyk/Semgrep para vulnerabilidades
4. 📦 **Build** — Generación de ejecutable con PyInstaller o imagen Docker
5. 🚀 **Release** — Publicación automática en GitHub Releases

---

## 📁 Estructura del Proyecto

```
SafeBridge/
├── main.py                         # Punto de entrada de la aplicación
├── requirements.txt                # Dependencias Python
│
├── domain/                         # Capa de Dominio (entidades puras)
│   ├── __init__.py
│   └── models.py                   # ConnectionConfig, BackupRecord, EngineType
│
├── application/                    # Capa de Aplicación (casos de uso)
│   ├── __init__.py
│   └── services/
│       ├── backup_service.py       # BackupProcess (orquestador principal)
│       ├── connection_service.py   # ConnectionService (Factory de conectores)
│       └── validation_service.py  # ValidationService (validación del sandbox)
│
├── infrastructure/                 # Capa de Infraestructura (detalles técnicos)
│   ├── __init__.py
│   ├── logger.py                   # SafeBridgeLogger (logging dual: archivo + UI)
│   ├── security.py                 # Cifrado/descifrado Fernet de credenciales
│   └── connectors/
│       ├── base_connector.py       # DatabaseConnector (clase abstracta)
│       ├── mysql_connector.py      # Conector MySQL
│       ├── postgresql_connector.py # Conector PostgreSQL
│       ├── sqlserver_connector.py  # Conector SQL Server
│       ├── oracle_connector.py     # Conector Oracle
│       └── sqlite_connector.py    # Conector SQLite
│
└── presentation/                   # Capa de Presentación (UI CustomTkinter)
    ├── __init__.py
    ├── login_window.py             # Ventana de inicio y gestión de conexiones
    ├── dashboard_window.py         # Panel principal de backup/validación
    ├── settings_window.py          # Ventana de configuración
    └── terminal_widget.py          # Widget de consola con logs en tiempo real

terraform/                          # Infraestructura como Código (AWS)
├── main.tf                         # Recursos principales (EC2, S3, VPC)
├── variables.tf                    # Variables configurables
├── outputs.tf                      # Salidas del despliegue
└── terraform.tfvars.example        # Plantilla de variables (sin datos sensibles)

.github/
└── workflows/
    └── ci-cd.yml                   # Pipeline de GitHub Actions
```

---

## 🤝 Contribución

1. Haz un Fork del repositorio.
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`.
3. Realiza tus cambios siguiendo la convención de commits semánticos.
4. Abre un Pull Request hacia `develop` con descripción detallada.
5. Espera la revisión de código y que los checks de CI pasen.

**Convención de commits:**
```
feat(backup): add differential backup support
fix(security): handle empty Fernet key file
docs(readme): update installation steps
ci(actions): add Snyk security scan
```

---

## 👥 Equipo

| Nombre | Rol | Código |
|--------|-----|--------|
| **Iker Alberto Sierra Ruiz** | Desarrollador Principal / Arquitecto | 2023077090 |
| **Julio Samuel Cortez Mamani** | Desarrollador / QA | 2023077283 |

**Institución:** Universidad Privada de Tacna, FAING-EPIS  
**Empresa:** BitCraft Solutions  
**Docente:** Ing. Patrick José Cuadros Quiroga  
**Curso:** Base de Datos II — Ciclo 2026-I

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

<div align="center">

*Hecho con ❤️ por BitCraft Solutions — UPT, Tacna, Perú 🇵🇪*

</div>
