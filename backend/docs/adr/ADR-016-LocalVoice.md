# ADR-016 — Local Voice Stack

**Status:** Accepted
**Sprint:** 13.8 (Local Voice)
**Date:** 2026-07-06

## Context

Objective 4: replace cloud voice with local Omnistudio + VibeVoice.
Pipeline: Wake Word → local STT → MissionGraph → Runtime → local TTS.

## Decision

STT/TTS are capabilities behind a `VoiceDriver` interface (injectable via
`voice_manager`):

- `voice.transcribe` — audio → text (local STT)
- `voice.speak` — text → audio (local TTS)

The voice loop reuses the normal pipeline: the wake word triggers
`voice.transcribe`, the transcript enters Hermes → MissionGraph → runtime.generate
like any chat message, and the response is spoken via `voice.speak`. No cloud
voice; the driver wraps the local engines. The driver is lazy/optional so the
backend runs without weights; `NullVoiceDriver` reports `degraded` and fails
cleanly.

## Consequences

**Positive**
- Voice is a first-class part of the same pipeline (no separate voice path);
  events/metrics/health apply. Hermetically tested via a fake driver (315 tests
  pass, +3, zero regression).

**Requires to run live (tracked)**
- Omnistudio/VibeVoice model weights on disk + a concrete `VoiceDriver` binding
  to them (the vendored `omnivoice-studio`/`vibevoice` trees provide the
  engines). Streaming/interruption/barge-in are driver-level features layered on
  the same interface once a real driver is bound.
- Wake-word detection is a host/Electron concern that calls `voice.transcribe`;
  the dashboard already shows an "ARMED: say Hey JARVIS" affordance.

## Alternatives considered
- Embedding the voice engines directly in capabilities — rejected (heavy import
  at startup, untestable headless). The driver seam keeps the backend light and
  the capabilities testable.
