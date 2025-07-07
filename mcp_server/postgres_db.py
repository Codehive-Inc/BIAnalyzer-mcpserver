import psycopg2
import os
from dotenv import load_dotenv
from .db_interface import DatabaseProtocol

load_dotenv()

class PostgresDB(DatabaseProtocol):
    def __init__(self):
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "mcp_db"),
            user=os.getenv("POSTGRES_USER", "mcp_user"),
            password=os.getenv("POSTGRES_PASSWORD", "secret"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432"))
        )
        with self.conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT);")
            self.conn.commit()

    def insert(self, data):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO users (name) VALUES (%s);", (data["name"],))
            self.conn.commit()
            return "Stored in Postgres"

    def read(self, query):
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    def close(self):
        self.conn.close()
