from mcp.server.fastmcp import FastMCP
import psycopg2

mcp=FastMCP('postgres-mcp-server')

# Connection details
def connect_to_db():
    conn = psycopg2.connect(
        dbname="test_db",
        user="postgres",
        password="secret123",
        host="localhost",
        port="5432"
    )
    return conn

# Create a table and insert data
@mcp.tool()
def init_db():
    conn=connect_to_db()
    with conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT);")
        cur.execute("INSERT INTO users (name) VALUES (%s)", ("Chandrahas",))
        conn.commit()
    conn.close()

# Read data
@mcp.tool()
def fetch_data():
    conn=connect_to_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users;")
        for row in cur.fetchall():
            print(row)
    conn.close()

# Run it
init_db()
fetch_data()