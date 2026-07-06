"""
RepositoryReadCapability — Sprint 12.9 Repository Grounding
===========================================================

Grounds repository/file queries ("Search README", "Summarize the README",
"Show README", "Open README") against the actual files on disk instead of
letting the LLM answer from prior knowledge.

Returns structured data:
    {
        "files": [{"path": ..., "name": ..., "content": ...}],
        "count": N,
        "query": <goal>,
    }

The runtime.generate node treats this output as authoritative ground truth,
so a summary of the README is a summary of *this repository's* README, never a
hallucinated one.
"""

from pathlib import Path

from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityCategory,
    CapabilityConfig,
    CapabilityContext,
    CapabilityDiagnostics,
    CapabilityManifest,
    CapabilityResult,
)
from app.config.settings import BASE_DIR
from app.security.permissions import permissions

# Repository root — backend/ lives one level below the repo root.
_REPO_ROOT = BASE_DIR.parent

# Known documentation files keyed by the token that appears in a user query.
# Order matters only for defaulting; every match is included.
_DOC_TOKENS = ("readme", "license", "changelog", "architecture", "contributing")

# Cap the amount of file content forwarded to the prompt so a large file does
# not blow the token budget.  README-class files are far below this.
_MAX_CHARS = 12_000


class RepositoryReadCapability(BaseCapability):
    """Reads repository documentation/files and returns structured content."""

    def __init__(self):
        manifest = CapabilityManifest(
            id="repository.read",
            name="Repository File Reader",
            version="1.0.0",
            author="System",
            description=(
                "Reads repository files (README, LICENSE, docs) and returns "
                "their content as authoritative grounding data."
            ),
            category=CapabilityCategory.FILESYSTEM,
            permissions=["read:repository"],
        )
        super().__init__(manifest, CapabilityConfig())

    def initialize(self, context: CapabilityContext) -> None:
        pass

    def validate(self, context: CapabilityContext) -> None:
        pass

    # ──────────────────────────────────────────────────────────────────────────
    # Target selection
    # ──────────────────────────────────────────────────────────────────────────

    def _target_tokens(self, goal_lower: str) -> list[str]:
        """Return the doc tokens referenced by the query, defaulting to README."""
        matched = [tok for tok in _DOC_TOKENS if tok in goal_lower]
        return matched or ["readme"]

    def _resolve_files(self, tokens: list[str]) -> list[Path]:
        """
        Resolve doc tokens to concrete files at the repository root.

        Case-insensitive: matches README.md, readme.rst, LICENSE, etc.  Only
        files inside an allowed root (permission-checked) are returned.
        """
        resolved: list[Path] = []
        try:
            entries = sorted(_REPO_ROOT.iterdir())
        except OSError:
            return resolved

        for entry in entries:
            if not entry.is_file():
                continue
            stem_lower = entry.stem.lower()
            name_lower = entry.name.lower()
            for tok in tokens:
                if stem_lower == tok or name_lower.startswith(tok):
                    if permissions.allowed(str(entry)) and entry not in resolved:
                        resolved.append(entry)
                    break
        return resolved

    def execute(
        self, context: CapabilityContext, diagnostics: CapabilityDiagnostics
    ) -> CapabilityResult:
        goal = (
            context.runtime_state.get("goal")
            or context.runtime_state.get("query")
            or ""
        )
        tokens = self._target_tokens(goal.lower())
        files = self._resolve_files(tokens)

        file_entries = []
        for path in files:
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            truncated = content[:_MAX_CHARS]
            file_entries.append(
                {
                    "path": str(path),
                    "name": path.name,
                    "content": truncated,
                    "truncated": len(content) > _MAX_CHARS,
                    "bytes": len(content),
                }
            )

        return CapabilityResult(
            success=True,
            status="completed",
            result={
                "files": file_entries,
                "count": len(file_entries),
                "query": goal,
                "root": str(_REPO_ROOT),
            },
        )

    def cleanup(self, context: CapabilityContext) -> None:
        pass

    def health_check(self) -> str:
        return "healthy"

    def estimate_cost(self, context: CapabilityContext) -> float:
        return 0.0

    def estimate_latency(self, context: CapabilityContext) -> float:
        return 2.0
