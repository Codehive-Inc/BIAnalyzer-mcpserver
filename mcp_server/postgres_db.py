import psycopg2
from db_interface import DatabaseProtocol

class PostgresDB(DatabaseProtocol):
    def __init__(self):
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(
            dbname="mcp_db",
            user="postgres",
            password="secret",
            host="localhost",
            port=5432
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
