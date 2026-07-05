from typing import Any, Callable, Dict

from app.mission.graph import MissionNode

CapabilityExecutor = Callable[[MissionNode], Any]

class CapabilityRegistry:
    """
    Registry for Graph Capabilities.
    Allows decoupling capabilities from the GraphExecutionManager.
    """
    def __init__(self):
        self._capabilities: Dict[str, CapabilityExecutor] = {}

    def register(self, capability_name: str, executor: CapabilityExecutor) -> None:
        """
        Register an executor for a specific capability name.
        """
        if capability_name in self._capabilities:
            import logging
            logging.getLogger(__name__).warning(f"Overwriting capability: {capability_name}")
        self._capabilities[capability_name] = executor

    def resolve(self, capability_name: str) -> CapabilityExecutor:
        """
        Resolve the executor for a capability name.
        """
        if capability_name not in self._capabilities:
            raise ValueError(f"Capability '{capability_name}' is not registered.")
        return self._capabilities[capability_name]

    def execute(self, node: MissionNode) -> Any:
        """
        Execute a node using its registered capability executor.
        """
        executor = self.resolve(node.capability)
        return executor(node)

# Global singleton
capability_registry = CapabilityRegistry()
