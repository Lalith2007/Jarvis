# Observability (Sprint 13.1)

Every mission is fully traceable via the structured event stream and the
capability metrics surface.

## Event taxonomy

Events are published through `EventPublisher.publish(subsystem, event_type,
mission_id, session_id, execution_id, payload, severity)` and delivered over the
platform WebSocket + event bus.

| Subsystem | Events |
|---|---|
| `hermes` | HermesReceivedRequest |
| `mission` | MissionCreated, MissionStarted, node_queued, node_started, node_completed, node_failed, node_cancelled, mission_completed, mission_failed, MissionCompleted |
| `athena` | AthenaDecision (unified), AthenaStarted/AthenaCompleted (legacy fallback only) |
| `capabilities` | CapabilityRegistered, CapabilityInitialized, CapabilityStarted, CapabilityCompleted, CapabilityFailed, CapabilityHealthChanged, CapabilityDisabled |
| `memory` | MemorySearchCompleted |
| `runtime` | RuntimeSessionStarted, RuntimeSessionCompleted |
| `reflection` | ReflectionStarted, ReflectionCompleted |

A single grounding request emits the full chain (verified live):
`HermesReceivedRequest → MissionCreated → MissionStarted → RuntimeSessionStarted
→ AthenaDecision → mission_started → (node_queued → node_started →
CapabilityInitialized → CapabilityStarted → CapabilityCompleted → node_completed)×N
→ mission_completed → ReflectionStarted → ReflectionCompleted → MissionCompleted
→ RuntimeSessionCompleted`.

## Metrics surface

Per-capability rolling metrics (`CapabilityMetrics`) recorded by the lifecycle:
`execution_count`, `failure_count`, `average_latency` (ms), `average_cost`,
`last_execution`, `health_score` (success-rate %).

Read-only API:
- `GET /api/capabilities` — manifests + live health + metrics
- `GET /api/capabilities/metrics` — metrics keyed by capability id
- `GET /api/capabilities/health` — health per capability

## Forensic validation

`scripts/forensic_live_trace.py` runs the real pipeline for the grounding
queries and asserts: correct execution order, grounding capability before
`runtime.generate`, full event sequence, reflection ran, zero bypasses
(`second_athena_route=0`, `legacy_vault_search=0`), and zero fabrication.
