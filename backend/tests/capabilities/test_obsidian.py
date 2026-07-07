"""Sprint 13.4 — Obsidian second-brain note capability (hermetic; temp vault)."""
from pathlib import Path

from app.mission.capabilities import capability_manager  # noqa: F401 register builtins
from app.capabilities.registry import capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics


def _ctx(state):
    return CapabilityContext(mission_id="m", graph_id="g", execution_id="e", node_id="n", runtime_state=state)


def test_obsidian_capability_registered():
    assert "obsidian.note" in capability_registry.ids()


def test_creates_linked_note(tmp_path, monkeypatch):
    from app.storage import service as storage_service
    monkeypatch.setattr(storage_service.storage, "root", tmp_path)

    cap = capability_registry.get("obsidian.note")
    result = capability_lifecycle.execute(cap, _ctx({
        "note_type": "person",
        "title": "Jane Smith",
        "content": "Backend lead on the auth refactor.",
        "tags": ["person", "backend"],
        "links": ["Auth Refactor", "Backend Team"],
    }))
    assert result.success
    p = Path(result.result["path"])
    assert p.exists()
    assert p.parent.as_posix().endswith("jarvis/people")
    text = p.read_text()
    # frontmatter + tags + wikilink backlinks
    assert text.startswith("---")
    assert "type: person" in text
    assert "backend" in text
    assert "[[Auth Refactor]]" in text
    assert "[[Backend Team]]" in text


def test_daily_note_named_by_date(tmp_path, monkeypatch):
    from app.storage import service as storage_service
    monkeypatch.setattr(storage_service.storage, "root", tmp_path)
    cap = capability_registry.get("obsidian.note")
    result = capability_lifecycle.execute(cap, _ctx({"note_type": "daily", "title": "Daily", "content": "notes"}))
    assert result.success
    assert Path(result.result["path"]).name.endswith(".md")
    assert Path(result.result["path"]).parent.as_posix().endswith("jarvis/daily")
