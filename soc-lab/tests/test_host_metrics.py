"""Regression tests for privacy-preserving laptop telemetry ingestion."""
from fastapi.testclient import TestClient
from app import main

TOKEN = "synthetic-test-token-only-32-characters-long"
HEADERS = {"Authorization": "Bearer " + TOKEN}


def test_windows_and_wsl_metrics_are_benign(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB", tmp_path / "metrics.db")
    monkeypatch.setenv("ROSE_SOC_TOKEN", TOKEN)
    client = TestClient(main.app)
    for host, source in [("Windows", "windows-readonly-metrics"), ("WSL2", "wsl2-readonly-metrics")]:
        payload = {"source": source, "host": host, "event_type": "system_metrics", "details": {"cpu_percent": 23.5, "memory_percent": 41.2}}
        response = client.post("/events", headers=HEADERS, json=payload)
        assert response.status_code == 201
        assert response.json()["alert_created"] is False
    assert client.get("/summary", headers=HEADERS).json() == {"events": 2, "open_alerts": 0}
    rows = client.get("/events", headers=HEADERS).json()
    assert {row["host"] for row in rows} == {"Windows", "WSL2"}
    assert all(row["event_type"] == "system_metrics" for row in rows)
    assert client.get("/alerts", headers=HEADERS).json() == []


def test_metrics_endpoint_requires_authentication(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB", tmp_path / "metrics.db")
    monkeypatch.setenv("ROSE_SOC_TOKEN", TOKEN)
    client = TestClient(main.app)
    payload = {"source": "test", "host": "WSL2", "event_type": "system_metrics", "details": {}}
    assert client.post("/events", json=payload).status_code == 401
    assert client.post("/events", headers={"Authorization": "Bearer wrong"}, json=payload).status_code == 401
    assert client.get("/events").status_code == 401


def test_alert_rule_still_operates_with_metrics(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB", tmp_path / "metrics.db")
    monkeypatch.setenv("ROSE_SOC_TOKEN", TOKEN)
    client = TestClient(main.app)
    for event_type in ("system_metrics", "ssh_auth_failure"):
        response = client.post("/events", headers=HEADERS, json={"source": "synthetic-test", "host": "WSL2", "event_type": event_type})
        assert response.status_code == 201
    alerts = client.get("/alerts", headers=HEADERS).json()
    assert len(alerts) == 1
    assert alerts[0]["rule"] == "SSH authentication failure"
