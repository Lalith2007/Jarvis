import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config.settings import settings

app = FastAPI(
    title="JARVIS Backend",
    version="0.1.0",
)


@app.on_event("startup")
def _validate_config() -> None:
    settings.validate()
    # Optionally probe model health in the background so routing avoids models
    # that don't respond. Off by default (keeps startup fast / tests hermetic);
    # enable in production with JARVIS_PROBE_ON_STARTUP=1.
    if os.getenv("JARVIS_PROBE_ON_STARTUP") == "1":
        import threading

        from app.providers.registry import provider_registry

        threading.Thread(target=provider_registry.probe_health, daemon=True).start()

    # Bind the keyless research provider so grounded research works out of the
    # box (no API key required).
    try:
        from app.research.provider import research_manager
        from app.research.duckduckgo import DuckDuckGoProvider

        research_manager.set_provider(DuckDuckGoProvider())
    except Exception:
        pass

    # Recover missions left in-flight by a previous process (Sprint 13.9).
    try:
        from app.mission.store import mission_store

        recovered = mission_store.recover_incomplete()
        if recovered:
            import logging

            logging.getLogger(__name__).info(
                "Recovered %d in-flight mission(s) after restart", len(recovered)
            )
    except Exception:
        pass

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def optional_token_auth(request: Request, call_next):
    """
    Optional bearer-token auth for /api routes.

    Enforced only when JARVIS_API_TOKEN is set in the environment, so local
    development and the bundled desktop frontend keep working without config
    while production deployments can require a token by setting the env var.
    Accepts `Authorization: Bearer <token>` or `X-API-Token: <token>`.
    """
    token = os.getenv("JARVIS_API_TOKEN")
    if token and request.url.path.startswith("/api"):
        auth = request.headers.get("authorization", "")
        provided = (
            auth[7:]
            if auth.lower().startswith("bearer ")
            else request.headers.get("x-api-token", "")
        )
        if provided != token:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)


app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "JARVIS Backend Running",
    }
