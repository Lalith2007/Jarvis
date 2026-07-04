from app.runtime.dispatcher import runtime_dispatcher
from app.runtime.manager import runtime_manager
from app.capabilities.models import CapabilityType

class RuntimeService:
    def execute_capability(self, capability: CapabilityType, *args, **kwargs):
        return runtime_dispatcher.dispatch(capability.value, *args, **kwargs)

runtime_service = RuntimeService()
