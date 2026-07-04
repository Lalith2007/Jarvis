from app.runtime.security import security_manager
from app.capabilities.models import CapabilityType
def test_security():
    assert security_manager.validate_permission(CapabilityType.FILESYSTEM, "read")
