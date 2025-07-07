#!/usr/bin/env python3
"""
MCP Server Wrapper for Windsurf
This script connects to the running MCP server Docker container and forwards stdin/stdout
"""

import subprocess
import sys
import os
import signal

def main():
    """Main function to run the MCP server wrapper"""
    print("Starting MCP server wrapper for Windsurf...", file=sys.stderr)
    
    try:
        # Connect to the running Docker container
        process = subprocess.Popen(
            [
                "docker", "exec", "-i", "mcp_server", 
                "python", "-m", "mcp_server.mcp_server"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # Unbuffered
        )
        
        # Forward stdin to the process
        def forward_stdin():
            while True:
                try:
                    line = sys.stdin.readline()
                    if not line:
                        break
                    process.stdin.write(line)
                    process.stdin.flush()
                except (BrokenPipeError, IOError):
                    break
        
        # Forward stdout from the process
        def forward_stdout():
            while True:
                try:
                    line = process.stdout.readline()
                    if not line:
                        break
                    sys.stdout.write(line)
                    sys.stdout.flush()
                except (BrokenPipeError, IOError):
                    break
        
        # Handle signals
        def handle_signal(sig, frame):
            process.terminate()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        
        # Start forwarding in the main thread
        try:
            forward_stdin()
        finally:
            process.terminate()
            process.wait()
    
    except Exception as e:
        print(f"Error in MCP server wrapper: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
