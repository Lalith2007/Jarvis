from app.capabilities.models import CapabilityType
from app.runtime.models import SecurityAction, RuntimePermission
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self):
        self._policies: dict[CapabilityType, set[SecurityAction]] = {}
        
    def set_policy(self, capability: CapabilityType, allowed_actions: list[SecurityAction]) -> None:
        self._policies[capability] = set(allowed_actions)

    def validate_permission(self, capability: CapabilityType, action: SecurityAction, resource: str | None = None) -> bool:
        allowed = self._policies.get(capability, set())
        is_allowed = action in allowed
        
        decision = "ALLOWED" if is_allowed else "DENIED"
        logger.info(f"Security Audit: {decision} {action.value} on {capability.value} (resource: {resource})")
        
        return is_allowed

security_manager = SecurityManager()
security_manager.set_policy(CapabilityType.FILESYSTEM, [SecurityAction.READ, SecurityAction.WRITE])
security_manager.set_policy(CapabilityType.TERMINAL, [SecurityAction.EXECUTE])
security_manager.set_policy(CapabilityType.PYTHON_RUNTIME, [SecurityAction.EXECUTE])
security_manager.set_policy(CapabilityType.BROWSER, [SecurityAction.CONNECT, SecurityAction.READ, SecurityAction.WRITE])
