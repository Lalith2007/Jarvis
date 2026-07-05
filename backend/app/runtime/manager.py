from typing import Dict
from app.runtime.session import RuntimeSession
from app.runtime.models import RuntimeStatus

class RuntimeManager:
    def __init__(self):
        self._active_sessions: Dict[str, RuntimeSession] = {}

    def create_session(self) -> RuntimeSession:
        from app.platform.publisher import EventPublisher
        session = RuntimeSession()
        session.transition_to(RuntimeStatus.STARTING)
        self._active_sessions[session.id] = session
        EventPublisher.publish(
            subsystem="runtime",
            event_type="RuntimeSessionStarted",
            payload={"session_id": session.id}
        )
        return session
        
    def get_session(self, session_id: str) -> RuntimeSession | None:
        return self._active_sessions.get(session_id)

    def cleanup_session(self, session_id: str) -> None:
        if session_id in self._active_sessions:
            from app.platform.publisher import EventPublisher
            session = self._active_sessions[session_id]
            session.cleanup()
            del self._active_sessions[session_id]
            EventPublisher.publish(
                subsystem="runtime",
                event_type="RuntimeSessionCompleted",
                payload={"session_id": session_id}
            )
            
    def get_statistics(self) -> dict:
        return {
            "active_sessions_count": len(self._active_sessions),
        }

runtime_manager = RuntimeManager()
