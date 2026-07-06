# Tool Context Schema — Sprint 12.8

## ToolResult envelope

Every capability output passed to `runtime.generate` follows this structure:

```json
{
  "tool_name": "<capability_id>",
  "success": true,
  "output": <CapabilityResult.result>
}
```

`output` may be:
- A **plain string** — legacy capabilities, e.g. planner output.
- A **structured dict or list** — grounding capabilities (see below).

## Grounding Capability Schemas

### registry.models

```json
{
  "models": [
    {
      "id": "z-ai/glm-5.2",
      "display_name": "GLM-5.2",
      "provider": "nvidia",
      "context_window": 1000000,
      "enabled": true,
      "healthy": true,
      "capabilities": ["chat", "reasoning", "coding", "tools", "long_context", "streaming"]
    }
  ],
  "count": 6
}
```

Source: `ProviderRegistry._models` (populated by `_register_defaults()`).

### registry.capabilities

```json
{
  "capabilities": [
    {
      "id": "runtime.generate",
      "name": "Runtime Generative Engine",
      "version": "1.0.0",
      "description": "Executes generative AI models (LLMs).",
      "category": "Tool",
      "permissions": ["execute:generation"]
    }
  ],
  "count": 10
}
```

Source: `CapabilityRegistry._capabilities` (populated by `register_builtins()`).

### memory.retrieve

```json
{
  "results": [
    {
      "id": "...",
      "content": "...",
      "title": "...",
      "tags": [],
      "created_at": "..."
    }
  ],
  "execution_time_ms": 12.4
}
```

Source: `MemoryEngine.search()`.

## MessageBuilder Serialisation (Sprint 12.8)

Structured `dict` / `list` outputs are serialised via `json.dumps(indent=2)`.

Plain string outputs are passed through as-is.

The containing system message reads:
```
Authoritative tool execution results
(treat as ground truth — do not invent alternative values):
```
