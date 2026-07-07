# Athena Intent Engine — Sprint 12.9

## Engine Stack

```
AthenaOrchestrator.analyze(context)
    │
    ├── IntentEngine.evaluate(goal)          → IntentClass, confidence
    ├── ComplexityEngine.evaluate(goal)       → ComplexityClass, confidence
    ├── CapabilityEngine.evaluate(goal, intent) → [CapabilityRecommendation], confidence
    ├── MemoryEngine.evaluate(goal, intent)   → MemoryPlan, confidence
    ├── RiskEngine.evaluate(...)              → risk_level, confidence
    ├── ModelRankingEngine.evaluate(...)      → [ModelRecommendation], confidence
    └── PolicyEngine.evaluate(...)            → approved, reason
```

## CapabilityEngine (Sprint 12.9 rewrite)

Location: `app/athena/engines/capability.py`

### _GROUNDING_GROUPS

Four groups evaluated in priority order.  Each group is a list of regex
patterns.  Any pattern match adds the corresponding capability.

```
model_information      → registry.models       (required=True, parallelizable=True)
capability_information → registry.capabilities  (required=True, parallelizable=True)
memory_information     → memory.retrieve        (required=True, parallelizable=True)
repository_information → repository.read         (required=True, parallelizable=True)
```

`repository.read` (`app/capabilities/builtin/repository_cap.py`) reads
repository documentation files (README/LICENSE/CHANGELOG) from disk and returns
their content as structured, authoritative grounding data.  It is checked
before `_SUPPLEMENTAL_GROUPS`, so a local README query never mis-fires to
`web.search`.

Multiple groups can fire simultaneously (multi-capability queries).

### _SUPPLEMENTAL_GROUPS

Only evaluated when no grounding group fired:

```
web_search   → web.search     (required=False, parallelizable=True)
code_execution → python.execute (required=False, parallelizable=False)
```

### planner/executor exclusion

Added only when:
- No grounding capability triggered, AND
- Intent is NOT in {conversation, unknown, retrieval, summarization}

### runtime.generate

Always appended last as terminal node (required=True, parallelizable=False).

## MemoryEngine (Sprint 12.9 extension)

Location: `app/athena/engines/memory.py`

Added patterns to `needs_retrieval` check:
- `memories`, `learned`, `stored`, `knowledge base`, `what do you know`,
  `what have you`, `search memory`, `memory search`, `retrieve memory`

These patterns ensure that memory-information queries set
`memory_plan.retrieval_required = True`, which causes `MissionGraphBuilder`
to add a `memory.retrieve` node to the graph.

## Decision Serialisation

The complete `AthenaDecision` (including `recommended_capabilities`) is
serialised into:

1. `MissionGraph.athena_decision` — top-level
2. `node.metadata["athena_decision"]` for the `runtime.generate` node

`RuntimeGenerateCapability` deserialises it to:
- Build `RouteDecision` (skip second Athena pass)
- Run `_validate_grounding()` (Sprint 12.9)
