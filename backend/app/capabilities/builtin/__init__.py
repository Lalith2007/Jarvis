from app.capabilities.registry import capability_registry
from app.capabilities.builtin.analyzer_cap import AnalyzerCapability
from app.capabilities.builtin.router_cap import RouterCapability
from app.capabilities.builtin.planner_cap import PlannerCapability
from app.capabilities.builtin.executor_cap import ExecutorCapability
from app.capabilities.builtin.reflector_cap import ReflectorCapability

def register_builtins():
    capability_registry.register(AnalyzerCapability())
    capability_registry.register(RouterCapability())
    capability_registry.register(PlannerCapability())
    capability_registry.register(ExecutorCapability())
    capability_registry.register(ReflectorCapability())
