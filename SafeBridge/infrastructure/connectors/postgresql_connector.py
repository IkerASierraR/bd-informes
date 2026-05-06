import psycopg2
import subprocess
import os
from .base_connector import DatabaseConnector


class PostgreSQLConnector(DatabaseConnector):
    def _dsn(self, dbname="postgres"):
        return f"host={self.config.host} port={self.config.port} dbname={dbname} user={self.config.user} password={self.config.password}"

    def test_connection(self):
        conn = psycopg2.connect(self._dsn())
        conn.close()
        return True

    def get_databases(self):
        conn = psycopg2.connect(self._dsn())
        cursor = conn.cursor()
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres'")
        dbs = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return dbs

    def backup(self, database, output_path):
        env = os.environ.copy()
        env["PGPASSWORD"] = self.config.password
        cmd = [
            "pg_dump",
            "-h", self.config.host,
            "-p", str(self.config.port),
            "-U", self.config.user,
            "-F", "p",
            "-f", output_path,
            database
        ]
        result = subprocess.run(cmd, env=env, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return True

    def restore(self, backup_file, temp_db):
        env = os.environ.copy()
        env["PGPASSWORD"] = self.config.password
        cmd = [
            "psql",
            "-h", self.config.host,
            "-p", str(self.config.port),
            "-U", self.config.user,
            "-d", temp_db,
            "-f", backup_file
        ]
        result = subprocess.run(cmd, env=env, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return True

    def create_temp_database(self, temp_db):
        env = os.environ.copy()
        env["PGPASSWORD"] = self.config.password
        cmd = [
            "createdb",
            "-h", self.config.host,
            "-p", str(self.config.port),
            "-U", self.config.user,
            temp_db
        ]
        result = subprocess.run(cmd, env=env, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return True

    def drop_database(self, temp_db):
        env = os.environ.copy()
        env["PGPASSWORD"] = self.config.password
        cmd = [
            "dropdb",
            "-h", self.config.host,
            "-p", str(self.config.port),
            "-U", self.config.user,
            temp_db
        ]
        result = subprocess.run(cmd, env=env, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return True

    def verify_tables(self, temp_db):
        conn = psycopg2.connect(self._dsn(dbname=temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = cursor.fetchall()
        cursor.close()
        conn.close()
        return len(tables) > 0