# Athena Pipeline Execution

The Athena Pipeline guarantees deterministic evaluation by routing user requests through sequential heuristic engines before attempting stochastic evaluation via an LLM.

## Flow Order

```text
Input (PromptContext)
↓
IntentEngine (Extracts primary objective class)
↓
ComplexityEngine (Measures task scale)
↓
CapabilityEngine (Identifies necessary JARVIS capabilities)
↓
MemoryEngine (Plans semantic retrieval)
↓
RiskEngine (Flags dangerous operations)
↓
ModelRankingEngine (Sorts available models by capability matching)
↓
PolicyEngine (Authorizes constraints and budgets)
↓
(IF confidence < threshold) -> LLM Fallback Reasoning
↓
AthenaDecision (Returned to Mission Controller)
```
