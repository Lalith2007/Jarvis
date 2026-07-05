import pytest
import time
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.executor import CapabilityExecutorLifecycle
from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityManifest, CapabilityCategory, CapabilityConfig,
    CapabilityContext, CapabilityDiagnostics, CapabilityResult
)

class StressMockCapability(BaseCapability):
    def __init__(self, id_val):
        manifest = CapabilityManifest(
            id=id_val, name=f"Stress_{id_val}", version="1.0", author="Sys",
            description="test", category=CapabilityCategory.CUSTOM
        )
        super().__init__(manifest, CapabilityConfig())

    def initialize(self, ctx): pass
    def validate(self, ctx): pass
    def cleanup(self, ctx): pass
    def health_check(self): return "healthy"
    def estimate_cost(self, ctx): return 0.0
    def estimate_latency(self, ctx): return 0.0
    
    def execute(self, ctx, diag): 
        # Simulated fast workload
        return CapabilityResult(success=True, status="ok")


def test_registry_stress():
    registry = CapabilityRegistry()
    start_time = time.time()
    
    # Register 500 capabilities
    for i in range(500):
        cap = StressMockCapability(f"mock.cap.{i}")
        registry.register(cap)
        
    registration_time = time.time() - start_time
    assert len(registry.list()) == 500
    assert registration_time < 2.0  # Should be extremely fast
    
    # Execute random graphs (simulate capability executions)
    executor = CapabilityExecutorLifecycle()
    ctx = CapabilityContext(mission_id="m1", graph_id="g1", execution_id="e1", node_id="n1")
    
    execute_start = time.time()
    for i in range(500):
        cap = registry.get(f"mock.cap.{i}")
        res = executor.execute(cap, ctx)
        assert res.success is True
        
    execution_time = time.time() - execute_start
    avg_latency = (execution_time / 500) * 1000
    
    # Execution lifecycle + pub/sub should be under 5ms on average
    assert avg_latency < 5.0
