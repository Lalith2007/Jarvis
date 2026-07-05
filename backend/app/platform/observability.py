import time
import traceback
from contextlib import ContextDecorator
from typing import Optional, Type, Any

from app.platform.publisher import EventPublisher

class TimingScope(ContextDecorator):
    """
    Context manager for standardizing observability, timing, and error handling.
    Emits Started, Completed, and Failed events.
    """
    def __init__(
        self,
        subsystem: str,
        event_base: str,
        session_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        payload: Optional[dict] = None
    ):
        self.subsystem = subsystem
        self.event_base = event_base
        self.session_id = session_id
        self.mission_id = mission_id
        self.execution_id = execution_id
        self.payload = payload or {}
        self.start_t = 0.0

    def __enter__(self):
        self.start_t = time.perf_counter()
        EventPublisher.publish(
            subsystem=self.subsystem,
            event_type=f"{self.event_base}Started",
            session_id=self.session_id,
            mission_id=self.mission_id,
            execution_id=self.execution_id,
            payload=self.payload
        )
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any]
    ) -> bool:
        dur = int((time.perf_counter() - self.start_t) * 1000)
        
        if exc_val is None:
            EventPublisher.publish(
                subsystem=self.subsystem,
                event_type=f"{self.event_base}Completed",
                session_id=self.session_id,
                mission_id=self.mission_id,
                execution_id=self.execution_id,
                duration_ms=dur,
                status="success",
                payload=self.payload
            )
            return False

        # Error case
        error_payload = {
            **self.payload,
            "error_type": exc_val.__class__.__name__,
            "error_message": str(exc_val),
            "recoverable": getattr(exc_val, "recoverable", False),
            "stack_trace": "".join(traceback.format_tb(exc_tb))
        }

        EventPublisher.publish(
            subsystem=self.subsystem,
            event_type=f"{self.event_base}Failed",
            session_id=self.session_id,
            mission_id=self.mission_id,
            execution_id=self.execution_id,
            duration_ms=dur,
            status="error",
            severity="error",
            payload=error_payload
        )
        
        # We do not suppress the exception unless it's a specific handled one,
        # but the constraint says: "Never throw raw exceptions directly to the frontend."
        # This means at the API boundary they should be caught, or here?
        # Re-raise so the pipeline can halt if it's not recoverable.
        return False
