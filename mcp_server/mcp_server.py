#!/usr/bin/env python3
"""
MCP Server for Database Classifier
Implements the Model Context Protocol to classify prompts and route to appropriate databases
"""

import asyncio
import json
import os
import sys
import logging
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
)

# Set up logging
log_dir = os.path.expanduser("~/mcp_server_logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "mcp_server.log")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("mcp_server")
logger.info("MCP server starting up")

# Log system information
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Script path: {os.path.abspath(__file__)}")

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Initialize MCP server
server = Server("database-classifier")

# Database connections
class DatabaseManager:
    def __init__(self):
        self.postgres_conn = None
        self.neo4j_driver = None
    
    async def get_postgres_connection(self):
        if not self.postgres_conn:
            import psycopg2
            self.postgres_conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB", "mcp_db"),
                user=os.getenv("POSTGRES_USER", "mcp_user"),
                password=os.getenv("POSTGRES_PASSWORD", "secret"),
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", "5432"))
            )
        return self.postgres_conn
    
    async def get_neo4j_driver(self):
        if not self.neo4j_driver:
            from neo4j import GraphDatabase
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7688")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "test12345")
            self.neo4j_driver = GraphDatabase.driver(uri, auth=(user, password))
        return self.neo4j_driver

db_manager = DatabaseManager()

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools"""
    return ListToolsResult(
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

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls"""
    
    if name == "classify_and_store":
        return await handle_classify_and_store(arguments)
    elif name == "query_postgres":
        return await handle_query_postgres(arguments)
    elif name == "query_neo4j":
        return await handle_query_neo4j(arguments)
    else:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )
            ]
        )

async def handle_classify_and_store(arguments: Dict[str, Any]) -> CallToolResult:
    """Classify prompt and store in appropriate database"""
    prompt = arguments.get("prompt", "")
    
    try:
        # Use Azure OpenAI to classify the prompt
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_API_KEY"),
            api_version="2023-05-15",
            azure_endpoint=os.getenv("AZURE_API_BASE")
        )
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are a classifier. Respond only with 'postgres' or 'neo4j'."},
                {"role": "user", "content": prompt}
            ]
        )
        
        db_choice = response.choices[0].message.content.strip().lower()
        
        # Store data in the chosen database
        if db_choice == "neo4j":
            result = await store_in_neo4j(prompt)
        else:
            result = await store_in_postgres(prompt)
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Classified as: {db_choice}\nResult: {result}"
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        )

async def store_in_postgres(data: str) -> str:
    """Store data in PostgreSQL"""
    conn = await db_manager.get_postgres_connection()
    with conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT);")
        cur.execute("INSERT INTO users (name) VALUES (%s);", (data,))
        conn.commit()
    return "Stored in PostgreSQL"

async def store_in_neo4j(data: str) -> str:
    """Store data in Neo4j"""
    driver = await db_manager.get_neo4j_driver()
    with driver.session() as session:
        session.run("MERGE (p:Person {name: $name})", name=data)
    return "Stored in Neo4j"

async def handle_query_postgres(arguments: Dict[str, Any]) -> CallToolResult:
    """Query PostgreSQL database"""
    query = arguments.get("query", "")
    
    try:
        conn = await db_manager.get_postgres_connection()
        with conn.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"PostgreSQL Query Results:\n{json.dumps(results, indent=2)}"
                )
            ]
        )
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"PostgreSQL Query Error: {str(e)}"
                )
            ]
        )

async def handle_query_neo4j(arguments: Dict[str, Any]) -> CallToolResult:
    """Query Neo4j database"""
    query = arguments.get("query", "")
    
    try:
        driver = await db_manager.get_neo4j_driver()
        with driver.session() as session:
            result = session.run(query)
            results = [record.data() for record in result]
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Neo4j Query Results:\n{json.dumps(results, indent=2)}"
                )
            ]
        )
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Neo4j Query Error: {str(e)}"
                )
            ]
        )

async def main():
    """Main function to run the MCP server"""
    logger.info("Entering main function")
    try:
        # Run the server
        logger.info("Setting up stdio server")
        async with stdio_server() as (read_stream, write_stream):
            from mcp.server.lowlevel.server import NotificationOptions
            
            logger.info("Starting MCP server run")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="database-classifier",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(tools_changed=True),
                        experimental_capabilities={}
                    ),
                ),
            )
            logger.info("MCP server run completed")
    except Exception as e:
        logger.error(f"Error in main function: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main()) 