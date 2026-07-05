import pytest
from app.capabilities.executor import CapabilityExecutorLifecycle
from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityManifest, CapabilityCategory, CapabilityConfig,
    CapabilityContext, CapabilityDiagnostics, CapabilityResult
)

class MockLifecycleCapability(BaseCapability):
    def __init__(self, should_fail_validation=False, should_fail_execution=False):
        manifest = CapabilityManifest(
            id="test.lifecycle", name="Test", version="1.0", author="Sys",
            description="test", category=CapabilityCategory.CUSTOM
        )
        super().__init__(manifest, CapabilityConfig())
        self.should_fail_validation = should_fail_validation
        self.should_fail_execution = should_fail_execution
        self.called_init = False
        self.called_cleanup = False

    def initialize(self, ctx): 
        self.called_init = True
        
    def validate(self, ctx): 
        if self.should_fail_validation:
            raise ValueError("Validation failed")
            
    def cleanup(self, ctx): 
        self.called_cleanup = True
        
    def health_check(self): return "healthy"
    def estimate_cost(self, ctx): return 0.0
    def estimate_latency(self, ctx): return 0.0
    
    def execute(self, ctx, diag): 
        if self.should_fail_execution:
            raise ValueError("Execution failed")
        return CapabilityResult(success=True, status="ok")


def test_successful_lifecycle():
    executor = CapabilityExecutorLifecycle()
    cap = MockLifecycleCapability()
    ctx = CapabilityContext(
        mission_id="m1", graph_id="g1", execution_id="e1", node_id="n1"
    )
    
    res = executor.execute(cap, ctx)
    
    assert res.success is True
    assert cap.called_init is True
    assert cap.called_cleanup is True
    assert res.diagnostics.started_at is not None
    assert res.diagnostics.completed_at is not None
    assert len(res.diagnostics.execution_trace) > 0

def test_validation_failure():
    executor = CapabilityExecutorLifecycle()
    cap = MockLifecycleCapability(should_fail_validation=True)
    ctx = CapabilityContext(
        mission_id="m1", graph_id="g1", execution_id="e1", node_id="n1"
    )
    
    res = executor.execute(cap, ctx)
    
    assert res.success is False
    assert cap.called_init is True
    assert cap.called_cleanup is True  # Cleanup must run even on failure
    assert len(res.errors) == 1
    assert "Validation failed" in res.errors[0]

def test_execution_failure():
    executor = CapabilityExecutorLifecycle()
    cap = MockLifecycleCapability(should_fail_execution=True)
    ctx = CapabilityContext(
        mission_id="m1", graph_id="g1", execution_id="e1", node_id="n1"
    )
    
    res = executor.execute(cap, ctx)
    
    assert res.success is False
    assert cap.called_init is True
    assert cap.called_cleanup is True
    assert len(res.errors) == 1
    assert "Execution failed" in res.errors[0]
