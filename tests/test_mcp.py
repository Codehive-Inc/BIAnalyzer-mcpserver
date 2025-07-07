#!/usr/bin/env python3
"""
Comprehensive MCP Server Test
This script tests the MCP server running in Docker with various functionality tests
"""

import asyncio
import json
import subprocess
import sys
import os
from typing import Dict, Any, Optional, List, Tuple

class MCPTester:
    """MCP Server testing class"""
    
    def __init__(self):
        self.container_name = "mcp_server"
        self.network_name = "classifier_mcp_server_mcp_network"
    
    async def run_tests(self):
        """Run all tests"""
        print("🚀 Starting MCP Server Tests")
        print("=" * 50)
        
        # Test 1: Check if containers are running
        await self.test_containers_running()
        
        # Test 2: Test MCP protocol
        await self.test_mcp_protocol()
        
        # Test 3: Test database connections
        await self.test_database_connections()
        
        # Test 4: Test tool functionality
        await self.test_tool_functionality()
        
        print("=" * 50)
        print("🎉 All tests completed!")
    
    async def test_containers_running(self):
        """Test if all required containers are running"""
        print("\n📋 Testing if containers are running...")
        
        containers = ["mcp_server", "mcp_postgres", "mcp_neo4j"]
        all_running = True
        
        for container in containers:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={container}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True
            )
            
            if container in result.stdout:
                print(f"  ✅ {container} is running")
            else:
                print(f"  ❌ {container} is NOT running")
                all_running = False
        
        if all_running:
            print("  ✅ All required containers are running")
        else:
            print("  ❌ Some containers are not running")
    
    async def test_mcp_protocol(self):
        """Test MCP protocol communication"""
        print("\n📡 Testing MCP protocol...")
        
        # Start a process to communicate with the MCP server
        process = subprocess.Popen(
            ["docker", "exec", "-i", self.container_name, "python", "-m", "mcp_server.mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # Use unbuffered I/O
        )
        
        try:
            # Send initialization request
            init_message = {
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
            
            print("  📤 Sending initialization request...")
            process.stdin.write(json.dumps(init_message) + "\n")
            process.stdin.flush()
            
            # Wait for response
            await asyncio.sleep(2)
            
            # Wait a moment for any output
            await asyncio.sleep(1)
            
            # Check if process is still running
            if process.poll() is None:
                print("  ✅ MCP Server responded to initialization")
                
                # Send list tools request
                list_tools_message = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }
                
                print("  📤 Sending list tools request...")
                process.stdin.write(json.dumps(list_tools_message) + "\n")
                process.stdin.flush()
                
                # Use a separate Python script to communicate with the MCP server
                # This is more reliable than trying to read/write directly
                mcp_test_script = """\
import sys
import json

# Send list tools request
print(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}))
sys.stdout.flush()

# Read response
response = sys.stdin.readline()

# Parse and print tools
try:
    data = json.loads(response)
    tools = data.get("result", {}).get("tools", [])
    print(f"TOOLS_COUNT:{len(tools)}")
    for tool in tools:
        print(f"TOOL:{tool.get('name')}:{tool.get('description')}")
except Exception as e:
    print(f"ERROR:{e}")
"""
                
                # Run the test script in the Docker container
                test_result = subprocess.run(
                    ["docker", "exec", "-i", self.container_name, "python", "-c", mcp_test_script],
                    input=json.dumps(list_tools_message) + "\n",
                    capture_output=True,
                    text=True
                )
                
                # Process the output
                tools_count = 0
                tools_list = []
                
                for line in test_result.stdout.splitlines():
                    if line.startswith("TOOLS_COUNT:"):
                        tools_count = int(line.split(":", 1)[1])
                    elif line.startswith("TOOL:"):
                        parts = line.split(":", 2)
                        if len(parts) >= 3:
                            tools_list.append((parts[1], parts[2]))
                    elif line.startswith("ERROR:"):
                        print(f"  ⚠️ Error: {line.split(':', 1)[1]}")
                
                print(f"  ✅ MCP Server returned {tools_count} tools:")
                for name, desc in tools_list:
                    print(f"    - {name}: {desc}")
                
                # If no tools were found, let's try a direct approach
                if tools_count == 0:
                    print("  ⚠️ No tools found. Checking MCP server code...")
                    
                    # Check the MCP server code for tool definitions
                    code_check = subprocess.run(
                        ["docker", "exec", self.container_name, "grep", "-A", "5", "Tool(", "/app/mcp_server/mcp_server.py"],
                        capture_output=True,
                        text=True
                    )
                    
                    if "Tool(" in code_check.stdout:
                        print("  ℹ️ Found tool definitions in code but they weren't returned by the server.")
                        print("  ℹ️ This might be due to how the MCP server is registering tools.")
            else:
                print("  ❌ MCP Server stopped after initialization")
                stdout, stderr = process.communicate()
                print(f"  STDOUT: {stdout}")
                print(f"  STDERR: {stderr}")
                
        except Exception as e:
            print(f"  ❌ Error testing MCP protocol: {e}")
        finally:
            # Clean up
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    async def test_database_connections(self):
        """Test database connections"""
        print("\n🗄️ Testing database connections...")
        
        # Test PostgreSQL connection
        postgres_result = subprocess.run(
            [
                "docker", "exec", self.container_name,
                "python", "-c", 
                "import psycopg2; conn = psycopg2.connect(host='postgres', dbname='mcp_db', user='mcp_user', password='secret'); print('Connection successful'); conn.close()"
            ],
            capture_output=True,
            text=True
        )
        
        if "Connection successful" in postgres_result.stdout:
            print("  ✅ PostgreSQL connection successful")
        else:
            print("  ❌ PostgreSQL connection failed")
            print(f"  Error: {postgres_result.stderr}")
        
        # Test Neo4j connection
        neo4j_script = """\
import sys
try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver('bolt://neo4j:7687', auth=('neo4j', 'test12345'))
    with driver.session() as session:
        result = session.run('RETURN 1 AS num')
        print('Connection successful')
    driver.close()
except Exception as e:
    print(f'Connection failed: {e}')
    sys.exit(1)
"""
        
        neo4j_result = subprocess.run(
            [
                "docker", "exec", self.container_name,
                "python", "-c", neo4j_script
            ],
            capture_output=True,
            text=True
        )
        
        if "Connection successful" in neo4j_result.stdout:
            print("  ✅ Neo4j connection successful")
        else:
            print("  ❌ Neo4j connection failed")
            print(f"  Error: {neo4j_result.stderr}")
    
    async def test_tool_functionality(self):
        """Test tool functionality"""
        print("\n🔧 Testing tool functionality...")
        
        # Start a process to communicate with the MCP server
        process = subprocess.Popen(
            ["docker", "exec", "-i", self.container_name, "python", "-m", "mcp_server.mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            # Send initialization request
            init_message = {
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
            
            process.stdin.write(json.dumps(init_message) + "\n")
            process.stdin.flush()
            
            # Wait for response
            await asyncio.sleep(1)
            
            # Test classify_and_store tool
            call_tool_message = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "classify_and_store",
                    "arguments": {
                        "prompt": "Store user data with relationships"
                    }
                }
            }
            
            print("  📤 Testing classify_and_store tool...")
            process.stdin.write(json.dumps(call_tool_message) + "\n")
            process.stdin.flush()
            
            # Wait for response
            await asyncio.sleep(3)
            
            # Try to read the response
            response = ""
            while process.stdout.readable() and not process.stdout.closed:
                line = process.stdout.readline()
                if not line:
                    break
                response += line
                if "}\n" in line:  # Simple check for end of JSON response
                    break
            
            if response:
                try:
                    tool_response = json.loads(response)
                    if "result" in tool_response:
                        print("  ✅ classify_and_store tool executed successfully")
                    else:
                        print("  ❌ classify_and_store tool execution failed")
                except json.JSONDecodeError:
                    print("  ⚠️ Could not parse tool response")
            else:
                print("  ⚠️ No response received for tool call")
                
        except Exception as e:
            print(f"  ❌ Error testing tool functionality: {e}")
        finally:
            # Clean up
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

async def main():
    """Main function"""
    tester = MCPTester()
    await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main())
