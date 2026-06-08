import sqlite3
from pathlib import Path
from typing import Iterable

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "osint_events.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT,
    source_type TEXT,
    title TEXT,
    url TEXT UNIQUE,
    published_at TEXT,
    country TEXT,
    language TEXT,
    summary TEXT,
    raw_text TEXT,
    event_type TEXT,
    severity TEXT,
    confidence TEXT,
    score INTEGER,
    dedupe_key TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at);
CREATE INDEX IF NOT EXISTS idx_events_country ON events(country);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity);
CREATE INDEX IF NOT EXISTS idx_events_dedupe ON events(dedupe_key);
"""


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.executescript(SCHEMA)
        conn.commit()


def insert_events(events: Iterable[dict]) -> int:
    init_db()
    inserted = 0
    fields = [
        "source_name", "source_type", "title", "url", "published_at", "country", "language",
        "summary", "raw_text", "event_type", "severity", "confidence", "score", "dedupe_key", "created_at"
    ]
    placeholders = ",".join(["?"] * len(fields))
    sql = f"INSERT OR IGNORE INTO events ({','.join(fields)}) VALUES ({placeholders})"
    with connect() as conn:
        for event in events:
            values = [event.get(field, "") for field in fields]
            cur = conn.execute(sql, values)
            inserted += cur.rowcount
        conn.commit()
    return inserted


def fetch_events(limit: int = 500):
    init_db()
    with connect() as conn:
        return conn.execute("SELECT * FROM events ORDER BY published_at DESC, created_at DESC LIMIT ?", (limit,)).fetchall()
