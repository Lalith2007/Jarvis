"""Sprint 13.3 — Memory intelligence: consolidation + reflection storage."""
from app.mission.capabilities import capability_manager  # noqa: F401 register builtins
from app.capabilities.registry import capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics
from app.memory.engine import MemoryEngine
from app.memory.core.models import MemoryType, MemoryRecord, MemoryQuery


def _ctx(state):
    return CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n", runtime_state=state
    )


def test_new_memory_types_exist():
    assert MemoryType.SEMANTIC.value == "semantic"
    assert MemoryType.WORKING.value == "working"


def test_consolidate_capability_registered():
    assert "memory.consolidate" in capability_registry.ids()


def test_consolidation_distills_working_into_summary():
    from app.memory import capabilities as memcaps

    engine = MemoryEngine()  # isolated in-memory instance
    for i in range(3):
        engine.store(MemoryRecord(type=MemoryType.WORKING, title=f"note {i}", content=f"working item {i}"))

    # Point the capability at the isolated engine.
    orig = memcaps.memory_engine
    memcaps.memory_engine = engine
    try:
        cap = memcaps.MemoryConsolidateCapability()
        result = cap.execute(_ctx({"topic": ""}), CapabilityDiagnostics())
    finally:
        memcaps.memory_engine = orig

    assert result.success
    assert result.result["consolidated"] == 3
    assert result.result["summary_id"] is not None
    # A long-term SUMMARY now exists; working memories were retired.
    summaries = engine.search(MemoryQuery(query="", types=[MemoryType.SUMMARY], limit=10)).results
    assert len(summaries) >= 1
    remaining_working = engine.search(MemoryQuery(query="", types=[MemoryType.WORKING], limit=10)).results
    assert len(remaining_working) == 0


def test_reflection_stores_memory():
    from app.reflection.orchestrator import reflection_orchestrator
    from app.memory.engine import memory_engine
    from app.memory.core.models import MemoryQuery, MemoryType

    class _Lesson:
        text = "Grounding capabilities must precede runtime.generate."

    reflection_orchestrator._store_reflection_memory("mission-xyz12345", [_Lesson()], [])
    found = memory_engine.search(
        MemoryQuery(query="grounding", types=[MemoryType.PROCEDURAL], limit=10)
    ).results
    assert any("reflection" in r.tags for r in found)
