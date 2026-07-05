from abc import ABC, abstractmethod
from typing import Any

from app.capabilities.core.models import (
    CapabilityManifest,
    CapabilityConfig,
    CapabilityContext,
    CapabilityResult,
    CapabilityDiagnostics,
)


class BaseCapability(ABC):
    """
    Formal abstract interface for all capabilities in JARVIS.
    """

    def __init__(self, manifest: CapabilityManifest, config: CapabilityConfig):
        self.manifest = manifest
        self.config = config
        self.enabled = manifest.enabled_by_default
        self.health_status = "unknown"

    @property
    def id(self) -> str:
        return self.manifest.id

    @property
    def name(self) -> str:
        return self.manifest.name
        
    @property
    def version(self) -> str:
        return self.manifest.version

    @abstractmethod
    def initialize(self, context: CapabilityContext) -> None:
        """
        Setup capability before execution.
        """
        pass

    @abstractmethod
    def validate(self, context: CapabilityContext) -> None:
        """
        Validate context, permissions, and dependencies before execution.
        Must raise an exception if validation fails.
        """
        pass

    @abstractmethod
    def execute(self, context: CapabilityContext, diagnostics: CapabilityDiagnostics) -> CapabilityResult:
        """
        Core execution logic. Must return CapabilityResult.
        """
        pass

    @abstractmethod
    def cleanup(self, context: CapabilityContext) -> None:
        """
        Resource cleanup. Always called, even on failure.
        """
        pass

    @abstractmethod
    def health_check(self) -> str:
        """
        Returns the current health status ('healthy', 'degraded', 'failed').
        """
        pass

    @abstractmethod
    def estimate_cost(self, context: CapabilityContext) -> float:
        """
        Estimate the financial cost of this execution.
        """
        pass

    @abstractmethod
    def estimate_latency(self, context: CapabilityContext) -> float:
        """
        Estimate the latency (in milliseconds) of this execution.
        """
        pass
