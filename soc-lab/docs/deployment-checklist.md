# Deployment readiness checklist

## Before running locally
- [ ] Confirm the GitHub branch is `feature/rose-soc-lab-phase1`
- [ ] Review changes and confirm no secrets or personal data were committed
- [ ] Create a fresh random token of 32+ characters; store it outside the repo
- [ ] Install Python dependencies in a dedicated virtual environment
- [ ] Run `pytest -q` and resolve any failures
- [ ] Bind Uvicorn to `127.0.0.1`, **never** `0.0.0.0`
- [ ] Run `python3 tools/smoke_test.py` with a matching local token
- [ ] Review `docs/retention.md` and decide on local backup/retention

## Before enabling the Raspberry Pi collector
- [ ] Confirm authorized ownership of both devices
- [ ] Configure and verify SSH key-based access and host-key verification
- [ ] Confirm the SSH local forward points to laptop loopback only
- [ ] Never expose port 8000 to the public Internet or local shared network
- [ ] Keep API token out of shell history, Git, screenshots, and chat
- [ ] Confirm only heartbeat events are being sent

## Not ready for production
- No TLS termination beyond SSH forwarding
- Single shared bearer token for read and write
- No device identity or token revocation
- No dashboard authentication, role-based access, or audit trail
- No live network sensors or verified CVE lookups
- No automated retention schedule
- No tested disaster recovery
