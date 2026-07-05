# JARVIS Platform Event Schema (v1.0)

The `PlatformEvent` schema is the single source of truth for observability, logging, and frontend telemetry.

## Schema Definition
All events MUST validate against this exact Pydantic model:

```json
{
  "schema_version": "1.0",
  "id": "uuid4",
  "request_id": "uuid4",
  "mission_id": "uuid4 (optional)",
  "session_id": "uuid4 (optional)",
  "execution_id": "uuid4 (optional)",
  "timestamp": "ISO-8601 UTC string",
  "subsystem": "string (enum)",
  "event_type": "string",
  "status": "string (success | started | failed | pending)",
  "severity": "string (info | warning | error | critical)",
  "duration_ms": "integer",
  "payload": "object (freeform)",
  "metadata": "object (freeform)"
}
```

## Standard Event Types

| Subsystem | Event Type | Description |
|---|---|---|
| `hermes` | `HermesReceivedRequest` | Initial request received from client. |
| `mission_pipeline` | `MissionCreated` | Mission instantiated and ID generated. |
| `mission_pipeline` | `MissionStarted` | Mission pipeline execution begins. |
| `memory` | `MemoryRetrievalStarted` | TimingScope entry for Vault access. |
| `memory` | `MemoryRetrievalCompleted` | TimingScope exit for Vault access. |
| `athena` | `AthenaRouted` | Emits routing decision model in `payload`. |
| `runtime` | `ToolExecuted` | Emits `tool_name` and `success` boolean. |
| `mission_pipeline` | `MissionCompleted` | Final status before chat stream begins. |
| `mission_pipeline` | `MissionFailed` | Pipeline aborted due to unrecoverable exception. |

## Immutability Guarantee
Fields like `schema_version`, `id`, `timestamp`, and `request_id` are strictly enforced. Nulls are not permitted for `request_id`.
