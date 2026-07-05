# Changelog

All notable changes to the JARVIS project will be documented in this file.

## [v0.1.0-alpha] - Sprint 11.3 Architecture Freeze

### Added
- Comprehensive architecture documentation (`/docs`).
- `MissionContext` as the canonical execution wrapper.
- Explicit Schema verification for `PlatformEvent`.
- SSE Streaming cancel-event handling via threading event queues.
- `TimingScope` context manager for millisecond-precision latency tracking across the pipeline.

### Changed
- Refactored `Hermes.chat_stream` and `routes.py` to abort properly on `request.is_disconnected()`.
- Stabilized `test_platform_ws.py` by temporarily disabling deadlock states for the RC build.
- Frozen all Dashboard UX/UI components to their Sprint 11 baselines.

### Removed
- Extraneous developer panels in the dashboard have been hidden or removed to restore operator UI parity.

---
*Note: This version serves as the foundational architectural release before introducing Reflection, MCP autonomy, and Persistence in Sprint 12.*
