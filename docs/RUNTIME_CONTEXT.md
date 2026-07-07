# Runtime Context — Sprint 12.8

## What CapabilityContext.runtime_state Contains at runtime.generate

When `runtime.generate` executes it receives `CapabilityContext.runtime_state`
populated by the `GraphExecutionManager`.  Prior node results are merged in at
`mission/engine.py:68`:

```python
node.payload[dep_node.capability] = dep_node.result
```

### Standard keys (always present)

| Key | Type | Source |
|---|---|---|
| `goal` | `str` | Original user query |
| `mission_id` | `str` | `MissionController.create()` |
| `execution_id` | `str` | `ExecutionManager.create()` |
| `session_id` | `str` | Hermes |
| `stream` | `bool` | Request flag |

### Grounding keys (present when capability ran)

| Key | Type | Source |
|---|---|---|
| `registry.models` | `dict` — `{"models": [...], "count": int}` | `RegistryCapability` |
| `registry.capabilities` | `dict` — `{"capabilities": [...], "count": int}` | `CapabilityRegistryCapability` |
| `memory.retrieve` | `dict` — `{"results": [...], "execution_time_ms": float}` | `MemoryReadCapability` |

## How runtime.generate Builds tool_results

```python
tool_results = []
for key, value in context.runtime_state.items():
    if key not in _INTERNAL_STATE_KEYS:
        tool_results.append(
            {"tool_name": key, "success": True, "output": value}
        )
```

`_INTERNAL_STATE_KEYS = {"goal", "query", "session_id", "mission_id", "execution_id", "stream"}`

All grounding keys pass through and become entries in `tool_results`.

## ContextBuilder Contract (Post-Sprint 12.8)

`ContextBuilder.build()` is a **formatter only**.  It accepts `tool_results`
as a parameter and formats them into `PromptContext`.  It does not:

- Query the vault
- Call Athena
- Retrieve memories
- Discover capabilities

All data arrives pre-computed from the Mission Graph.
