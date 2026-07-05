# Reflection & Learning Engine

The Reflection & Learning Engine evaluates completed missions to generate structured Learning Artifacts without impacting user-facing latency or modifying upstream system states. 

It is completely read-only and deterministic.

## Execution Order
Mission Execution -> Response to Client -> ReflectionOrchestrator starts asynchronously -> ReflectionResult published.

## Deterministic Nature
The engine relies on pure rule-based extractors (independent engines) to prevent unreliability and latency bloat compared to LLM-based approaches.
