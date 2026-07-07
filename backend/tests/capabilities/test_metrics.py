"""Sprint 13.1 — capability execution metrics + observability."""
from fastapi.testclient import TestClient

from app.mission.capabilities import capability_manager  # noqa: F401  register builtins
from app.capabilities.registry import CapabilityRegistry, capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics


def _ctx():
    return CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n", runtime_state={}
    )


def test_record_metrics_success_and_failure():
    reg = CapabilityRegistry()
    reg.record_metrics("x.cap", success=True, latency_ms=100.0)
    reg.record_metrics("x.cap", success=True, latency_ms=200.0)
    reg.record_metrics("x.cap", success=False, latency_ms=300.0)
    m = reg.metrics()["x.cap"]
    assert m.execution_count == 3
    assert m.failure_count == 1
    assert m.average_latency == 200.0  # (100+200+300)/3
    assert m.health_score == round((2 / 3) * 100, 1)
    assert m.last_execution is not None


def test_lifecycle_records_metrics():
    cap = capability_registry.get("registry.models")
    before = capability_registry.metrics().get("registry.models")
    before_count = before.execution_count if before else 0
    capability_lifecycle.execute(cap, _ctx())
    after = capability_registry.metrics()["registry.models"]
    assert after.execution_count == before_count + 1
    assert after.average_latency >= 0


def test_metrics_endpoint():
    import main
    c = TestClient(main.app)
    r = c.get("/api/capabilities/metrics")
    assert r.status_code == 200
    body = r.json()
    assert "metrics" in body and "count" in body


def test_capabilities_endpoint_includes_health_and_metrics():
    import main
    c = TestClient(main.app)
    r = c.get("/api/capabilities")
    assert r.status_code == 200
    caps = r.json()["capabilities"]
    assert len(caps) > 0
    # Each capability entry carries health + metrics keys (metrics may be None
    # if never executed).
    for entry in caps:
        assert "health" in entry
        assert "metrics" in entry
