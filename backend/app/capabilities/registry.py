import logging
from datetime import datetime, timezone
from typing import Dict, List, Any

from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import CapabilityManifest, CapabilityMetrics


logger = logging.getLogger(__name__)


class CapabilityRegistry:
    """
    Centralized Capability Registry for JARVIS.
    Supports discovery, dependency resolution, version tracking, health
    reporting, and per-capability execution metrics (Sprint 13.1 observability).
    """
    def __init__(self):
        self._capabilities: Dict[str, BaseCapability] = {}
        self._metrics: Dict[str, CapabilityMetrics] = {}

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

    def record_metrics(
        self, capability_id: str, success: bool, latency_ms: float, cost: float = 0.0
    ) -> None:
        """
        Update rolling execution metrics for a capability. Called by the
        capability lifecycle after every execution (success or failure).
        """
        m = self._metrics.get(capability_id)
        if m is None:
            m = CapabilityMetrics()
            self._metrics[capability_id] = m
        n = m.execution_count
        m.execution_count = n + 1
        if not success:
            m.failure_count += 1
        # Rolling means
        m.average_latency = (m.average_latency * n + latency_ms) / (n + 1)
        m.average_cost = (m.average_cost * n + cost) / (n + 1)
        m.last_execution = datetime.now(timezone.utc)
        # Health score = success rate * 100
        ok = m.execution_count - m.failure_count
        m.health_score = round((ok / m.execution_count) * 100, 1)

    def metrics(self) -> Dict[str, CapabilityMetrics]:
        """Return execution metrics keyed by capability id."""
        return dict(self._metrics)

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
