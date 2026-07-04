from app.runtime.security import security_manager
from app.capabilities.models import CapabilityType
from app.runtime.models import SecurityAction

def test_permission_denied():
    result = security_manager.validate_permission(CapabilityType.BROWSER, SecurityAction.EXECUTE)
    assert result is False

def test_permission_allowed():
    result = security_manager.validate_permission(CapabilityType.FILESYSTEM, SecurityAction.READ)
    assert result is True
