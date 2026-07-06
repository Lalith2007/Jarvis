# ADR-011 — Memory Intelligence

**Status:** Accepted
**Sprint:** 13.3 (Memory Intelligence)
**Date:** 2026-07-06

## Context

Objective 5 requires MemoryEngine to be a real second brain: semantic,
episodic, procedural, working, and long-term memory, plus **consolidation** and
**automatic reflection storage** — all accessed only through capabilities.

## Decision

Extend the existing MemoryEngine/pipeline rather than add a new store.

- **Memory types**: add `SEMANTIC` (distilled knowledge) and `WORKING`
  (short-term scratch) to `MemoryType`; define `LONG_TERM_TYPES`
  (`SEMANTIC, SUMMARY, PROCEDURAL, FACT`) as the consolidation target. Existing
  types (`EPISODIC`, `PROCEDURAL`, …) unchanged — backward compatible.
- **Consolidation**: new `memory.consolidate` capability distills `WORKING`
  memories into a durable `SUMMARY` record and retires the working ones. It runs
  through the standard capability lifecycle and touches memory only via
  `MemoryEngine` (no direct store access outside the engine).
- **Automatic reflection storage**: `ReflectionOrchestrator` persists each
  mission's lessons/suggestions as a `PROCEDURAL` long-term memory tagged
  `reflection`, so the system learns across missions. The write is offloaded to
  a daemon thread so it never inflates the reflection compute path (the stress
  budget of <10 ms/reflection is preserved).
- **Access discipline**: reads/writes/consolidation are capabilities
  (`memory.retrieve`, `memory.store`, `memory.consolidate`). The reflection hook
  is the memory subsystem persisting its own reflections — an internal engine
  concern, not an external feature bypassing capabilities.

## Consequences

**Positive**
- Working→long-term consolidation and cross-mission learning without a new
  subsystem; all memory access still flows through `MemoryEngine`.
- New MCP/other capabilities can consolidate memory via `memory.consolidate`.
- 294 tests pass (+4), stress budget preserved, zero regression.

**Remaining (tracked)**
- Embedding-based semantic retrieval is still keyword/heuristic in the pipeline;
  a vector index is a later enhancement (the `embeddings/` package is scaffolded).
- Consolidation is manual/triggered; scheduled auto-consolidation can be added
  with the long-running-missions scheduler (Sprint 13.9).

## Alternatives considered
- A separate long-term store — rejected (duplicate system). Tiering via
  `MemoryType` + consolidation keeps one engine as the source of truth.
