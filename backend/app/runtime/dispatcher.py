from app.runtime.registry import runtime_registry
from app.runtime.executor import runtime_executor
from app.runtime.models import RuntimeResult
from app.capabilities.models import CapabilityDecision

class RuntimeDispatcher:
    def dispatch(self, capability: str, *args, **kwargs) -> RuntimeResult:
        handler = runtime_registry.get_handler(capability)
        if not handler:
            return RuntimeResult(success=False, error=f"No runtime handler for {capability}")
        return runtime_executor.execute(handler, *args, **kwargs)

runtime_dispatcher = RuntimeDispatcher()
