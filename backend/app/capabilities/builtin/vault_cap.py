"""
VaultSearchCapability — Sprint 13.11 (grounding for the user's Obsidian vault).

Reads the user's actual Obsidian notes (e.g. brain/North Star.md) so queries
like "review my North Star" are grounded in real vault content instead of the
LLM's prior knowledge. Wraps the existing VaultService (index + search); vault
access is only ever through this capability (ContextBuilder stays formatter-only).
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


class VaultSearchCapability(BaseCapability):
    def __init__(self):
        super().__init__(
            CapabilityManifest(
                id="vault.search",
                name="Vault Search",
                version="1.0.0",
                author="System",
                description="Searches and reads the user's Obsidian vault notes as authoritative grounding.",
                category=CapabilityCategory.MEMORY,
                permissions=["read:vault"],
                parameters={"query": {"type": "string"}, "limit": {"type": "integer"}},
            ),
            CapabilityConfig(),
        )

    def initialize(self, context): ...
    def validate(self, context): ...
    def cleanup(self, context): ...
    def health_check(self):
        try:
            from app.config.settings import settings
            return "healthy" if settings.VAULT_PATH else "degraded"
        except Exception:
            return "degraded"
    def estimate_cost(self, context): return 0.0
    def estimate_latency(self, context): return 30.0

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        query = rs.get("query") or rs.get("goal") or ""
        limit = int(rs.get("limit", 5))
        try:
            from app.memory.vault.service import vault
            from app.query.service import query_processor

            processed = query_processor.process(query)
            results = vault.search(processed, limit=limit)
            notes = [
                {
                    "path": r.note.path,
                    "title": r.note.title,
                    "score": r.score,
                    "content": r.note.content[:8000],
                }
                for r in results
            ]
            return CapabilityResult(
                success=True,
                status="completed",
                result={"query": query, "notes": notes, "count": len(notes)},
            )
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])
