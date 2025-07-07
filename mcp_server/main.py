from fastapi import FastAPI
from pydantic import BaseModel
from postgres_db import PostgresDB
from neo4j_db import Neo4jDB
from azure_openai import choose_db_from_prompt
from db_interface import DBContext

class PromptRequest(BaseModel):
    prompt: str

app = FastAPI()

pg = PostgresDB(); pg.connect()
neo4j = Neo4jDB(); neo4j.connect()
context = DBContext(pg)

@app.get("/health")
def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "mcp_server"}

@app.post("/process")
def process_input(data: PromptRequest):
    try:
        db_choice = choose_db_from_prompt(data.prompt)
        if db_choice == "neo4j":
            context.switch(neo4j)
        else:
            context.switch(pg)
        result = context.insert({"name": data.prompt})
        return {"db_used": db_choice, "result": result}
    except Exception as e:
        return {"error": str(e)}
