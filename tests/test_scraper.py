from unittest.mock import MagicMock, patch

from summarizer.scraper import fetch_article_text

FULL_PAGE_HTML = """
<html>
  <head><title>Test Article</title></head>
  <body>
    <nav>Navigation links here</nav>
    <header>Site header</header>
    <article>
      <div class="entry-content">
        <p>This is the main article content.</p>
        <p>It has multiple paragraphs with useful information.</p>
      </div>
    </article>
    <aside>Related posts</aside>
    <footer>Site footer</footer>
    <script>alert('noise')</script>
  </body>
</html>
"""

NO_ENTRY_CONTENT_HTML = """
<html>
  <body>
    <nav>Nav</nav>
    <article>
      <p>Article without entry-content class.</p>
    </article>
    <footer>Footer</footer>
  </body>
</html>
"""


def _mock_response(html: str):
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


def test_extracts_entry_content():
    with patch("summarizer.scraper.httpx.get", return_value=_mock_response(FULL_PAGE_HTML)):
        text = fetch_article_text("https://example.com/article", max_chars=10000)
    assert "main article content" in text
    assert "multiple paragraphs" in text


def test_strips_nav_and_footer():
    with patch("summarizer.scraper.httpx.get", return_value=_mock_response(FULL_PAGE_HTML)):
        text = fetch_article_text("https://example.com/article", max_chars=10000)
    assert "Navigation links" not in text
    assert "Site footer" not in text
    assert "Site header" not in text


def test_strips_script_tags():
    with patch("summarizer.scraper.httpx.get", return_value=_mock_response(FULL_PAGE_HTML)):
        text = fetch_article_text("https://example.com/article", max_chars=10000)
    assert "alert" not in text


def test_falls_back_to_article_tag():
    with patch("summarizer.scraper.httpx.get", return_value=_mock_response(NO_ENTRY_CONTENT_HTML)):
        text = fetch_article_text("https://example.com/article", max_chars=10000)
    assert "Article without entry-content" in text


def test_max_chars_truncates():
    with patch("summarizer.scraper.httpx.get", return_value=_mock_response(FULL_PAGE_HTML)):
        text = fetch_article_text("https://example.com/article", max_chars=10)
    assert len(text) <= 10
