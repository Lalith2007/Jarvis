# ADR 005: Transport-Agnostic Streaming

## Status
Accepted

## Context
In Sprint 12.6, we discovered a major architectural violation: `Hermes.chat_stream` was bypassing the `MissionPipeline` entirely and calling the `llm_provider.stream` directly via a Python generator in order to stream responses back to the user. This meant streamed requests were not planned, executed, evaluated, or checked by policy engines, destroying the platform's core premise of having a unified intelligence layer (`Athena`).

We needed a way to stream responses back to the client while strictly enforcing that every request traverses the full `Hermes -> MissionController -> Athena -> Graph -> Capability` path. The challenge was that the graph execution model was synchronous and capabilities returned serializable result models (`CapabilityResult`), which are fundamentally incompatible with raw Python generators.

## Decision
We decided to treat streaming as a **transport concern** rather than a graph or capability return type concern.

1. **`StreamRegistry` Abstraction**: We introduced a `StreamRegistry` in the Runtime layer. When `RuntimeGenerateCapability` receives a request with `stream=True`, it allocates a new `StreamHandle` (with a queue and ID) in the registry.
2. **Background Execution**: The generation itself runs in a background thread spawned by the capability. Tokens are pushed into the `StreamHandle` queue as they arrive.
3. **Serializable Pointer**: The capability immediately returns a serializable pointer to the stream (`StreamResult` containing the `stream_id`). This allows the Graph Execution Manager to finish the graph and return standard serializable data through `AgentResult` and `ToolResult`.
4. **Synchronous Consumption**: `Hermes.chat_stream` invokes the pipeline with `stream=True`. Once the graph returns the `stream_id`, Hermes looks up the `StreamHandle` in the registry and yields the chunks synchronously.

## Consequences

### Positive
- The `MissionGraph` and `CapabilityResult` remain fully serializable, satisfying persistence and observability constraints.
- Every request (sync or stream) now correctly traverses the `MissionPipeline`.
- Streaming logic is completely decoupled from graph execution, allowing capabilities to stream asynchronously.

### Negative
- Streaming involves thread creation within the capability, slightly increasing resource usage.
- Error handling in the background stream worker must be carefully managed to ensure the stream handle is always terminated properly.
