from app.runtime.dispatcher import runtime_dispatcher
from app.runtime.manager import runtime_manager
from app.capabilities.models import CapabilityType
from app.runtime.models import SecurityAction
from app.runtime.session import RuntimeSession

class RuntimeService:
    def create_session(self) -> RuntimeSession:
        return runtime_manager.create_session()
        
    def execute_capability(self, capability: CapabilityType, session: RuntimeSession, action: SecurityAction = SecurityAction.EXECUTE, resource: str | None = None, provider_name: str | None = None, *args, **kwargs):
        from app.platform.publisher import EventPublisher
        EventPublisher.publish(
            subsystem="runtime",
            event_type="ProviderStarted",
            payload={"capability": capability, "provider_name": provider_name}
        )
        result = runtime_dispatcher.dispatch(capability, session, action, resource, provider_name, *args, **kwargs)
        EventPublisher.publish(
            subsystem="runtime",
            event_type="ProviderCompleted",
            payload={"capability": capability, "provider_name": provider_name, "success": result.success}
        )
        return result
        
    def cleanup_session(self, session: RuntimeSession) -> None:
        runtime_manager.cleanup_session(session.id)

runtime_service = RuntimeService()
