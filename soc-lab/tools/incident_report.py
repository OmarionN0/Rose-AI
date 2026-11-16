"""Generate a local incident triage report from SOC SQLite data.

Reports may contain sensitive host metadata. Never commit generated output.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

DEFAULT_DB = Path(__file__).resolve().parents[1] / "soc.db"

def render(db_path: Path):
    with sqlite3.connect(db_path) as db:
        alerts = db.execute(
            "SELECT a.id, a.severity, a.rule, a.description, a.status, e.timestamp, e.host "
            "FROM alerts a JOIN events e ON e.id = a.event_id ORDER BY a.id DESC LIMIT 100"
        ).fetchall()
    lines = ["# R.O.S.E. SOC Lab — Incident Triage Report", "",
             f"Generated (UTC): {datetime.now(timezone.utc).isoformat()}", "",
             f"Alerts reviewed: {len(alerts)}", ""]
    for alert_id, severity, rule, description, status, timestamp, host in alerts:
        # Neutralize Markdown line breaks in untrusted database fields.
        safe = lambda v: str(v).replace(chr(13), " ").replace(chr(10), " ").replace("|", "/")
        lines.extend([f"## Alert {alert_id}: {safe(rule)}",
                      f"- Severity: {safe(severity)}",
                      f"- Status: {safe(status)}",
                      f"- Observed: {safe(timestamp)}",
                      f"- Host: {safe(host)}",
                      f"- Triage: {safe(description)}",
                      "- Analyst decision: Pending review", ""])
    return chr(10).join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not args.db.is_file():
        parser.error("database does not exist")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(args.db), encoding="utf-8")
    args.out.chmod(0o600)
    print(f"Report saved locally to {args.out}")

if __name__ == "__main__":
    main()
