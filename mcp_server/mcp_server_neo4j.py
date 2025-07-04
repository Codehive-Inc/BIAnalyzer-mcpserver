from neo4j import GraphDatabase
from mcp.server.fastmcp import FastMCP

mcp=FastMCP('neo4j-mcp-server')

# Credentials and bolt URL
def connect_to_db():
    URI = "bolt://localhost:7687"
    USERNAME = "neo4j"
    PASSWORD = "test12345"

    # Create driver
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    return driver

# Define a simple function to create a node
@mcp.tool()
def create_node(name):
    driver=connect_to_db()
    with driver.session() as session:
        session.run("MERGE (p:Person {name: $name})", name=name)
    driver.close()

# Create a node
create_node("Akshay")