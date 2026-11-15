# Secure Pi → laptop setup (manual deployment)

**Do not expose the API to the LAN or Internet.** The laptop API is loopback-only and uses a bearer token. SSH supplies encryption for transport. This requires the Pi to be able to SSH into the laptop; WSL2 SSH access can require Windows firewall/port forwarding configuration. Do not open a public firewall rule.

1. On the laptop, generate a unique token and store it in a local file outside the Git checkout:
   `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`
2. Export it only in your local shell: `export ROSE_SOC_TOKEN='PASTE_GENERATED_SECRET_HERE'`. Never paste the actual token into GitHub or chat.
3. Start the laptop API: `uvicorn app.main:app --host 127.0.0.1 --port 8000`.
4. Configure SSH key authentication from the Pi to the laptop. Verify the laptop SSH host key out-of-band before connecting.
5. On the Pi, establish a local forward: `ssh -N -L 8000:127.0.0.1:8000 YOUR_LAPTOP_SSH_USER@YOUR_LAPTOP_SSH_HOST`.
6. In another Pi shell, set the **same** token as a local environment variable, then run `python3 collector/pi_collector.py`.
7. Check the laptop API using an authenticated request. No real events should be committed to Git.

The collector currently sends only a synthetic-like heartbeat with a user-defined device label. It does not collect packet data, real SSH logs, process lists, or device inventories. This is intentional until storage retention, privacy controls, and alerting are reviewed.

## Next engineering milestones
- Restrict SSH access to the Pi and use key-based authentication
- Per-device credentials and token rotation
- Local encrypted backup and configurable retention
- Opt-in SSH failure detection with sensitive fields redacted
- Explicit allowlist for authorized network scans
- Case workflow and vulnerability reporting
