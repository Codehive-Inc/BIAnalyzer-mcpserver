#!/usr/bin/env python3
"""
Test script for the MCP server
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any

async def test_mcp_server():
    """Test the MCP server functionality"""
    
    print("🧪 Testing MCP Server...")
    
    # Test 1: Check if the server can be started
    try:
        # Start the MCP server as a subprocess
        process = subprocess.Popen(
            [sys.executable, "mcp_server/mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send a simple test message
        test_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send the message
        process.stdin.write(json.dumps(test_message) + "\n")
        process.stdin.flush()
        
        # Wait a bit for response
        await asyncio.sleep(1)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ MCP Server started successfully")
            
            # Terminate the process
            process.terminate()
            process.wait()
        else:
            print("❌ MCP Server failed to start")
            stdout, stderr = process.communicate()
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
    
    # Test 2: Test database connections
    print("\n🔗 Testing Database Connections...")
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.getcwd(), 'mcp_server'))
        from postgres_db import PostgresDB
        pg = PostgresDB()
        pg.connect()
        print("✅ PostgreSQL connection successful")
        pg.close()
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.getcwd(), 'mcp_server'))
        from neo4j_db import Neo4jDB
        neo = Neo4jDB()
        neo.connect()
        print("✅ Neo4j connection successful")
        neo.close()
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
    
    # Test 3: Test Azure OpenAI connection
    print("\n🤖 Testing Azure OpenAI...")
    
    try:
        from openai import AzureOpenAI
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_API_KEY"),
            api_version="2023-05-15",
            azure_endpoint=os.getenv("AZURE_API_BASE")
        )
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are a classifier. Respond only with 'postgres' or 'neo4j'."},
                {"role": "user", "content": "Store user data with relationships"}
            ]
        )
        
        result = response.choices[0].message.content.strip().lower()
        print(f"✅ Azure OpenAI test successful: {result}")
        
    except Exception as e:
        print(f"❌ Azure OpenAI test failed: {e}")
    
    print("\n🎉 MCP Server testing complete!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 