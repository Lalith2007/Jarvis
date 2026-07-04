class MCPRegistry:
    def __init__(self):
        self.servers = {}
        
    def register(self, name: str):
        self.servers[name] = True
mcp_registry = MCPRegistry()
