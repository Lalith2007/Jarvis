# Decision Trace

The `decision_trace` field in the `AthenaDecision` object is an exactly-ordered diagnostic log populated deterministically during the intelligence phase.

Example Trace:
```text
1. Intent classified: coding (conf: 0.90)
2. Complexity estimated: high (conf: 0.85)
3. Capabilities selected: 2 recommendations (conf: 0.90)
4. Memory planned: working (conf: 0.95)
5. Risk analyzed: medium (conf: 0.80)
6. Models ranked: openai/gpt-oss-120b primary (conf: 0.98)
7. Policy evaluated: True - Policy checks passed.
8. Execution strategy selected: parallel
```

This trace provides extreme explainability into *why* the intelligence layer constructed the specific graph it did. It allows developers to debug misclassifications by isolating which engine triggered the errant heuristic.
