# JARVIS Architecture

JARVIS is a production-grade AI Operating System designed as an event-driven intelligence pipeline.

## Core Principles
1. **Stateless Subsystems**: All state is managed by `MissionContext` and `MemoryService`.
2. **Event-Driven**: Frontend observes state; Backend publishes state via WebSockets (`PlatformEvent`).
3. **Pydantic Contracts**: Strict JSON validation boundaries for all intra-system transitions.

## Hermes Pipeline
The Hermes Pipeline is the entry point for all asynchronous operations, delegating intent to Athena and tasks to the Mission Controller.

```mermaid
sequenceDiagram
    participant User
    participant Hermes
    participant MissionController
    participant Memory
    participant Athena

    User->>Hermes: POST /api/chat/stream
    Hermes->>MissionController: Start Mission
    MissionController-->>Hermes: MissionContext
    Hermes->>Memory: Build PromptContext
    Hermes->>Athena: Route Request
    Athena-->>Hermes: Streamed Tokens
    Hermes-->>User: SSE Chunk
```

## Mission Lifecycle
Missions represent discrete units of agentic execution. They transition linearly and cannot be re-opened.

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Started : MissionCreated Event
    Started --> Running : Tool Delegated
    Running --> Completed : Agent Finished
    Running --> Failed : Error Bound Reached
    Completed --> [*]
    Failed --> [*]
```

## Runtime Flow
The Sandbox handles tool execution in isolation.

```mermaid
flowchart TD
    A[Planner] --> B{Task Executable?}
    B -- Yes --> C[Runtime Manager]
    B -- No --> D[Athena Clarification]
    C --> E[Execution Sandbox]
    E --> F[Tool Output]
    F --> G[Platform Event: ToolExecuted]
```

## Memory Flow
```mermaid
flowchart LR
    A[Hermes] -->|Query| B[Memory Retrieval]
    B --> C{TimingScope}
    C --> D[Vault Search]
    C --> E[Conversation DB]
    D --> F[Build Context]
    E --> F
    F -->|Insert| G[MissionContext]
```

## Chat Streaming Flow
Handling client-disconnects safely to avoid token leakage.
```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Queue
    participant HermesThread

    Client->>FastAPI: POST /api/chat/stream
    FastAPI->>HermesThread: _run_stream() + CancelEvent
    HermesThread->>Queue: Yield Token
    Queue-->>FastAPI: Get Token
    FastAPI-->>Client: SSE Chunk
    Client--xFastAPI: Disconnect
    FastAPI->>Queue: Set CancelEvent
    Queue->>HermesThread: Break Loop
```
