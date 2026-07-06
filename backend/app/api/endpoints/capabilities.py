from fastapi import APIRouter

from app.capabilities.registry import capability_registry

router = APIRouter(prefix="/capabilities", tags=["capabilities"])


@router.get("")
def get_capabilities():
    manifests = capability_registry.list()
    return {
        "capabilities": [m.model_dump() for m in manifests],
        "count": len(manifests),
    }
