import hashlib
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup


def fetch_listing(url: str, lookback_days: int) -> list[dict]:
    """Fetch a blog listing page and return articles published within the lookback window."""
    response = httpx.get(url, follow_redirects=True, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)

    base = f"{response.url.scheme}://{response.url.host}"
    items = []

    for card in soup.find_all(class_="blog_cms_item"):
        try:
            link_tag = card.find("a", href=True)
            title_tag = card.find(class_="card_blog_title")
            date_tag = (
                card.find(class_="card_blog_date")
                or card.find(class_="u-text-style-caption")
                or card.find("time")
            )

            if not link_tag or not title_tag or not date_tag:
                continue

            source_url = urljoin(base, link_tag["href"])
            title = title_tag.get_text(strip=True)
            date_text = date_tag.get_text(strip=True)
            # Support both "April 2, 2026" and "Apr 2, 2026"
            for fmt in ("%B %d, %Y", "%b %d, %Y"):
                try:
                    published_at = datetime.strptime(date_text, fmt).replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    continue
            else:
                continue

            if published_at < cutoff:
                continue

            items.append({
                "content_id": hashlib.sha256(source_url.encode()).hexdigest(),
                "source_type": "website",
                "source_url": source_url,
                "title": title,
                "published_at": published_at,
                "categories": "",
                "metadata": {"listing_url": url},
            })
        except (ValueError, AttributeError):
            continue

    return items
