from fastapi import FastAPI
from .api.health import router as health_router
from .context.api.v1 import router as context_router

app = FastAPI(
    title="AI Workflow Orchestrator - Quality Control",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(context_router)


@app.get("/")
def root():
    return {"status": "ok"}
