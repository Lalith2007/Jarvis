from typing import Any, Dict, Optional
from app.platform.models import PlatformEvent
from app.platform.event_bus import event_bus

class EventPublisher:
    """
    Helper interface for subsystems to easily construct and publish events.
    """
    @staticmethod
    def publish(
        subsystem: str,
        event_type: str,
        mission_id: Optional[str] = None,
        session_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        status: str = "success",
        severity: str = "info",
        duration_ms: int = 0,
        payload: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        event = PlatformEvent(
            subsystem=subsystem,
            event_type=event_type,
            mission_id=mission_id,
            session_id=session_id,
            execution_id=execution_id,
            status=status,
            severity=severity,
            duration_ms=duration_ms,
            payload=payload or {},
            metadata=metadata or {}
        )
        event_bus.publish(event)
