from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, List

class MCPConnectionStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    INITIALIZING = "initializing"
    DISCOVERING_TOOLS = "discovering_tools"
    READY = "ready"
    FAILED = "failed"
    TIMEOUT = "timeout"
    UNAVAILABLE = "unavailable"


class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    id: str | None = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: str | None = None
    result: Any | None = None
    error: Dict[str, Any] | None = None

class MCPServerMetadata(BaseModel):
    name: str
    version: str
    capabilities: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)


class MCPTool(BaseModel):
    """A single tool exposed by an MCP server (from tools/list)."""

    name: str
    description: str = ""
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    server: str = ""


class MCPServerConfig(BaseModel):
    """
    Configuration for connecting to an MCP server.

    transport: "stdio" (spawn `command`+`args`) or "http" (remote `endpoint`).
    auth_token/headers are attached to requests for authenticated servers.
    """

    name: str
    transport: str = "stdio"
    command: str | None = None
    args: List[str] = Field(default_factory=list)
    cwd: str | None = None
    env: Dict[str, str] = Field(default_factory=dict)
    endpoint: str | None = None
    auth_token: str | None = None
    headers: Dict[str, str] = Field(default_factory=dict)
    permissions: List[str] = Field(default_factory=list)
