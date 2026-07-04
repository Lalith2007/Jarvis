from pydantic import BaseModel

class MCPConnection(BaseModel):
    server_id: str
    status: str
