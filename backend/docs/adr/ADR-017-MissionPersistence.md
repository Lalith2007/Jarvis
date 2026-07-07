# ADR-017 — Long-Running Mission Persistence

**Status:** Accepted
**Sprint:** 13.9 (Long-Running Missions)
**Date:** 2026-07-06

## Context

Objective 9: background missions that survive an Electron/backend restart —
pause/resume/cancel, progress, checkpointing, recovery. Closing the app must not
lose missions.

## Decision

Add a durable `MissionStore` that checkpoints `Mission` snapshots (pydantic →
JSON) to `data/missions/` (gitignored). `MissionService` checkpoints on every
status transition (create/update/complete/fail) and gains `pause`/`resume`/
`cancel`. On startup, `mission_store.recover_incomplete()` loads missions that
were in flight (ANALYZING/PLANNING/EXECUTING/WAITING/REFLECTING) when the
process died and marks them `WAITING` + `metadata.recovered=True` so they are
resumable rather than lost.

Checkpointing is best-effort (never breaks execution) and writes are small JSON
files keyed by mission id.

## Consequences

**Positive**
- Missions persist across restarts; recovery is automatic at startup (wired in
  `main.py`). pause/resume/cancel transitions are durable.
- Hermetically tested by simulating a restart with a second `MissionStore`
  instance reading the same dir. 318 tests pass (+3), zero regression.

**Remaining (tracked)**
- Full *background scheduler* (detached execution threads that continue after
  the HTTP request returns, with progress notifications) builds on this store;
  the state layer required for it is now in place.
- Graph-level resume (re-enter the mission graph at the last incomplete node)
  is a follow-on; today recovery restores mission state + status.

## Alternatives considered
- Redis/Postgres — rejected for V1 (extra infra). File-per-mission JSON is
  simple, inspectable, and sufficient; the store interface can be swapped later.
