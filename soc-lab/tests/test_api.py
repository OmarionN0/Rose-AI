import pytest
from fastapi.testclient import TestClient
from app import main

@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB", tmp_path / "soc.db")
    monkeypatch.setenv("ROSE_SOC_TOKEN", "synthetic-test-token-only-32-characters-long")

client = TestClient(main.app)
HEADERS = {"Authorization": "Bearer synthetic-test-token-only-32-characters-long"}

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_reject_unauthorized():
    assert client.get("/alerts").status_code == 401
    assert client.post("/events", json={"source": "test", "event_type": "heartbeat", "host": "demo"}).status_code == 401

def test_alert_detection():
    result = client.post("/events", headers=HEADERS, json={"source": "synthetic-test", "event_type": "ssh_auth_failure", "host": "demo-host", "details": {"message": "synthetic"}})
    assert result.status_code == 201
    assert result.json()["alert_created"] is True
    assert any(a["rule"] == "SSH authentication failure" for a in client.get("/alerts", headers=HEADERS).json())

def test_benign_event():
    result = client.post("/events", headers=HEADERS, json={"source": "synthetic-test", "event_type": "heartbeat", "host": "demo-host"})
    assert result.status_code == 201
    assert result.json()["alert_created"] is False

def test_unconfigured_auth_fails_closed(monkeypatch):
    monkeypatch.delenv("ROSE_SOC_TOKEN")
    assert client.get("/alerts", headers=HEADERS).status_code == 503

def test_alert_triage():
    created = client.post("/events", headers=HEADERS, json={"source": "synthetic-test", "event_type": "new_listening_port", "host": "demo-host"})
    assert created.status_code == 201
    alert = client.get("/alerts", headers=HEADERS).json()[0]
    response = client.patch(f"/alerts/{alert['id']}", headers=HEADERS, json={"status": "investigating"})
    assert response.status_code == 200
    assert response.json()["status"] == "investigating"
    assert client.patch(f"/alerts/{alert['id']}", headers=HEADERS, json={"status": "invalid"}).status_code == 422
    assert client.patch("/alerts/999999", headers=HEADERS, json={"status": "resolved"}).status_code == 404
