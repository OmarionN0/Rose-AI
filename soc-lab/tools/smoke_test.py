"""Local-only API smoke test with synthetic telemetry."""
import json
import os
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8000"
TOKEN = os.environ.get("ROSE_SOC_TOKEN", "")

def call(path, method="GET", payload=None):
    if len(TOKEN) < 32:
        raise SystemExit("Set ROSE_SOC_TOKEN (at least 32 characters) before running")
    body = json.dumps(payload).encode() if payload is not None else None
    headers = {"Authorization": "Bearer " + TOKEN}
    if body is not None:
        headers["Content-Type"] = "application/json"
    with urlopen(Request(BASE + path, data=body, headers=headers, method=method), timeout=5) as response:
        return json.load(response)

def main():
    event = {"source": "smoke-test", "event_type": "ssh_auth_failure",
             "host": "synthetic-host", "details": {"note": "test-only"}}
    created = call("/events", "POST", event)
    assert created["alert_created"], created
    alerts = call("/alerts")
    assert any(a["event_id"] == created["event_id"] for a in alerts)
    print("PASS: authenticated synthetic event created an alert")

if __name__ == "__main__":
    main()
