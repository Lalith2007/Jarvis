# ADR-007 — Semantic Capability Planning

**Status:** Accepted
**Sprint:** 12.9
**Date:** 2026-07-06

## Context

Sprint 12.8.1 forensic audit proved the Sprint 12.8 architecture was correctly
wired but that 6/7 grounding queries returned hallucinated responses.  Root
cause: `CapabilityEngine` used brittle regex matching that missed most
production query phrasings.

Specific failures:

| Query | Expected | Actual |
|---|---|---|
| "Which model are you?" | registry.models | only runtime.generate |
| "What memories do you have?" | memory.retrieve | only runtime.generate |
| "How many providers are configured?" | registry.models | only runtime.generate |
| "What tools do you have?" | registry.capabilities | runtime.generate only (sometimes) |
| "Search my README." | repository.read | planner + executor + web.search (wrong) |
| "Summarize the README." | repository.read | runtime.generate only (hallucinated summary) |

## Decision

### 1. Semantic Intent Group Table

Replace ad-hoc regex conditions with a structured `_GROUNDING_GROUPS` table.
Each entry is `(name, patterns, cap_id, confidence, reason)`.  Multiple groups
can fire on a single query.  Patterns are OR-ed against `goal.lower()`.

### 2. Required Flag on Grounding Capabilities

All grounding capability recommendations are emitted with `required=True`.
This signals `RuntimeGenerateCapability._validate_grounding()` to refuse
generation when the output is missing.

### 3. Grounding Validation Before Generation

`RuntimeGenerateCapability` runs `_validate_grounding()` before building the
prompt.  If any required grounding output is absent in `context.runtime_state`,
it returns a structured refusal string instead of generating from prior
knowledge.

### 4. Planner/Executor Exclusion for Grounding Queries

`planner.plan` and `executor.execute` are excluded whenever a grounding
capability is recommended.  Grounding queries are short (< 10ms each) and do
not need plan-execute orchestration.

### 5. Extended Memory Patterns

`MemoryEngine` pattern for `needs_retrieval` extended to cover:
`memories, learned, stored, knowledge base, search memory, retrieve memory`.

### 6. Repository Grounding Capability

Repository/file queries ("Search README", "Summarize the README", "Open
README", "Show the LICENSE") route to a new `repository.read` grounding
capability (`app/capabilities/builtin/repository_cap.py`) that reads the
requested repository documentation file from disk and returns its content as
authoritative, structured data.  It is a required grounding capability and is
evaluated before the supplemental `web.search` group so a local file request
never leaks to the web.  This guarantees a README summary is a summary of the
actual on-disk README, not a fabricated one.

## Consequences

**Positive:**
- All production system-information queries now route to correct grounding caps.
- Grounding validation prevents hallucination when capabilities fail.
- Multi-capability queries supported natively.
- Repository/file queries are grounded against on-disk files.
- 70+ semantic routing tests added.

**Negative / Trade-offs:**
- Pattern tables must be maintained as new query phrasings emerge.
- `required=True` on grounding caps can produce a refusal for edge cases where
  the capability fails transiently.  Mitigated by capability retry logic in
  `GraphExecutionManager`.

## Alternatives Considered

**LLM-based capability selection** — rejected because it adds latency (100-500ms
extra per request) and circular dependency (LLM to decide which LLM capabilities
to use).

**Single expanded regex per capability** — rejected because maintaining one
giant regex is worse than a named-group table with individual patterns.
