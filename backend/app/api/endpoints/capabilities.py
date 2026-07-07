from fastapi import APIRouter

from app.capabilities.registry import capability_registry

router = APIRouter(prefix="/capabilities", tags=["capabilities"])


@router.get("")
def get_capabilities():
    manifests = capability_registry.list()
    metrics = capability_registry.metrics()
    health = capability_registry.health()
    return {
        "capabilities": [
            {
                **m.model_dump(),
                "health": health.get(m.id),
                "metrics": (
                    metrics[m.id].model_dump() if m.id in metrics else None
                ),
            }
            for m in manifests
        ],
        "count": len(manifests),
    }


@router.get("/metrics")
def get_capability_metrics():
    """Per-capability execution metrics (Sprint 13.1 observability)."""
    metrics = capability_registry.metrics()
    return {
        "metrics": {cid: m.model_dump() for cid, m in metrics.items()},
        "count": len(metrics),
    }


@router.get("/health")
def get_capability_health():
    return capability_registry.health()
