from app.runtime.registry import runtime_registry
from app.runtime.executor import runtime_executor
from app.runtime.models import RuntimeResult, SecurityAction, RuntimeStatus
from app.runtime.security import security_manager
from app.capabilities.models import CapabilityType
from app.runtime.session import RuntimeSession

class RuntimeDispatcher:
    def dispatch(
        self, 
        capability: CapabilityType, 
        session: RuntimeSession, 
        action: SecurityAction = SecurityAction.EXECUTE,
        resource: str | None = None,
        provider_name: str | None = None,
        *args, 
        **kwargs
    ) -> RuntimeResult:
        if not security_manager.validate_permission(capability, action, resource):
            result = RuntimeResult(success=False, error=f"Permission denied: {action.value} on {capability.value}")
            session.add_result(result)
            return result
            
        provider = runtime_registry.get_provider(capability, provider_name)
        if not provider:
            result = RuntimeResult(success=False, error=f"No healthy runtime provider found for {capability.value}")
            session.add_result(result)
            return result
            
        session.transition_to(RuntimeStatus.RUNNING)
        session.active_runtime = provider.metadata.name
        
        result = runtime_executor.execute(provider.handler, session, *args, **kwargs)
        
        session.add_result(result)
        
        if result.success:
            session.transition_to(RuntimeStatus.COMPLETED)
        else:
            session.transition_to(RuntimeStatus.FAILED)
            
        return result

runtime_dispatcher = RuntimeDispatcher()
