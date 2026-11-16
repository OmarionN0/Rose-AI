# R.O.S.E. SOC Lab — laptop-first delivery roadmap

## Product target
Local desktop-style security operations application for one Windows laptop and its WSL2 Linux distributions. Privacy by default, read-only collection, explicit opt-in for sensitive telemetry, no inbound LAN listener, and no cloud upload. This is an educational tool, not a replacement for endpoint protection.

## Phase A — foundation (partially implemented)
- [x] FastAPI API, SQLite event and alert storage, bearer authentication, basic rules
- [x] React dashboard with alerts, events, host aggregate metrics and manual triage
- [x] Read-only Windows PowerShell and WSL2 Python aggregate CPU/RAM collectors
- [x] Regression tests for telemetry and alert separation
- [x] Ignore local tokens and build outputs in Git
- [ ] Validate Python tests, frontend build, and Windows script on target laptop
- [ ] Verify safe startup/shutdown and correct localhost connectivity on Windows + WSL2

## Phase B — secure local desktop experience
- [ ] Single local launcher for API, UI, and collectors, with graceful shutdown
- [ ] Desktop packaging (Tauri or equivalent) and signed installer strategy
- [ ] Local API session model, token rotation, per-collector credentials and restricted CORS
- [ ] Structured configuration, diagnostics, health checks, startup error display
- [ ] Durable schema migrations, SQLite backup and recovery, configurable retention
- [ ] CI checks for Python, React, PowerShell and dependency/security scans

## Phase C — host telemetry and detection
- [ ] Windows Event Log collector with explicit channel allowlist, bookmarks, least privilege and redaction
- [ ] WSL2 journal/auth collector with documented permission boundaries
- [ ] Read-only process/service inventory with no command lines or environment variables by default
- [ ] Network connection and listening-port change detection without active scanning
- [ ] Event normalization, bounded queues, retries, deduplication and collector health
- [ ] Versioned rules with severity, evidence, false-positive controls and tests

## Phase D — analyst workflow
- [ ] Alert detail and correlated timeline, filters, search and pagination
- [ ] Investigation notes, ownership, audit trail and incident lifecycle
- [ ] Evidence-safe exports and local incident reports
- [ ] Trends, baselines, alert quality metrics and dashboard accessibility

## Phase E — vulnerability intelligence and local AI
- [ ] Local software inventory with explicit consent and no secret capture
- [ ] CVE/advisory enrichment with caching and uncertainty labels
- [ ] Optional Ollama explanations using redacted local context, with no automated remediation
- [ ] Prompt-injection boundaries, model timeouts and explainability tests

## Phase F — release readiness
- [ ] End-to-end Windows + WSL2 test matrix, offline mode, upgrade and rollback tests
- [ ] CPU/RAM/disk performance budgets and failure-injection testing
- [ ] Threat model, privacy review, security hardening and dependency review
- [ ] Installer, user documentation, troubleshooting guide and release artifacts

## Definition of done
All applicable tests pass; Windows and WSL2 collectors are validated on a real laptop; tokens and telemetry remain local; install/uninstall and backup/recovery are verified; user-facing features are demonstrably working. Do not mark a phase complete from code commits alone.
