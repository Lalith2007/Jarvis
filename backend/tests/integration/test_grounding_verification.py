"""
Sprint 12.8 — Grounding Verification Suite.

For each grounding query this test file verifies:
  1. The MissionGraph topology (which nodes are created and in what order).
  2. That capability nodes execute and return structured CapabilityResult data.
  3. That runtime.generate receives authoritative tool context, not LLM hallucinations.
  4. That the unified AthenaDecision flows from MissionGraphBuilder into
     RuntimeGenerateCapability (no second Athena routing pass).

These tests are OFFLINE — they do NOT call any external LLM.  The LLM call
inside RuntimeGenerateCapability is patched out so we can inspect the exact
prompt context it would send.
"""
from __future__ import annotations

import json
import types
from unittest.mock import MagicMock, patch

import pytest

# ── Trigger capability registration ──────────────────────────────────────────
from app.mission.capabilities import capability_manager  # noqa: F401 (side-effect)
from app.capabilities.registry import capability_registry
from app.mission.builder import mission_graph_builder
from app.mission.models import Mission
from app.mission.graph import MissionGraph, MissionNode
from app.athena.models import AthenaDecision, ModelType
from app.providers.registry import provider_registry


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_mission(goal: str) -> Mission:
    from app.mission.service import mission_service
    return mission_service.create(goal)


def _build_graph(goal: str) -> MissionGraph:
    mission = _make_mission(goal)
    return mission_graph_builder.build(mission)


def _capability_ids(graph: MissionGraph) -> list[str]:
    """Return capability IDs in topological execution order."""
    order = []
    resolved: set[str] = set()

    def _visit(node_id: str) -> None:
        node = graph.nodes[node_id]
        for dep in node.dependencies:
            if dep not in resolved:
                _visit(dep)
        if node_id not in resolved:
            order.append(node.capability)
            resolved.add(node_id)

    for nid in graph.nodes:
        _visit(nid)
    return order


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestAthenaUnification:
    """Verify that MissionGraphBuilder embeds AthenaDecision in the graph."""

    def test_graph_carries_athena_decision(self):
        graph = _build_graph("Which model are you?")
        assert graph.athena_decision is not None, (
            "MissionGraph.athena_decision must be set by MissionGraphBuilder"
        )

    def test_runtime_node_carries_athena_decision(self):
        graph = _build_graph("Which model are you?")
        runtime_nodes = [
            n for n in graph.nodes.values() if n.capability == "runtime.generate"
        ]
        assert runtime_nodes, "Graph must contain a runtime.generate node"
        node = runtime_nodes[0]
        assert "athena_decision" in node.metadata, (
            "runtime.generate node must carry athena_decision in metadata"
        )
        ad = node.metadata["athena_decision"]
        assert "recommended_models" in ad
        assert len(ad["recommended_models"]) > 0

    def test_no_second_athena_routing_when_decision_present(self):
        """
        When CapabilityContext.athena_decision is present,
        RuntimeGenerateCapability must NOT call athena.route().
        """
        from app.capabilities.builtin.runtime_cap import RuntimeGenerateCapability
        from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics

        # Build a real AthenaDecision for the context
        graph = _build_graph("Which model are you?")
        runtime_node = next(
            n for n in graph.nodes.values() if n.capability == "runtime.generate"
        )
        from app.athena.models import AthenaDecision
        ad = AthenaDecision.model_validate(runtime_node.metadata["athena_decision"])

        ctx = CapabilityContext(
            mission_id="test-mission",
            graph_id="test-graph",
            execution_id="test-exec",
            node_id=runtime_node.id,
            athena_decision=ad,
            runtime_state={"goal": "Which model are you?", "stream": False},
        )

        cap = RuntimeGenerateCapability()

        with (
            patch("app.llm.service.LLMService.chat", return_value="mocked response"),
            patch("app.athena.router.Athena.route") as mock_route,
        ):
            result = cap.execute(ctx, CapabilityDiagnostics())

        mock_route.assert_not_called(), (
            "athena.route() must NOT be called when AthenaDecision is already present"
        )
        assert result.success

    def test_fallback_route_when_no_decision(self):
        """
        When CapabilityContext.athena_decision is None the fallback path
        via athena.route() must be invoked.
        """
        from app.capabilities.builtin.runtime_cap import RuntimeGenerateCapability
        from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics
        from app.athena.models import RouteDecision, ModelRecommendation, ModelType

        ctx = CapabilityContext(
            mission_id="test-mission",
            graph_id="test-graph",
            execution_id="test-exec",
            node_id="node_fallback",
            athena_decision=None,
            runtime_state={"goal": "Hello", "stream": False},
        )
        cap = RuntimeGenerateCapability()

        fallback_decision = RouteDecision(
            primary=ModelType.LLAMA31,
            recommendations=[ModelRecommendation(model=ModelType.LLAMA31, score=1.0)],
            reason="Fallback",
        )

        # Patch athena.route on the singleton AND the provider so no network
        # request is made.  Do NOT patch LLMService.chat — we need _route()
        # to actually execute so we can verify it calls athena.route.
        with (
            patch("app.athena.router.athena.route", return_value=fallback_decision) as mock_route,
            patch("app.llm.provider.llm_provider.chat", return_value="ok"),
        ):
            result = cap.execute(ctx, CapabilityDiagnostics())

        assert mock_route.called, (
            "athena.route() must be called when no AthenaDecision is present"
        )
        assert result.success


class TestGroundingQueries:
    """
    For each canonical grounding query verify graph topology and that
    the appropriate grounding capability executes.
    """

    # ── "Which model are you?" ────────────────────────────────────────────────

    def test_which_model_graph_topology(self):
        graph = _build_graph("Which model are you?")
        caps = _capability_ids(graph)
        assert "runtime.generate" in caps, "runtime.generate must always be present"

    def test_which_model_decision_contains_model(self):
        graph = _build_graph("Which model are you?")
        ad = graph.athena_decision
        assert ad is not None
        models = [r["model"] for r in ad["recommended_models"]]
        assert len(models) > 0, "AthenaDecision must recommend at least one model"

    # ── "What models are available?" ─────────────────────────────────────────

    def test_available_models_graph_contains_registry_models(self):
        graph = _build_graph("What models are available?")
        caps = _capability_ids(graph)
        assert "registry.models" in caps, (
            "Query about available models must trigger registry.models capability"
        )

    def test_available_models_registry_models_precedes_runtime(self):
        graph = _build_graph("What models are available?")
        caps = _capability_ids(graph)
        ri = caps.index("registry.models")
        rg = caps.index("runtime.generate")
        assert ri < rg, "registry.models must execute BEFORE runtime.generate"

    def test_registry_models_returns_structured_data(self):
        """registry.models CapabilityResult.result must be a dict with 'models' key."""
        from app.capabilities.builtin.registry_cap import RegistryCapability
        from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics

        cap = RegistryCapability()
        ctx = CapabilityContext(
            mission_id="t", graph_id="g", execution_id="e", node_id="n",
            runtime_state={},
        )
        result = cap.execute(ctx, CapabilityDiagnostics())
        assert result.success
        assert isinstance(result.result, dict)
        assert "models" in result.result
        assert isinstance(result.result["models"], list)
        assert len(result.result["models"]) > 0

    def test_registry_models_structured_fields(self):
        from app.capabilities.builtin.registry_cap import RegistryCapability
        from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics

        cap = RegistryCapability()
        ctx = CapabilityContext(
            mission_id="t", graph_id="g", execution_id="e", node_id="n",
            runtime_state={},
        )
        result = cap.execute(ctx, CapabilityDiagnostics())
        first = result.result["models"][0]
        for field in ("id", "display_name", "provider", "context_window", "capabilities"):
            assert field in first, f"Model entry missing field: {field}"

    def test_registry_models_source_is_provider_registry(self):
        """Every model returned by registry.models must exist in ProviderRegistry."""
        from app.capabilities.builtin.registry_cap import RegistryCapability
        from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics

        cap = RegistryCapability()
        ctx = CapabilityContext(
            mission_id="t", graph_id="g", execution_id="e", node_id="n",
            runtime_state={},
        )
        result = cap.execute(ctx, CapabilityDiagnostics())
        registry_ids = {m.id for m in provider_registry.all()}
        returned_ids = {m["id"] for m in result.result["models"]}
        assert returned_ids == registry_ids, (
            "registry.models must return exactly the models in ProviderRegistry"
        )

    # ── "What tools do you have?" ─────────────────────────────────────────────

    def test_tools_query_graph_contains_registry_capabilities(self):
        graph = _build_graph("What tools do you have?")
        caps = _capability_ids(graph)
        assert "registry.capabilities" in caps, (
            "Query about tools must trigger registry.capabilities capability"
        )

    def test_tools_query_registry_capabilities_precedes_runtime(self):
        graph = _build_graph("What capabilities exist?")
        caps = _capability_ids(graph)
        rc = caps.index("registry.capabilities")
        rg = caps.index("runtime.generate")
        assert rc < rg

    def test_registry_capabilities_returns_structured_data(self):
        from app.capabilities.builtin.capabilities_cap import CapabilityRegistryCapability
        from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics

        cap = CapabilityRegistryCapability()
        ctx = CapabilityContext(
            mission_id="t", graph_id="g", execution_id="e", node_id="n",
            runtime_state={},
        )
        result = cap.execute(ctx, CapabilityDiagnostics())
        assert result.success
        assert isinstance(result.result, dict)
        assert "capabilities" in result.result
        assert result.result["count"] > 0

    def test_registry_capabilities_contains_builtin_ids(self):
        from app.capabilities.builtin.capabilities_cap import CapabilityRegistryCapability
        from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics

        cap = CapabilityRegistryCapability()
        ctx = CapabilityContext(
            mission_id="t", graph_id="g", execution_id="e", node_id="n",
            runtime_state={},
        )
        result = cap.execute(ctx, CapabilityDiagnostics())
        cap_ids = {c["id"] for c in result.result["capabilities"]}
        for expected in ("runtime.generate", "registry.models", "registry.capabilities"):
            assert expected in cap_ids, f"Expected {expected} in capability registry output"

    # ── "What capabilities exist?" ────────────────────────────────────────────

    def test_capabilities_exist_triggers_registry_cap(self):
        graph = _build_graph("What capabilities exist?")
        caps = _capability_ids(graph)
        assert "registry.capabilities" in caps

    # ── "What can you do?" ───────────────────────────────────────────────────

    def test_what_can_you_do_triggers_registry_cap(self):
        graph = _build_graph("What can you do?")
        caps = _capability_ids(graph)
        assert "registry.capabilities" in caps

    # ── "Summarize the README." ──────────────────────────────────────────────

    def test_readme_query_graph_contains_repository_read(self):
        graph = _build_graph("Summarize the README.")
        caps = _capability_ids(graph)
        assert "repository.read" in caps, (
            "README query must trigger repository.read grounding capability"
        )

    def test_readme_repository_read_precedes_runtime(self):
        graph = _build_graph("Search my README.")
        caps = _capability_ids(graph)
        ri = caps.index("repository.read")
        rg = caps.index("runtime.generate")
        assert ri < rg, "repository.read must execute BEFORE runtime.generate"

    def test_readme_query_has_no_web_search(self):
        graph = _build_graph("Search my README.")
        caps = _capability_ids(graph)
        assert "web.search" not in caps, (
            "A local README query must not resolve to web.search"
        )

    def test_repository_read_returns_structured_readme(self):
        from app.capabilities.builtin.repository_cap import RepositoryReadCapability
        from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics

        cap = RepositoryReadCapability()
        ctx = CapabilityContext(
            mission_id="t", graph_id="g", execution_id="e", node_id="n",
            runtime_state={"goal": "Summarize the README."},
        )
        result = cap.execute(ctx, CapabilityDiagnostics())
        assert result.success
        assert isinstance(result.result, dict)
        assert result.result["count"] >= 1
        readme = result.result["files"][0]
        for field in ("path", "name", "content", "bytes"):
            assert field in readme, f"repository.read entry missing field: {field}"
        assert readme["name"].lower().startswith("readme")
        assert len(readme["content"]) > 0


class TestStructuredToolContext:
    """
    Verify that MessageBuilder serialises structured (dict/list) tool outputs
    as JSON and wraps them in the authoritative system message.
    """

    def test_dict_output_serialised_as_json(self):
        from app.llm.builder import MessageBuilder
        from app.agents.hermes.models import PromptContext

        builder = MessageBuilder()
        ctx = PromptContext(
            system_prompt="system",
            conversation=[],
            knowledge=[],
            tool_results=[
                {
                    "tool_name": "registry.models",
                    "success": True,
                    "output": {"models": [{"id": "x", "display_name": "X"}], "count": 1},
                }
            ],
            user_query="What models are available?",
        )
        messages = builder.build(ctx)
        tool_message = next(
            m for m in messages if "Authoritative tool execution results" in m.get("content", "")
        )
        assert '"id": "x"' in tool_message["content"], (
            "Structured dict output must appear as JSON in tool context"
        )

    def test_authoritative_label_present(self):
        from app.llm.builder import MessageBuilder
        from app.agents.hermes.models import PromptContext

        builder = MessageBuilder()
        ctx = PromptContext(
            system_prompt="s",
            conversation=[],
            knowledge=[],
            tool_results=[{"tool_name": "t", "success": True, "output": "value"}],
            user_query="q",
        )
        messages = builder.build(ctx)
        tool_msg = next(
            m for m in messages if "Tool:" in m.get("content", "")
        )
        assert "Authoritative tool execution results" in tool_msg["content"]

    def test_string_output_unchanged(self):
        from app.llm.builder import MessageBuilder
        from app.agents.hermes.models import PromptContext

        builder = MessageBuilder()
        ctx = PromptContext(
            system_prompt="s",
            conversation=[],
            knowledge=[],
            tool_results=[{"tool_name": "t", "success": True, "output": "plain text"}],
            user_query="q",
        )
        messages = builder.build(ctx)
        tool_msg = next(m for m in messages if "Tool:" in m.get("content", ""))
        assert "plain text" in tool_msg["content"]


class TestContextBuilderIsFormatterOnly:
    """ContextBuilder must not call any retrieval or routing logic."""

    def test_build_does_not_call_vault(self):
        from app.agents.hermes.context_builder import context_builder

        with patch("app.memory.vault.service.VaultService.search") as mock_vault:
            context_builder.build(user_query="test")
        mock_vault.assert_not_called()

    def test_build_does_not_call_athena_route(self):
        from app.agents.hermes.context_builder import context_builder

        with patch("app.athena.router.Athena.route") as mock_route:
            context_builder.build(user_query="test")
        mock_route.assert_not_called()

    def test_selected_model_in_metadata(self):
        from app.agents.hermes.context_builder import context_builder

        ctx = context_builder.build(
            user_query="Which model are you?",
            selected_model="openai/gpt-oss-120b",
        )
        assert ctx.metadata.get("selected_model") == "openai/gpt-oss-120b"

    def test_build_returns_prompt_context(self):
        from app.agents.hermes.context_builder import context_builder
        from app.agents.hermes.models import PromptContext

        ctx = context_builder.build(user_query="hello")
        assert isinstance(ctx, PromptContext)


class TestSelectedModelInjection:
    """
    When runtime.generate embeds the selected model in prompt metadata,
    LLMOrchestrator must include it in the injected system message.
    """

    def test_active_model_in_injected_message(self):
        from app.llm.orchestrator import LLMOrchestrator
        from app.athena.models import RouteDecision, ModelRecommendation, ModelType
        from app.agents.hermes.models import PromptContext

        orch = LLMOrchestrator()
        decision = RouteDecision(
            primary=ModelType.GPT_OSS_120B,
            recommendations=[
                ModelRecommendation(model=ModelType.GPT_OSS_120B, score=1.0)
            ],
            reason="test",
        )
        ctx = PromptContext(
            system_prompt="s",
            conversation=[],
            knowledge=[],
            tool_results=[],
            user_query="Which model are you?",
            metadata={"selected_model": "openai/gpt-oss-120b"},
        )
        messages = [
            {"role": "system", "content": "s"},
            {"role": "user", "content": "Which model are you?"},
        ]
        rec = decision.recommendations[0]
        injected = orch._inject_metadata(messages, rec, decision, ctx)

        runtime_msg = next(
            m for m in injected if "Active Model" in m.get("content", "")
        )
        assert "openai/gpt-oss-120b" in runtime_msg["content"]


class TestNoHardcodedModelLists:
    """
    Verify that the models returned by RegistryCapability are exclusively
    those registered in ProviderRegistry — not any hardcoded list elsewhere.
    """

    def test_model_count_matches_provider_registry(self):
        from app.capabilities.builtin.registry_cap import RegistryCapability
        from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics

        cap = RegistryCapability()
        ctx = CapabilityContext(
            mission_id="t", graph_id="g", execution_id="e", node_id="n",
            runtime_state={},
        )
        result = cap.execute(ctx, CapabilityDiagnostics())
        expected_count = len(provider_registry.all())
        assert result.result["count"] == expected_count

    def test_adding_provider_model_appears_in_registry_cap(self):
        """
        Dynamically registering a new model must appear in registry.models
        output without any code changes.
        """
        from app.capabilities.builtin.registry_cap import RegistryCapability
        from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics
        from app.providers.models import ProviderModel, ProviderType, ProviderCapability

        new_model = ProviderModel(
            id="test/dynamic-model-12345",
            provider=ProviderType.NVIDIA,
            display_name="Dynamic Test Model",
            context_window=4096,
            capabilities=[ProviderCapability.CHAT],
        )
        provider_registry.register(new_model)

        cap = RegistryCapability()
        ctx = CapabilityContext(
            mission_id="t", graph_id="g", execution_id="e", node_id="n",
            runtime_state={},
        )
        result = cap.execute(ctx, CapabilityDiagnostics())
        ids = [m["id"] for m in result.result["models"]]

        # Clean up
        if new_model.id in provider_registry._models:
            del provider_registry._models[new_model.id]

        assert "test/dynamic-model-12345" in ids, (
            "Dynamically registered model must appear in registry.models output"
        )
