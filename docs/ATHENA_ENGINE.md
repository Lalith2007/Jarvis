# Athena Engine Architecture

The Athena Intelligence Engine is the deterministic-first intelligence layer of the JARVIS AI Operating System.

## Core Philosophy

Athena is **NOT** just an LLM router. It is a deeply heuristic pipeline that attempts to completely categorize, plan, and route a task deterministically before ever invoking an LLM. 

By running tasks through a set of heuristic engines (Intent, Complexity, Capability, Memory, Risk), Athena generates an `AthenaDecision` object containing strict execution limits (token budget, latency limits) and topological graph requirements. 

Only when the deterministic confidence score drops below `ATHENA_CONFIDENCE_THRESHOLD` (default 0.80) does Athena invoke an LLM for fallback reasoning.

## The Engines
1. **IntentEngine**: Detects the goal type (coding, research, etc.).
2. **ComplexityEngine**: Measures task scope and difficulty.
3. **CapabilityEngine**: Emits `CapabilityRecommendation` objects.
4. **MemoryEngine**: Constructs a `MemoryPlan` for semantic/episodic retrieval.
5. **RiskEngine**: Evaluates execution safety.
6. **PolicyEngine**: Authorizes graph execution.
7. **ModelRankingEngine**: Selects the optimal LLM.
