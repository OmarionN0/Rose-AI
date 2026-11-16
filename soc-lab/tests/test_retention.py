from datetime import datetime, timedelta, timezone
import sqlite3

from tools.retention import prune

def test_retention_dry_run_and_apply(tmp_path):
    db_path = tmp_path / "soc.db"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE events(id INTEGER PRIMARY KEY, timestamp TEXT)")
        db.execute("CREATE TABLE alerts(id INTEGER PRIMARY KEY, event_id INTEGER)")
        old = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
        new = datetime.now(timezone.utc).isoformat()
        db.executemany("INSERT INTO events VALUES (?,?)", [(1, old), (2, new)])
        db.executemany("INSERT INTO alerts VALUES (?,?)", [(1, 1), (2, 2)])
    assert prune(db_path, 30) == {"events": 1, "alerts": 1, "applied": False}
    with sqlite3.connect(db_path) as db:
        assert db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 2
    assert prune(db_path, 30, apply=True)["events"] == 1
    with sqlite3.connect(db_path) as db:
        assert db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM alerts").fetchone()[0] == 1
