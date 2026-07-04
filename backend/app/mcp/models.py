from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, List

class MCPConnectionStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class MCPRequest(BaseModel):
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    id: str | None = None

class MCPResponse(BaseModel):
    id: str | None = None
    result: Any | None = None
    error: Dict[str, Any] | None = None

class MCPServerMetadata(BaseModel):
    name: str
    version: str
    capabilities: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
