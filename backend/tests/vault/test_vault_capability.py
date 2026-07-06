"""Sprint 13.11 — vault.search grounds queries in the user's real Obsidian notes."""
from app.mission.capabilities import capability_manager  # noqa: F401
from app.capabilities.registry import capability_registry
from app.athena.engines.capability import CapabilityEngine
from app.athena.engines.intent import IntentEngine


def test_vault_search_registered_and_grounding():
    assert "vault.search" in capability_registry.ids()
    from app.capabilities.core.grounding import GROUNDING_CAPABILITY_IDS
    assert "vault.search" in GROUNDING_CAPABILITY_IDS


def test_vault_queries_route_to_vault_search():
    ie, ce = IntentEngine(), CapabilityEngine()
    for q in ["Review my Obsidian vault North Star", "What are my goals?",
              "summarize my north star", "read my notes"]:
        intent, _ = ie.evaluate(q)
        recs, _ = ce.evaluate(q, intent)
        caps = [r.capability for r in recs]
        assert "vault.search" in caps, f"{q} -> {caps}"
        assert "runtime.generate" in caps


def test_plain_greeting_not_routed_to_vault():
    ie, ce = IntentEngine(), CapabilityEngine()
    intent, _ = ie.evaluate("Hello")
    caps = [r.capability for r in ce.evaluate("Hello", intent)[0]]
    assert "vault.search" not in caps
