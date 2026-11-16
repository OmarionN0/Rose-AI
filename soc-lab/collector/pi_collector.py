"""Minimal opt-in Raspberry Pi host telemetry collector.

Use only with an SSH tunnel to the laptop API. No packet capture, network scanning,
or sensitive raw journal data is collected by this prototype.
"""
import json
import os
import socket
import time
from urllib.request import Request, urlopen

API = os.getenv("ROSE_SOC_URL", "http://127.0.0.1:8000/events")
TOKEN = os.getenv("ROSE_SOC_TOKEN", "")
HOST = os.getenv("ROSE_SOC_HOST_LABEL", "pi-lab")
INTERVAL = max(30, int(os.getenv("ROSE_SOC_INTERVAL", "60")))

def send(event_type, details):
    if not API.startswith("http://127.0.0.1:") and not API.startswith("http://localhost:"):
        raise RuntimeError("Collector only supports loopback API via an SSH tunnel")
    if len(TOKEN) < 32:
        raise RuntimeError("Set ROSE_SOC_TOKEN to a random secret of at least 32 characters")
    body = json.dumps({"source": "pi-host-collector", "event_type": event_type, "host": HOST, "details": details}).encode()
    request = Request(API, data=body, headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=10) as response:
        return response.status

def main():
    while True:
        try:
            send("heartbeat", {"collector": "pi", "status": "running"})
            print("Heartbeat sent", flush=True)
        except Exception as exc:
            print(f"Delivery failed: {type(exc).__name__}", flush=True)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
