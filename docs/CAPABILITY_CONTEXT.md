# Capability Context

Capabilities NEVER communicate directly with the global graph engine. Instead, they receive a localized `CapabilityContext`.

## Schema
- `mission_id`: Associated mission UUID.
- `graph_id`: Graph UUID.
- `execution_id`: Node execution UUID.
- `resource_budget`: Pre-approved execution limits set by Athena.
- `runtime_state`: A localized clone of node inputs and runtime memory.
- `approved_resources`: Sandbox isolation paths restricting filesystem/network access.

Capabilities failing to respect their resource budget or attempting to break sandbox isolation will be forcefully terminated.
