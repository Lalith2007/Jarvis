"""
Voice driver abstraction (Sprint 13.8).

STT/TTS behind an interface so the local engines (Omnistudio, VibeVoice) are
lazy/optional and hermetically mockable. Pipeline: Wake Word -> STT ->
MissionGraph -> Runtime -> TTS. Live use requires the model weights on disk;
default NullVoiceDriver reports degraded.
"""
from abc import ABC, abstractmethod


class VoiceDriver(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str: ...

    @abstractmethod
    def synthesize(self, text: str, out_path: str) -> str: ...

    def available(self) -> bool:
        return True


class NullVoiceDriver(VoiceDriver):
    def transcribe(self, audio_path: str) -> str:
        raise RuntimeError("No local voice engine configured (Omnistudio/VibeVoice weights missing).")

    def synthesize(self, text: str, out_path: str) -> str:
        raise RuntimeError("No local voice engine configured (Omnistudio/VibeVoice weights missing).")

    def available(self) -> bool:
        return False


class VoiceManager:
    def __init__(self):
        self._driver: VoiceDriver | None = None

    def set_driver(self, driver: VoiceDriver) -> None:
        self._driver = driver

    def driver(self) -> VoiceDriver:
        if self._driver is None:
            self._driver = NullVoiceDriver()
        return self._driver


voice_manager = VoiceManager()
