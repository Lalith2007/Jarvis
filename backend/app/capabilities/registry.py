import logging
from typing import Dict, List, Any

from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import CapabilityManifest


logger = logging.getLogger(__name__)


class CapabilityRegistry:
    """
    Centralized Capability Registry for JARVIS.
    Supports discovery, dependency resolution, version tracking, and health reporting.
    """
    def __init__(self):
        self._capabilities: Dict[str, BaseCapability] = {}

    def register(self, capability: BaseCapability) -> None:
        """
        Registers a capability, validating its dependencies.
        """
        manifest = capability.manifest
        
        # Dependency Validation: missing dependencies
        for dep in manifest.dependencies:
            if dep not in self._capabilities:
                raise ValueError(f"Missing dependency: {dep} required by {manifest.id}")
                
        # Future: version compatibility validation (pseudo implementation for now)
        # e.g., dep might specify "network@>=1.0.0"
        
        self._capabilities[manifest.id] = capability
        
        # Emit event
        from app.platform.publisher import EventPublisher
        EventPublisher.publish(
            subsystem="capabilities",
            event_type="CapabilityRegistered",
            payload={"capability_id": manifest.id, "version": manifest.version}
        )

        # Validate cyclic dependencies across all registered capabilities
        self._validate_no_cycles()

    def _validate_no_cycles(self):
        visited = set()
        path = set()

        def visit(node_id: str):
            if node_id in path:
                raise ValueError(f"Cyclic dependency detected involving {node_id}")
            if node_id in visited:
                return
                
            path.add(node_id)
            if node_id in self._capabilities:
                for dep in self._capabilities[node_id].manifest.dependencies:
                    visit(dep)
            path.remove(node_id)
            visited.add(node_id)

        for cap_id in self._capabilities:
            visit(cap_id)

    def unregister(self, capability_id: str) -> None:
        if capability_id in self._capabilities:
            del self._capabilities[capability_id]
            # Emit event
            from app.platform.publisher import EventPublisher
            EventPublisher.publish(
                subsystem="capabilities",
                event_type="CapabilityDisabled",
                payload={"capability_id": capability_id}
            )

    def reload(self) -> None:
        """
        Hot-reload capabilities (mock implementation for plugins).
        """
        self._capabilities.clear()

    def discover(self) -> None:
        """
        Discover capabilities from disk (mock implementation for plugins).
        """
        pass

    def list(self) -> List[CapabilityManifest]:
        """
        List all registered capability manifests.
        """
        return [cap.manifest for cap in self._capabilities.values()]

    def ids(self) -> List[str]:
        """Return all registered capability IDs."""
        return list(self._capabilities.keys())

    def health(self) -> Dict[str, str]:
        """
        Returns health status of all capabilities.
        """
        return {cap.id: cap.health_check() for cap in self._capabilities.values()}

    def get(self, capability_id: str) -> BaseCapability:
        if capability_id not in self._capabilities:
            raise ValueError(f"Capability '{capability_id}' not found.")
        return self._capabilities[capability_id]
        
    def export_state(self) -> Dict[str, Any]:
        """
        Serialize the registry state.
        """
        return {
            "capabilities": [cap.manifest.model_dump() for cap in self._capabilities.values()]
        }

# Global singleton
capability_registry = CapabilityRegistry()
