from fastapi import APIRouter
from app.runtime.registry import runtime_registry
from app.runtime.manager import runtime_manager

router = APIRouter(prefix="/runtime", tags=["runtime"])

@router.get("/providers")
def get_providers():
    providers = []
    for cap, plist in runtime_registry._providers.items():
        for p in plist:
            providers.append({
                "capability": cap,
                "metadata": p.metadata.model_dump(),
                "priority": p.priority
            })
    return providers

@router.get("/sessions")
def get_sessions():
    return [s.model_dump() for s in runtime_manager._active_sessions.values()]

@router.get("/statistics")
def get_statistics():
    return runtime_manager.get_statistics()
