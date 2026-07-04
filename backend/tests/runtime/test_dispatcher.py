from app.runtime.dispatcher import runtime_dispatcher
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
