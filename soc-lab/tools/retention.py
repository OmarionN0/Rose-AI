"""Delete expired SOC telemetry from the local database.

Dry-run is the default. Back up locally before applying destructive changes.
"""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3

DEFAULT_DB = Path(__file__).resolve().parents[1] / "soc.db"

def prune(db_path: Path, days: int, apply: bool = False):
    if not 1 <= days <= 3650:
        raise ValueError("days must be between 1 and 3650")
    if not db_path.is_file():
        raise FileNotFoundError(db_path)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with sqlite3.connect(db_path) as db:
        db.execute("PRAGMA foreign_keys=ON")
        event_count = db.execute("SELECT COUNT(*) FROM events WHERE timestamp < ?", (cutoff,)).fetchone()[0]
        alert_count = db.execute(
            "SELECT COUNT(*) FROM alerts WHERE event_id IN (SELECT id FROM events WHERE timestamp < ?)", (cutoff,)
        ).fetchone()[0]
        if apply:
            db.execute("DELETE FROM alerts WHERE event_id IN (SELECT id FROM events WHERE timestamp < ?)", (cutoff,))
            db.execute("DELETE FROM events WHERE timestamp < ?", (cutoff,))
            db.commit()
    return {"events": event_count, "alerts": alert_count, "applied": apply}

def main():
    parser = argparse.ArgumentParser(description="SOC local telemetry retention (dry run by default)")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    result = prune(args.db, args.days, args.apply)
    print(f"{'Deleted' if result['applied'] else 'Would delete'} {result['events']} events and {result['alerts']} alerts")

if __name__ == "__main__":
    main()
