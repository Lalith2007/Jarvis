from app.runtime.dispatcher import runtime_dispatcher
from app.runtime.manager import runtime_manager
from app.capabilities.models import CapabilityType
from app.runtime.models import SecurityAction
from app.runtime.session import RuntimeSession

class RuntimeService:
    def create_session(self) -> RuntimeSession:
        return runtime_manager.create_session()
        
    def execute_capability(self, capability: CapabilityType, session: RuntimeSession, action: SecurityAction = SecurityAction.EXECUTE, resource: str | None = None, *args, **kwargs):
        return runtime_dispatcher.dispatch(capability, session, action, resource, *args, **kwargs)
        
    def cleanup_session(self, session: RuntimeSession) -> None:
        runtime_manager.cleanup_session(session.id)

runtime_service = RuntimeService()
