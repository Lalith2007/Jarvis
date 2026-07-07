# ADR-009 — Capability Contract & Observability Backbone

**Status:** Accepted
**Sprint:** 13.1 (Capability Ecosystem + Observability)
**Date:** 2026-07-06

## Context

Every Sprint 13 objective (MCP, Web, Computer, Voice, Social, Research, …) must
be delivered as a `BaseCapability` and must be fully observable. Sprint 12
already provided most of the contract (manifest, lifecycle, events). What was
missing: per-capability **execution metrics** and a documented, uniform
**observability surface** so "every mission is traceable" holds for all future
capabilities without per-feature wiring.

## Decision

The `BaseCapability` contract (unchanged interface) is the single extension
point. Every capability is executed only through `CapabilityExecutorLifecycle`,
which now, in addition to the existing event emissions, records rolling metrics
into the `CapabilityRegistry`:

- `execution_count`, `failure_count`
- `average_latency` (ms), `average_cost`
- `last_execution`, `health_score` (success-rate %)

Metrics recording is best-effort (never breaks execution) and happens on both
success and failure paths, with `start_time` established before
`initialize()`/`validate()` so a failure there is still counted.

Observability is exposed read-only over the existing API:
- `GET /api/capabilities` — manifests + health + metrics
- `GET /api/capabilities/metrics` — metrics keyed by id
- `GET /api/capabilities/health` — health per capability

The event taxonomy every capability emits (via the lifecycle, no per-feature
code): `CapabilityRegistered`, `CapabilityInitialized`, `CapabilityStarted`,
`CapabilityCompleted`, `CapabilityFailed`, `CapabilityHealthChanged`,
`CapabilityDisabled`.

## Consequences

**Positive**
- Any new capability (built-in or MCP-derived) is automatically metered,
  health-checked, and observable — no bespoke telemetry per feature.
- The dashboard can render live capability health/metrics from one endpoint.
- No new subsystem; extends the existing registry/lifecycle. No bypass.

**Trade-offs**
- Metrics are in-memory (reset on restart). Persistence deferred to the
  long-running-missions sprint (13.9), which introduces durable state.

## Alternatives considered
- A separate metrics service — rejected (duplicate system; the registry is
  already the single source of truth for capabilities).
- Decorator-based per-capability metrics — rejected (bypassable; the lifecycle
  is the one mandatory execution path, so metrics belong there).
