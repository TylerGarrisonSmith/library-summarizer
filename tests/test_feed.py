from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import feedparser

from summarizer.feed import fetch_feed

MOCK_RSS = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com</link>
    <description>Test</description>
    <item>
      <title>Recent Article</title>
      <link>https://example.com/recent</link>
      <pubDate>{recent}</pubDate>
      <category>Azure</category>
      <category>Fabric</category>
      <guid>https://example.com/recent</guid>
    </item>
    <item>
      <title>Old Article</title>
      <link>https://example.com/old</link>
      <pubDate>{old}</pubDate>
      <guid>https://example.com/old</guid>
    </item>
  </channel>
</rss>
"""


def _make_feed(lookback_days: int = 1):
    now = datetime.now(timezone.utc)
    recent = (now - timedelta(hours=12)).strftime("%a, %d %b %Y %H:%M:%S +0000")
    old = (now - timedelta(days=10)).strftime("%a, %d %b %Y %H:%M:%S +0000")
    raw = MOCK_RSS.format(recent=recent, old=old)

    parsed = feedparser.parse(raw)
    with patch("summarizer.feed.feedparser.parse", return_value=parsed):
        return fetch_feed("https://example.com/feed", lookback_days)


def test_recent_article_included():
    items = _make_feed(lookback_days=1)
    assert any(i["title"] == "Recent Article" for i in items)


def test_old_article_excluded():
    items = _make_feed(lookback_days=1)
    assert not any(i["title"] == "Old Article" for i in items)


def test_categories_joined():
    items = _make_feed(lookback_days=1)
    recent = next(i for i in items if i["title"] == "Recent Article")
    assert recent["categories"] == "Azure, Fabric"


def test_content_id_is_sha256_of_url():
    import hashlib
    items = _make_feed(lookback_days=1)
    recent = next(i for i in items if i["title"] == "Recent Article")
    expected = hashlib.sha256("https://example.com/recent".encode()).hexdigest()
    assert recent["content_id"] == expected


def test_source_type_is_rss():
    items = _make_feed(lookback_days=1)
    assert all(i["source_type"] == "rss" for i in items)


def test_lookback_zero_returns_nothing():
    items = _make_feed(lookback_days=0)
    assert items == []
