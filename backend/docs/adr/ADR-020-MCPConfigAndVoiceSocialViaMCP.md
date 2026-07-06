# ADR-020 — Config-Driven MCP (Voice & Social via MCP)

**Status:** Accepted
**Sprint:** 13.2 completion / 13.4 Voice / 13.10 Social
**Date:** 2026-07-06

## Context

Voice (Obj 4) and Social (Obj 7) were framework-only, blocked on model weights /
API tokens. But the architecture states "Everything is a Capability or MCP tool"
and "Athena sees no difference" between native and MCP. The vendored OmniVoice
Studio **already exposes an MCP server** (`backend/mcp_server.py`) with exactly
`generate_speech` (TTS), `transcribe` (STT), `list_voices`, `list_languages`.
Most social platforms have off-the-shelf MCP servers (GitHub, Slack, …). So the
right realization is config-driven MCP, not bespoke per-service drivers.

## Decision

Add `app/mcp/config.py`: a Claude-Desktop-style `mcpServers` JSON config
(location from `JARVIS_MCP_CONFIG`, else `<repo>/mcp_servers.json` if present —
no hardcoded path). At startup, `autoconnect()` connects each configured server;
via the Sprint-13.2 adapter, every discovered tool becomes a `BaseCapability`
(`mcp.<server>.<tool>`) that Athena selects dynamically (ADR-019).

Consequences for the two blocked objectives:
- **Voice**: point config at the OmniVoice MCP server → `mcp.omnivoice.generate_speech`
  / `mcp.omnivoice.transcribe` register as capabilities; the voice loop
  (wake→STT→pipeline→TTS) runs through them. Local, no cloud, no bespoke driver.
- **Social**: add e.g. the GitHub/Slack MCP server with a token in config →
  `mcp.github.*` / `mcp.slack.*` become capabilities. No per-platform code.

`mcp_servers.example.json` documents both; the real `mcp_servers.json` is
gitignored (may hold tokens).

## Consequences

**Positive**
- Voice and Social (and any future service) are added by **config**, not code —
  the extensible endgame the architecture describes.
- Hermetic tests cover config parsing + autoconnect→capability registration.
  340 tests pass, zero regression.

**Requires to run live**
- Voice: the user runs OmniVoice Studio (its backend on :3900) and adds it to
  `mcp_servers.json`. Social: a platform MCP server + token in config.
  JARVIS then connects and the tools are live — no further JARVIS code.

## Alternatives considered
- Bespoke `VoiceDriver` / per-platform `SocialConnector` implementations —
  retained as an option, but MCP is the lower-maintenance, architecture-aligned
  path ("Athena sees no difference").
