from fastapi import APIRouter

from app.system.models import SystemSnapshot
from app.system.service import system_telemetry
from app.athena.registry import model_registry

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/snapshot", response_model=SystemSnapshot)
def system_snapshot() -> SystemSnapshot:
    return system_telemetry.snapshot()

@router.get("/models")
def get_models():
    return [p.model_dump() for p in model_registry.list_profiles()]

@router.get("/health")
def get_health():
    return {"status": "ok"}
