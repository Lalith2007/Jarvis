# Policy Engine

The Policy Engine executes prior to any graph generation. Its responsibility is to enforce global safety and resource usage invariants.

## Rule Evaluations
1. **Token Budgets**: If the `token_budget` proposed by the complexity engine exceeds the system's absolute maximum of 32,000 tokens, the request is immediately flagged and capabilities are dropped.
2. **Safety and Risk**: High-risk tasks are flagged for frontend authorization. If authorization is bypassed, the capability is wiped.
3. **Capability Restrictions**: The engine verifies that no recommended capability is on the dynamically updated global ban-list.

If the Policy Engine returns `approved=False`, the pipeline aborts graph generation to ensure zero risk of rogue execution.
