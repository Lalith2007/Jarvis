# Graph Execution Engine

The `GraphExecutionManager` (`app/mission/engine.py`) is the topological scheduler for Mission Graphs. It replaces the static, hardcoded linear execution logic found in the legacy pipeline.

## Execution Mechanics

1. **Topological Sorting & Dependencies**: 
   The engine builds a reverse dependency map to continuously evaluate which nodes are eligible (runnable). A node becomes runnable when all its defined `dependencies` have successfully transitioned to the `COMPLETED` state.
   
2. **Parallel Scheduling**:
   Runnable nodes are queued concurrently using a `ThreadPoolExecutor` (allowing multiple parallel tool boundaries or future autonomous multi-agent routes).
   
3. **Payload Injection**:
   Before a node is started, the execution engine retrieves the `result` from all its completed dependencies and merges them sequentially into the current node's `payload`.
   For example, when `planner` yields a `Plan` object, the execution manager injects this object into the downstream `executor` node's payload.

4. **Fail-Fast & Cancellation**:
   If any node enters a `FAILED` state (exhausting all retry limits), the execution engine immediately:
   - Registers a graph failure.
   - Triggers `_cancel_node()` cascading across all remaining `PENDING` or `QUEUED` nodes in the topology.
   - Prevents further scheduling and halts the `Mission`.

5. **Retry Logic**:
   The `_execute_node_with_retries` module wraps the `CapabilityManager` boundary in an attempt loop governed by `node.retry_count`.

## Architectural Boundaries

The execution engine **strictly evaluates scheduling**. 
It evaluates:
- `node.dependencies`
- `node.status`
- `node.retry_count`

It **never** evaluates:
- `node.type`
- Business logic or LLM context routing.

Execution is delegated blindly and exclusively to the `CapabilityManager`.
