from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_alert_detection():
    result = client.post("/events", json={"source": "synthetic-test", "event_type": "ssh_auth_failure", "host": "demo-host", "details": {"message": "synthetic"}})
    assert result.status_code == 201
    assert result.json()["alert_created"] is True
    assert any(a["rule"] == "SSH authentication failure" for a in client.get("/alerts").json())

def test_benign_event():
    result = client.post("/events", json={"source": "synthetic-test", "event_type": "heartbeat", "host": "demo-host"})
    assert result.status_code == 201
    assert result.json()["alert_created"] is False
