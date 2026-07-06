import time
import logging
from datetime import datetime, timezone

from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import CapabilityContext, CapabilityResult, CapabilityDiagnostics
from app.platform.publisher import EventPublisher


logger = logging.getLogger(__name__)


class CapabilityExecutorLifecycle:
    """
    Manages the strict lifecycle of capability execution.
    """
    
    def execute(self, capability: BaseCapability, context: CapabilityContext) -> CapabilityResult:
        diagnostics = CapabilityDiagnostics(
            initialized_at=datetime.now(timezone.utc)
        )
        # Defined up front so metrics recording works even if initialize/validate raises.
        start_time = time.time()

        EventPublisher.publish(
            subsystem="capabilities",
            event_type="CapabilityInitialized",
            payload={"capability_id": capability.id, "mission_id": context.mission_id}
        )
        
        try:
            # 1. Initialize
            capability.initialize(context)
            diagnostics.execution_trace.append("Initialized successfully.")
            
            # 2. Validate
            capability.validate(context)
            diagnostics.execution_trace.append("Validation passed.")
            
            # 3. Execute
            diagnostics.started_at = datetime.now(timezone.utc)
            EventPublisher.publish(
                subsystem="capabilities",
                event_type="CapabilityStarted",
                payload={"capability_id": capability.id, "mission_id": context.mission_id}
            )
            
            start_time = time.time()
            result: CapabilityResult = capability.execute(context, diagnostics)
            execution_time = time.time() - start_time
            
            # 4. Metrics & Diagnostics
            result.execution_time = execution_time
            diagnostics.completed_at = datetime.now(timezone.utc)
            diagnostics.execution_trace.append(f"Execution completed in {execution_time:.3f}s.")
            result.diagnostics = diagnostics
            
            EventPublisher.publish(
                subsystem="capabilities",
                event_type="CapabilityCompleted",
                payload={"capability_id": capability.id, "mission_id": context.mission_id, "success": result.success}
            )

            self._record_metrics(capability, result.success, execution_time * 1000)
            return result

        except Exception as e:
            diagnostics.exceptions.append(str(e))
            diagnostics.execution_trace.append(f"Execution failed: {e}")
            logger.error(f"Capability {capability.id} failed: {e}", exc_info=True)

            EventPublisher.publish(
                subsystem="capabilities",
                event_type="CapabilityFailed",
                payload={"capability_id": capability.id, "mission_id": context.mission_id, "error": str(e)}
            )

            self._record_metrics(capability, False, (time.time() - start_time) * 1000)
            return CapabilityResult(
                success=False,
                status="failed",
                errors=[str(e)],
                diagnostics=diagnostics
            )
            
        finally:
            # 5. Cleanup (always runs)
            try:
                capability.cleanup(context)
                diagnostics.execution_trace.append("Cleanup successful.")
            except Exception as e:
                logger.error(f"Capability {capability.id} cleanup failed: {e}", exc_info=True)
                diagnostics.execution_trace.append(f"Cleanup failed: {e}")

            # 6. Health Check (post-execution)
            try:
                health = capability.health_check()
                if health != capability.health_status:
                    capability.health_status = health
                    EventPublisher.publish(
                        subsystem="capabilities",
                        event_type="CapabilityHealthChanged",
                        payload={"capability_id": capability.id, "status": health}
                    )
            except Exception as e:
                logger.error(f"Capability {capability.id} health check failed: {e}", exc_info=True)

    @staticmethod
    def _record_metrics(capability: BaseCapability, success: bool, latency_ms: float) -> None:
        """Record execution metrics in the registry (Sprint 13.1 observability)."""
        try:
            from app.capabilities.registry import capability_registry
            capability_registry.record_metrics(capability.id, success, latency_ms)
        except Exception as exc:  # metrics must never break execution
            logger.debug("metrics recording skipped for %s: %s", capability.id, exc)

capability_lifecycle = CapabilityExecutorLifecycle()
