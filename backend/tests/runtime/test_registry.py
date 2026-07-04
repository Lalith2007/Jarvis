from app.runtime.registry import RuntimeRegistry, RuntimeProvider, ProviderMetadata
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
