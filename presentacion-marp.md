---
marp: true
theme: default
class: lead
paginate: true
backgroundColor: '#0d1117'
color: '#e6edf3'
style: |
  section {
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
  }
  section.lead {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d2137 100%);
    text-align: center;
  }
  h1 {
    color: #58a6ff;
    font-size: 2.2em;
    border-bottom: 3px solid #238636;
    padding-bottom: 0.3em;
  }
  h2 {
    color: #79c0ff;
    font-size: 1.6em;
    border-left: 5px solid #238636;
    padding-left: 0.5em;
  }
  h3 {
    color: #56d364;
    font-size: 1.2em;
  }
  strong {
    color: #f0883e;
  }
  code {
    background-color: #161b22;
    color: #79c0ff;
    border-radius: 4px;
    padding: 0.1em 0.4em;
    font-size: 0.85em;
  }
  pre {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 1em;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.85em;
  }
  th {
    background-color: #238636;
    color: #fff;
    padding: 0.5em 1em;
  }
  td {
    border: 1px solid #30363d;
    padding: 0.4em 1em;
    background-color: #161b22;
  }
  .badge {
    display: inline-block;
    background: #238636;
    color: white;
    padding: 0.2em 0.7em;
    border-radius: 20px;
    font-size: 0.75em;
    margin: 0.2em;
  }
  footer {
    color: #8b949e;
    font-size: 0.75em;
    text-align: center;
  }
---

<!-- ================================================================
  DIAPOSITIVA 1 — PORTADA
================================================================ -->

# 🛡️ SafeBridge

## Orquestador Multi-Motor de Respaldos
## y Validación de Integridad

<br>

**Universidad Privada de Tacna**
FAING-EPIS — Ingeniería de Sistemas — 7mo Ciclo

<br>

🏢 **BitCraft Solutions**
👤 **Iker Alberto Sierra Ruiz**
📅 **2026**

---
<!-- footer: SafeBridge | BitCraft Solutions | UPT — FAING-EPIS 2026 -->

<!-- ================================================================
  DIAPOSITIVA 2 — EL PROBLEMA
================================================================ -->

# 🔥 El Problema

## *"Los backups que nadie prueba son inútiles"*

<br>

### ¿Cuántas organizaciones hacen esto?

```
07:00 — Script automatizado ejecuta: BACKUP DATABASE produccion
07:01 — ✅ Archivo .bak generado exitosamente
07:01 — 🔚 Proceso terminado. Sistema "protegido".

...

MESES DESPUÉS — Desastre en producción...
¿Es restaurable el backup?   ❓ ¿Quién sabe?
¿Es el archivo completo?     ❓ ¿Quién sabe?
¿Los datos son consistentes? ❓ ¿Quién sabe?
```

<br>

### Los 3 problemas reales:

| ❌ Problema | Consecuencia |
|------------|--------------|
| **Archivo .bak corrupto o incompleto** | Backup inútil en el peor momento |
| **Falsa sensación de seguridad** | Confianza sin evidencia |
| **Cero trazabilidad** | Sin auditoría, sin prueba de continuidad |

---

<!-- ================================================================
  DIAPOSITIVA 3 — LA SOLUCIÓN
================================================================ -->

# 🛡️ La Solución: SafeBridge

## Cierra el ciclo de confianza del backup

<br>

```
SIN SafeBridge:
  [Backup] ──────────────────────────────────▶ ❓ ¿Funciona?

CON SafeBridge:
  [Backup] ──▶ [Restore en Sandbox] ──▶ [Verify] ──▶ [Cleanup] ──▶ ✅ VALIDADO
```

<br>

### Lo que SafeBridge garantiza:

✅ **Backup generado** con nomenclatura automática y fecha/hora  
✅ **Restaurado automáticamente** en base de datos temporal aislada  
✅ **Integridad verificada**: tablas, estructura, consistencia  
✅ **Sandbox eliminado** sin rastro en producción  
✅ **Log completo** con evidencia auditable de cada paso  

<br>

> *SafeBridge no asume que tu backup funciona. Lo demuestra.*

---

<!-- ================================================================
  DIAPOSITIVA 4 — MOTORES Y TECNOLOGÍAS
================================================================ -->

# 🔌 Soporte Multi-Motor

## 5 motores de base de datos en una sola herramienta

<br>

| Motor | Driver | Puerto | Herramienta de Backup |
|-------|--------|--------|----------------------|
| **SQL Server** | `pyodbc` ODBC 18 | 1433 | `BACKUP DATABASE` T-SQL |
| **MySQL** | `mysql-connector-python` | 3306 | `mysqldump` |
| **PostgreSQL** | `psycopg2-binary` | 5432 | `pg_dump` |
| **Oracle DB** | `oracledb` | 1521 | `expdp` / `exp` |
| **SQLite** | `sqlite3` stdlib | N/A | File copy + integrity check |

<br>

### Stack tecnológico principal:

<span class="badge">Python 3.12+</span>
<span class="badge">CustomTkinter</span>
<span class="badge">cryptography (Fernet)</span>
<span class="badge">threading</span>
<span class="badge">Terraform</span>
<span class="badge">GitHub Actions</span>

---

<!-- ================================================================
  DIAPOSITIVA 5 — ARQUITECTURA LIMPIA
================================================================ -->

# 🏗️ Arquitectura: Clean Architecture

## Separación estricta de responsabilidades

```
╔══════════════════════════════════════════════════════╗
║              🖥️  PRESENTATION LAYER                  ║
║     LoginWindow │ DashboardWindow │ TerminalWidget    ║
╠══════════════════════════════════════════════════════╣
║              ⚙️  APPLICATION LAYER                   ║
║   BackupProcess │ ConnectionService │ ValidationService║
╠══════════════════════════════════════════════════════╣
║              📦  DOMAIN LAYER                        ║
║        ConnectionConfig │ BackupRecord │ EngineType   ║
╠══════════════════════════════════════════════════════╣
║              🔧  INFRASTRUCTURE LAYER                ║
║  MySQLConnector │ PgConnector │ SQLServerConnector    ║
║       OracleConnector │ SQLiteConnector              ║
║           SafeBridgeLogger │ Security (Fernet)        ║
╚══════════════════════════════════════════════════════╝
```

### Beneficios clave:

🔀 **Inyección de Dependencias** — `ConnectionService.get_connector(config)` actúa como Factory  
🔒 **Regla de Dependencia** — Las capas internas NO conocen las externas  
🧪 **Testabilidad** — Cada capa es mockeable e independiente  

---

<!-- ================================================================
  DIAPOSITIVA 6 — SEGURIDAD: FERNET + CI/CD
================================================================ -->

# 🔒 Seguridad: Defensa en Profundidad

## Capa 1: Cifrado de Credenciales en Reposo

```python
# infrastructure/security.py
# Fernet = AES-128-CBC + HMAC-SHA256

def save_connections(connections: list[dict]) -> None:
    fernet = Fernet(_get_or_create_key())          # Lee/genera clave de 32 bytes
    encrypted = fernet.encrypt(json.dumps(connections).encode())
    open("~/.safebridge/connections.json.enc","wb").write(encrypted)
    # ✅ Nunca texto plano en disco
```

<br>

## Capa 2: Pipeline de Seguridad (GitHub Actions)

| Herramienta | Tipo | ¿Qué detecta? |
|-------------|------|---------------|
| **Semgrep** | SAST | Inyección SQL, secretos en código, OWASP Top 10 |
| **Snyk** | SCA | CVEs en dependencias (`requirements.txt`) |
| **Bandit** | Python SAST | Patrones inseguros específicos de Python |
| **pip-audit** | SCA | Vulnerabilidades conocidas en paquetes pip |

<br>

> 🔐 *Cero vulnerabilidades críticas antes de cada merge a `main`*

---

<!-- ================================================================
  DIAPOSITIVA 7 — PIPELINE CI/CD
================================================================ -->

# 🔄 Pipeline CI/CD: GitHub Actions

## Del código al ejecutable en minutos

```
Push / PR
    │
    ▼
┌──────────┐    ┌──────────┐    ┌──────────────────┐
│ 🔍 Lint  │───▶│ 🧪 Tests │───▶│ 🔒 Security Scan │
│  flake8  │    │  pytest  │    │ Semgrep+Snyk     │
│  pylint  │    │  >70% cov│    │ Bandit+pip-audit │
└──────────┘    └──────────┘    └────────┬─────────┘
                                         │
                          Solo en push   ▼
                          ┌──────────────────────┐
                          │ 📦 Build             │
                          │ PyInstaller → .exe   │
                          │ Docker → Image       │
                          └──────────┬───────────┘
                                     │
                          Solo en tag v*.*.*
                                     ▼
                          ┌──────────────────────┐
                          │ 🚀 Release           │
                          │ GitHub Releases      │
                          │ Docker Hub Push      │
                          └──────────────────────┘
```

---

<!-- ================================================================
  DIAPOSITIVA 8 — INFRAESTRUCTURA COMO CÓDIGO (TERRAFORM)
================================================================ -->

# ☁️ Infraestructura como Código

## Terraform + AWS: Entorno de Pruebas Reproducible

```hcl
# terraform/main.tf

resource "aws_s3_bucket" "safebridge_backups" {
  bucket = "safebridge-backups-prod"
  # Almacena backups validados con durabilidad 99.999999999%
  tags = { Project = "SafeBridge", Team = "BitCraft" }
}

resource "aws_instance" "test_db_server" {
  ami           = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2023
  instance_type = "t3.micro"               # ~$8.50/mes (Free Tier eligible)
  # Servidor de BD para pruebas de restauración remota
}
```

<br>

### Beneficios del enfoque IaC:

| Principio | Beneficio |
|-----------|-----------|
| **Reproducibilidad** | Mismo entorno en cualquier región, en segundos |
| **Control de costos** | `terraform destroy` al finalizar las pruebas |
| **Auditabilidad** | Cambios de infraestructura en Git como código |
| **Seguridad** | Security Groups con mínimos permisos por defecto |

---

<!-- ================================================================
  DIAPOSITIVA 9 — DEMOSTRACIÓN EN VIVO
================================================================ -->

# 🎬 Demostración

## SafeBridge en acción

<br>

<div style="text-align: center; padding: 3em; border: 3px dashed #238636; border-radius: 16px; background: #161b22;">

### 📹 VIDEO PLACEHOLDER

*[Insertar grabación de pantalla aquí]*

**Flujo a demostrar:**
1. 🔌 Configurar conexión a MySQL (credenciales cifradas)
2. 🗄️ Seleccionar base de datos `demo_produccion`
3. ▶️ Iniciar "Backup y Validación"
4. 📟 Observar el Terminal Widget en tiempo real
5. ✅ Resultado: "Backup y validación exitosos"

</div>

<br>

> *Duración aproximada del proceso: 45-90 segundos para 500MB*

---

<!-- ================================================================
  DIAPOSITIVA 10 — ROADMAP Y CIERRE
================================================================ -->

# 🗺️ Roadmap y Conclusiones

## Evolución de SafeBridge: 6 meses

| Versión | Fecha | Hito Principal |
|:-------:|-------|----------------|
| **v1.0** ✅ | Mayo 2026 | Multi-motor, Validación temporal, Fernet, UI |
| **v1.1** 🔄 | Junio 2026 | Exportar PDF, Retención, Notificaciones desktop |
| **v1.2** 📋 | Julio 2026 | Backups diferenciales, Programador de tareas |
| **v2.0** 📋 | Agosto 2026 | **Docker**: validación en contenedores temporales |
| **v2.1** 📋 | Sept. 2026 | **Telegram Bot**: alertas automáticas |
| **v3.0** 🔮 | Oct. 2026 | **NoSQL** (MongoDB), AWS S3, Panel web |

<br>

## 💡 Conclusión

> **SafeBridge transforma la gestión de respaldos de una actividad de fe en un proceso científico y auditable.**

<br>

🙋 **¿Preguntas?**

👤 Iker Alberto Sierra Ruiz | 🏢 BitCraft Solutions | 🎓 UPT FAING-EPIS 2026

---
<!-- footer: "" -->

<!-- ================================================================
  DIAPOSITIVA 11 — GRACIAS (CIERRE)
================================================================ -->

<br><br><br>

# 🛡️ SafeBridge

<br>

## *"Un backup no probado es solo un archivo."*

<br><br>

**Repositorio:** `github.com/IkerASierraR/bd-informes`  
**Equipo:** BitCraft Solutions  
**Institución:** Universidad Privada de Tacna, FAING-EPIS  
**Docente:** Ing. Patrick José Cuadros Quiroga  

<br>

---

*¡Gracias por su atención!*
