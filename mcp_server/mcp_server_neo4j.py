from neo4j import GraphDatabase
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv

load_dotenv()

mcp=FastMCP('neo4j-mcp-server')

# Credentials and bolt URL
def connect_to_db():
    URI = os.getenv("NEO4J_URI", "bolt://localhost:7688")
    USERNAME = os.getenv("NEO4J_USER", "neo4j")
    PASSWORD = os.getenv("NEO4J_PASSWORD", "test12345")

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