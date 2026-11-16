# Local laptop startup — Phase A/B integration

**Status:** Development launcher implemented, but not yet verified on the target Windows/WSL2 laptop. This is a localhost web UI, not a packaged Windows executable.

In WSL2, after pulling the development branch:

```bash
cd ~/ROSE-SOC-Lab/soc-lab
source .venv/bin/activate
pip install -r requirements.txt
cd dashboard && npm install && cd ..
python tools/check_local_setup.py
python tools/launch_local.py
```

Open `http://127.0.0.1:5173` in Windows. The launcher creates `.soc-token` on first use if necessary and keeps the token out of command-line arguments. To unlock the UI, retrieve the token **locally** from the `.soc-token` file; never post it or commit it. Ctrl+C shuts down the launcher and its direct child processes. To run without WSL2 metrics, add `--no-wsl-collector`.

**Windows monitoring remains separate:** in Windows PowerShell, set `ROSE_SOC_TOKEN` locally to the same secret and run `collector/windows_metrics.ps1` as described in `dashboard/README.md`. Windows localhost forwarding to WSL2 must be tested; never bind the API to 0.0.0.0 as a workaround.

## Validation checklist on the actual laptop

1. Run `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q` from `soc-lab`.
2. Run `npm run build` in `soc-lab/dashboard`.
3. Start the launcher; check `http://127.0.0.1:8000/health` and open the dashboard.
4. Verify both Windows and WSL2 metric samples arrive, without credentials or host-identifying data in event details.
5. Stop with Ctrl+C; confirm ports 8000 and 5173 are released and child processes terminate.
6. Restart and confirm alerts persist locally; ensure `.soc-token`, `soc.db`, and `dashboard/node_modules` remain untracked.

Phase A is **not complete** until this checklist passes. Phase B still requires secure desktop packaging, migrations, retention and backup, token lifecycle, and a Windows validation matrix.
