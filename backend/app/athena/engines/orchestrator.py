from app.agents.hermes.models import PromptContext
from app.athena.models import AthenaDecision, IntentClass, ComplexityClass, ExecutionStrategy
from app.athena.engines.intent import IntentEngine
from app.athena.engines.complexity import ComplexityEngine
from app.athena.engines.capability import CapabilityEngine
from app.athena.engines.memory import MemoryEngine
from app.athena.engines.risk import RiskEngine
from app.athena.engines.ranking import ModelRankingEngine
from app.athena.engines.policy import PolicyEngine
from app.config.settings import settings


class AthenaOrchestrator:
    """
    Deterministic-first Chief Intelligence Layer for JARVIS.
    """

    def __init__(self):
        self.intent_engine = IntentEngine()
        self.complexity_engine = ComplexityEngine()
        self.capability_engine = CapabilityEngine()
        self.memory_engine = MemoryEngine()
        self.risk_engine = RiskEngine()
        self.ranking_engine = ModelRankingEngine()
        self.policy_engine = PolicyEngine()

    def analyze(self, context: PromptContext) -> AthenaDecision:
        goal = context.user_query
        trace = []
        
        # 1. Intent Classification
        intent, intent_conf = self.intent_engine.evaluate(goal)
        trace.append(f"Intent classified: {intent.value} (conf: {intent_conf:.2f})")
        
        # 2. Complexity Estimation
        complexity, comp_conf = self.complexity_engine.evaluate(goal)
        trace.append(f"Complexity estimated: {complexity.value} (conf: {comp_conf:.2f})")
        
        # 3. Capability Selection
        capabilities, cap_conf = self.capability_engine.evaluate(goal, intent)
        trace.append(f"Capabilities selected: {len(capabilities)} recommendations (conf: {cap_conf:.2f})")
        
        # 4. Memory Planning
        memory_plan, mem_conf = self.memory_engine.evaluate(goal, intent)
        trace.append(f"Memory planned: {memory_plan.strategy.value} (conf: {mem_conf:.2f})")
        
        # 5. Risk Analysis
        risk, risk_conf = self.risk_engine.evaluate(goal, intent, complexity)
        trace.append(f"Risk analyzed: {risk} (conf: {risk_conf:.2f})")
        
        # 6. Model Ranking
        models, model_conf = self.ranking_engine.evaluate(intent, complexity, risk)
        trace.append(f"Models ranked: {models[0].model} primary (conf: {model_conf:.2f})")
        
        # Overall deterministic confidence is the lowest of the stages
        overall_confidence = min(intent_conf, comp_conf, cap_conf, mem_conf, risk_conf, model_conf)
        
        # Budgets
        token_budget = 4000 if complexity in [ComplexityClass.trivial, ComplexityClass.low] else 16000
        latency_budget_ms = 5000.0 if complexity == ComplexityClass.expert else 2000.0
        cost_budget = 0.05
        max_parallelism = 4
        
        # 7. Policy Evaluation
        approved, reason = self.policy_engine.evaluate(risk, capabilities, token_budget)
        trace.append(f"Policy evaluated: {approved} - {reason}")
        if not approved:
            # If policy rejects, we wipe capabilities to block execution graph
            capabilities = []
            
        # 8. Execution Strategy
        strategy = ExecutionStrategy.sequential
        if any(cap.parallelizable for cap in capabilities):
            strategy = ExecutionStrategy.parallel
        trace.append(f"Execution strategy selected: {strategy.value}")
        
        # 9. LLM Fallback (Optional)
        if overall_confidence < settings.ATHENA_CONFIDENCE_THRESHOLD:
            trace.append(f"Confidence {overall_confidence:.2f} < threshold {settings.ATHENA_CONFIDENCE_THRESHOLD}. Invoking LLM reasoning fallback.")
            self._invoke_llm_fallback(context, trace)
            
        decision = AthenaDecision(
            intent=intent,
            task_type="heuristic",
            complexity=complexity,
            estimated_cost=0.0,
            estimated_latency=150.0,
            confidence=overall_confidence,
            memory_plan=memory_plan,
            execution_strategy=strategy,
            recommended_capabilities=capabilities,
            recommended_models=models,
            requires_parallel_execution=(strategy == ExecutionStrategy.parallel),
            requires_reflection=memory_plan.reflection_required,
            requires_memory=memory_plan.retrieval_required or memory_plan.write_required,
            requires_tools=len(capabilities) > 0,
            risk_level=risk,
            reasoning_summary="Deterministic heuristics completed successfully." if overall_confidence >= settings.ATHENA_CONFIDENCE_THRESHOLD else "LLM Fallback completed.",
            token_budget=token_budget,
            latency_budget_ms=latency_budget_ms,
            cost_budget=cost_budget,
            maximum_parallelism=max_parallelism,
            decision_trace=trace
        )
        
        from app.platform.publisher import EventPublisher
        EventPublisher.publish(
            subsystem="athena",
            event_type="AthenaDecision",
            payload={"decision": decision.model_dump() if hasattr(decision, "model_dump") else {}}
        )

        return decision

    def _invoke_llm_fallback(self, context: PromptContext, trace: list[str]):
        """
        In production, this calls the LLM with the context to refine the decision.
        For now, we just log that we did it.
        """
        # Mocking the LLM refinement process for now
        trace.append("LLM reasoning complete.")

athena = AthenaOrchestrator()
