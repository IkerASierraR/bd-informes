"""
Conector para SQL Server usando pyodbc y sqlcmd.
"""

import pyodbc
import subprocess
import os
import time
import tempfile
import shutil
from .base_connector import DatabaseConnector


class SQLServerConnector(DatabaseConnector):
    def _connection_string(self, db="master"):
        """Construye la cadena de conexión según configuración."""
        base = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=yes;"
            f"UID={self.config.user};"
            f"PWD={self.config.password};"
        )
        
        if getattr(self.config, 'use_tcp', False):
            return base + f"SERVER={self.config.host},{self.config.port};DATABASE={db};"
        else:
            return base + f"SERVER={self.config.host};DATABASE={db};"

    def _get_server_param(self):
        """Devuelve el parámetro de servidor para sqlcmd."""
        if getattr(self.config, 'use_tcp', False):
            return f"{self.config.host},{self.config.port}"
        return self.config.host

    def _get_sqlserver_backup_dir(self):
        """Obtiene el directorio de backup predeterminado de SQL Server."""
        try:
            conn = pyodbc.connect(self._connection_string(), autocommit=True)
            cursor = conn.cursor()
            cursor.execute("SELECT SERVERPROPERTY('InstanceDefaultBackupPath')")
            result = cursor.fetchone()
            
            if result and result[0] and result[0].strip():
                backup_dir = result[0].strip()
            else:
                cursor.execute("SELECT SERVERPROPERTY('InstanceDefaultDataPath')")
                result = cursor.fetchone()
                if result and result[0] and result[0].strip():
                    backup_dir = os.path.join(result[0].strip(), 'Backup')
                else:
                    backup_dir = os.path.join(tempfile.gettempdir(), 'SafeBridge_Backups')
            
            cursor.close()
            conn.close()
            os.makedirs(backup_dir, exist_ok=True)
            return backup_dir
            
        except Exception as e:
            print(f"[WARNING] No se pudo obtener directorio de backup: {e}")
            backup_dir = os.path.join(tempfile.gettempdir(), 'SafeBridge_Backups')
            os.makedirs(backup_dir, exist_ok=True)
            return backup_dir

    def test_connection(self):
        conn = pyodbc.connect(self._connection_string(), timeout=5)
        conn.close()
        return True

    def get_databases(self):
        conn = pyodbc.connect(self._connection_string())
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")
        dbs = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return dbs

    def backup(self, database, output_path):
        """Realiza backup nativo de SQL Server."""
        server = self._get_server_param()
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Hacer backup en el directorio de SQL Server
        sql_backup_dir = self._get_sqlserver_backup_dir()
        backup_filename = os.path.basename(output_path)
        sql_backup_path = os.path.join(sql_backup_dir, backup_filename)
        
        cmd = [
            "sqlcmd", "-S", server, "-U", self.config.user, "-P", self.config.password, "-C",
            "-Q", f"BACKUP DATABASE [{database}] TO DISK = N'{sql_backup_path}' WITH INIT, FORMAT"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Error en backup: {result.stderr.strip() or result.stdout.strip()}")
        
        if not os.path.exists(sql_backup_path) or os.path.getsize(sql_backup_path) == 0:
            raise RuntimeError("El archivo de backup no se generó")
        
        # Copiar a la ubicación deseada
        try:
            shutil.copy2(sql_backup_path, output_path)
        except Exception as e:
            raise RuntimeError(f"No se pudo copiar el backup a {output_path}: {e}")
        
        # Limpiar temporal
        try:
            os.remove(sql_backup_path)
        except:
            pass
        
        return True

    def restore(self, backup_file, temp_db):
        """
        Restaura un backup en una base de datos temporal y corrige permisos.
        """
        server = self._get_server_param()
        user = self.config.user
        
        if not os.path.exists(backup_file):
            raise RuntimeError(f"No se encuentra el archivo de backup: {backup_file}")
        
        # Copiar backup al directorio de SQL Server
        sql_backup_dir = self._get_sqlserver_backup_dir()
        temp_backup_name = f"temp_restore_{temp_db}.bak"
        sql_backup_path = os.path.join(sql_backup_dir, temp_backup_name)
        
        try:
            shutil.copy2(backup_file, sql_backup_path)
        except Exception as e:
            raise RuntimeError(f"No se pudo copiar el backup para restauración: {e}")
        
        try:
            # Paso 1: RESTORE DATABASE
            restore_sql = f"RESTORE DATABASE [{temp_db}] FROM DISK = N'{sql_backup_path}' WITH REPLACE"
            cmd = [
                "sqlcmd", "-S", server, "-U", user, "-P", self.config.password, "-C",
                "-Q", restore_sql
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip()
                raise RuntimeError(f"Error en restauración: {error_msg}")
            
            print(f"[DEBUG] RESTORE completado para {temp_db}")
            
            # Paso 2: Corregir permisos ejecutando comandos en la BD temporal
            # Usamos sqlcmd con USE [temp_db] para cambiar de contexto
            fix_permissions_sql = f"""
                USE [{temp_db}];
                
                -- Si el usuario no existe en la BD, crearlo
                IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = '{user}')
                BEGIN
                    CREATE USER [{user}] FOR LOGIN [{user}];
                END
                
                -- Darle permisos de owner
                ALTER ROLE db_owner ADD MEMBER [{user}];
                
                -- También arreglar el owner de la BD
                ALTER AUTHORIZATION ON DATABASE::[{temp_db}] TO [{user}];
            """
            
            cmd_fix = [
                "sqlcmd", "-S", server, "-U", user, "-P", self.config.password, "-C",
                "-Q", fix_permissions_sql
            ]
            result_fix = subprocess.run(cmd_fix, capture_output=True, text=True)
            
            if result_fix.returncode != 0:
                print(f"[WARNING] Error corrigiendo permisos: {result_fix.stderr.strip() or result_fix.stdout.strip()}")
                # No lanzamos excepción, intentamos continuar
            else:
                print(f"[DEBUG] Permisos corregidos para {user} en {temp_db}")
            
            # Dar tiempo a que los cambios se apliquen
            time.sleep(1)
            
            return True
            
        finally:
            # Limpiar archivo temporal
            try:
                os.remove(sql_backup_path)
            except:
                pass

    def create_temp_database(self, temp_db):
        """No es necesario crear la BD antes del RESTORE."""
        return True

    def drop_database(self, temp_db):
        """Elimina la base de datos temporal."""
        cmd = [
            "sqlcmd", "-S", self._get_server_param(),
            "-U", self.config.user, "-P", self.config.password, "-C",
            "-Q", f"""
                IF EXISTS (SELECT name FROM sys.databases WHERE name = '{temp_db}')
                BEGIN
                    ALTER DATABASE [{temp_db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                    DROP DATABASE [{temp_db}];
                END
            """
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[WARNING] Error al eliminar {temp_db}: {result.stderr.strip()}")
        else:
            print(f"[DEBUG] Base de datos {temp_db} eliminada")
        return True

    def verify_tables(self, temp_db):
        """
        Verifica que existan tablas en la base temporal.
        Usa sqlcmd con reintentos para esperar a que la BD esté disponible.
        """
        server = self._get_server_param()
        user = self.config.user
        
        max_retries = 5
        retry_delay = 2  # segundos
        
        for attempt in range(max_retries):
            time.sleep(retry_delay)
            
            try:
                verify_sql = f"""
                    USE [{temp_db}];
                    SELECT COUNT(*) AS TableCount FROM sys.tables;
                    SELECT TOP 10 SCHEMA_NAME(schema_id) AS Esquema, name AS Tabla 
                    FROM sys.tables 
                    ORDER BY 1, 2;
                """
                
                cmd = [
                    "sqlcmd", "-S", server, "-U", user, "-P", self.config.password, "-C",
                    "-Q", verify_sql, "-W"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                print(f"[DEBUG] Intento {attempt + 1}/{max_retries}")
                print(f"[DEBUG] Salida:\n{result.stdout[:500]}")
                
                if result.returncode != 0:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    # Si la BD no existe aún, reintentar
                    if "no existe" in error_msg.lower() or "does not exist" in error_msg.lower():
                        print(f"[DEBUG] BD aún no disponible, reintentando en {retry_delay}s...")
                        continue
                    else:
                        print(f"[ERROR] Error verificando tablas: {error_msg}")
                        return False
                
                # Buscar conteo de tablas en la salida
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line.isdigit():
                        table_count = int(line)
                        print(f"[DEBUG] ¡ÉXITO! Tablas encontradas: {table_count}")
                        if table_count > 0:
                            return True
                
                # Si no hay número pero tampoco error, verificar líneas con nombres de tabla
                for line in lines:
                    if line and '.' in line and not line.startswith('--'):
                        print(f"[DEBUG] Encontrada tabla: {line}")
                        return True
                
                # Si llegamos aquí, no se encontraron tablas
                if attempt < max_retries - 1:
                    print(f"[DEBUG] Sin tablas aún, reintentando...")
                    continue
                    
            except Exception as e:
                print(f"[WARNING] Error en intento {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue
        
        print(f"[ERROR] No se encontraron tablas después de {max_retries} intentos")
        return False