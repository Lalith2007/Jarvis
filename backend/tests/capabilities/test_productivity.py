from pathlib import Path
from app.mission.capabilities import capability_manager  # noqa: F401
from app.capabilities.registry import capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics


def _run(cid, st):
    return capability_lifecycle.execute(capability_registry.get(cid), CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n", runtime_state=st))


def test_registered():
    assert "calendar.create" in capability_registry.ids()
    assert "email.compose" in capability_registry.ids()


def test_calendar_ics(tmp_path):
    out = tmp_path / "e.ics"
    r = _run("calendar.create", {"title": "Standup", "start": "2026-07-07T09:00:00", "duration_min": 15, "out_path": str(out)})
    assert r.success and out.exists()
    t = out.read_text()
    assert "BEGIN:VCALENDAR" in t and "SUMMARY:Standup" in t and "DTSTART:20260707T090000Z" in t


def test_email_eml(tmp_path):
    out = tmp_path / "d.eml"
    r = _run("email.compose", {"to": "a@b.com", "subject": "Hi", "body": "hello", "out_path": str(out)})
    assert r.success and out.exists()
    t = out.read_text()
    assert "To: a@b.com" in t and "Subject: Hi" in t and "hello" in t


def test_validation():
    assert not _run("calendar.create", {}).success
    assert not _run("email.compose", {"to": "x"}).success
