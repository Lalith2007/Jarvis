from app.capabilities.registry import capability_registry
from app.capabilities.builtin.analyzer_cap import AnalyzerCapability
from app.capabilities.builtin.router_cap import RouterCapability
from app.capabilities.builtin.planner_cap import PlannerCapability
from app.capabilities.builtin.executor_cap import ExecutorCapability
from app.capabilities.builtin.reflector_cap import ReflectorCapability
from app.capabilities.builtin.runtime_cap import RuntimeGenerateCapability
from app.capabilities.builtin.registry_cap import RegistryCapability
from app.capabilities.builtin.capabilities_cap import CapabilityRegistryCapability
from app.capabilities.builtin.repository_cap import RepositoryReadCapability
from app.memory.capabilities import MemoryReadCapability, MemoryWriteCapability


def register_builtins():
    capability_registry.register(AnalyzerCapability())
    capability_registry.register(RouterCapability())
    capability_registry.register(PlannerCapability())
    capability_registry.register(ExecutorCapability())
    capability_registry.register(ReflectorCapability())
    capability_registry.register(RuntimeGenerateCapability())
    capability_registry.register(RegistryCapability())
    capability_registry.register(CapabilityRegistryCapability())
    capability_registry.register(RepositoryReadCapability())
    capability_registry.register(MemoryReadCapability())
    capability_registry.register(MemoryWriteCapability())
