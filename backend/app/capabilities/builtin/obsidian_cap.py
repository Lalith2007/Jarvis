"""
ObsidianNoteCapability — Sprint 13.4 (Obsidian Second Brain).

Turns structured content into linked Obsidian vault notes (People, Projects,
Meetings, Research, Daily, Architecture, Conversations, Ideas, Tasks,
Knowledge) with YAML frontmatter, tags, and [[wikilink]] backlinks. Writes go
through the StorageService (single vault I/O owner). JARVIS-authored notes are
namespaced under ``jarvis/<type>/`` so the user's curated structure is never
clobbered.
"""

import re
from datetime import datetime

from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityCategory,
    CapabilityConfig,
    CapabilityContext,
    CapabilityDiagnostics,
    CapabilityManifest,
    CapabilityResult,
)
from app.storage.models import StorageObject
from app.storage.service import storage

# note type -> vault subfolder (all under jarvis/)
_TYPE_FOLDERS = {
    "person": "jarvis/people",
    "project": "jarvis/projects",
    "meeting": "jarvis/meetings",
    "research": "jarvis/research",
    "daily": "jarvis/daily",
    "architecture": "jarvis/architecture",
    "conversation": "jarvis/conversations",
    "idea": "jarvis/ideas",
    "task": "jarvis/tasks",
    "knowledge": "jarvis/knowledge",
    "note": "jarvis/notes",
}


def _slug(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text.strip().lower())
    s = re.sub(r"[\s_-]+", "-", s)
    return s[:80] or "untitled"


class ObsidianNoteCapability(BaseCapability):
    def __init__(self):
        manifest = CapabilityManifest(
            id="obsidian.note",
            name="Obsidian Note Writer",
            version="1.0.0",
            author="System",
            description="Creates or updates a linked Obsidian vault note with frontmatter, tags, and wikilinks.",
            category=CapabilityCategory.FILESYSTEM,
            permissions=["write:vault"],
            parameters={
                "note_type": {"type": "string", "description": "person|project|meeting|research|daily|architecture|conversation|idea|task|knowledge|note"},
                "title": {"type": "string", "description": "Note title"},
                "content": {"type": "string", "description": "Markdown body"},
                "tags": {"type": "array", "description": "Frontmatter tags"},
                "links": {"type": "array", "description": "Titles of notes to backlink via [[wikilinks]]"},
            },
        )
        super().__init__(manifest, CapabilityConfig())

    def initialize(self, context: CapabilityContext) -> None:
        pass

    def validate(self, context: CapabilityContext) -> None:
        if not (context.runtime_state.get("title") or context.runtime_state.get("goal")):
            raise ValueError("obsidian.note requires a 'title'")

    def _build_markdown(self, note_type, title, content, tags, links) -> str:
        now = datetime.now()
        fm_tags = ", ".join(tags) if tags else note_type
        frontmatter = (
            "---\n"
            f"date: {now.strftime('%Y-%m-%d')}\n"
            f"type: {note_type}\n"
            f"tags: [{fm_tags}]\n"
            f"created_by: jarvis\n"
            "---\n\n"
        )
        body = f"# {title}\n\n{content.strip()}\n"
        if links:
            related = "\n".join(f"- [[{l}]]" for l in links)
            body += f"\n## Related\n{related}\n"
        return frontmatter + body

    def execute(self, context: CapabilityContext, diagnostics: CapabilityDiagnostics) -> CapabilityResult:
        rs = context.runtime_state or {}
        note_type = (rs.get("note_type") or "note").lower()
        title = rs.get("title") or rs.get("goal") or "Untitled"
        content = rs.get("content", "")
        tags = rs.get("tags") or []
        links = rs.get("links") or []

        folder = _TYPE_FOLDERS.get(note_type, _TYPE_FOLDERS["note"])
        # Daily notes are named by date; others by slugified title.
        filename = (
            f"{datetime.now().strftime('%Y-%m-%d')}.md"
            if note_type == "daily"
            else f"{_slug(title)}.md"
        )
        markdown = self._build_markdown(note_type, title, content, tags, links)

        try:
            path = storage.save(StorageObject(folder=folder, filename=filename, content=markdown))
            return CapabilityResult(
                success=True,
                status="completed",
                result={
                    "path": str(path),
                    "note_type": note_type,
                    "title": title,
                    "links": links,
                    "tags": tags,
                },
            )
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])

    def cleanup(self, context: CapabilityContext) -> None:
        pass

    def health_check(self) -> str:
        return "healthy" if getattr(storage, "root", None) else "degraded"

    def estimate_cost(self, context: CapabilityContext) -> float:
        return 0.0

    def estimate_latency(self, context: CapabilityContext) -> float:
        return 10.0
