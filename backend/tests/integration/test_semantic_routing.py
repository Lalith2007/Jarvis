"""
Sprint 12.9 — Semantic Capability Routing Tests
================================================
Verifies that CapabilityEngine maps every production query variant to the
correct grounding capability without phrase-level brittleness.

Offline — no LLM calls.
"""
from __future__ import annotations

import pytest

from app.mission.capabilities import capability_manager  # noqa: F401 side-effect
from app.athena.engines.capability import CapabilityEngine
from app.athena.engines.intent import IntentEngine
from app.athena.models import IntentClass

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ie = IntentEngine()
_ce = CapabilityEngine()


def _caps(query: str) -> list[str]:
    intent, _ = _ie.evaluate(query)
    recs, _ = _ce.evaluate(query, intent)
    return [r.capability for r in recs]


def _required_caps(query: str) -> list[str]:
    intent, _ = _ie.evaluate(query)
    recs, _ = _ce.evaluate(query, intent)
    return [r.capability for r in recs if r.required]


def _assert_contains(query: str, *expected: str):
    caps = _caps(query)
    for cap in expected:
        assert cap in caps, f"{query!r} → {caps} — missing {cap!r}"


def _assert_not_contains(query: str, *forbidden: str):
    caps = _caps(query)
    for cap in forbidden:
        assert cap not in caps, f"{query!r} → {caps} — unexpected {cap!r}"


# ---------------------------------------------------------------------------
# Model / Provider Information
# ---------------------------------------------------------------------------

class TestModelInformationRouting:
    """Every variant must include registry.models and runtime.generate."""

    @pytest.mark.parametrize("query", [
        "Which model are you?",
        "What model are you?",
        "What model is active?",
        "What model is running?",
        "Which model is selected?",
        "Which LLM are you?",
        "Which LLM are you using?",
        "What LLM are you?",
        "What LLM do you use?",
        "Which AI are you?",
        "Are you GPT?",
        "Are you Claude?",
        "What models are available?",
        "Which models are available?",
        "What models do you have?",
        "Which models do you have?",
        "What models exist?",
        "What models can I use?",
        "Available models",
        "List models",
        "List all models",
        "List available models",
        "Show models",
        "Show available models",
        "What models",
        "Which models",
        "Model list",
        "Model registry",
        "How many providers are configured?",
        "Which providers exist?",
        "What providers are available?",
        "Available providers",
        "List providers",
        "Configured providers",
        "How many providers",
    ])
    def test_model_query_routes_to_registry_models(self, query: str):
        _assert_contains(query, "registry.models", "runtime.generate")

    @pytest.mark.parametrize("query", [
        "Which model are you?",
        "What models are available?",
        "How many providers are configured?",
    ])
    def test_no_planner_for_model_queries(self, query: str):
        _assert_not_contains(query, "planner.plan", "executor.execute")

    @pytest.mark.parametrize("query", [
        "Which model are you?",
        "What models are available?",
    ])
    def test_registry_models_is_required(self, query: str):
        required = _required_caps(query)
        assert "registry.models" in required, (
            f"{query!r} — registry.models should be required, got {required}"
        )


# ---------------------------------------------------------------------------
# Capability / Tool Information
# ---------------------------------------------------------------------------

class TestCapabilityInformationRouting:
    """Every variant must include registry.capabilities and runtime.generate."""

    @pytest.mark.parametrize("query", [
        "What tools do you have?",
        "Which tools do you have?",
        "What tools are available?",
        "Which tools are available?",
        "What capabilities do you have?",
        "Which capabilities do you have?",
        "What capabilities exist?",
        "Which capabilities are available?",
        "Available capabilities",
        "List capabilities",
        "List all capabilities",
        "List available capabilities",
        "List your capabilities",
        "Show capabilities",
        "Show your capabilities",
        "What can you do?",
        "What are you capable of?",
        "What are your capabilities?",
        "What are your tools?",
        "What are your functions?",
        "What functions exist?",
        "What functions do you have?",
        "Show abilities",
        "List abilities",
        "What abilities do you have?",
        "Capability registry",
        "Installed capabilities",
        "Registered capabilities",
    ])
    def test_capability_query_routes_to_registry_capabilities(self, query: str):
        _assert_contains(query, "registry.capabilities", "runtime.generate")

    @pytest.mark.parametrize("query", [
        "What can you do?",
        "What tools do you have?",
    ])
    def test_no_planner_for_capability_queries(self, query: str):
        _assert_not_contains(query, "planner.plan", "executor.execute")

    @pytest.mark.parametrize("query", [
        "What can you do?",
        "What tools do you have?",
    ])
    def test_registry_capabilities_is_required(self, query: str):
        required = _required_caps(query)
        assert "registry.capabilities" in required


# ---------------------------------------------------------------------------
# Memory Information
# ---------------------------------------------------------------------------

class TestMemoryInformationRouting:
    """Every variant must include memory.retrieve and runtime.generate."""

    @pytest.mark.parametrize("query", [
        "What memories do you have?",
        "What do you remember?",
        "What is in your memory?",
        "What is in your knowledge base?",
        "Recall previous information",
        "Retrieve my memories",
        "Find my memories",
        "Search memory",
        "Search my memory",
        "What have you learned?",
        "What have you stored?",
        "What have you saved?",
        "Show what you remember",
        "List my memories",
        "Memory contents",
        "Memory search",
        "Previous information",
        "Previous context",
        "Previous history",
    ])
    def test_memory_query_routes_to_memory_retrieve(self, query: str):
        _assert_contains(query, "memory.retrieve", "runtime.generate")

    @pytest.mark.parametrize("query", [
        "What memories do you have?",
        "What do you remember?",
    ])
    def test_no_planner_for_memory_queries(self, query: str):
        _assert_not_contains(query, "planner.plan", "executor.execute")


# ---------------------------------------------------------------------------
# Repository / File Information
# ---------------------------------------------------------------------------

class TestRepositoryInformationRouting:
    """Every README/repository variant must include repository.read + runtime.generate."""

    @pytest.mark.parametrize("query", [
        "Search README",
        "Search my README",
        "Search my README.",
        "Find README",
        "Find the README",
        "Open README",
        "Open the README file",
        "Show README",
        "Show me the README",
        "Read the README",
        "Summarize the README",
        "Summarize my README",
        "Explain the README",
        "What is in the README?",
        "Show the LICENSE",
        "Read the CHANGELOG",
        "Show repository contents",
        "Read the repository file",
    ])
    def test_repository_query_routes_to_repository_read(self, query: str):
        _assert_contains(query, "repository.read", "runtime.generate")

    @pytest.mark.parametrize("query", [
        "Search my README.",
        "Summarize the README.",
        "Show README",
    ])
    def test_no_planner_for_repository_queries(self, query: str):
        _assert_not_contains(query, "planner.plan", "executor.execute")

    @pytest.mark.parametrize("query", [
        "Search my README.",
        "Summarize the README.",
    ])
    def test_repository_query_does_not_use_web_search(self, query: str):
        # README is a local repository file — must never resolve to web.search.
        _assert_not_contains(query, "web.search")

    @pytest.mark.parametrize("query", [
        "Search my README.",
        "Summarize the README.",
    ])
    def test_repository_read_is_required(self, query: str):
        assert "repository.read" in _required_caps(query)

    def test_web_search_still_works_for_web_queries(self):
        # A genuine web query must NOT be captured by repository grounding.
        _assert_contains("Search the web for the latest news", "web.search")
        _assert_not_contains("Search the web for the latest news", "repository.read")


# ---------------------------------------------------------------------------
# Multi-capability queries
# ---------------------------------------------------------------------------

class TestMultiCapabilityRouting:
    """Queries that span multiple grounding groups get all relevant caps."""

    def test_models_and_capabilities(self):
        _assert_contains(
            "What models and capabilities exist?",
            "registry.models",
            "registry.capabilities",
            "runtime.generate",
        )

    def test_models_and_memories(self):
        _assert_contains(
            "What models do you have and what do you remember?",
            "registry.models",
            "memory.retrieve",
            "runtime.generate",
        )

    def test_no_planner_in_multi_grounding(self):
        _assert_not_contains(
            "What models and capabilities exist?",
            "planner.plan",
            "executor.execute",
        )


# ---------------------------------------------------------------------------
# Non-grounding queries (should NOT trigger grounding caps)
# ---------------------------------------------------------------------------

class TestNonGroundingQueries:
    """Simple conversational queries must NOT add grounding nodes."""

    @pytest.mark.parametrize("query", [
        "Hello",
        "How are you?",
        "Good morning",
        "Write me a poem",
        "Tell me a joke",
        "Summarize this text",
        "What is 2 + 2?",
    ])
    def test_no_grounding_caps_for_simple_queries(self, query: str):
        _assert_not_contains(
            query,
            "registry.models",
            "registry.capabilities",
            "memory.retrieve",
        )

    @pytest.mark.parametrize("query", [
        "Hello",
        "How are you?",
        "Write me a poem",
    ])
    def test_runtime_generate_always_present(self, query: str):
        _assert_contains(query, "runtime.generate")


# ---------------------------------------------------------------------------
# Grounding required flag
# ---------------------------------------------------------------------------

class TestGroundingRequiredFlag:
    """All grounding capabilities must be marked required=True."""

    @pytest.mark.parametrize("query, cap_id", [
        ("What models are available?",    "registry.models"),
        ("What tools do you have?",       "registry.capabilities"),
        ("What memories do you have?",    "memory.retrieve"),
        ("Summarize the README.",         "repository.read"),
    ])
    def test_grounding_cap_is_required(self, query: str, cap_id: str):
        intent, _ = _ie.evaluate(query)
        recs, _ = _ce.evaluate(query, intent)
        matching = [r for r in recs if r.capability == cap_id]
        assert matching, f"Capability {cap_id!r} not found in recommendations for {query!r}"
        assert matching[0].required, (
            f"Capability {cap_id!r} should be required=True for {query!r}"
        )
        assert matching[0].parallelizable, (
            f"Grounding capability {cap_id!r} should be parallelizable=True"
        )


# ---------------------------------------------------------------------------
# Confidence scores
# ---------------------------------------------------------------------------

class TestConfidenceScores:
    """Grounding queries should have high confidence (deterministic path)."""

    @pytest.mark.parametrize("query", [
        "What models are available?",
        "What tools do you have?",
        "What memories do you have?",
    ])
    def test_high_confidence_for_grounding(self, query: str):
        intent, _ = _ie.evaluate(query)
        _, conf = _ce.evaluate(query, intent)
        assert conf >= 0.95, f"{query!r} confidence {conf} < 0.95"

    @pytest.mark.parametrize("query", [
        "Hello",
        "Write me a poem",
    ])
    def test_lower_confidence_for_pure_generation(self, query: str):
        intent, _ = _ie.evaluate(query)
        _, conf = _ce.evaluate(query, intent)
        assert conf < 0.97, f"{query!r} confidence {conf} unexpectedly high for pure generation"
