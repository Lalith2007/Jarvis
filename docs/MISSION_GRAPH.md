# Mission Graph Architecture

JARVIS now utilizes a Capability-Driven Mission Execution Graph.

## Overview

The legacy linear pipeline (`analyze` -> `route` -> `plan` -> `execute` -> `reflect`) has been fully decoupled into an immutable, versioned graph structure consisting of independent nodes.

## Domain Models

### `MissionGraph`

A directed acyclic graph (DAG) representing the complete execution flow of a `Mission`.

- **Attributes**:
    - `graph_id`: Independent identifier tracking graph topology.
    - `schema_version`: Defines the structure of the JSON blob (Sprint 12.1 is `1.0`).
    - `graph_version`: Defines the specific logic iteration.
    - `nodes`: Map of `node_id` to `MissionNode`.
- **Metrics**:
    - Tracks overall execution duration, successful nodes, and failed nodes.
- **Persistence**:
    - Exposes `.to_dict()`, `.from_dict()`, `.to_json()`, and `.from_json()` to support persistent storage, replay, and timeline visualization in the Dashboard.

### `MissionNode`

An individual execution vertex in the graph. It strictly defines the *capability* required, without binding to runtime Python Callables.

- **Attributes**:
    - `type`: Category of the node (`LLM`, `MEMORY`, `TOOL`, `PLANNER`, `RUNTIME`, `AGGREGATOR`).
    - `status`: Execution state (`PENDING`, `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`).
    - `dependencies`: List of `node_id`s that must complete successfully before this node starts.
    - `capability`: The string identifier of the requested subsystem capability (e.g., `planner.plan`).
    - `payload`: Execution parameters injected into the node.
- **Execution & Telemetry**:
    - Emits metrics like `queue_time_ms`, `execution_time_ms`, `capability_latency`.
    - Enforces resilience bounds: `retry_count`, `timeout`.

## Mission Identifiers

Every `Mission` object now carries decoupled, independent identifiers to facilitate future distributed tracing:
- `mission_id`: Uniquely identifies the user's root goal.
- `graph_id`: Identifies the execution topology schema.
- `execution_id`: Identifies the specific runtime `ExecutionContext`.
