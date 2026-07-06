"""Sprint 13.7 — Research gather capability (hermetic, fake provider)."""
from app.mission.capabilities import capability_manager  # noqa: F401 register builtins
from app.capabilities.registry import capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics
from app.research.provider import SearchProvider, SearchHit, research_manager


class FakeSearchProvider(SearchProvider):
    def search(self, query, limit=8):
        return [
            SearchHit(title="A", url="https://a.com", snippet=f"about {query} 1"),
            SearchHit(title="B", url="https://b.com", snippet=f"about {query} 2"),
            SearchHit(title="A-dup", url="https://a.com", snippet="dup"),  # dedup by url
        ]

    def fetch(self, url):
        return f"full content of {url}"


def _run(state):
    cap = capability_registry.get("research.gather")
    return capability_lifecycle.execute(cap, CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n", runtime_state=state))


def setup_module(_):
    research_manager.set_provider(FakeSearchProvider())


def test_registered():
    assert "research.gather" in capability_registry.ids()


def test_gather_dedupes_and_cites():
    r = _run({"query": "quantum computing"})
    assert r.success
    srcs = r.result["sources"]
    assert len(srcs) == 2  # deduped by url
    assert [s["id"] for s in srcs] == ["S1", "S2"]  # stable citation ids
    assert all("quantum computing" in s["snippet"] for s in srcs)
    assert "cite each fact as [S#]" in r.result["citation_instruction"]


def test_gather_with_fetch():
    r = _run({"query": "x", "fetch": True})
    assert r.success
    assert r.result["sources"][0]["content"].startswith("full content of")


def test_requires_query():
    r = _run({})
    assert not r.success
