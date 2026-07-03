from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="JARVIS Backend",
    version="0.1.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "JARVIS Backend Running",
    }
