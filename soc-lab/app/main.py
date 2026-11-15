from datetime import datetime, timezone
from pathlib import Path
import json
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB = Path(__file__).resolve().parent.parent / "soc.db"
app = FastAPI(title="ROSE SOC Lab", version="0.1.0")

class Event(BaseModel):
    source: str = Field(min_length=1, max_length=100)
    event_type: str = Field(min_length=1, max_length=100)
    host: str = Field(min_length=1, max_length=100)
    details: dict = Field(default_factory=dict)

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, timestamp TEXT, source TEXT, event_type TEXT, host TEXT, details TEXT)")
    db.execute('CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY, event_id INTEGER, severity TEXT, rule TEXT, description TEXT, status TEXT DEFAULT "open")')
    db.commit()
    return db

def detect(event: Event):
    if event.event_type == "ssh_auth_failure":
        return ("medium", "SSH authentication failure", "Investigate failed SSH authentication")
    if event.event_type == "new_listening_port":
        return ("high", "Unexpected listening port", "Verify the newly observed service is authorized")
    return None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/events", status_code=201)
def ingest(event: Event):
    with connect() as db:
        cur = db.execute("INSERT INTO events(timestamp,source,event_type,host,details) VALUES(?,?,?,?,?)", (datetime.now(timezone.utc).isoformat(), event.source, event.event_type, event.host, json.dumps(event.details)))
        result = detect(event)
        if result:
            db.execute("INSERT INTO alerts(event_id,severity,rule,description) VALUES(?,?,?,?)", (cur.lastrowid, *result))
        return {"event_id": cur.lastrowid, "alert_created": bool(result)}

@app.get("/events")
def events(limit: int = 50):
    if not 1 <= limit <= 200:
        raise HTTPException(400, "limit must be 1-200")
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))]

@app.get("/alerts")
def alerts():
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 100")]

@app.get("/summary")
def summary():
    with connect() as db:
        return {"events": db.execute("SELECT COUNT(*) FROM events").fetchone()[0], "open_alerts": db.execute("SELECT COUNT(*) FROM alerts WHERE status='open'").fetchone()[0]}
