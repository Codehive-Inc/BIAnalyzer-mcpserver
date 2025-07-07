from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from db_interface import DatabaseProtocol

load_dotenv()

class Neo4jDB(DatabaseProtocol):
    def __init__(self):
        self.driver = None

    def connect(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7688")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "test12345")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def insert(self, data):
        with self.driver.session() as session:
            session.run("MERGE (p:Person {name: $name})", name=data["name"])
            return "Stored in Neo4j"

    def read(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]

    def close(self):
        self.driver.close()
