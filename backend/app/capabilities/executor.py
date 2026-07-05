import time
import logging
from datetime import datetime

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
            initialized_at=datetime.utcnow()
        )
        
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
            diagnostics.started_at = datetime.utcnow()
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
            diagnostics.completed_at = datetime.utcnow()
            diagnostics.execution_trace.append(f"Execution completed in {execution_time:.3f}s.")
            result.diagnostics = diagnostics
            
            EventPublisher.publish(
                subsystem="capabilities",
                event_type="CapabilityCompleted",
                payload={"capability_id": capability.id, "mission_id": context.mission_id, "success": result.success}
            )
            
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

capability_lifecycle = CapabilityExecutorLifecycle()
