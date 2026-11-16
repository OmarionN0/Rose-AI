"""Local preflight checks; prints no token or host-identifying telemetry."""
import os
import shutil
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def port_state(port):
    with socket.socket() as sock:
        sock.settimeout(0.4)
        return sock.connect_ex(('127.0.0.1', port)) == 0


def main():
    print('R.O.S.E. SOC Lab local preflight')
    print('Python:', sys.version.split()[0])
    print('Node.js:', 'found' if shutil.which('node') else 'missing')
    print('npm:', 'found' if shutil.which('npm') else 'missing')
    print('Dashboard:', 'present' if (ROOT / 'dashboard' / 'package.json').is_file() else 'missing')
    print('API port 8000:', 'in use' if port_state(8000) else 'available')
    print('UI port 5173:', 'in use' if port_state(5173) else 'available')
    token = os.environ.get('ROSE_SOC_TOKEN', '')
    print('Token environment:', 'configured' if len(token) >= 32 else 'not configured')
    print('Local token file:', 'present' if (ROOT / '.soc-token').is_file() else 'missing')
    print('No secrets or host details are printed.')


if __name__ == '__main__':
    main()
