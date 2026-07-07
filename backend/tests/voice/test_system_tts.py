"""Sprint 13.8 — local system TTS driver (macOS `say`)."""
import os
import shutil

from app.mission.capabilities import capability_manager  # noqa: F401
from app.capabilities.registry import capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics
from app.voice.driver import voice_manager
from app.voice.system_driver import SystemVoiceDriver


def test_system_tts_live(tmp_path):
    if not shutil.which("say"):
        return  # non-macOS; skip
    voice_manager.set_driver(SystemVoiceDriver())
    out = tmp_path / "v.aiff"
    cap = capability_registry.get("voice.speak")
    r = capability_lifecycle.execute(cap, CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n",
        runtime_state={"text": "local voice", "out_path": str(out)}))
    assert r.success
    assert out.exists() and out.stat().st_size > 0


def test_system_driver_stt_signals_clearly():
    d = SystemVoiceDriver()
    try:
        d.transcribe("/tmp/x.wav")
        assert False, "should raise"
    except RuntimeError as e:
        assert "OmniVoice" in str(e) or "STT" in str(e)
