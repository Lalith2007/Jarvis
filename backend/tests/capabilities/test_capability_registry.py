import pytest
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityManifest, CapabilityCategory, CapabilityConfig,
    CapabilityContext, CapabilityDiagnostics, CapabilityResult
)

class MockCapability(BaseCapability):
    def __init__(self, manifest):
        super().__init__(manifest, CapabilityConfig())
    def initialize(self, ctx): pass
    def validate(self, ctx): pass
    def cleanup(self, ctx): pass
    def health_check(self): return "healthy"
    def estimate_cost(self, ctx): return 0.0
    def estimate_latency(self, ctx): return 0.0
    def execute(self, ctx, diag): return CapabilityResult(success=True, status="ok")

def test_successful_registration():
    registry = CapabilityRegistry()
    manifest = CapabilityManifest(
        id="test.cap", name="Test", version="1.0", author="Sys",
        description="test", category=CapabilityCategory.CUSTOM
    )
    cap = MockCapability(manifest)
    registry.register(cap)
    
    assert registry.get("test.cap") == cap
    assert len(registry.list()) == 1

def test_missing_dependency():
    registry = CapabilityRegistry()
    manifest = CapabilityManifest(
        id="test.cap", name="Test", version="1.0", author="Sys",
        description="test", category=CapabilityCategory.CUSTOM,
        dependencies=["missing.cap"]
    )
    cap = MockCapability(manifest)
    
    with pytest.raises(ValueError, match="Missing dependency"):
        registry.register(cap)

def test_cyclic_dependency():
    registry = CapabilityRegistry()
    
    cap_a = MockCapability(CapabilityManifest(
        id="a", name="A", version="1.0", author="Sys",
        description="A", category=CapabilityCategory.CUSTOM,
    ))
    registry.register(cap_a)
    
    cap_b = MockCapability(CapabilityManifest(
        id="b", name="B", version="1.0", author="Sys",
        description="B", category=CapabilityCategory.CUSTOM,
        dependencies=["a"]
    ))
    registry.register(cap_b)
    
    # Update cap_a to depend on cap_b, creating a cycle
    cap_a.manifest.dependencies = ["b"]
    
    with pytest.raises(ValueError, match="Cyclic dependency"):
        registry._validate_no_cycles()

def test_export_state():
    registry = CapabilityRegistry()
    manifest = CapabilityManifest(
        id="test.cap", name="Test", version="1.0", author="Sys",
        description="test", category=CapabilityCategory.CUSTOM
    )
    cap = MockCapability(manifest)
    registry.register(cap)
    
    state = registry.export_state()
    assert "capabilities" in state
    assert len(state["capabilities"]) == 1
    assert state["capabilities"][0]["id"] == "test.cap"

def test_registry_reload():
    registry = CapabilityRegistry()
    cap = MockCapability(CapabilityManifest(
        id="test.cap", name="Test", version="1.0", author="Sys",
        description="test", category=CapabilityCategory.CUSTOM
    ))
    registry.register(cap)
    
    assert len(registry.list()) == 1
    registry.reload()
    assert len(registry.list()) == 0
