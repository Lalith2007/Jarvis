# Graph Event Telemetry Model

With Sprint 12.1, the internal backend `MissionEventBus` is extended to support comprehensive Graph Telemetry via the `PlatformEvent` subsystem.

## Graph Lifecycle Events

Events are natively pushed to `EventPublisher` and injected into the overall JARVIS event stream (for eventual consumption by UI Dashboards or downstream loggers).

### Mission-Level Telemetry
- `MissionStarted`: Triggered when the `MissionGraph` begins execution.
- `MissionCompleted`: Triggered when all leaf nodes successfully evaluate.
- `MissionFailed`: Triggered when the graph fails (due to timeout, max retries exhausted, or catastrophic exception).

### Node-Level Telemetry
- `NodeQueued`: Triggered when dependencies are met and the Node is added to the concurrency thread pool.
- `NodeStarted`: Triggered when execution begins. Includes `attempt` count for retry visibility.
- `NodeCompleted`: Triggered when execution finishes. Includes `execution_time_ms`.
- `NodeFailed`: Triggered upon failure. Includes error payload and active `attempt`.
- `NodeCancelled`: Triggered when the node is skipped due to a fail-fast cascade failure occurring upstream.

## Payload Characteristics
Events uniformly pass:
- `mission_id`: Uniquely tying telemetry to the mission trace.
- `session_id`: Runtime UI or environment trace.
- Node telemetry is injected into the event `payload` object.
