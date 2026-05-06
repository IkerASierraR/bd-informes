"""
Conector para Oracle usando python-oracledb (driver moderno, sin compilación).
"""

import oracledb
import subprocess
import os
from .base_connector import DatabaseConnector


class OracleConnector(DatabaseConnector):
    def _get_connection_params(self):
        """Devuelve los parámetros de conexión."""
        return dict(
            user=self.config.user,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port,
            service_name=self.config.service_name
        )

    def test_connection(self):
        conn = oracledb.connect(**self._get_connection_params())
        conn.close()
        return True

    def get_databases(self):
        """Devuelve los esquemas (usuarios) disponibles."""
        conn = oracledb.connect(**self._get_connection_params())
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username FROM all_users 
            WHERE username NOT IN (
                'SYS','SYSTEM','DBSNMP','APPQOSSYS','AUDSYS','CTXSYS',
                'DVSYS','DBSFWUSER','DVF','GSMADMIN_INTERNAL','LBACSYS',
                'MDSYS','OJVMSYS','OLAPSYS','ORDDATA','ORDSYS','OUTLN',
                'REMOTE_SCHEDULER_AGENT','SI_INFORMTN_SCHEMA','SYSBACKUP',
                'SYSDG','SYSKM','SYSRAC','WMSYS','XDB','XS$NULL'
            )
            ORDER BY username
        """)
        schemas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return schemas

    def backup(self, database, output_path):
        """
        Realiza backup usando Data Pump (expdp) o exp como fallback.
        Nota: Data Pump requiere acceso al servidor, aquí usamos método alternativo.
        """
        conn = oracledb.connect(**self._get_connection_params())
        cursor = conn.cursor()
        
        # Método: generar DDL y datos mediante consultas
        try:
            # Crear directorio para archivos temporales
            temp_dir = os.path.dirname(output_path)
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generar backup script usando DBMS_METADATA y spool
            backup_script = f"""
            SET ECHO OFF
            SET HEADING OFF
            SET PAGESIZE 0
            SET LONG 1000000
            SET LONGCHUNKSIZE 1000000
            SET TRIMSPOOL ON
            SET FEEDBACK OFF
            
            SPOOL {output_path}
            
            -- Obtener DDL de todas las tablas del esquema
            BEGIN
                FOR t IN (SELECT table_name FROM all_tables WHERE owner = UPPER('{database}')) LOOP
                    DBMS_OUTPUT.PUT_LINE('-- Table: ' || t.table_name);
                    FOR ddl IN (
                        SELECT DBMS_METADATA.GET_DDL('TABLE', t.table_name, UPPER('{database}')) AS ddl_text 
                        FROM DUAL
                    ) LOOP
                        DBMS_OUTPUT.PUT_LINE(ddl.ddl_text);
                        DBMS_OUTPUT.PUT_LINE('/');
                    END LOOP;
                END LOOP;
            END;
            /
            
            SPOOL OFF
            """
            
            cursor.execute(backup_script)
            conn.commit()
            
            # Si lo anterior falla, usar método simplificado con SELECT
            if not os.path.exists(output_path) or os.path.getsize(output_path) < 100:
                # Backup simplificado: exportar estructura y datos
                with open(output_path, 'w', encoding='utf-8') as f:
                    # Escribir headers
                    f.write(f"-- Backup de {database}\n")
                    f.write(f"-- Generado por SafeBridge\n\n")
                    
                    # Obtener lista de tablas
                    cursor.execute(f"SELECT table_name FROM all_tables WHERE owner = UPPER('{database}')")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    for table in tables:
                        f.write(f"\n-- Tabla: {table}\n")
                        
                        # Obtener CREATE TABLE
                        try:
                            cursor.execute(f"""
                                SELECT DBMS_METADATA.GET_DDL('TABLE', '{table}', UPPER('{database}')) 
                                FROM DUAL
                            """)
                            ddl = cursor.fetchone()[0]
                            f.write(ddl.read() if hasattr(ddl, 'read') else str(ddl))
                            f.write(";\n\n")
                        except:
                            f.write(f"-- No se pudo obtener DDL para {table}\n")
                        
                        # Exportar datos como INSERT (limitado a 1000 registros por tabla)
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM {database}.{table}")
                            count = cursor.fetchone()[0]
                            f.write(f"-- {count} registros en {table}\n")
                            
                            if count > 0 and count <= 1000:
                                cursor.execute(f"SELECT * FROM {database}.{table}")
                                columns = [col[0] for col in cursor.description]
                                rows = cursor.fetchall()
                                
                                for row in rows[:1000]:  # Máximo 1000 registros
                                    values = []
                                    for val in row:
                                        if val is None:
                                            values.append('NULL')
                                        elif isinstance(val, (int, float)):
                                            values.append(str(val))
                                        else:
                                            values.append(f"'{str(val).replace(chr(39), chr(39)+chr(39))}'")
                                    
                                    insert = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
                                    f.write(insert)
                            else:
                                f.write(f"-- Demasiados registros para exportar ({count})\n")
                        except Exception as e:
                            f.write(f"-- Error exportando datos: {str(e)}\n")
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Error en backup Oracle: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def restore(self, backup_file, temp_db):
        """
        Restaura un backup SQL en un esquema temporal.
        """
        conn = oracledb.connect(**self._get_connection_params())
        cursor = conn.cursor()
        
        try:
            # Leer y ejecutar el archivo SQL
            with open(backup_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Reemplazar el nombre del esquema original por el temporal
            sql_content = sql_content.replace(f'"{self.config.user.upper()}"', f'"{temp_db.upper()}"')
            sql_content = sql_content.replace(self.config.user.upper(), temp_db.upper())
            
            # Dividir por comandos y ejecutar uno a uno
            commands = sql_content.split(';')
            for cmd in commands:
                cmd = cmd.strip()
                if cmd and not cmd.startswith('--'):
                    try:
                        cursor.execute(cmd)
                    except Exception as e:
                        # Ignorar errores no críticos durante la restauración
                        if 'ORA-' in str(e):
                            print(f"Warning en restauración: {str(e)}")
                            continue
            
            conn.commit()
            return True
            
        except Exception as e:
            raise RuntimeError(f"Error en restauración Oracle: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def create_temp_database(self, temp_db):
        """Crea un esquema/usuario temporal."""
        conn = oracledb.connect(**self._get_connection_params())
        cursor = conn.cursor()
        try:
            cursor.execute(f'CREATE USER {temp_db} IDENTIFIED BY "{temp_db}"')
            cursor.execute(f"GRANT CONNECT, RESOURCE TO {temp_db}")
            cursor.execute(f"ALTER USER {temp_db} QUOTA UNLIMITED ON USERS")
            conn.commit()
            return True
        except Exception as e:
            raise RuntimeError(f"Error creando esquema temporal: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def drop_database(self, temp_db):
        """Elimina el esquema temporal."""
        conn = oracledb.connect(**self._get_connection_params())
        cursor = conn.cursor()
        try:
            cursor.execute(f"DROP USER {temp_db} CASCADE")
            conn.commit()
            return True
        except Exception as e:
            raise RuntimeError(f"Error eliminando esquema temporal: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def verify_tables(self, temp_db):
        """Verifica que existan tablas en el esquema temporal."""
        conn = oracledb.connect(
            user=temp_db,
            password=temp_db,
            host=self.config.host,
            port=self.config.port,
            service_name=self.config.service_name
        )
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT table_name FROM user_tables")
            tables = cursor.fetchall()
            return len(tables) > 0
        finally:
            cursor.close()
            conn.close()