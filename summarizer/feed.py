import hashlib
from datetime import datetime, timedelta, timezone

import feedparser


def fetch_feed(url: str, lookback_days: int) -> list[dict]:
    """Fetch and parse an RSS feed, returning items published within the lookback window."""
    feed = feedparser.parse(url)
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    items = []

    for entry in feed.entries:
        # feedparser normalizes published_parsed to a time.struct_time in UTC
        if not getattr(entry, "published_parsed", None):
            continue
        published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        if published_at < cutoff:
            continue

        categories = ", ".join(t.term for t in getattr(entry, "tags", []))
        items.append({
            "content_id": hashlib.sha256(entry.link.encode()).hexdigest(),
            "source_type": "rss",
            "source_url": entry.link,
            "title": entry.title,
            "published_at": published_at,
            "categories": categories,
            "metadata": {"feed_url": url},
        })

    return items
