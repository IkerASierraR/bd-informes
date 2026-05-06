import mysql.connector
import subprocess
import os
from .base_connector import DatabaseConnector


class MySQLConnector(DatabaseConnector):
    def test_connection(self):
        conn = mysql.connector.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password
        )
        conn.close()
        return True

    def get_databases(self):
        conn = mysql.connector.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password
        )
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        dbs = [row[0] for row in cursor.fetchall()
               if row[0] not in ("information_schema", "performance_schema", "mysql", "sys")]
        cursor.close()
        conn.close()
        return dbs

    def backup(self, database, output_path):
        cmd = [
            "mysqldump",
            f"--host={self.config.host}",
            f"--port={self.config.port}",
            f"--user={self.config.user}",
            f"--password={self.config.password}",
            "--single-transaction",
            "--routines",
            "--triggers",
            database
        ]
        with open(output_path, "w", encoding="utf-8") as out:
            result = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return True

    def restore(self, backup_file, temp_db):
        cmd = [
            "mysql",
            f"--host={self.config.host}",
            f"--port={self.config.port}",
            f"--user={self.config.user}",
            f"--password={self.config.password}",
            temp_db
        ]
        with open(backup_file, "r", encoding="utf-8") as infile:
            result = subprocess.run(cmd, stdin=infile, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return True

    def create_temp_database(self, temp_db):
        conn = mysql.connector.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE `{temp_db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        cursor.close()
        conn.close()
        return True

    def drop_database(self, temp_db):
        conn = mysql.connector.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password
        )
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE `{temp_db}`")
        conn.commit()
        cursor.close()
        conn.close()
        return True

    def verify_tables(self, temp_db):
        conn = mysql.connector.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=temp_db
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.close()
        conn.close()
        return len(tables) > 0