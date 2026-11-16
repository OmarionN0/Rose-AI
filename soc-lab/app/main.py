from datetime import datetime, timezone
from pathlib import Path
import hmac
import json
import os
import sqlite3

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

DB = Path(__file__).resolve().parent.parent / "soc.db"
app = FastAPI(title="ROSE SOC Lab", version="0.2.0")

class Event(BaseModel):
    source: str = Field(min_length=1, max_length=100)
    event_type: str = Field(min_length=1, max_length=100)
    host: str = Field(min_length=1, max_length=100)
    details: dict = Field(default_factory=dict)

def authorize(authorization: str | None = Header(default=None)):
    token = os.getenv("ROSE_SOC_TOKEN", "")
    if len(token) < 32:
        raise HTTPException(503, "Server authentication is not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Bearer token required", headers={"WWW-Authenticate": "Bearer"})
    if not hmac.compare_digest(authorization[7:], token):
        raise HTTPException(401, "Invalid token", headers={"WWW-Authenticate": "Bearer"})

def connect():
    db = sqlite3.connect(DB, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
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

@app.post("/events", status_code=201, dependencies=[Depends(authorize)])
def ingest(event: Event):
    with connect() as db:
        cur = db.execute("INSERT INTO events(timestamp,source,event_type,host,details) VALUES(?,?,?,?,?)", (datetime.now(timezone.utc).isoformat(), event.source, event.event_type, event.host, json.dumps(event.details)))
        result = detect(event)
        if result:
            db.execute("INSERT INTO alerts(event_id,severity,rule,description) VALUES(?,?,?,?)", (cur.lastrowid, *result))
        return {"event_id": cur.lastrowid, "alert_created": bool(result)}

@app.get("/events", dependencies=[Depends(authorize)])
def events(limit: int = 50):
    if not 1 <= limit <= 200:
        raise HTTPException(400, "limit must be 1-200")
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))]

@app.get("/alerts", dependencies=[Depends(authorize)])
def alerts():
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 100")]

@app.get("/summary", dependencies=[Depends(authorize)])
def summary():
    with connect() as db:
        return {"events": db.execute("SELECT COUNT(*) FROM events").fetchone()[0], "open_alerts": db.execute("SELECT COUNT(*) FROM alerts WHERE status='open'").fetchone()[0]}

class AlertStatus(BaseModel):
    status: str = Field(pattern="^(open|investigating|resolved|false_positive)$")

@app.patch("/alerts/{alert_id}", dependencies=[Depends(authorize)])
def update_alert(alert_id: int, update: AlertStatus):
    with connect() as db:
        cur = db.execute("UPDATE alerts SET status=? WHERE id=?", (update.status, alert_id))
        if cur.rowcount == 0:
            raise HTTPException(404, "Alert not found")
        return {"alert_id": alert_id, "status": update.status}
