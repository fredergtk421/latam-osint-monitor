from datetime import datetime, timezone
from dateutil import parser as dateparser
import feedparser
from bs4 import BeautifulSoup
from app.models import Event


def clean_html(value: str) -> str:
    return BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)


def parse_date(entry) -> str:
    for key in ["published", "updated", "created"]:
        if entry.get(key):
            try:
                return dateparser.parse(entry[key]).astimezone(timezone.utc).isoformat()
            except Exception:
                pass
    return datetime.now(timezone.utc).isoformat()


def fetch_rss(feed_config: dict, max_items: int = 30) -> list[Event]:
    parsed = feedparser.parse(feed_config["url"])
    events = []
    for entry in parsed.entries[:max_items]:
        title = clean_html(entry.get("title", "Untitled"))
        summary = clean_html(entry.get("summary", ""))
        link = entry.get("link", "")
        if not link:
            continue
        events.append(Event(
            source_name=feed_config.get("name", "RSS"),
            source_type="rss",
            title=title,
            url=link,
            published_at=parse_date(entry),
            country=feed_config.get("country", "Unknown"),
            language="es",
            summary=summary,
            raw_text=f"{title}. {summary}",
        ))
    return events
