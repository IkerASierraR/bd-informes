<center>

![./media/logo-upt.png](./media/logo-upt.png)

**UNIVERSIDAD PRIVADA DE TACNA**

**FACULTAD DE INGENIERÍA**

**Escuela Profesional de Ingeniería de Sistemas**

**Proyecto: *SafeBridge: Orquestador Multi-Motor de Respaldos y Validación de Integridad***

Curso: *Base de Datos II*

Docente: *Ing. Patrick José Cuadros Quiroga*

Integrantes:

***Sierra Ruiz, Iker Alberto (2023077090)***

***Cortez Mamani, Julio Samuel (2023077283)***

**Empresa / Equipo: BitCraft Solutions**

**Tacna – Perú**

***2026***

</center>

<div style="page-break-after: always; visibility: hidden"></div>

**Sistema: *SafeBridge: Orquestador Multi-Motor de Respaldos y Validación de Integridad***

**Informe FD02 — Roadmap, Características y Gestión del Producto**

**Versión *1.0***

| CONTROL DE VERSIONES | | | | | |
|:---:|---|---|---|---|---|
| Versión | Hecha por | Revisada por | Aprobada por | Fecha | Motivo |
| 1.0 | IASR / JSCM | Ing. P. Cuadros | Ing. P. Cuadros | 06/05/2026 | Versión Original |

<div style="page-break-after: always; visibility: hidden"></div>

---

# ÍNDICE GENERAL

1. [Descripción General del Producto](#1-descripción-general-del-producto)
2. [Características Actuales del Producto](#2-características-actuales-del-producto)
   - [2.1 Conexión Multi-Motor](#21-conexión-multi-motor)
   - [2.2 Validación Asíncrona en Base Temporal](#22-validación-asíncrona-en-base-temporal)
   - [2.3 Cifrado de Credenciales con Fernet](#23-cifrado-de-credenciales-con-fernet)
   - [2.4 Interfaz Gráfica con CustomTkinter](#24-interfaz-gráfica-con-customtkinter)
   - [2.5 Sistema de Logging Detallado](#25-sistema-de-logging-detallado)
   - [2.6 Arquitectura Limpia e Inyección de Dependencias](#26-arquitectura-limpia-e-inyección-de-dependencias)
3. [Roadmap y Futuras Versiones](#3-roadmap-y-futuras-versiones)
4. [Gestión de Tareas con GitHub Projects y Ramas](#4-gestión-de-tareas-con-github-projects-y-ramas)
   - [4.1 Organización en GitHub Projects](#41-organización-en-github-projects)
   - [4.2 Estrategia de Ramas (Branching Strategy)](#42-estrategia-de-ramas-branching-strategy)
   - [4.3 Ciclo de Vida de una Feature](#43-ciclo-de-vida-de-una-feature)
5. [Conclusiones](#5-conclusiones)

<div style="page-break-after: always; visibility: hidden"></div>

---

## 1. Descripción General del Producto

**SafeBridge** es una aplicación de escritorio desarrollada en **Python 3.12+** con interfaz gráfica moderna mediante **CustomTkinter**, diseñada para automatizar de manera confiable el ciclo completo de *backup*, *restauración temporal* y *validación de integridad* de bases de datos heterogéneas.

A diferencia de las soluciones convencionales de respaldo que únicamente generan un archivo `.bak`, `.dump` o `.sql`, SafeBridge cierra el ciclo de confianza probando automáticamente que cada respaldo generado es **efectivamente restaurable**. Esto se logra mediante un entorno **sandbox temporal** en el que se restaura el backup, se verifican las estructuras internas, y se descarta la base temporal sin afectar el entorno productivo.

El producto se enmarca en la filosofía de **continuidad del negocio y recuperación ante desastres (BCDR)**, siendo una herramienta universitaria con proyección hacia entornos profesionales reales.

<div style="page-break-after: always; visibility: hidden"></div>

---

## 2. Características Actuales del Producto

> Esta sección sirve como contenido base para las **GitHub Wikis** del repositorio oficial del proyecto.

### 2.1 Conexión Multi-Motor

SafeBridge implementa soporte para **cinco motores de base de datos** en la versión actual (v1.0):

| Motor | Driver / Librería | Protocolo |
|-------|------------------|-----------|
| **SQL Server** | `pyodbc` + ODBC Driver 18 | TDS / Named Pipes |
| **MySQL** | `mysql-connector-python` | TCP/IP |
| **PostgreSQL** | `psycopg2-binary` | TCP/IP |
| **Oracle DB** | `oracledb` | TCP/IP + TNS |
| **SQLite** | Módulo estándar `sqlite3` | Sistema de archivos local |

La clase abstracta `DatabaseConnector` (en `infrastructure/connectors/base_connector.py`) define la **interfaz común** que cada conector debe implementar:

- `test_connection()` — Verifica la conectividad con el motor.
- `get_databases()` — Lista las bases de datos disponibles.
- `backup(database, output_path)` — Genera el archivo de respaldo.
- `restore(backup_file, temp_db)` — Restaura en la base temporal.
- `create_temp_database(temp_db)` — Crea el sandbox de validación.
- `drop_database(temp_db)` — Elimina el sandbox al concluir.
- `verify_tables(temp_db)` — Verifica la integridad estructural de la restauración.

La selección del conector concreto se realiza mediante **inyección de dependencias** a través de `ConnectionService.get_connector(config: ConnectionConfig)`, que actúa como *Factory* y desacopla completamente el código de negocio de la implementación tecnológica.

### 2.2 Validación Asíncrona en Base Temporal

El proceso de backup y validación se ejecuta en un **hilo de trabajo independiente** (mediante `threading.Thread`), evitando el bloqueo de la interfaz gráfica durante operaciones de larga duración.

El flujo completo es el siguiente:

```
[Usuario solicita backup]
        ↓
[BackupProcess.start() → hilo daemon]
        ↓
[connector.backup(db, output_path)]
        ↓
[ValidationService.validate_backup(connector, backup_file, temp_db)]
        ├─ connector.create_temp_database(temp_db)
        ├─ connector.restore(backup_file, temp_db)
        ├─ connector.verify_tables(temp_db)
        └─ connector.drop_database(temp_db)
        ↓
[queue.put(("success"/"error", mensaje))]
        ↓
[UI actualiza terminal widget con resultado]
```

La comunicación asíncrona entre el hilo de trabajo y la interfaz gráfica se gestiona mediante una cola thread-safe (`queue.Queue`), garantizando la seguridad en la actualización de la UI desde hilos secundarios.

### 2.3 Cifrado de Credenciales con Fernet

Las credenciales de conexión (usuario, contraseña, host, puerto) **nunca se almacenan en texto plano**. SafeBridge implementa cifrado simétrico **Fernet** (basado en AES-128-CBC + HMAC-SHA256) de la librería `cryptography`:

- La **clave Fernet** se genera una única vez y se persiste localmente en `~/.safebridge/fernet_key.key`.
- Las conexiones guardadas se serializan a JSON y se cifran, almacenándose en `~/.safebridge/connections.json.enc`.
- Las funciones `encrypt_data()`, `decrypt_data()`, `save_connections()` y `load_connections()` encapsulan toda la lógica de seguridad en `infrastructure/security.py`.

> **Consideración de seguridad:** La clave Fernet es el activo más crítico del sistema. En versiones futuras se contempla integración con gestores de secretos como AWS Secrets Manager o HashiCorp Vault.

### 2.4 Interfaz Gráfica con CustomTkinter

La capa de presentación utiliza **CustomTkinter ≥ 5.2.0**, que provee widgets modernos con soporte nativo para tema oscuro y claro. Las ventanas principales son:

| Módulo | Descripción |
|--------|-------------|
| `login_window.py` | Pantalla de inicio con selección/creación de perfiles de conexión |
| `dashboard_window.py` | Panel principal con selección de base de datos, ruta de backup y botones de acción |
| `settings_window.py` | Configuración de parámetros de la aplicación (rutas, retención, cifrado) |
| `terminal_widget.py` | Widget de consola incrustado que muestra logs en tiempo real con codificación por colores |

### 2.5 Sistema de Logging Detallado

El módulo `infrastructure/logger.py` implementa `SafeBridgeLogger`, que registra cada evento del proceso con:

- **Nivel de severidad:** `INFO`, `WARNING`, `ERROR`.
- **Marca de tiempo** (timestamp) con precisión de milisegundos.
- **Salida dual:** archivo de log en disco (`~/.safebridge/logs/`) y widget de terminal en la UI.
- **Rotación de logs** por fecha, evitando acumulación indefinida de archivos.

### 2.6 Arquitectura Limpia e Inyección de Dependencias

SafeBridge implementa los principios de **Clean Architecture (Robert C. Martin)**:

```
┌───────────────────────────────────────────┐
│            Presentation Layer             │
│   (CustomTkinter UI — login, dashboard)   │
├───────────────────────────────────────────┤
│            Application Layer             │
│  (BackupProcess, ConnectionService,       │
│   ValidationService)                     │
├───────────────────────────────────────────┤
│              Domain Layer                │
│  (ConnectionConfig, BackupRecord,         │
│   EngineType, BackupStatus)              │
├───────────────────────────────────────────┤
│           Infrastructure Layer           │
│  (DatabaseConnector, MySQLConnector,      │
│   PostgreSQLConnector, SQLServerConnector,│
│   OracleConnector, SQLiteConnector,       │
│   SafeBridgeLogger, security.py)         │
└───────────────────────────────────────────┘
```

La **regla de dependencia** se respeta estrictamente: las capas internas no conocen las externas. La UI invoca casos de uso de la capa de aplicación; los servicios de aplicación interactúan con el dominio e invocan la infraestructura mediante interfaces.

<div style="page-break-after: always; visibility: hidden"></div>

---

## 3. Roadmap y Futuras Versiones

La siguiente tabla presenta el plan de evolución de SafeBridge para los próximos seis (6) meses, estructurado en versiones con fechas de liberación estimadas y características principales asociadas.

| Versión | Release Date (estimado) | Estado | Características Principales |
|:-------:|:----------------------:|:------:|------------------------------|
| **v1.0** | Mayo 2026 | ✅ Liberada | Soporte SQL Server, MySQL, PostgreSQL, Oracle, SQLite. Validación temporal asíncrona. Cifrado Fernet. UI CustomTkinter. Sistema de logging. |
| **v1.1** | Junio 2026 | 🔄 En desarrollo | Exportación de reportes de validación a PDF. Política de retención configurable de backups. Notificaciones de escritorio (toast) al completar procesos. Mejoras de UX en el terminal widget (filtrado por nivel). |
| **v1.2** | Julio 2026 | 📋 Planificada | Soporte para backups diferenciales e incrementales. Programador de tareas integrado (cron-like) para backups automáticos. Integración básica con almacenamiento local en red (NAS/SMB). |
| **v2.0** | Agosto 2026 | 📋 Planificada | **Integración con Docker:** Levantar automáticamente contenedores temporales del motor correspondiente para la validación, eliminando la dependencia de instancias instaladas localmente. Soporte de orquestación con `docker-compose`. |
| **v2.1** | Septiembre 2026 | 📋 Planificada | **Alertas por Telegram:** Bot de Telegram configurable para enviar notificaciones de éxito/error de backups con detalles del proceso y adjunto del log. Integración opcional con Slack. |
| **v3.0** | Octubre 2026 | 🔮 Visión | **Soporte NoSQL:** Módulos de backup/restore para MongoDB y Redis. Integración con almacenamiento en la nube (AWS S3, Azure Blob Storage) para transferencia automática de backups validados. Panel web de monitoreo (FastAPI + React). |

### Detalle de Características por Versión

#### v1.1 — Reportes y UX (Junio 2026)

- **Exportación a PDF:** Generación de informes de validación en formato PDF utilizando `reportlab`, incluyendo metadatos del backup, resultado de las validaciones, tiempos de ejecución y firma del sistema.
- **Retención configurable:** Interfaz en `settings_window` para definir la cantidad máxima de backups a retener por base de datos, con limpieza automática por antigüedad o cantidad.
- **Notificaciones nativas:** Uso de `plyer` o `win10toast` para alertas de sistema operativo independientes de la UI.

#### v2.0 — Integración Docker (Agosto 2026)

- **Validación containerizada:** En lugar de requerir que el motor de base de datos esté instalado localmente para la validación temporal, SafeBridge levantará un contenedor Docker (ej. `mysql:8.0`, `postgres:16`) con nombre aleatorio, realizará la restauración, ejecutará las verificaciones y destruirá el contenedor.
- **Beneficio clave:** Aislamiento total del entorno de validación y compatibilidad con entornos donde solo se dispone de Docker Desktop.

#### v2.1 — Alertas y Notificaciones (Septiembre 2026)

- **Bot de Telegram:** Integración con la API de Telegram Bot para envío de mensajes automáticos con el resultado del proceso, incluyendo nombre de la BD, motor, tamaño del backup, duración y estado de validación.

#### v3.0 — Nube y NoSQL (Octubre 2026)

- **AWS S3:** Subida automática del archivo de backup validado a un bucket S3 configurado por el usuario, con generación de URL prefirmada para descarga segura.
- **MongoDB:** Implementación de `MongoConnector` usando `mongodump` / `mongorestore` adaptado a la interfaz `DatabaseConnector`.
- **Panel web:** Interfaz web opcional para monitoreo centralizado de múltiples instancias de SafeBridge en red.

<div style="page-break-after: always; visibility: hidden"></div>

---

## 4. Gestión de Tareas con GitHub Projects y Ramas

### 4.1 Organización en GitHub Projects

El desarrollo de SafeBridge se gestiona mediante **GitHub Projects** con tablero tipo **Kanban**, utilizando la siguiente estructura de columnas:

| Columna | Descripción |
|---------|-------------|
| **Backlog** | Issues registradas pero no priorizadas para el sprint actual |
| **Sprint Actual** | Tareas comprometidas para la iteración en curso (2 semanas) |
| **En Progreso** | Issues actualmente en desarrollo, asignadas a un desarrollador |
| **En Revisión** | Pull Requests abiertos, pendientes de code review |
| **Hecho** | Issues cerradas y mergeadas a la rama principal |

Cada **Issue** en GitHub representa una historia de usuario, tarea técnica o bug, con los siguientes campos obligatorios:
- **Título:** Descripción breve en formato imperativo.
- **Cuerpo:** Historia de usuario completa, criterios de aceptación en Gherkin.
- **Labels:** `feature`, `bug`, `documentation`, `security`, `infrastructure`.
- **Milestone:** Versión objetivo (ej. `v1.1`, `v2.0`).
- **Assignee:** Desarrollador responsable.

### 4.2 Estrategia de Ramas (Branching Strategy)

SafeBridge adopta el modelo **GitHub Flow** adaptado, con las siguientes ramas principales:

```
main                  ← Rama de producción. Solo código liberado y etiquetado.
│
develop               ← Integración continua. Base para todas las features.
│
├── feature/ISSUE-XX-descripcion   ← Nuevas funcionalidades
├── bugfix/ISSUE-XX-descripcion    ← Corrección de errores
├── hotfix/descripcion             ← Fixes urgentes sobre main
└── release/vX.Y                  ← Preparación de release (freeze de features)
```

**Reglas de protección de ramas:**
- `main` y `develop` tienen protección habilitada: requieren Pull Request con al menos **1 aprobación** y que todos los **checks de CI pasen** (linting, tests, escaneo de seguridad) antes de permitir el merge.
- No se permiten commits directos (*force push* deshabilitado) en `main` o `develop`.
- Toda rama de feature debe ser creada desde `develop` y mergeada de regreso a `develop`.

### 4.3 Ciclo de Vida de una Feature

El siguiente diagrama ilustra el flujo completo desde la creación de una tarea hasta su liberación:

```
[Issue creada en GitHub Projects]
        ↓
[Desarrollador la arrastra a "Sprint Actual"]
        ↓
[git checkout -b feature/ISSUE-42-docker-validation develop]
        ↓
[Desarrollo local → commits frecuentes]
        ↓
[git push origin feature/ISSUE-42-docker-validation]
        ↓
[Pull Request → develop]
   ├─ CI/CD automático: lint, tests, SonarQube, Snyk
   └─ Code Review por el otro integrante
        ↓
[Merge a develop (squash merge)]
        ↓
[Issue cerrada automáticamente → "Hecho"]
        ↓
[Al alcanzar el scope del milestone → release/vX.Y]
        ↓
[Tests de integración → Merge a main → Tag vX.Y → GitHub Release]
```

**Vinculación Issues ↔ PR:** Los Pull Requests referencian automáticamente la issue correspondiente usando palabras clave en la descripción: `Closes #42`, `Fixes #42`. Esto cierra la issue automáticamente al hacer merge y mueve la tarjeta de Project a la columna "Hecho".

**Commits semánticos:** Se adopta la convención **Conventional Commits** para mensajes de commit:
- `feat(backup): add differential backup support`
- `fix(security): handle empty Fernet key file`
- `docs(readme): update installation steps for Oracle`
- `ci(actions): add Snyk security scan step`

<div style="page-break-after: always; visibility: hidden"></div>

---

## 5. Conclusiones

El producto SafeBridge en su versión actual (v1.0) constituye una solución funcional y arquitectónicamente sólida para la problemática de la validación de respaldos de bases de datos. La adopción de **Clean Architecture**, **inyección de dependencias** y **cifrado Fernet** garantiza que la herramienta sea segura, extensible y mantenible.

El **roadmap** estructurado en versiones semestrales con hitos claros (Docker, Alertas, NoSQL/Nube) proporciona una visión de producto coherente que permite priorizar el desarrollo de forma iterativa e incremental, alineada con los principios ágiles.

La integración de **GitHub Projects** con un modelo de ramas protegidas, revisión de código obligatoria y CI/CD automatizado establece un proceso de desarrollo profesional que minimiza riesgos técnicos y garantiza la calidad del software en cada entrega.

---

*Documento generado por el equipo BitCraft Solutions — Universidad Privada de Tacna, FAING-EPIS, Ciclo 2026-I.*
