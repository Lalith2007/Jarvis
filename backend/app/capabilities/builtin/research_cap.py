"""
Research capability — Sprint 13.7 (Objective 8).

`research.gather` collects sources for a query from the configured SearchProvider,
dedupes them, and returns STRUCTURED, citation-tagged sources. It does NOT call
the LLM — runtime.generate (the terminal node) summarizes from these grounded
sources, so every claim in the final answer is attributable (citations). This
makes research a grounding capability, consistent with the Sprint 12 model.
"""

from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityCategory,
    CapabilityConfig,
    CapabilityContext,
    CapabilityDiagnostics,
    CapabilityManifest,
    CapabilityResult,
)
from app.research.provider import research_manager


class ResearchGatherCapability(BaseCapability):
    def __init__(self):
        super().__init__(
            CapabilityManifest(
                id="research.gather",
                name="Research Gather",
                version="1.0.0",
                author="System",
                description="Gathers deduped, citation-tagged sources for a query (grounding for runtime.generate).",
                category=CapabilityCategory.NETWORK,
                permissions=["research:search"],
                parameters={"query": {"type": "string"}, "limit": {"type": "integer"}, "fetch": {"type": "boolean"}},
            ),
            CapabilityConfig(),
        )

    def initialize(self, context): ...
    def validate(self, context):
        if not ((context.runtime_state or {}).get("query") or (context.runtime_state or {}).get("goal")):
            raise ValueError("research.gather requires a 'query'")
    def cleanup(self, context): ...
    def health_check(self):
        try:
            return "healthy" if research_manager.provider().available() else "degraded"
        except Exception:
            return "degraded"
    def estimate_cost(self, context): return 0.0
    def estimate_latency(self, context): return 1500.0

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        query = rs.get("query") or rs.get("goal")
        limit = int(rs.get("limit", 8))
        do_fetch = bool(rs.get("fetch", False))
        provider = research_manager.provider()
        try:
            hits = provider.search(query, limit=limit)
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])

        # Dedup by URL, preserve order, assign stable citation ids.
        seen, sources = set(), []
        for h in hits:
            if h.url in seen:
                continue
            seen.add(h.url)
            entry = {
                "id": f"S{len(sources) + 1}",
                "title": h.title,
                "url": h.url,
                "snippet": h.snippet,
                "source_type": h.source_type,
            }
            if do_fetch:
                try:
                    entry["content"] = provider.fetch(h.url)[:6000]
                except Exception:
                    entry["content"] = ""
            sources.append(entry)

        return CapabilityResult(
            success=True,
            status="completed",
            result={
                "query": query,
                "sources": sources,
                "count": len(sources),
                "citation_instruction": "Answer ONLY from these sources; cite each fact as [S#].",
            },
        )
