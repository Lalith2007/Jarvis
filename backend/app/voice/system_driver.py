"""
SystemVoiceDriver — local TTS via the OS (macOS `say`), Sprint 13.8 live.

Proves "voice is local" with zero cloud, zero weights, zero download: `say`
synthesizes speech to an audio file on the machine. STT is delegated to a
richer local engine (OmniVoice/VibeVoice via MCP) when configured; the base
system driver raises for transcribe so callers get a clear signal.
"""
import shutil
import subprocess

from app.voice.driver import VoiceDriver


class SystemVoiceDriver(VoiceDriver):
    def available(self) -> bool:
        return shutil.which("say") is not None

    def synthesize(self, text: str, out_path: str) -> str:
        if not self.available():
            raise RuntimeError("System TTS (`say`) not available on this OS.")
        # -o writes audio locally; no network involved.
        subprocess.run(["say", "-o", out_path, text], check=True, timeout=60)
        return out_path

    def transcribe(self, audio_path: str) -> str:
        raise RuntimeError(
            "System driver has no local STT; configure OmniVoice/VibeVoice via MCP for transcription."
        )
