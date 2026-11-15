# R.O.S.E. SOC Lab — Phase 1

A lightweight, **local-only** security telemetry and detection prototype.

## Privacy and safety

This repository is public. Never commit real telemetry, hostnames, IP inventories, credentials, tokens, packet captures, incident evidence, or generated databases. All examples use synthetic data. The API has **no authentication** and is intended for loopback-only development; do not expose it to the LAN, public Internet, or a cloud service. Collect data only from systems you own or are authorized to monitor.

## Start in WSL2

```bash
cd soc-lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs

## Synthetic test event

```bash
curl -X POST http://127.0.0.1:8000/events -H 'Content-Type: application/json' --data @examples/ssh_failure.json
curl http://127.0.0.1:8000/alerts
```

## Scope

Current: event ingestion, SQLite persistence, two basic detection rules, alert listing, summary. Not yet implemented: Pi collectors, authentication, secure transport, vulnerability scanning, real SIEM, dashboard, notifications, or incident case management. Do not connect live devices until authentication and transport controls are added.
