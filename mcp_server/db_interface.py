from typing import Protocol, Any

class DatabaseProtocol(Protocol):
    def connect(self) -> None: ...
    def insert(self, data: dict) -> str: ...
    def read(self, query: str) -> Any: ...
    def close(self) -> None: ...

class DBContext:
    def __init__(self, db: DatabaseProtocol):
        self.db = db

    def switch(self, db: DatabaseProtocol):
        self.db = db

    def insert(self, data: dict):
        return self.db.insert(data)

    def read(self, query: str):
        return self.db.read(query)
