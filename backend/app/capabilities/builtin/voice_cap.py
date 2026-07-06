"""
Local Voice capabilities — Sprint 13.8 (Objective 4).

`voice.transcribe` (STT) and `voice.speak` (TTS) wrap the local voice engines
(Omnistudio/VibeVoice) through the VoiceDriver. The voice loop is:
Wake Word -> voice.transcribe -> MissionGraph (normal pipeline) -> runtime.generate
-> voice.speak. Cloud voice is replaced entirely by the local driver.
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
from app.voice.driver import voice_manager


class _VoiceBase(BaseCapability):
    def initialize(self, context): ...
    def validate(self, context): ...
    def cleanup(self, context): ...
    def health_check(self):
        try:
            return "healthy" if voice_manager.driver().available() else "degraded"
        except Exception:
            return "degraded"
    def estimate_cost(self, context): return 0.0
    def estimate_latency(self, context): return 600.0


class VoiceTranscribeCapability(_VoiceBase):
    def __init__(self):
        super().__init__(CapabilityManifest(
            id="voice.transcribe", name="Voice STT", version="1.0.0", author="System",
            description="Transcribe local audio to text (local STT).",
            category=CapabilityCategory.VOICE, permissions=["voice:listen"],
            parameters={"audio_path": {"type": "string"}},
        ), CapabilityConfig())

    def validate(self, context):
        if not (context.runtime_state or {}).get("audio_path"):
            raise ValueError("voice.transcribe requires 'audio_path'")

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        try:
            text = voice_manager.driver().transcribe(rs["audio_path"])
            return CapabilityResult(success=True, status="completed", result={"text": text})
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])


class VoiceSpeakCapability(_VoiceBase):
    def __init__(self):
        super().__init__(CapabilityManifest(
            id="voice.speak", name="Voice TTS", version="1.0.0", author="System",
            description="Synthesize text to speech audio (local TTS).",
            category=CapabilityCategory.VOICE, permissions=["voice:speak"],
            parameters={"text": {"type": "string"}, "out_path": {"type": "string"}},
        ), CapabilityConfig())

    def validate(self, context):
        if not (context.runtime_state or {}).get("text"):
            raise ValueError("voice.speak requires 'text'")

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        out_path = rs.get("out_path") or "/tmp/jarvis_tts.wav"
        try:
            path = voice_manager.driver().synthesize(rs["text"], out_path)
            return CapabilityResult(success=True, status="completed", result={"audio_path": path})
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])
