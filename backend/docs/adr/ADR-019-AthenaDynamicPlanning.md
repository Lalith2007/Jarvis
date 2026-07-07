# ADR-019 — Athena Dynamic Planning (Tool Selection)

**Status:** Accepted
**Sprint:** 13.11 (Autonomous Planning)
**Date:** 2026-07-06

## Context

Objective 10 / architecture "Athena → Tool Planning": Athena must plan with any
registered capability — including dynamically-registered MCP tools — not just a
fixed set of intent groups. ADR-010 explicitly deferred "Athena selects MCP
capabilities" to this sprint.

## Decision

Add dynamic tool selection to `CapabilityEngine`: for non-grounding queries, it
scans the live `CapabilityRegistry` and recommends any ACTION capability whose
id/name/tags share a meaningful token with the query. Infrastructure/grounding
capabilities and internal analyzers are excluded (they are handled by static
groups). This runs after static grounding groups, so:

- grounding queries keep their deterministic routing;
- action queries ("run a terminal command", "please translate this paragraph")
  select the matching capability — built-in **or** MCP — with no per-tool code;
- greetings/simple queries match nothing and stay clean;
- when dynamic tools are selected, the planner/executor cycle is skipped (the
  selected capabilities are the plan).

Combined with existing pieces, Athena's plan now covers the architecture's
Athena boxes: intent, complexity, risk, policy, budget, memory plan,
**capability/tool plan** (this ADR), model plan (health-aware, ADR-008), and
**parallelization strategy** (parallelizable → fork/join in the graph).

## Consequences

**Positive**
- MCP tools become first-class to Athena the moment they register — verified:
  a fake MCP `translate` tool is selected for "please translate this paragraph".
- No hardcoded per-capability routing for the action layer; token match over
  the registry generalizes. 326 tests pass (+3), zero regression.

**Remaining (tracked)**
- Selection is token-overlap based; an embedding/LLM-assisted selector is a
  future refinement (the seam is the single `_dynamic_select` function).
- Parallel/cost/latency optimization uses the existing parallelizable flag +
  health-aware model ranking; a full cost-optimizing scheduler is future work.

## Alternatives considered
- Enumerating every capability in static regex groups — rejected (doesn't scale,
  can't cover dynamic MCP tools). Registry-driven selection is the generalization.
