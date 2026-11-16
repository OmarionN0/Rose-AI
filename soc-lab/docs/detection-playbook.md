# Detection and investigation playbook

This is a **lab-only** playbook. Investigate only assets you own or have explicit permission to monitor.

## SSH authentication failure
- Trigger: `ssh_auth_failure` event (currently synthetic; no live journal integration).
- Initial severity: medium.
- Confirm source host, time, and whether the activity matches an expected administrative action.
- Correlate with authorized local login history; avoid uploading raw logs to GitHub.
- Escalate when failures cluster or are followed by unexpected successful access.
- Record an analyst conclusion and remediation steps outside the public repository.

## Newly listening port
- Trigger: `new_listening_port` event (currently synthetic; no live port inventory).
- Initial severity: high.
- Compare the port to an approved service baseline.
- Verify process ownership and deployment changes on the affected host.
- If unexpected, restrict exposure through the host firewall and investigate.
- Do not perform broad scans of campus, apartment, or third-party networks.

## Incident report
Run locally from `soc-lab/`:
```bash
python3 tools/incident_report.py --out reports/triage.md
```
Generated reports are gitignored and may contain sensitive host labels. Keep them on your own machine. This report is a triage aid, not proof of compromise.
