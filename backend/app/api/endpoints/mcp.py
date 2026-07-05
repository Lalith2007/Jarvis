from fastapi import APIRouter
from app.mcp.registry import mcp_registry

router = APIRouter(prefix="/mcp", tags=["mcp"])

@router.get("/servers")
def get_servers():
    return [s.model_dump() for s in mcp_registry.list_servers()]
