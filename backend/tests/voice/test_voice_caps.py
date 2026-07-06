"""Sprint 13.8 — Local voice capabilities (hermetic, fake driver)."""
from app.mission.capabilities import capability_manager  # noqa: F401 register builtins
from app.capabilities.registry import capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics
from app.voice.driver import VoiceDriver, voice_manager, NullVoiceDriver


class FakeVoiceDriver(VoiceDriver):
    def transcribe(self, audio_path):
        return f"transcript of {audio_path}"

    def synthesize(self, text, out_path):
        return out_path


def _run(cid, state):
    cap = capability_registry.get(cid)
    return capability_lifecycle.execute(cap, CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n", runtime_state=state))


def test_registered():
    assert "voice.transcribe" in capability_registry.ids()
    assert "voice.speak" in capability_registry.ids()


def test_transcribe_and_speak_with_driver():
    voice_manager.set_driver(FakeVoiceDriver())
    t = _run("voice.transcribe", {"audio_path": "/tmp/a.wav"})
    assert t.success and t.result["text"] == "transcript of /tmp/a.wav"
    s = _run("voice.speak", {"text": "hello", "out_path": "/tmp/out.wav"})
    assert s.success and s.result["audio_path"] == "/tmp/out.wav"


def test_null_driver_reports_degraded_and_fails_gracefully():
    voice_manager.set_driver(NullVoiceDriver())
    cap = capability_registry.get("voice.transcribe")
    assert cap.health_check() == "degraded"
    r = _run("voice.transcribe", {"audio_path": "/tmp/a.wav"})
    assert not r.success  # no engine -> clean failure, no crash
