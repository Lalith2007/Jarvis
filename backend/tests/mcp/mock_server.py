#!/usr/bin/env python3
"""
A dummy mock MCP server that implements the FastMCP stdio protocol for testing.
"""
import sys
import json
import time
import threading

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        
        line = line.strip()
        if not line:
            continue
            
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            
            # Simulate FastMCP log output mixing with JSON-RPC
            print("INFO: Mock FastMCP received message:", method, file=sys.stderr)
            print("non-json junk line to test robustness")
            sys.stdout.flush()

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "serverInfo": {"name": "mock-server", "version": "1.0.0"}
                    }
                }
                print(json.dumps(resp))
                sys.stdout.flush()
                
            elif method == "notifications/initialized":
                # Fire an async notification after initialized
                def delayed_notif():
                    time.sleep(0.1)
                    notif = {
                        "jsonrpc": "2.0",
                        "method": "notifications/message",
                        "params": {"message": "hello from mock server"}
                    }
                    print(json.dumps(notif))
                    sys.stdout.flush()
                threading.Thread(target=delayed_notif).start()

            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [
                            {
                                "name": "mock_tool",
                                "description": "A test tool",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {"arg": {"type": "string"}}
                                }
                            }
                        ]
                    }
                }
                print(json.dumps(resp))
                sys.stdout.flush()

            elif method == "tools/call":
                params = req.get("params", {})
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Called {params.get('name')} with {params.get('arguments')}"}]
                    }
                }
                print(json.dumps(resp))
                sys.stdout.flush()
                
            elif method == "ping":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {}
                }
                print(json.dumps(resp))
                sys.stdout.flush()

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
