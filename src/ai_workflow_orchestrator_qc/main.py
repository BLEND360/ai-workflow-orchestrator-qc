from fastapi import FastAPI
from ai_workflow_orchestrator_qc.api.defects import router as defects_router
from ai_workflow_orchestrator_qc.api.health import router as health_router

app = FastAPI(
    title="AI Workflow Orchestrator - Quality Control",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(defects_router)


@app.get("/")
def root():
    return {"status": "ok"}
