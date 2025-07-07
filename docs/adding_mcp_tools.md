# Adding and Testing MCP Tools

This guide explains how to add new tools to the MCP server and how to test them effectively.

## Understanding MCP Tools

MCP (Model Context Protocol) tools are functions that can be called by clients through the MCP protocol. Each tool:

1. Has a unique name
2. Has a description
3. Accepts specific input parameters defined by a JSON schema
4. Returns results that can be consumed by clients

## Adding a New Tool

To add a new tool to the MCP server, follow these steps:

### 1. Define the Tool Handler Function

In `mcp_server/mcp_server.py`, add a new async function to handle your tool's functionality:

```python
async def handle_your_new_tool(arguments: Dict[str, Any]) -> Any:
    """
    Implementation of your new tool
    
    Args:
        arguments: Dictionary containing the tool's input parameters
        
    Returns:
        Tool execution result
    """
    # Your tool implementation here
    result = "Your tool result"
    
    # Return the result as a TextContent object
    return TextContent(type="text", text=result)
```

### 2. Register the Tool in the Tools List

In the `handle_list_tools()` function, add your new tool to the list of tools:

```python
@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    return ListToolsResult(
        tools=[
            # Existing tools...
            
            Tool(
                name="your_new_tool",
                description="Description of what your new tool does",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "Description of parameter 1"
                        },
                        "param2": {
                            "type": "integer",
                            "description": "Description of parameter 2"
                        }
                        # Add more parameters as needed
                    },
                    "required": ["param1"]  # List required parameters
                }
            )
        ]
    )
```

### 3. Register the Tool Call Handler

Add a decorator to register your tool handler function:

```python
@server.call_tool("your_new_tool")
async def handle_your_new_tool(arguments: Dict[str, Any]) -> Any:
    # Your implementation here
```

## Testing MCP Tools

There are several ways to test MCP tools:

### Method 1: Direct Function Testing

This method tests the tool function directly by importing it from the MCP server module:

```python
# Create a test script inside the Docker container
docker exec -it mcp_server bash -c "cat > /tmp/test_your_tool.py << 'EOF'
import sys
sys.path.append('/app')
from mcp_server.mcp_server import handle_your_new_tool
import json
import asyncio

async def main():
    result = await handle_your_new_tool({'param1': 'value1', 'param2': 42})
    print(json.dumps(result, default=str, indent=2))

asyncio.run(main())
EOF"

# Run the test script
docker exec -it mcp_server python /tmp/test_your_tool.py
```

### Method 2: Using the MCP Protocol

This method tests the tool through the MCP protocol, which is how clients would call it:

```python
# Create a test script inside the Docker container
docker exec -it mcp_server bash -c "cat > /tmp/test_mcp_protocol.py << 'EOF'
import sys
import json

# Initialize the MCP server
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

print(json.dumps(init_message))
sys.stdout.flush()

# Read initialization response
init_response = sys.stdin.readline()

# Call the tool
tool_message = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "your_new_tool",
        "arguments": {
            "param1": "value1",
            "param2": 42
        }
    }
}

print(json.dumps(tool_message))
sys.stdout.flush()

# Read tool response
tool_response = sys.stdin.readline()
print(f"RESPONSE:{tool_response}")
EOF"

# Run the test
docker exec -it mcp_server bash -c "python -m mcp_server.mcp_server < /tmp/test_mcp_protocol.py"
```

### Method 3: Using the Test Framework

The most convenient way is to use our test framework in `tests/test_mcp_tools.py`:

1. Add a new test method to the `MCPToolTester` class:

```python
async def test_your_new_tool(self):
    """Test the your_new_tool tool"""
    print("\n🔧 Testing your_new_tool...")
    
    # Call the tool with test parameters
    result = await self.direct_tool_test(
        "your_new_tool", 
        {"param1": "value1", "param2": 42}
    )
    
    if result and result.get("success"):
        print("  ✅ your_new_tool executed successfully")
    else:
        print("  ❌ your_new_tool execution failed")
```

2. Add your tool to the `test_specific_tool` method:

```python
async def test_specific_tool(self, tool_name):
    """Test a specific tool based on its name"""
    print(f"\n🔍 Testing specific tool: {tool_name}")
    
    if tool_name == "classify_and_store":
        await self.test_classify_and_store()
    elif tool_name == "query_postgres":
        await self.test_query_postgres()
    elif tool_name == "query_neo4j":
        await self.test_query_neo4j()
    elif tool_name == "your_new_tool":  # Add your tool here
        await self.test_your_new_tool()
    else:
        print(f"\n⚠️ Unknown tool: {tool_name}")
        print("Available tools: classify_and_store, query_postgres, query_neo4j, your_new_tool")
```

3. Add your tool to the `run_tests` method:

```python
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
        
        # Test 5: your_new_tool
        await self.test_your_new_tool()
    
    print("=" * 50)
    print("🎉 Tool tests completed!")
```

4. Run the test:

```bash
# Test all tools
python tests/test_mcp_tools.py

# Test only your new tool
python tests/test_mcp_tools.py --tool your_new_tool
```

## Troubleshooting

If your tool is not appearing in the tools list:

1. Verify that you've added it to the `handle_list_tools()` function
2. Check that you've used the correct decorator: `@server.call_tool("your_tool_name")`
3. Ensure the tool name in the decorator matches the name in the tools list
4. Check the MCP server logs for any errors: `docker logs mcp_server`

If your tool is returning errors:

1. Verify that your input schema matches the actual parameters your function expects
2. Check for any exceptions in your tool implementation
3. Test the tool directly using Method 1 to isolate MCP protocol issues

## Example: Adding a Simple Echo Tool

Here's a complete example of adding a simple echo tool:

```python
# In mcp_server/mcp_server.py

# 1. Add the tool to the tools list
@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    return ListToolsResult(
        tools=[
            # Existing tools...
            
            Tool(
                name="echo",
                description="Echoes back the input message",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to echo back"
                        }
                    },
                    "required": ["message"]
                }
            )
        ]
    )

# 2. Implement and register the tool handler
@server.call_tool("echo")
async def handle_echo(arguments: Dict[str, Any]) -> Any:
    message = arguments.get("message", "")
    return TextContent(type="text", text=f"Echo: {message}")
```

Test the new echo tool:

```bash
# Direct function test
docker exec -it mcp_server bash -c "cat > /tmp/test_echo.py << 'EOF'
import sys
sys.path.append('/app')
from mcp_server.mcp_server import handle_echo
import json
import asyncio

async def main():
    result = await handle_echo({'message': 'Hello, MCP!'})
    print(json.dumps(result, default=str, indent=2))

asyncio.run(main())
EOF"

docker exec -it mcp_server python /tmp/test_echo.py
```
