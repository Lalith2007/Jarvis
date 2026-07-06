# Semantic Capability Routing — Sprint 12.9

## Overview

Sprint 12.9 replaces the brittle phrase-matching heuristics in `CapabilityEngine`
with a structured semantic intent-group table.  Every production query that
requests system information now deterministically resolves to the correct
grounding capability.

## Intent Groups

Four grounding groups are evaluated against every query:

| Group | Triggers | Capability Added | Required |
|---|---|---|---|
| model_information | "which model are you", "list models", "how many providers", ... | `registry.models` | ✓ |
| capability_information | "what tools do you have", "list capabilities", "what can you do", ... | `registry.capabilities` | ✓ |
| memory_information | "what memories do you have", "recall previous", "search memory", ... | `memory.retrieve` | ✓ |
| repository_information | "search README", "summarize the README", "open README", "show the LICENSE", ... | `repository.read` | ✓ |

## Routing Logic

```
User query
    │
    ▼
CapabilityEngine.evaluate(goal, intent)
    │
    ├── Check all _GROUNDING_GROUPS (pattern lists OR-ed)
    │     └── Match → add grounding capability (required=True, parallelizable=True)
    │
    ├── If no grounding triggered → check _SUPPLEMENTAL_GROUPS (web, code)
    │
    ├── If no grounding triggered AND intent is complex → add planner + executor
    │
    └── Always append runtime.generate (required=True, parallelizable=False)
```

## Multi-Capability Queries

Multiple grounding groups can fire on the same query:

```
"What models and capabilities exist?"
→ registry.models (model_information group)
→ registry.capabilities (capability_information group)
→ runtime.generate
```

All grounding nodes execute before runtime.generate (enforced by graph dependency chain).

## Planner/Executor Exclusion Rule

`planner.plan` and `executor.execute` are never added when:
- At least one grounding capability was triggered, OR
- Intent is `unknown`, `conversation`, `retrieval`, or `summarization`

This prevents heavyweight plan-execute cycles for simple system-information queries.

## Pattern Coverage

### model_information patterns (sample)
- `which model are you` — active model identity
- `what model is (active|running|selected)` — state query
- `which llm (are you|is|do you use)` — LLM-specific
- `what models (are available|do you have|exist)` — availability query
- `list (available )?models` — enumeration
- `how many providers` — provider count
- `provider(s)? (configured|available|registered)` — provider state

### capability_information patterns (sample)
- `what (tools|capabilities|functions|abilities) do you have` — possession query
- `what can you do` — ability query
- `list (your )?(capabilities|tools|functions)` — enumeration
- `available (capabilities|tools|features|skills)` — availability
- `capability registry` — direct registry reference

### memory_information patterns (sample)
- `what (do you remember|memories do you have)` — state query
- `recall previous information` — retrieval directive
- `search (my |your |the )?(memory|memories)` — search directive
- `what have you (learned|stored|saved)` — knowledge query

### repository_information patterns (sample)
- `\breadme\b` / `\blicense\b` / `\bchangelog\b` — direct doc-file references
- `(search|find|open|show|read|summarize) (the |my )?readme` — verb + README
- `(repo|repository|codebase|project) (structure|contents|files|documentation)` — repo query

Because grounding groups are checked before `_SUPPLEMENTAL_GROUPS`, a query like
"Search my README" resolves to the local `repository.read` capability and never
mis-fires to `web.search`.  A genuine web query ("Search the web for …") does not
match any doc token and still routes to `web.search`.

## Files Changed

| File | Change |
|---|---|
| `app/athena/engines/capability.py` | Intent group table + repository_information group |
| `app/athena/engines/memory.py` | Extended retrieval patterns |
| `app/capabilities/builtin/runtime_cap.py` | Grounding validation + refusal (incl. `repository.read`) |
| `app/capabilities/builtin/repository_cap.py` | New `repository.read` grounding capability |
| `tests/integration/test_semantic_routing.py` | 70+ routing tests (incl. repository) |
