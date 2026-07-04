import os

BASE_DIR = "/Users/lalithpraveen/Desktop/Jarvis/backend"

runtime_files = {
    "app/runtime/models.py": '''from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class RuntimeStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class RuntimeResult(BaseModel):
    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict = Field(default_factory=dict)
''',
    "app/runtime/security.py": '''from app.capabilities.models import CapabilityType

class SecurityManager:
    def validate_permission(self, capability: CapabilityType, action: str) -> bool:
        return True

security_manager = SecurityManager()
''',
    "app/runtime/session.py": '''from uuid import uuid4
from pydantic import BaseModel, Field

class RuntimeSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    active_runtime: str | None = None
    opened_resources: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    
    def cleanup(self):
        self.opened_resources.clear()
''',
    "app/runtime/registry.py": '''from typing import Any, Callable

class RuntimeRegistry:
    def __init__(self):
        self._handlers = {}

    def register(self, capability: str, handler: Callable):
        self._handlers[capability] = handler

    def get_handler(self, capability: str) -> Callable | None:
        return self._handlers.get(capability)

runtime_registry = RuntimeRegistry()
''',
    "app/runtime/executor.py": '''from app.runtime.models import RuntimeResult
from typing import Any

class RuntimeExecutor:
    def execute(self, handler, *args, **kwargs) -> RuntimeResult:
        try:
            output = handler(*args, **kwargs)
            return RuntimeResult(success=True, output=output)
        except Exception as e:
            return RuntimeResult(success=False, error=str(e))

runtime_executor = RuntimeExecutor()
''',
    "app/runtime/dispatcher.py": '''from app.runtime.registry import runtime_registry
from app.runtime.executor import runtime_executor
from app.runtime.models import RuntimeResult
from app.capabilities.models import CapabilityDecision

class RuntimeDispatcher:
    def dispatch(self, capability: str, *args, **kwargs) -> RuntimeResult:
        handler = runtime_registry.get_handler(capability)
        if not handler:
            return RuntimeResult(success=False, error=f"No runtime handler for {capability}")
        return runtime_executor.execute(handler, *args, **kwargs)

runtime_dispatcher = RuntimeDispatcher()
''',
    "app/runtime/result.py": '''from app.runtime.models import RuntimeResult

def create_success(output: str) -> RuntimeResult:
    return RuntimeResult(success=True, output=output)

def create_error(error: str) -> RuntimeResult:
    return RuntimeResult(success=False, error=error)
''',
    "app/runtime/manager.py": '''from app.runtime.session import RuntimeSession
from app.runtime.dispatcher import runtime_dispatcher

class RuntimeManager:
    def create_session(self) -> RuntimeSession:
        return RuntimeSession()

runtime_manager = RuntimeManager()
''',
    "app/runtime/service.py": '''from app.runtime.dispatcher import runtime_dispatcher
from app.runtime.manager import runtime_manager
from app.capabilities.models import CapabilityType

class RuntimeService:
    def execute_capability(self, capability: CapabilityType, *args, **kwargs):
        return runtime_dispatcher.dispatch(capability.value, *args, **kwargs)

runtime_service = RuntimeService()
''',
    "app/runtime/__init__.py": '''from app.runtime.service import runtime_service
__all__ = ["runtime_service"]
''',
    "app/mcp/models.py": '''from pydantic import BaseModel

class MCPConnection(BaseModel):
    server_id: str
    status: str
''',
    "app/mcp/transport.py": '''class MCPTransport:
    def connect(self):
        pass
''',
    "app/mcp/protocol.py": '''class MCPProtocol:
    def parse(self, data):
        return data
''',
    "app/mcp/registry.py": '''class MCPRegistry:
    def __init__(self):
        self.servers = {}
        
    def register(self, name: str):
        self.servers[name] = True
mcp_registry = MCPRegistry()
''',
    "app/mcp/client.py": '''class MCPClient:
    pass
''',
    "app/mcp/manager.py": '''class MCPManager:
    pass
''',
    "app/mcp/__init__.py": '''# MCP Module
''',
    "tests/runtime/test_registry.py": '''from app.runtime.registry import runtime_registry
def test_registry():
    assert runtime_registry is not None
''',
    "tests/runtime/test_dispatcher.py": '''from app.runtime.dispatcher import runtime_dispatcher
def test_dispatcher():
    assert runtime_dispatcher is not None
''',
    "tests/runtime/test_session.py": '''from app.runtime.session import RuntimeSession
def test_session():
    s = RuntimeSession()
    assert s.id is not None
''',
    "tests/runtime/test_security.py": '''from app.runtime.security import security_manager
from app.capabilities.models import CapabilityType
def test_security():
    assert security_manager.validate_permission(CapabilityType.FILESYSTEM, "read")
''',
    "tests/mcp/test_registry.py": '''from app.mcp.registry import mcp_registry
def test_mcp_registry():
    mcp_registry.register("test")
    assert "test" in mcp_registry.servers
'''
}

def setup():
    for filepath, content in runtime_files.items():
        full_path = os.path.join(BASE_DIR, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
            
    # Modify execution/models.py
    exec_models_path = os.path.join(BASE_DIR, "app/execution/models.py")
    with open(exec_models_path, "r") as f:
        content = f.read()
    
    if "runtime_session: Any = None" not in content:
        content = content.replace(
            "available_capabilities: list[CapabilityType] = Field(default_factory=list)",
            "available_capabilities: list[CapabilityType] = Field(default_factory=list)\\n\\n    runtime_session: Any = None\\n    runtime_state: dict = Field(default_factory=dict)\\n    runtime_results: dict = Field(default_factory=dict)\\n    active_capabilities: list[CapabilityType] = Field(default_factory=list)\\n    executed_capabilities: list[CapabilityType] = Field(default_factory=list)"
        )
        with open(exec_models_path, "w") as f:
            f.write(content)

if __name__ == "__main__":
    setup()
    print("Setup complete")
