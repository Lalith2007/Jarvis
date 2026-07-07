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
    import logging
    logger = logging.getLogger("jarvis.startup")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(ch)

    logger.info("STAGE 1: settings.validate()")
    settings.validate()
    
    logger.info("STAGE 2: model health probes (background)")
    if os.getenv("JARVIS_PROBE_ON_STARTUP") == "1":
        import threading
        from app.providers.registry import provider_registry
        threading.Thread(target=provider_registry.probe_health, daemon=True).start()

    logger.info("STAGE 3: voice initialization")
    try:
        from app.voice.driver import voice_manager
        from app.voice.system_driver import SystemVoiceDriver
        drv = SystemVoiceDriver()
        if drv.available():
            voice_manager.set_driver(drv)
    except Exception as e:
        logger.warning(f"Voice init failed: {e}")

    logger.info("STAGE 4: research initialization")
    try:
        from app.research.provider import research_manager
        from app.research.duckduckgo import DuckDuckGoProvider
        research_manager.set_provider(DuckDuckGoProvider())
    except Exception as e:
        logger.warning(f"Research init failed: {e}")

    logger.info("STAGE 5: MCP autoconnect")
    try:
        from app.mcp.config import autoconnect
        autoconnect()
    except Exception as e:
        logger.warning(f"MCP autoconnect failed: {e}")

    logger.info("STAGE 6: mission recovery")
    try:
        from app.mission.store import mission_store
        recovered = mission_store.recover_incomplete()
        if recovered:
            logger.info("Recovered %d in-flight mission(s) after restart", len(recovered))
    except Exception as e:
        logger.warning(f"Mission recovery failed: {e}")
        
    logger.info("STAGE 7: application startup complete")

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
