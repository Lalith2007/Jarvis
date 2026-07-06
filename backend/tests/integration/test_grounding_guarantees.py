"""
Sprint 12.9 grounding-guarantee regression tests (offline).

Covers the correctness fixes:
  - MemoryReadCapability reads the "goal" key (not the non-existent "query").
  - runtime.generate surfaces a policy rejection instead of generating.
  - The controller emits a grounding-failure refusal when a required grounding
    capability failed/was cancelled (instead of a silent "Mission completed.").
  - The MissionGraph does not contain duplicate memory.retrieve nodes.
"""
from __future__ import annotations

from unittest.mock import patch

from app.mission.capabilities import capability_manager  # noqa: F401 (registers builtins)
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics


def test_memory_capability_reads_goal_key():
    from app.capabilities.builtin import MemoryReadCapability  # noqa: PLC0415
    from app.memory.capabilities import MemoryReadCapability as MRC

    captured = {}

    class _Result:
        results = []
        execution_time_ms = 1.0
        total_candidates_evaluated = 0

    def _fake_search(query):
        captured["query"] = query.query
        return _Result()

    cap = MRC()
    ctx = CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n",
        runtime_state={"goal": "what do you remember about auth?"},
    )
    with patch("app.memory.capabilities.memory_engine.search", side_effect=_fake_search):
        result = cap.execute(ctx, CapabilityDiagnostics())
    assert result.success
    assert captured["query"] == "what do you remember about auth?", (
        "MemoryReadCapability must read the 'goal' key, not empty 'query'"
    )


def test_runtime_generate_surfaces_policy_rejection():
    from app.capabilities.builtin.runtime_cap import RuntimeGenerateCapability
    from app.athena.models import (
        AthenaDecision, IntentClass, ComplexityClass, ExecutionStrategy,
        MemoryPlan, MemoryStrategy,
    )

    decision = AthenaDecision(
        intent=IntentClass.unknown,
        task_type="heuristic",
        complexity=ComplexityClass.low,
        estimated_cost=0.0,
        estimated_latency=0.0,
        confidence=1.0,
        memory_plan=MemoryPlan(
            strategy=MemoryStrategy.none, retrieval_required=False,
            write_required=False, reflection_required=False,
            expected_memories=0, retrieval_budget=0.0,
        ),
        execution_strategy=ExecutionStrategy.sequential,
        recommended_capabilities=[],
        recommended_models=[],
        requires_parallel_execution=False,
        requires_reflection=False,
        requires_memory=False,
        requires_tools=False,
        risk_level="high",
        reasoning_summary="blocked",
        policy_rejection="This request was blocked by policy (high risk).",
        token_budget=4000,
        latency_budget_ms=2000.0,
        cost_budget=0.05,
        maximum_parallelism=4,
    )
    ctx = CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n",
        athena_decision=decision,
        runtime_state={"goal": "do something risky"},
    )
    cap = RuntimeGenerateCapability()
    # Must NOT call the LLM — should return the rejection directly.
    with patch("app.llm.service.llm.chat") as mock_chat:
        result = cap.execute(ctx, CapabilityDiagnostics())
    mock_chat.assert_not_called()
    assert result.status == "policy_rejected"
    assert "blocked by policy" in result.result


def test_no_duplicate_memory_node():
    from app.mission.builder import mission_graph_builder
    from app.mission.service import mission_service

    mission = mission_service.create("what do you remember about the incident?")
    graph = mission_graph_builder.build(mission)
    mem_nodes = [
        n for n in graph.nodes.values() if n.capability == "memory.retrieve"
    ]
    assert len(mem_nodes) <= 1, (
        f"Expected at most one memory.retrieve node, got {len(mem_nodes)}"
    )


def test_controller_grounding_failure_message():
    from app.mission.controller import mission_controller
    from app.mission.builder import mission_graph_builder
    from app.mission.service import mission_service
    from app.mission.graph import NodeStatus

    mission = mission_service.create("What models are available?")
    graph = mission_graph_builder.build(mission)
    # Simulate a failed grounding node.
    for node in graph.nodes.values():
        if node.capability == "registry.models":
            node.status = NodeStatus.FAILED
    msg = mission_controller._grounding_failure_message(graph)
    assert msg is not None
    assert "registry.models" in msg
    assert "will not fabricate" in msg.lower()
