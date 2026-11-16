"""Read-only WSL2 aggregate metrics collector. No IPs, usernames, or process details."""
import argparse
import json
import os
import time
import urllib.request
from pathlib import Path


def cpu_ticks():
    fields = Path('/proc/stat').read_text().splitlines()[0].split()[1:]
    values = [int(v) for v in fields]
    return sum(values), sum(values[3:5])


def memory_percent():
    rows = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        rows[key] = int(value.strip().split()[0])
    total = rows['MemTotal']
    return round(100 * (1 - rows['MemAvailable'] / total), 1)


def sample(interval):
    total1, idle1 = cpu_ticks()
    time.sleep(interval)
    total2, idle2 = cpu_ticks()
    diff = total2 - total1
    cpu = round(100 * (1 - (idle2 - idle1) / diff), 1) if diff else 0.0
    return {'cpu_percent': max(0, min(100, cpu)), 'memory_percent': memory_percent()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', default='http://127.0.0.1:8000/events')
    p.add_argument('--interval', type=int, default=30)
    p.add_argument('--once', action='store_true')
    args = p.parse_args()
    if args.interval < 5:
        p.error('--interval must be at least 5 seconds')
    if args.url != 'http://127.0.0.1:8000/events':
        p.error('collector only supports local loopback API')
    token = os.getenv('ROSE_SOC_TOKEN', '')
    if len(token) < 32:
        p.error('ROSE_SOC_TOKEN must be configured (at least 32 characters)')
    while True:
        payload = {'source': 'wsl2-readonly-metrics', 'host': 'WSL2', 'event_type': 'system_metrics', 'details': sample(1)}
        request = urllib.request.Request(args.url, data=json.dumps(payload).encode(), headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                print('WSL2 aggregate metrics submitted:', response.status)
        except Exception as exc:
            print('Local API unavailable:', type(exc).__name__)
        if args.once:
            break
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
