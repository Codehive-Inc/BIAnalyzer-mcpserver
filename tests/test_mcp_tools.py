#!/usr/bin/env python3
"""
Test script for MCP server tools
This script tests each of the tools provided by the MCP server
"""

import asyncio
import json
import subprocess
import sys
import argparse
from typing import Dict, Any, Optional

class MCPToolTester:
    """Class to test MCP server tools"""
    
    def __init__(self):
        self.container_name = "mcp_server"
    
    async def run_tests(self, specific_tool=None):
        """Run all tool tests or a specific tool test"""
        print("🧪 Testing MCP Server Tools")
        print("=" * 50)
        
        if specific_tool:
            await self.test_specific_tool(specific_tool)
        else:
            # Test 1: List available tools
            await self.test_list_tools()
            
            # Test 2: classify_and_store tool
            await self.test_classify_and_store()
            
            # Test 3: query_postgres tool
            await self.test_query_postgres()
            
            # Test 4: query_neo4j tool
            await self.test_query_neo4j()
        
        print("=" * 50)
        print("🎉 Tool tests completed!")
    
    async def test_specific_tool(self, tool_name):
        """Test a specific tool based on its name"""
        print(f"\n🔍 Testing specific tool: {tool_name}")
        
        if tool_name == "classify_and_store":
            await self.test_classify_and_store()
        elif tool_name == "query_postgres":
            await self.test_query_postgres()
        elif tool_name == "query_neo4j":
            await self.test_query_neo4j()
        elif tool_name == "list" or tool_name == "tools_list":
            await self.test_list_tools()
        else:
            print(f"\n⚠️ Unknown tool: {tool_name}")
            print("Available tools: classify_and_store, query_postgres, query_neo4j, list")
    
    async def test_list_tools(self):
        """Test the tools/list endpoint by directly examining the handle_list_tools function"""
        print("\n📋 Testing tools/list endpoint...")
        
        # Create a Python script to directly call the handle_list_tools function
        test_script = """
#!/usr/bin/env python3
import sys
sys.path.append('/app')
from mcp_server.mcp_server import handle_list_tools
import json
import asyncio

async def main():
    # Call the handle_list_tools function directly
    result = await handle_list_tools()
    
    # Print the result
    if result and hasattr(result, 'tools'):
        print(f"Found {len(result.tools)} tools:")
        for tool in result.tools:
            print(f"Tool: {tool.name}")
            print(f"  Description: {tool.description}")
            print(f"  Schema: {json.dumps(tool.inputSchema, indent=2)}")
            print()
    else:
        print("No tools found or invalid result format")

asyncio.run(main())
"""
        
        # Save the script to a temporary file in the container
        script_path = "/tmp/test_list_tools_direct.py"
        subprocess.run(
            ["docker", "exec", "-i", self.container_name, "bash", "-c", f"cat > {script_path} << 'EOF'\n{test_script}\nEOF"]
        )
        
        # Make the script executable
        subprocess.run(
            ["docker", "exec", self.container_name, "chmod", "+x", script_path]
        )
        
        # Run the script
        result = subprocess.run(
            ["docker", "exec", "-i", self.container_name, "python", script_path],
            capture_output=True,
            text=True,
            timeout=10  # Add a timeout to prevent hanging
        )
        
        # Print the output
        if result.stdout:
            print(result.stdout)
            print("  ✅ Successfully retrieved tools list")
        
        if result.stderr:
            print("  ⚠️ Errors:")
            print(result.stderr)
    
    async def direct_tool_test(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Test a tool directly by importing it from the MCP server module"""
        print(f"\n🔧 Testing tool directly: {tool_name}")
        
        # Create a Python script to test the tool directly
        test_script = f"""
#!/usr/bin/env python3
import sys
sys.path.append('/app')
from mcp_server.mcp_server import handle_{tool_name}
import json
import asyncio

async def main():
    result = await handle_{tool_name}({json.dumps(arguments)})
    print(json.dumps(result, default=str, indent=2))

asyncio.run(main())
"""
        
        # Save the script to a temporary file in the container
        script_path = f"/tmp/test_{tool_name}.py"
        subprocess.run(
            ["docker", "exec", "-i", self.container_name, "bash", "-c", f"cat > {script_path} << 'EOF'\n{test_script}\nEOF"]
        )
        
        # Make the script executable
        subprocess.run(
            ["docker", "exec", self.container_name, "chmod", "+x", script_path]
        )
        
        # Run the script
        result = subprocess.run(
            ["docker", "exec", "-i", self.container_name, "python", script_path],
            capture_output=True,
            text=True
        )
        
        # Print the output
        if result.stdout:
            print("  📝 Tool output:")
            print(result.stdout)
            return {"success": True, "output": result.stdout}
        
        if result.stderr:
            print("  ⚠️ Tool error:")
            print(result.stderr)
            return {"success": False, "error": result.stderr}
        
        return None
    
    async def test_classify_and_store(self):
        """Test the classify_and_store tool"""
        print("\n📊 Testing classify_and_store tool...")
        
        # Call the tool with a test prompt
        result = await self.direct_tool_test(
            "classify_and_store", 
            {"prompt": "Store customer information with name John Doe, age 35, and purchase history"}
        )
        
        if result and result.get("success"):
            print("  ✅ classify_and_store tool executed successfully")
        else:
            print("  ❌ classify_and_store tool execution failed")
    
    async def test_query_postgres(self):
        """Test the query_postgres tool"""
        print("\n🗃️ Testing query_postgres tool...")
        
        # Call the tool with a test query
        result = await self.direct_tool_test(
            "query_postgres", 
            {"query": "SELECT * FROM users LIMIT 5"}
        )
        
        if result and result.get("success"):
            print("  ✅ query_postgres tool executed successfully")
        else:
            print("  ❌ query_postgres tool execution failed")
    
    async def test_query_neo4j(self):
        """Test the query_neo4j tool"""
        print("\n🕸️ Testing query_neo4j tool...")
        
        # Call the tool with a test query
        result = await self.direct_tool_test(
            "query_neo4j", 
            {"query": "MATCH (n) RETURN n LIMIT 5"}
        )
        
        if result and result.get("success"):
            print("  ✅ query_neo4j tool executed successfully")
        else:
            print("  ❌ query_neo4j tool execution failed")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test MCP server tools")
    parser.add_argument("--tool", help="Specific tool to test (classify_and_store, query_postgres, query_neo4j, list)")
    args = parser.parse_args()
    
    tester = MCPToolTester()
    await tester.run_tests(args.tool)

if __name__ == "__main__":
    asyncio.run(main())
