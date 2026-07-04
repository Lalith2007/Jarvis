import os

BASE_DIR = "/Users/lalithpraveen/Desktop/Jarvis/backend"

runtime_files = {
    "app/runtime/models.py": '''from enum import Enum
from typing import Any
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field
from app.capabilities.models import CapabilityType

class RuntimeStatus(str, Enum):
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CLEANED_UP = "cleaned_up"

class RuntimeResult(BaseModel):
    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict = Field(default_factory=dict)
    execution_time_ms: float = 0.0

class SecurityAction(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    CONNECT = "connect"

class RuntimePermission(BaseModel):
    capability: CapabilityType
    action: SecurityAction
    resource: str | None = None
''',
    "app/runtime/session.py": '''from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field
from app.runtime.models import RuntimeStatus, RuntimeResult

class RuntimeSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    status: RuntimeStatus = RuntimeStatus.CREATED
    active_runtime: str | None = None
    opened_resources: list[str] = Field(default_factory=list)
    history: list[RuntimeResult] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def transition_to(self, new_status: RuntimeStatus) -> None:
        self.status = new_status
        self.updated_at = datetime.now()

    def add_result(self, result: RuntimeResult) -> None:
        self.history.append(result)
        self.updated_at = datetime.now()
        
    def cleanup(self) -> None:
        self.opened_resources.clear()
        self.transition_to(RuntimeStatus.CLEANED_UP)
''',
    "app/runtime/registry.py": '''from typing import Any, Callable, Dict
from pydantic import BaseModel
from app.capabilities.models import CapabilityType

class ProviderMetadata(BaseModel):
    name: str
    version: str
    description: str
    is_healthy: bool = True

class RuntimeProvider(BaseModel):
    capability: CapabilityType
    handler: Callable
    metadata: ProviderMetadata
    priority: int = 0

class RuntimeRegistry:
    def __init__(self):
        self._providers: Dict[CapabilityType, list[RuntimeProvider]] = {}

    def register(self, provider: RuntimeProvider) -> None:
        if provider.capability not in self._providers:
            self._providers[provider.capability] = []
        
        for p in self._providers[provider.capability]:
            if p.handler == provider.handler:
                return

        self._providers[provider.capability].append(provider)
        self._providers[provider.capability].sort(key=lambda p: p.priority, reverse=True)

    def unregister(self, capability: CapabilityType, handler_name: str) -> None:
        if capability in self._providers:
            self._providers[capability] = [
                p for p in self._providers[capability] 
                if p.handler.__name__ != handler_name
            ]

    def get_provider(self, capability: CapabilityType) -> RuntimeProvider | None:
        providers = self._providers.get(capability, [])
        for p in providers:
            if p.metadata.is_healthy:
                return p
        return None

runtime_registry = RuntimeRegistry()
''',
    "app/runtime/security.py": '''from app.capabilities.models import CapabilityType
from app.runtime.models import SecurityAction, RuntimePermission
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self):
        self._policies: dict[CapabilityType, set[SecurityAction]] = {}
        
    def set_policy(self, capability: CapabilityType, allowed_actions: list[SecurityAction]) -> None:
        self._policies[capability] = set(allowed_actions)

    def validate_permission(self, capability: CapabilityType, action: SecurityAction, resource: str | None = None) -> bool:
        allowed = self._policies.get(capability, set())
        is_allowed = action in allowed
        
        decision = "ALLOWED" if is_allowed else "DENIED"
        logger.info(f"Security Audit: {decision} {action.value} on {capability.value} (resource: {resource})")
        
        return is_allowed

security_manager = SecurityManager()
security_manager.set_policy(CapabilityType.FILESYSTEM, [SecurityAction.READ, SecurityAction.WRITE])
security_manager.set_policy(CapabilityType.TERMINAL, [SecurityAction.EXECUTE])
security_manager.set_policy(CapabilityType.PYTHON_RUNTIME, [SecurityAction.EXECUTE])
security_manager.set_policy(CapabilityType.BROWSER, [SecurityAction.CONNECT, SecurityAction.READ, SecurityAction.WRITE])
''',
    "app/runtime/executor.py": '''from app.runtime.models import RuntimeResult
import time
from typing import Any

class RuntimeExecutor:
    def execute(self, handler, *args, **kwargs) -> RuntimeResult:
        start_time = time.time()
        try:
            output = handler(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            return RuntimeResult(success=True, output=output, execution_time_ms=duration)
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return RuntimeResult(success=False, error=str(e), execution_time_ms=duration)

runtime_executor = RuntimeExecutor()
''',
    "app/runtime/dispatcher.py": '''from app.runtime.registry import runtime_registry
from app.runtime.executor import runtime_executor
from app.runtime.models import RuntimeResult, SecurityAction, RuntimeStatus
from app.runtime.security import security_manager
from app.capabilities.models import CapabilityType
from app.runtime.session import RuntimeSession

class RuntimeDispatcher:
    def dispatch(
        self, 
        capability: CapabilityType, 
        session: RuntimeSession, 
        action: SecurityAction = SecurityAction.EXECUTE,
        resource: str | None = None,
        *args, 
        **kwargs
    ) -> RuntimeResult:
        if not security_manager.validate_permission(capability, action, resource):
            result = RuntimeResult(success=False, error=f"Permission denied: {action.value} on {capability.value}")
            session.add_result(result)
            return result
            
        provider = runtime_registry.get_provider(capability)
        if not provider:
            result = RuntimeResult(success=False, error=f"No healthy runtime provider found for {capability.value}")
            session.add_result(result)
            return result
            
        session.transition_to(RuntimeStatus.RUNNING)
        session.active_runtime = provider.metadata.name
        
        result = runtime_executor.execute(provider.handler, session, *args, **kwargs)
        
        session.add_result(result)
        
        if result.success:
            session.transition_to(RuntimeStatus.COMPLETED)
        else:
            session.transition_to(RuntimeStatus.FAILED)
            
        return result

runtime_dispatcher = RuntimeDispatcher()
''',
    "app/runtime/manager.py": '''from typing import Dict
from app.runtime.session import RuntimeSession
from app.runtime.models import RuntimeStatus

class RuntimeManager:
    def __init__(self):
        self._active_sessions: Dict[str, RuntimeSession] = {}

    def create_session(self) -> RuntimeSession:
        session = RuntimeSession()
        session.transition_to(RuntimeStatus.STARTING)
        self._active_sessions[session.id] = session
        return session
        
    def get_session(self, session_id: str) -> RuntimeSession | None:
        return self._active_sessions.get(session_id)

    def cleanup_session(self, session_id: str) -> None:
        if session_id in self._active_sessions:
            session = self._active_sessions[session_id]
            session.cleanup()
            del self._active_sessions[session_id]
            
    def get_statistics(self) -> dict:
        return {
            "active_sessions_count": len(self._active_sessions),
        }

runtime_manager = RuntimeManager()
''',
    "app/runtime/service.py": '''from app.runtime.dispatcher import runtime_dispatcher
from app.runtime.manager import runtime_manager
from app.capabilities.models import CapabilityType
from app.runtime.models import SecurityAction
from app.runtime.session import RuntimeSession

class RuntimeService:
    def create_session(self) -> RuntimeSession:
        return runtime_manager.create_session()
        
    def execute_capability(self, capability: CapabilityType, session: RuntimeSession, action: SecurityAction = SecurityAction.EXECUTE, resource: str | None = None, *args, **kwargs):
        return runtime_dispatcher.dispatch(capability, session, action, resource, *args, **kwargs)
        
    def cleanup_session(self, session: RuntimeSession) -> None:
        runtime_manager.cleanup_session(session.id)

runtime_service = RuntimeService()
''',
    "app/mcp/models.py": '''from enum import Enum
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
''',
    "app/mcp/protocol.py": '''import json
from app.mcp.models import MCPRequest, MCPResponse

class MCPProtocol:
    def serialize_request(self, request: MCPRequest) -> str:
        return request.model_dump_json(exclude_none=True)

    def parse_response(self, data: str) -> MCPResponse:
        try:
            parsed = json.loads(data)
            return MCPResponse(**parsed)
        except Exception as e:
            return MCPResponse(error={"code": -32700, "message": "Parse error", "data": str(e)})

mcp_protocol = MCPProtocol()
''',
    "app/mcp/transport.py": '''from app.mcp.models import MCPConnectionStatus

class MCPTransport:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.status = MCPConnectionStatus.DISCONNECTED

    def connect(self) -> bool:
        self.status = MCPConnectionStatus.CONNECTED
        return True

    def disconnect(self) -> None:
        self.status = MCPConnectionStatus.DISCONNECTED

    def send(self, data: str) -> str:
        if self.status != MCPConnectionStatus.CONNECTED:
            raise ConnectionError("Not connected")
        return '{"result": "success"}'
''',
    "app/mcp/registry.py": '''from typing import Dict
from app.mcp.models import MCPServerMetadata

class MCPRegistry:
    def __init__(self):
        self._servers: Dict[str, MCPServerMetadata] = {}

    def register(self, metadata: MCPServerMetadata) -> None:
        self._servers[metadata.name] = metadata

    def unregister(self, name: str) -> None:
        self._servers.pop(name, None)

    def get_server(self, name: str) -> MCPServerMetadata | None:
        return self._servers.get(name)

    def list_servers(self) -> list[MCPServerMetadata]:
        return list(self._servers.values())

mcp_registry = MCPRegistry()
''',
    "app/mcp/client.py": '''from app.mcp.transport import MCPTransport
from app.mcp.protocol import mcp_protocol
from app.mcp.models import MCPRequest, MCPResponse, MCPConnectionStatus

class MCPClient:
    def __init__(self, name: str, endpoint: str):
        self.name = name
        self.transport = MCPTransport(endpoint)

    def connect(self) -> bool:
        return self.transport.connect()

    def disconnect(self) -> None:
        self.transport.disconnect()

    def get_status(self) -> MCPConnectionStatus:
        return self.transport.status

    def send_request(self, request: MCPRequest) -> MCPResponse:
        serialized = mcp_protocol.serialize_request(request)
        try:
            raw_response = self.transport.send(serialized)
            return mcp_protocol.parse_response(raw_response)
        except Exception as e:
            return MCPResponse(id=request.id, error={"message": str(e)})
''',
    "app/mcp/manager.py": '''from typing import Dict
from app.mcp.client import MCPClient
from app.mcp.registry import mcp_registry
from app.mcp.models import MCPServerMetadata

class MCPManager:
    def __init__(self):
        self._clients: Dict[str, MCPClient] = {}

    def register_server(self, name: str, endpoint: str, capabilities: list[str]) -> None:
        metadata = MCPServerMetadata(name=name, version="1.0.0", capabilities=capabilities)
        mcp_registry.register(metadata)
        
        client = MCPClient(name, endpoint)
        self._clients[name] = client
        client.connect()

    def get_client(self, name: str) -> MCPClient | None:
        return self._clients.get(name)

    def remove_server(self, name: str) -> None:
        mcp_registry.unregister(name)
        client = self._clients.pop(name, None)
        if client:
            client.disconnect()

mcp_manager = MCPManager()
''',
    "tests/runtime/test_registry.py": '''from app.runtime.registry import RuntimeRegistry, RuntimeProvider, ProviderMetadata
from app.capabilities.models import CapabilityType

def test_registry_lifecycle():
    registry = RuntimeRegistry()
    def dummy_handler(): pass
    
    provider = RuntimeProvider(
        capability=CapabilityType.FILESYSTEM,
        handler=dummy_handler,
        metadata=ProviderMetadata(name="TestFS", version="1.0", description="Test")
    )
    
    registry.register(provider)
    assert registry.get_provider(CapabilityType.FILESYSTEM) is not None
    
    registry.register(provider)
    assert len(registry._providers[CapabilityType.FILESYSTEM]) == 1
    
    registry.unregister(CapabilityType.FILESYSTEM, "dummy_handler")
    assert registry.get_provider(CapabilityType.FILESYSTEM) is None
''',
    "tests/runtime/test_dispatcher.py": '''from app.runtime.dispatcher import runtime_dispatcher
from app.runtime.registry import runtime_registry, RuntimeProvider, ProviderMetadata
from app.capabilities.models import CapabilityType
from app.runtime.session import RuntimeSession
from app.runtime.security import security_manager
from app.runtime.models import SecurityAction

def test_dispatch_success():
    def mock_handler(session, *args, **kwargs): return "success data"
    
    provider = RuntimeProvider(
        capability=CapabilityType.FILESYSTEM,
        handler=mock_handler,
        metadata=ProviderMetadata(name="TestFS", version="1.0", description="Test")
    )
    runtime_registry.register(provider)
    
    session = RuntimeSession()
    
    result = runtime_dispatcher.dispatch(CapabilityType.FILESYSTEM, session, SecurityAction.READ)
    assert result.success is True
    assert result.output == "success data"
    
def test_dispatch_failure():
    def failing_handler(session, *args, **kwargs): raise ValueError("Crash")
    
    provider = RuntimeProvider(
        capability=CapabilityType.PYTHON_RUNTIME,
        handler=failing_handler,
        metadata=ProviderMetadata(name="TestPy", version="1.0", description="Test")
    )
    runtime_registry.register(provider)
    
    session = RuntimeSession()
    result = runtime_dispatcher.dispatch(CapabilityType.PYTHON_RUNTIME, session, SecurityAction.EXECUTE)
    assert result.success is False
    assert "Crash" in result.error
''',
    "tests/runtime/test_session.py": '''from app.runtime.manager import runtime_manager
from app.runtime.models import RuntimeStatus

def test_session_lifecycle():
    session = runtime_manager.create_session()
    assert session.id is not None
    assert session.status == RuntimeStatus.STARTING
    
    session.opened_resources.append("file.txt")
    
    runtime_manager.cleanup_session(session.id)
    assert len(session.opened_resources) == 0
    assert session.status == RuntimeStatus.CLEANED_UP
    assert runtime_manager.get_session(session.id) is None
''',
    "tests/runtime/test_security.py": '''from app.runtime.security import security_manager
from app.capabilities.models import CapabilityType
from app.runtime.models import SecurityAction

def test_permission_denied():
    result = security_manager.validate_permission(CapabilityType.BROWSER, SecurityAction.EXECUTE)
    assert result is False

def test_permission_allowed():
    result = security_manager.validate_permission(CapabilityType.FILESYSTEM, SecurityAction.READ)
    assert result is True
''',
    "tests/mcp/test_registry.py": '''from app.mcp.manager import mcp_manager
from app.mcp.registry import mcp_registry

def test_mcp_registration_discovery():
    mcp_manager.register_server("TestMCP", "http://localhost:8000", ["tool_usage"])
    
    server = mcp_registry.get_server("TestMCP")
    assert server is not None
    assert "tool_usage" in server.capabilities
    
    client = mcp_manager.get_client("TestMCP")
    assert client is not None
    assert client.get_status() == "connected"
    
    mcp_manager.remove_server("TestMCP")
    assert mcp_registry.get_server("TestMCP") is None
''',
    "tests/mcp/test_protocol.py": '''from app.mcp.protocol import mcp_protocol
from app.mcp.models import MCPRequest

def test_mcp_serialization():
    req = MCPRequest(method="execute", params={"arg": 1}, id="req-1")
    serialized = mcp_protocol.serialize_request(req)
    assert '"execute"' in serialized
    
    resp = mcp_protocol.parse_response('{"id": "req-1", "result": "success"}')
    assert resp.result == "success"
'''
}

def setup():
    for filepath, content in runtime_files.items():
        full_path = os.path.join(BASE_DIR, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

if __name__ == "__main__":
    setup()
    print("Upgrade complete")
