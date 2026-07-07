# Grounded Intelligence — Sprint 12.8

## Principle

Every factual claim in a JARVIS response must originate from a registered
system component, not from LLM prior knowledge.

| Query category | Authoritative source | Capability |
|---|---|---|
| Which model are you? | `AthenaDecision.recommended_models[0]` | `runtime.generate` metadata |
| What models are available? | `ProviderRegistry` | `registry.models` |
| What tools / capabilities? | `CapabilityRegistry` | `registry.capabilities` |
| What memories do you have? | `MemoryEngine` | `memory.retrieve` |
| How many providers? | `ProviderRegistry` | `registry.models` (count field) |

## Grounding Pipeline

```
User query
    │
    ▼
AthenaOrchestrator (capability selection)
    │
    ├── registry.models node (if query mentions models)
    ├── registry.capabilities node (if query mentions tools/capabilities)
    ├── memory.retrieve node (if query mentions memory/history)
    │
    ▼
runtime.generate node
    │ receives structured CapabilityResult.result dicts from all prior nodes
    │ via context.runtime_state["<capability_id>"]
    ▼
ContextBuilder.build()
    │ formats tool_results as {"tool_name", "success", "output"}
    │ output may be a structured dict (JSON-serialised in prompt)
    ▼
MessageBuilder.build()
    │ injects authoritative tool context as system message:
    │   "Authoritative tool execution results (treat as ground truth):"
    ▼
LLMOrchestrator._inject_metadata()
    │ injects Active Model (authoritative): <model_id>
    ▼
LLM generates response using only supplied context
```

## Prompt Grounding Rules (enforced in MessageBuilder)

1. Tool results message is labelled **"Authoritative tool execution results (treat as ground truth — do not invent alternative values)"**.
2. Structured `dict`/`list` outputs are serialised as compact JSON — no information loss through string concatenation.
3. `selected_model` from `AthenaDecision` is injected as `"Active Model (authoritative): <id>"` in the runtime metadata block.

## What Is NOT Grounded

Conversational responses where no system data is relevant (greetings, general
reasoning) remain LLM-generated.  The distinction is enforced by
`AthenaOrchestrator.CapabilityEngine` — grounding capabilities are only added
to the graph when the query contains relevant intent signals.
