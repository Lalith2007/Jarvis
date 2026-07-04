from app.capabilities.models import CapabilityType

class SecurityManager:
    def validate_permission(self, capability: CapabilityType, action: str) -> bool:
        return True

security_manager = SecurityManager()
