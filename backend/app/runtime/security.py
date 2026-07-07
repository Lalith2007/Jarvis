import logging

from app.capabilities.models import CapabilityType
from app.runtime.models import RuntimePermission, SecurityAction

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Runtime permission gate.

    Default-deny: an action must be present in the capability's policy set.
    For FILESYSTEM actions carrying a concrete `resource` path, the path is
    additionally validated against the filesystem permission roots
    (resolve-then-validate) so a granted FILESYSTEM policy still cannot reach
    outside the sandbox.
    """

    def __init__(self):
        self._policies: dict[CapabilityType, set[SecurityAction]] = {}

    def set_policy(
        self, capability: CapabilityType, allowed_actions: list[SecurityAction]
    ) -> None:
        self._policies[capability] = set(allowed_actions)

    def validate_permission(
        self,
        capability: CapabilityType,
        action: SecurityAction,
        resource: str | None = None,
    ) -> bool:
        allowed_actions = self._policies.get(capability, set())
        is_allowed = action in allowed_actions

        # Resource-aware defense-in-depth for filesystem access: even with a
        # granted policy, the resolved path must be inside an allowed root.
        if is_allowed and capability == CapabilityType.FILESYSTEM and resource:
            from app.security.permissions import permissions

            if permissions.resolve_if_allowed(resource) is None:
                is_allowed = False
                logger.warning(
                    "Security Audit: filesystem resource outside sandbox: %s",
                    resource,
                )

        decision = "ALLOWED" if is_allowed else "DENIED"
        logger.info(
            "Security Audit: %s %s on %s (resource: %s)",
            decision,
            action.value,
            capability.value,
            resource,
        )
        return is_allowed


security_manager = SecurityManager()
security_manager.set_policy(
    CapabilityType.FILESYSTEM, [SecurityAction.READ, SecurityAction.WRITE]
)
# Code/terminal execution remain policy-granted (JARVIS is an AI OS that runs
# code) but MUST be run inside a sandboxed provider — see runtime providers.
security_manager.set_policy(CapabilityType.TERMINAL, [SecurityAction.EXECUTE])
security_manager.set_policy(CapabilityType.PYTHON_RUNTIME, [SecurityAction.EXECUTE])
security_manager.set_policy(
    CapabilityType.BROWSER,
    [SecurityAction.CONNECT, SecurityAction.READ, SecurityAction.WRITE],
)
