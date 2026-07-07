# Capability Contract (Sprint 13.1)

Every unit of functionality in JARVIS — built-in or MCP-derived — is a
`BaseCapability`. No feature may bypass the Capability System.

## Interface (`app/capabilities/core/base.py`)

| Method | Purpose |
|---|---|
| `initialize(context)` | Setup before execution |
| `validate(context)` | Precondition/permission check — raise to abort |
| `execute(context, diagnostics)` | Core logic → `CapabilityResult` |
| `cleanup(context)` | Always runs, even on failure |
| `health_check()` | `healthy` / `degraded` / `failed` |
| `estimate_cost(context)` | $ estimate |
| `estimate_latency(context)` | ms estimate |

Manifest (`CapabilityManifest`): `id`, `name`, `version`, `author`,
`description`, `category`, `permissions`, `parameters`, `dependencies`, tags,
scheduling hints.

## Guarantees provided automatically by the lifecycle

Executing a capability **only** through `CapabilityExecutorLifecycle.execute`
(via `CapabilityManager`) gives every capability, for free:

- **Registration**: `CapabilityRegistry.register` (dependency + cycle validation)
- **Permissions**: `validate()` + runtime `SecurityManager`
- **Health**: `health_check()` after every run; `CapabilityHealthChanged` event
- **Metrics**: execution/failure counts, avg latency/cost, health score
  (`CapabilityRegistry.record_metrics`)
- **Events**: Registered/Initialized/Started/Completed/Failed/HealthChanged
- **Diagnostics**: `CapabilityDiagnostics` execution trace on every result

## Checklist for a new capability

1. Subclass `BaseCapability` with a complete manifest (incl. `parameters`).
2. Register in `app/capabilities/builtin/__init__.py` (or via MCP adapter).
3. Add it to Athena's capability planning if it is a grounding/tool capability.
4. Tests: unit (execute), integration (through the graph), and — for grounding
   capabilities — a forensic assertion that it precedes `runtime.generate`.
5. Docs: one line in this file's capability list is not required, but the
   manifest `description` is (surfaced by `registry.capabilities`).
