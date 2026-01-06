from fastapi.testclient import TestClient
from ai_workflow_orchestrator_qc.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
