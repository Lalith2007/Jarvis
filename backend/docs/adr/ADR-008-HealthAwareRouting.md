# ADR-008 — Health-Aware Model Routing

**Status:** Accepted
**Sprint:** 13.0 (Baseline Stabilization)
**Date:** 2026-07-06

## Context

Live forensic validation of Sprint 12.9 succeeded but was extremely slow
(53–240s per query). Root cause was model availability, not architecture:

| Model | Observed live behaviour |
|---|---|
| `meta/llama-3.1-70b-instruct` | healthy, ~477 ms |
| `nvidia/nemotron-3-ultra-550b-a55b` | healthy, ~849 ms |
| `openai/gpt-oss-120b` | intermittent — sometimes empty choices |
| `minimaxai/minimax-m3` | slow (5–28 s) / empty choices on full prompts |
| `z-ai/glm-5.2` | times out (>180 s) |
| `deepseek-ai/deepseek-v4-pro` | intermittent — timeout or 60–240 s |

`ModelRankingEngine` ranked models by a static heuristic and `ProviderRegistry`
hardcoded `healthy=True`, so Athena routinely selected `minimax` (the static
primary for simple queries) even though it was slow/empty. `runtime.generate`
then stalled on the LLM call, and the orchestrator fell through the list into
the timing-out models.

## Decision

Keep **all** registered models routable — none are ever disabled or removed
(the operator explicitly wants every model available). Instead, make routing
**health- and latency-aware**:

1. `ProviderModel` gains `avg_latency_ms` (measured, nullable).
2. `ProviderRegistry.probe_health(timeout)` pings each enabled model with a
   1-token chat and sets `healthy` (a response with empty `choices` counts as
   unhealthy) and `avg_latency_ms`. Live network calls — run at startup
   (gated by `JARVIS_PROBE_ON_STARTUP=1`) or on demand, never in the hot path.
3. `ModelRankingEngine` re-orders its recommendations with a stable sort keyed
   by `(healthy_rank, latency, -score)`. Responsive low-latency models lead;
   slow/unresponsive ones sink to the end as fallbacks but remain selectable.
4. When no probe has run (default / tests), latency is unknown and treated as
   `0.0`, so the stable sort preserves the original score-based order — zero
   behavioural change and zero regression.

## Consequences

**Positive**
- `runtime.generate` routes to a working model, so chat is fast and live
  forensic validation completes in seconds instead of minutes.
- No model is disabled; the registry stays the single source of truth.
- No architectural bypass — routing still flows through Athena → the same
  `RouteDecision` → `runtime.generate`.
- Hermetic tests unaffected (stable order when unprobed): 284 passed.

**Trade-offs**
- Health is only as fresh as the last probe. Mitigation: startup probe +
  future periodic refresh (Sprint 13.1 observability can schedule it).
- Enabling the startup probe adds a few seconds of startup latency (parallel
  probe is future work).

## Alternatives considered

- **Disable slow models** — rejected: operator requires all models available.
- **Raise `LLM_TIMEOUT` and always wait** — rejected: makes chat unusable when
  the primary is dead; waiting 180s per request is not viable.
- **Hardcode a preferred model** — rejected: reintroduces hardcoded knowledge
  and ignores real-time availability.
