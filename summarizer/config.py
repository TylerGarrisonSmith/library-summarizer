import os

from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID: str = os.environ["GCP_PROJECT_ID"]
BIGQUERY_DATASET: str = os.environ["BIGQUERY_DATASET"]
BIGQUERY_TABLE: str = os.environ["BIGQUERY_TABLE"]
FEED_URL: str = os.getenv("FEED_URL", "https://blog.fabric.microsoft.com/en-us/blog/feed/")
LISTING_URLS: list[str] = [u.strip() for u in os.getenv("LISTING_URLS", "").split(",") if u.strip()]
VERTEX_AI_REGION: str = os.getenv("VERTEX_AI_REGION", "us-central1")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Operational constants — adjust here if needed, not via environment
LOOKBACK_DAYS: int = 2
MAX_ARTICLES_PER_RUN: int = 25
MAX_TEXT_CHARS: int = 15000
