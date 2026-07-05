from fastapi import APIRouter
from app.capabilities.registry import capability_registry

router = APIRouter(prefix="/capabilities", tags=["capabilities"])

@router.get("")
def get_capabilities():
    return capability_registry.get_all()
