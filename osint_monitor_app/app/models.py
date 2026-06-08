from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Event:
    source_name: str
    source_type: str
    title: str
    url: str
    published_at: str
    country: str = "Unknown"
    language: str = "unknown"
    summary: str = ""
    raw_text: str = ""
    event_type: str = "other"
    severity: str = "low"
    confidence: str = "low"
    score: int = 0
    dedupe_key: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        if not data.get("created_at"):
            data["created_at"] = datetime.now(timezone.utc).isoformat()
        return data
