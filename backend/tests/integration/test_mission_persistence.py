"""Sprint 13.9 — mission persistence, recovery across restart."""
from app.mission.store import MissionStore
from app.mission.models import Mission, MissionStatus


def test_checkpoint_and_reload_across_restart(tmp_path):
    store = MissionStore(root=tmp_path)
    m = Mission(id="mission-1", goal="Do a long thing")
    m.status = MissionStatus.EXECUTING
    store.checkpoint(m)

    # Simulate a process restart: a fresh store reads from disk.
    store2 = MissionStore(root=tmp_path)
    loaded = store2.load("mission-1")
    assert loaded is not None
    assert loaded.goal == "Do a long thing"
    assert loaded.status == MissionStatus.EXECUTING


def test_recover_incomplete_marks_waiting(tmp_path):
    store = MissionStore(root=tmp_path)
    running = Mission(id="r1", goal="in flight")
    running.status = MissionStatus.EXECUTING
    done = Mission(id="d1", goal="finished")
    done.status = MissionStatus.COMPLETED
    store.checkpoint(running)
    store.checkpoint(done)

    store2 = MissionStore(root=tmp_path)
    recovered = store2.recover_incomplete()
    ids = {m.id for m in recovered}
    assert "r1" in ids and "d1" not in ids  # only in-flight recovered
    assert store2.load("r1").status == MissionStatus.WAITING
    assert store2.load("r1").metadata.get("recovered") is True


def test_service_pause_resume_cancel(tmp_path, monkeypatch):
    import app.mission.store as store_mod
    monkeypatch.setattr(store_mod, "mission_store", MissionStore(root=tmp_path))
    from app.mission.service import MissionService

    svc = MissionService()
    m = svc.create("goal")
    svc.pause(m)
    assert m.status == MissionStatus.WAITING and m.metadata.get("paused")
    svc.resume(m)
    assert m.status == MissionStatus.EXECUTING and not m.metadata.get("paused")
    svc.cancel(m)
    assert m.status == MissionStatus.CANCELLED
    # persisted
    assert store_mod.mission_store.load(m.id).status == MissionStatus.CANCELLED
