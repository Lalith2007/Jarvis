# Athena Unification — Sprint 12.8

## Problem (Pre-Sprint 12.8)

Two independent Athena instances operated on every request:

| Instance | Location | Role | Data produced |
|---|---|---|---|
| `AthenaOrchestrator` | `athena/engines/orchestrator.py` | Graph topology | `AthenaDecision` with `recommended_models` |
| `Athena` router | `athena/router.py` | LLM model selection | `RouteDecision` |

These ran **sequentially and independently**.  The `recommended_models` field
inside `AthenaDecision` was computed and then **discarded**.  `LLMService`
called `athena.route()` again from scratch, re-running intent detection,
scoring, and ranking on identical input.

## Solution (Post-Sprint 12.8)

### Single AthenaDecision authority

`MissionGraphBuilder.build()` serialises the `AthenaDecision` into
`graph.athena_decision` and into `runtime.generate` node metadata
(`node.metadata["athena_decision"]`).

### Forwarding chain

```
AthenaOrchestrator.analyze()
        │
        │ AthenaDecision (contains recommended_models)
        ▼
MissionGraphBuilder.build()
        │
        │ serialised into MissionGraph.athena_decision
        │ and into runtime.generate node metadata
        ▼
CapabilityManager.execute()
        │
        │ deserialises → CapabilityContext.athena_decision
        ▼
RuntimeGenerateCapability.execute()
        │
        │ _build_route_decision() → RouteDecision from pre-computed models
        ▼
LLMService.chat(route_decision=...)
        │
        │ skips athena.route() entirely
        ▼
LLMOrchestrator.execute()
```

### Fallback

When `CapabilityContext.athena_decision is None` (legacy test paths, missing
metadata), `LLMService._route()` calls the legacy `athena.route()` as before.
No breaking change.

## Files Changed

| File | Change |
|---|---|
| `app/mission/graph.py` | Added `athena_decision: dict | None` field to `MissionGraph` |
| `app/mission/builder.py` | Serialises `AthenaDecision` into graph and runtime.generate node |
| `app/mission/capabilities.py` | Deserialises `athena_decision` from node metadata into `CapabilityContext` |
| `app/capabilities/builtin/runtime_cap.py` | Added `_build_route_decision()` to consume pre-computed decision |
| `app/llm/service.py` | Added `route_decision` param to `chat()` and `stream()`; fallback preserved |

## Invariants

- `AthenaOrchestrator.analyze()` is called **exactly once** per mission.
- `Athena.route()` is called **zero times** when a valid `AthenaDecision` is present.
- `RouteDecision` consumed by `LLMOrchestrator` originates from the same `AthenaDecision` that determined graph topology.
