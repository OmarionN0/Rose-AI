"""Start the local API, dashboard, and optional WSL2 metrics collector together.

Development launcher only: no Windows service installation, privilege escalation,
or network exposure. Ctrl+C terminates child processes.
"""
import argparse
import os
from pathlib import Path
import secrets
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
TOKEN_FILE = ROOT / '.soc-token'


def load_token():
    token = os.environ.get('ROSE_SOC_TOKEN', '').strip()
    if token:
        if len(token) < 32:
            raise ValueError('ROSE_SOC_TOKEN must be at least 32 characters')
        return token
    if not TOKEN_FILE.exists():
        fd = os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as stream:
            stream.write(secrets.token_urlsafe(48) + '\\n')
    token = TOKEN_FILE.read_text().strip()
    if len(token) < 32:
        raise ValueError('Local token file is invalid')
    return token


def commands(with_collector):
    npm = shutil.which('npm')
    if not npm:
        raise RuntimeError('npm is missing; install Node.js and npm first')
    if not (ROOT / 'dashboard' / 'node_modules').is_dir():
        raise RuntimeError('Dashboard dependencies missing; run npm install in soc-lab/dashboard')
    result = [([sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], ROOT),
              ([npm, 'run', 'dev', '--', '--host', '127.0.0.1'], ROOT / 'dashboard')]
    if with_collector:
        result.append(([sys.executable, 'collector/wsl_metrics.py', '--interval', '30'], ROOT))
    return result


def main():
    parser = argparse.ArgumentParser(description='Launch local R.O.S.E. SOC Lab')
    parser.add_argument('--no-wsl-collector', action='store_true')
    args = parser.parse_args()
    try:
        token = load_token()
        children = []
        try:
            for command, cwd in commands(not args.no_wsl_collector):
                child = subprocess.Popen(command, cwd=cwd, env={**os.environ, 'ROSE_SOC_TOKEN': token})
                children.append(child)
            print('Local dashboard: http://127.0.0.1:5173 (Ctrl+C to stop)', flush=True)
            while True:
                for child in children:
                    if child.poll() is not None:
                        raise RuntimeError('A component exited; stopping all local components')
                time.sleep(0.5)
        finally:
            for child in reversed(children):
                if child.poll() is None:
                    child.terminate()
            for child in reversed(children):
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
    except KeyboardInterrupt:
        print('R.O.S.E. SOC Lab stopped.')
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(1, 'Startup error: ' + str(exc) + '\\n')


if __name__ == '__main__':
    main()
