from fastapi import APIRouter

from app.system.models import SystemSnapshot
from app.system.service import system_telemetry

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/snapshot", response_model=SystemSnapshot)
def system_snapshot() -> SystemSnapshot:
    return system_telemetry.snapshot()

