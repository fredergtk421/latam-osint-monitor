import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml
from app.classifier import enrich_event_dict
from app.database import insert_events, init_db
from app.rss import fetch_rss
from app.gdelt import fetch_gdelt


def load_config():
    with open(ROOT / "config" / "sources.yml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    init_db()
    config = load_config()
    all_events = []

    print("Reading RSS feeds...")
    for feed in config.get("rss_feeds", []):
        try:
            events = fetch_rss(feed)
            print(f"  {feed.get('name')}: {len(events)} items")
            all_events.extend(events)
        except Exception as exc:
            print(f"  Failed {feed.get('name')}: {exc}")

    gdelt_config = config.get("gdelt", {})
    if gdelt_config.get("enabled", False):
        print("Reading GDELT...")
        for query in gdelt_config.get("queries", []):
            events = fetch_gdelt(
                query=query,
                max_records=gdelt_config.get("max_records_per_query", 50),
                timespan=gdelt_config.get("timespan", "24h"),
            )
            print(f"  GDELT query [{query}]: {len(events)} items")
            all_events.extend(events)

    enriched = [enrich_event_dict(e.to_dict()) for e in all_events]
    inserted = insert_events(enriched)
    print(f"Done. New events inserted: {inserted}. Total fetched this run: {len(enriched)}")


if __name__ == "__main__":
    main()
