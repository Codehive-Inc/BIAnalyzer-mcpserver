from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from .postgres_db import PostgresDB
from .neo4j_db import Neo4jDB
from .azure_openai import choose_db_from_prompt
from .db_interface import DBContext

class PromptRequest(BaseModel):
    prompt: str

class Tool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class ToolsResponse(BaseModel):
    tools: List[Tool]

class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

app = FastAPI()

pg = PostgresDB(); pg.connect()
neo4j = Neo4jDB(); neo4j.connect()
context = DBContext(pg)

@app.get("/health")
def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "mcp_server"}

@app.get("/resources")
def list_resources():
    """List all resources from both databases"""
    try:
        # Get resources from PostgreSQL
        context.switch(pg)
        pg_resources = context.read("SELECT * FROM prompts LIMIT 100")
        
        # Get resources from Neo4j
        context.switch(neo4j)
        neo4j_resources = context.read("MATCH (n:Prompt) RETURN n LIMIT 100")
        
        return {
            "postgres_resources": pg_resources,
            "neo4j_resources": neo4j_resources
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/tools")
def list_tools():
    """List available MCP tools"""
    return ToolsResponse(
        tools=[
            Tool(
                name="classify_and_store",
                description="Classify a prompt and store data in the appropriate database (PostgreSQL or Neo4j)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The prompt to classify and store"
                        }
                    },
                    "required": ["prompt"]
                }
            ),
            Tool(
                name="query_postgres",
                description="Query data from PostgreSQL database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL query to execute"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="query_neo4j",
                description="Query data from Neo4j database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Cypher query to execute"
                        }
                    },
                    "required": ["query"]
                }
            )
        ]
    )

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

@app.post("/call_tool")
def call_tool(request: ToolCallRequest):
    """Call a specific MCP tool"""
    try:
        if request.name == "classify_and_store":
            prompt = request.arguments.get("prompt")
            if not prompt:
                raise HTTPException(status_code=400, detail="Prompt is required")
                
            db_choice = choose_db_from_prompt(prompt)
            if db_choice == "neo4j":
                context.switch(neo4j)
            else:
                context.switch(pg)
            result = context.insert({"name": prompt})
            return {
                "content": [
                    {"type": "text", "text": f"Classified as: {db_choice}\nResult: {result}"}
                ]
            }
            
        elif request.name == "query_postgres":
            query = request.arguments.get("query")
            if not query:
                raise HTTPException(status_code=400, detail="Query is required")
                
            context.switch(pg)
            result = context.read(query)
            return {
                "content": [
                    {"type": "text", "text": f"Query result: {result}"}
                ]
            }
            
        elif request.name == "query_neo4j":
            query = request.arguments.get("query")
            if not query:
                raise HTTPException(status_code=400, detail="Query is required")
                
            context.switch(neo4j)
            result = context.read(query)
            return {
                "content": [
                    {"type": "text", "text": f"Query result: {result}"}
                ]
            }
            
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {request.name}")
            
    except Exception as e:
        return {
            "content": [
                {"type": "text", "text": f"Error: {str(e)}"}
            ]
        }
