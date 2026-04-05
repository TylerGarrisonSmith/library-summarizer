import hashlib
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from summarizer.listing import fetch_listing

BASE_URL = "https://claude.com"


def _make_html(articles: list[dict]) -> str:
    cards = ""
    for a in articles:
        cards += f"""
        <div class="blog_cms_item">
            <a href="{a['href']}">
                <div class="card_blog_title">{a['title']}</div>
            </a>
            <div class="card_blog_date">{a['date']}</div>
        </div>
        """
    return f"<html><body>{cards}</body></html>"


def _mock_response(html: str, base_url: str = BASE_URL):
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    mock.url.scheme = "https"
    mock.url.host = "claude.com"
    return mock


def _make_date(days_ago: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.strftime("%B %d, %Y")


def test_recent_article_included():
    html = _make_html([{"href": "/blog/recent", "title": "Recent Post", "date": _make_date(1)}])
    with patch("summarizer.listing.httpx.get", return_value=_mock_response(html)):
        items = fetch_listing(BASE_URL, lookback_days=2)
    assert any(i["title"] == "Recent Post" for i in items)


def test_old_article_excluded():
    html = _make_html([{"href": "/blog/old", "title": "Old Post", "date": _make_date(10)}])
    with patch("summarizer.listing.httpx.get", return_value=_mock_response(html)):
        items = fetch_listing(BASE_URL, lookback_days=2)
    assert items == []


def test_content_id_is_sha256_of_full_url():
    html = _make_html([{"href": "/blog/recent", "title": "Recent Post", "date": _make_date(1)}])
    with patch("summarizer.listing.httpx.get", return_value=_mock_response(html)):
        items = fetch_listing(BASE_URL, lookback_days=2)
    expected = hashlib.sha256("https://claude.com/blog/recent".encode()).hexdigest()
    assert items[0]["content_id"] == expected


def test_source_type_is_website():
    html = _make_html([{"href": "/blog/recent", "title": "Recent Post", "date": _make_date(1)}])
    with patch("summarizer.listing.httpx.get", return_value=_mock_response(html)):
        items = fetch_listing(BASE_URL, lookback_days=2)
    assert items[0]["source_type"] == "website"


def test_metadata_contains_listing_url():
    html = _make_html([{"href": "/blog/recent", "title": "Recent Post", "date": _make_date(1)}])
    with patch("summarizer.listing.httpx.get", return_value=_mock_response(html)):
        items = fetch_listing(BASE_URL, lookback_days=2)
    assert items[0]["metadata"]["listing_url"] == BASE_URL


def test_missing_date_skips_item():
    html = "<html><body><div class='blog_cms_item'><a href='/blog/x'><div class='card_blog_title'>No Date</div></a></div></body></html>"
    with patch("summarizer.listing.httpx.get", return_value=_mock_response(html)):
        items = fetch_listing(BASE_URL, lookback_days=2)
    assert items == []


def test_abbreviated_month_date_parsed():
    """Handles 'Apr 2, 2026' format as well as 'April 2, 2026'."""
    html = _make_html([{"href": "/blog/recent", "title": "Recent Post", "date": "Apr 02, 2026"}])
    with patch("summarizer.listing.httpx.get", return_value=_mock_response(html)):
        items = fetch_listing(BASE_URL, lookback_days=9999)
    assert len(items) == 1
    assert items[0]["published_at"].month == 4
