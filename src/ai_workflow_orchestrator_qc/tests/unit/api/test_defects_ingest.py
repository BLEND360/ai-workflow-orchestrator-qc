from datetime import datetime, timezone

from fastapi.testclient import TestClient

from ai_workflow_orchestrator_qc.main import app


client = TestClient(app)


def _iso_now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def test_defect_ingest_accepts_and_returns_ack():
    payload = {
        "event_id": "evt-accept-001",
        "defect_type": "Sensor Calibration Drift",
        "severity": "HIGH",
        "category": "FUNCTIONAL",
        "description": "Sensor calibration drift detected.",
        "component": "temperature-sensor",
        "detected_at": _iso_now_z(),
        "detected_by": "unit-test",
        "metadata": {"source": "test"},
    }

    resp = client.post("/api/v1/defects/ingest", json=payload)
    assert resp.status_code == 201
    body = resp.json()

    assert body["event_id"] == payload["event_id"]
    assert body["status"] == "accepted"
    assert "correlation_id" in body
    assert "ingested_at" in body
    assert body["message"]


def test_defect_ingest_is_idempotent_by_event_id():
    payload = {
        "event_id": "evt-dupe-001",
        "defect_type": "Image Quality Degradation",
        "severity": "MEDIUM",
        "category": "DATA_QUALITY",
        "description": "Blur detected in frame sequence.",
        "component": "vision-sensor-01",
        "detected_at": _iso_now_z(),
        "detected_by": "unit-test",
    }

    r1 = client.post("/api/v1/defects/ingest", json=payload)
    assert r1.status_code == 201
    b1 = r1.json()
    assert b1["status"] == "accepted"

    r2 = client.post("/api/v1/defects/ingest", json=payload)
    assert r2.status_code == 201
    b2 = r2.json()
    assert b2["status"] == "duplicate"

    # Duplicate should return the original correlation_id (idempotent behavior).
    assert b2["correlation_id"] == b1["correlation_id"]

