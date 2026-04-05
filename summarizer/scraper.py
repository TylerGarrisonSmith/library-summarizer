import httpx
from bs4 import BeautifulSoup


def fetch_article_text(url: str, max_chars: int) -> str:
    """Fetch an article page and return its main body as plain text."""
    response = httpx.get(url, follow_redirects=True, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    # Strip noise elements before extracting text
    for tag in soup(["nav", "header", "footer", "script", "style", "aside"]):
        tag.decompose()

    # Try progressively broader selectors for the main content block
    main = (
        soup.find("div", class_="u-rich-text-blog")
        or soup.find("div", class_="entry-content")
        or soup.find("article")
        or soup.find("main")
        or soup.body
    )

    text = main.get_text(separator="\n", strip=True) if main else ""
    return text[:max_chars]
