from fastapi import APIRouter

from app.system.service import system_telemetry
from app.mission.service import mission_service
from app.mcp.registry import mcp_registry
from app.runtime.manager import runtime_manager
from app.capabilities.registry import capability_registry
from app.athena.registry import model_registry

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("")
def get_dashboard_snapshot():
    # A unified snapshot for initial load
    return {
        "system": system_telemetry.snapshot().model_dump(),
        "missions": [m.model_dump() for m in mission_service.all()],
        "mcp_servers": [s.model_dump() for s in mcp_registry.list_servers()],
        "runtime_sessions": [s.model_dump() for s in runtime_manager._active_sessions.values()],
        "capabilities": [cap.model_dump() for cap in capability_registry.list()],
        "models": [p.model_dump() for p in model_registry.all().values()]
    }
