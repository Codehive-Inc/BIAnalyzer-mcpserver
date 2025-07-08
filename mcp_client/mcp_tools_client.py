#!/usr/bin/env python3
"""
MCP Tools Client
A client for interacting with the MCP server's tools interface
"""

import os
import requests
import json
from typing import Dict, Any, List, Optional

# Get server URL from environment variable, with a fallback for local development
SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8000")

def list_tools():
    """List all available tools from the MCP server"""
    try:
        response = requests.get(f"{SERVER_URL}/tools")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error listing tools: {e}")
        return {"tools": []}

def list_resources():
    """List all resources from both PostgreSQL and Neo4j databases"""
    try:
        response = requests.get(f"{SERVER_URL}/resources")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error listing resources: {e}")
        return {"error": str(e)}

def call_tool(tool_name: str, arguments: Dict[str, Any]):
    """Call a specific tool on the MCP server"""
    try:
        payload = {
            "name": tool_name,
            "arguments": arguments
        }
        response = requests.post(f"{SERVER_URL}/call_tool", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling tool {tool_name}: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}

def display_tool_result(result):
    """Display the result of a tool call in a readable format"""
    if "content" in result:
        for item in result["content"]:
            if item["type"] == "text":
                print(f"✅ {item['text']}")
    else:
        print(f"✅ Result: {json.dumps(result, indent=2)}")

def run():
    """Run the MCP tools client"""
    print("🔧 MCP Tools Client")
    print("=================")
    
    # List available tools
    tools_response = list_tools()
    tools = tools_response.get("tools", [])
    
    if not tools:
        print("❌ No tools available or couldn't connect to server")
        return
    
    print(f"📋 Available tools ({len(tools)}):")
    for i, tool in enumerate(tools):
        print(f"  {i+1}. {tool['name']}: {tool['description']}")
    
    while True:
        print("\n📝 Choose an option:")
        print("  1. List tools")
        print("  2. Call a tool")
        print("  3. List resources")
        print("  4. Exit")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            # List tools again
            print(f"📋 Available tools ({len(tools)}):")
            for i, tool in enumerate(tools):
                print(f"  {i+1}. {tool['name']}: {tool['description']}")
                
        elif choice == "2":
            # Call a tool
            print("\n📋 Select a tool to call:")
            for i, tool in enumerate(tools):
                print(f"  {i+1}. {tool['name']}")
            
            try:
                tool_idx = int(input("Enter tool number: ").strip()) - 1
                if tool_idx < 0 or tool_idx >= len(tools):
                    print("❌ Invalid tool number")
                    continue
                
                selected_tool = tools[tool_idx]
                print(f"\n🔧 Calling tool: {selected_tool['name']}")
                print(f"📝 Description: {selected_tool['description']}")
                
                # Build arguments based on the tool's input schema
                arguments = {}
                required_props = selected_tool['inputSchema'].get('required', [])
                properties = selected_tool['inputSchema'].get('properties', {})
                
                for prop_name, prop_details in properties.items():
                    is_required = prop_name in required_props
                    prompt = f"Enter {prop_name}"
                    if "description" in prop_details:
                        prompt += f" ({prop_details['description']})"
                    if is_required:
                        prompt += " [required]"
                    prompt += ": "
                    
                    value = input(prompt).strip()
                    if is_required and not value:
                        print(f"❌ {prop_name} is required")
                        continue
                    
                    if value:
                        arguments[prop_name] = value
                
                # Call the tool
                result = call_tool(selected_tool['name'], arguments)
                display_tool_result(result)
                
            except ValueError:
                print("❌ Please enter a valid number")
                
        elif choice == "3":
            # List resources
            print("\n📋 Fetching resources from databases...")
            resources = list_resources()
            
            if "error" in resources:
                print(f"❌ Error: {resources['error']}")
                continue
                
            # Display PostgreSQL resources
            print("\n📊 PostgreSQL Resources:")
            pg_resources = resources.get("postgres_resources", [])
            if not pg_resources:
                print("  No resources found")
            else:
                for i, resource in enumerate(pg_resources):
                    print(f"  {i+1}. {resource}")
            
            # Display Neo4j resources
            print("\n🔄 Neo4j Resources:")
            neo4j_resources = resources.get("neo4j_resources", [])
            if not neo4j_resources:
                print("  No resources found")
            else:
                for i, resource in enumerate(neo4j_resources):
                    print(f"  {i+1}. {resource}")
                    
        elif choice == "4":
            # Exit
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    run()
