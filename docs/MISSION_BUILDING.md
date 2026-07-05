# Dynamic Mission Graph Building

The `MissionGraphBuilder` no longer uses a static pipeline.

It dynamically assembles Directed Acyclic Graphs (DAG) based purely on the `AthenaDecision`.

1. **Pre-requisite Nodes**: If `memory_plan.retrieval_required` is True, it inserts a `NodeType.MEMORY` node at the root.
2. **Capability Nodes**: For every capability in `recommended_capabilities`, it generates a `NodeType.TOOL` node (or `PLANNER` if applicable) that depends on the root.
3. **Execution Strategy**: If `execution_strategy == parallel`, multiple capability nodes are generated side-by-side with identical dependencies.
4. **Reflection**: A `NodeType.AGGREGATOR` reflection node is placed as the final terminal node if `requires_reflection` is True.
