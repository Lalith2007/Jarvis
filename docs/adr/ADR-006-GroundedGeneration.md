# ADR-006 — Grounded Generation

**Status:** Accepted  
**Sprint:** 12.8  
**Date:** 2026-07-06

## Context

Prior to Sprint 12.8 the JARVIS backend had two structural problems:

1. **Dual Athena** — `AthenaOrchestrator` computed a full `AthenaDecision`
   including model rankings, then discarded the rankings.  `LLMService`
   independently called `Athena.route()` for a second scoring pass on identical
   input.

2. **Ungrounded generation** — `runtime.generate` passed tool results as
   concatenated plain-text strings.  The LLM could ignore them or mix them
   with prior knowledge, producing hallucinated system metadata.

## Decision

### 1. Single Athena Authority

`AthenaOrchestrator.analyze()` is the sole source of routing decisions.  Its
`AthenaDecision` is serialised into `MissionGraph.athena_decision` and into
the `runtime.generate` node metadata.  `RuntimeGenerateCapability` constructs
a `RouteDecision` directly from `decision.recommended_models` and passes it to
`LLMService.chat(route_decision=...)`, bypassing `Athena.route()`.

The fallback path (`Athena.route()`) is preserved for legacy usage and is
invoked only when `CapabilityContext.athena_decision is None`.

### 2. Structured Tool Context

`CapabilityResult.result` is now a typed structure (dict/list) for all
grounding capabilities.  `MessageBuilder._format_tool_result()` serialises
dicts and lists as `json.dumps(indent=2)`.  The containing message is labelled
"Authoritative tool execution results (treat as ground truth)".

### 3. Capability-first ContextBuilder

`ContextBuilder.build()` is a pure formatter.  Removed: vault query,
capability discovery call.  All data arrives as parameters.

### 4. New Grounding Capabilities

| Capability ID | Answers |
|---|---|
| `registry.models` | What models are available? |
| `registry.capabilities` | What tools / capabilities exist? |

`registry.capabilities` returns the live `CapabilityRegistry` manifest list —
automatically reflects any newly registered capability.

## Consequences

**Positive:**
- Single Athena call per request.
- Model routing is consistent with graph planning.
- Grounding queries return provably correct system data.
- `ContextBuilder` has no hidden side-effects.

**Negative / Trade-offs:**
- `LLMService.chat()` signature changed (new optional `route_decision` param).
  Callers that bypass `RuntimeGenerateCapability` and call `llm.chat()` directly
  still work — they hit the fallback path automatically.
- Grounding capabilities add one extra graph node per matched query type,
  adding negligible latency (~1 ms each).

## Alternatives Considered

**Annotate tool results in the system prompt only** — rejected because it does
not provide structured JSON to the LLM; string concatenation loses type info.

**Merge both Athena instances into one class** — rejected because it would
require modifying `athena/router.py` (used by existing tests) and increases
change blast radius.  Forwarding the decision is simpler and reversible.
