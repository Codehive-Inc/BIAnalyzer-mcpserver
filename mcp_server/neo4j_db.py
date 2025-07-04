from neo4j import GraphDatabase
from db_interface import DatabaseProtocol

class Neo4jDB(DatabaseProtocol):
    def __init__(self):
        self.driver = None

    def connect(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "test12345"))

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
