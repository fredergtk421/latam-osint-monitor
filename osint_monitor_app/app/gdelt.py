from datetime import datetime, timezone
from urllib.parse import urlencode
import requests
from app.models import Event

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"


def fetch_gdelt(query: str, max_records: int = 50, timespan: str = "24h") -> list[Event]:
    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "maxrecords": max_records,
        "timespan": timespan,
        "sort": "HybridRel",
        "format": "json",
    }
    url = f"{GDELT_DOC_API}?{urlencode(params)}"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return []

    events = []
    for article in data.get("articles", []):
        title = article.get("title") or "Untitled"
        article_url = article.get("url") or ""
        if not article_url:
            continue
        published = article.get("seendate") or datetime.now(timezone.utc).isoformat()
        events.append(Event(
            source_name=article.get("sourceCommonName", "GDELT"),
            source_type="gdelt",
            title=title,
            url=article_url,
            published_at=published,
            country="Unknown",
            language=article.get("language", "unknown"),
            summary=article.get("domain", ""),
            raw_text=f"{title}. {article.get('domain', '')}",
        ))
    return events
