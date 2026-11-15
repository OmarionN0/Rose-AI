# R.O.S.E. SOC Lab — Phase 1 + Secure Collector Foundation

Local security monitoring prototype in `soc-lab/`. **Existing R.O.S.E. application is unchanged.**

## Security model
- All API routes except `/health` require a bearer token of at least 32 characters, provided through `ROSE_SOC_TOKEN`. The server fails closed if the token is unset.
- Bind the API to **127.0.0.1 only**. Never expose it to the LAN or Internet. There is no TLS endpoint in the app itself.
- Raspberry Pi collector sends a heartbeat over an **SSH local port forward**, never over unencrypted network HTTP.
- All repository examples are synthetic. Never commit real telemetry, device inventories, credentials, packet captures, databases, or incident evidence.
- This is an educational prototype, **not a production SIEM**. API read access and write access share a token; rotate it if exposed.

## Laptop setup (WSL2)
```bash
cd soc-lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ROSE_SOC_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Save the token securely outside the repository for the Pi. Never paste the secret into GitHub or chat.

## Synthetic test event (another shell)
```bash
curl -X POST http://127.0.0.1:8000/events -H "Authorization: Bearer $ROSE_SOC_TOKEN" -H "Content-Type: application/json" --data @examples/ssh_failure.json
curl -H "Authorization: Bearer $ROSE_SOC_TOKEN" http://127.0.0.1:8000/alerts
pytest -q
```

## Raspberry Pi
See [docs/pi-setup.md](docs/pi-setup.md) for SSH forwarding and collector instructions. The collector currently sends heartbeat events only; no live packet capture or scans.

## API
`GET /health` (public), `POST /events`, `GET /events`, `GET /alerts`, `GET /summary` (authenticated).

## Next
Device-specific auth, alert investigation workflow, configurable retention, authorized vulnerability scans, and optional Wazuh integration.
