# ADR 004: Reflection Engine

## Rationale
Missions must evaluate their own performance to build long-term agent memory.

## Alternatives Considered
- LLM-based reflection: Rejected for V1 due to high latency, token cost, and non-determinism.
- Inline reflection: Rejected due to adding latency to user requests.

## Decision
Implement an offline, asynchronous, fully deterministic rule-based evaluation pipeline that runs immediately after mission success/failure.

## Future Extensions
Incorporate offline LLM review for CRITICAL failure missions where heuristics fall short.
