# Capability Selection — Sprint 12.9

## Contract

`CapabilityEngine.evaluate(goal, intent)` returns
`(List[CapabilityRecommendation], confidence)`.

Each `CapabilityRecommendation` carries:

| Field | Type | Meaning |
|---|---|---|
| `capability` | str | Registered capability ID |
| `confidence` | float | 0–1 score |
| `priority` | str | critical / high / medium / low |
| `reason` | str | Human-readable rationale |
| `required` | bool | If True and output missing → grounding refusal |
| `parallelizable` | bool | If True → may execute concurrently with other nodes |

## Confidence Schedule

| Scenario | Confidence |
|---|---|
| Grounding group matched | 0.97 |
| Only supplemental caps (web, code) | 0.85 |
| Pure generation (no caps besides runtime.generate) | 0.70 |

## Recommendation Ordering in Graph

`MissionGraphBuilder` iterates `recommended_capabilities` in order.
Sequential nodes depend on the previous node.
Parallelizable nodes depend on the last non-parallelizable node.

For a grounding query like "What models and capabilities exist?":

```
[registry.models]    ← parallelizable, depends on nothing
[registry.capabilities] ← parallelizable, depends on nothing
[runtime.generate]   ← not parallelizable, depends on both above
```

For a repository query like "Summarize the README.":

```
[repository.read]    ← parallelizable, depends on nothing (reads README.md from disk)
[runtime.generate]   ← not parallelizable, depends on repository.read
```

The README summary is therefore a summary of *this repository's* README —
ground truth read from disk — not a hallucinated one.

For a complex task like "Research and plan a refactor":

```
[planner.plan]       ← not parallelizable, depends on nothing
[executor.execute]   ← not parallelizable, depends on planner
[runtime.generate]   ← depends on executor
```

## Grounding Guarantee

When a grounding capability is marked `required=True` and its output is absent
from `context.runtime_state` at generation time, `RuntimeGenerateCapability`
returns a structured refusal:

```
"I was unable to retrieve the authoritative system information required to
answer this question. The following data sources did not return results:
registry.models. I will not fabricate this information from prior knowledge."
```

This guarantee is enforced in `app/capabilities/builtin/runtime_cap.py:_validate_grounding()`.
