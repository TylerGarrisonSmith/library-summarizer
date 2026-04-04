import os

from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID: str = os.environ["GCP_PROJECT_ID"]
BIGQUERY_DATASET: str = os.environ["BIGQUERY_DATASET"]
BIGQUERY_TABLE: str = os.environ["BIGQUERY_TABLE"]
FEED_URL: str = os.getenv("FEED_URL", "https://blog.fabric.microsoft.com/en-us/blog/feed/")
LOOKBACK_DAYS: int = int(os.getenv("LOOKBACK_DAYS", "1"))
MAX_ARTICLES_PER_RUN: int = int(os.getenv("MAX_ARTICLES_PER_RUN", "25"))
MAX_TEXT_CHARS: int = int(os.getenv("MAX_TEXT_CHARS", "15000"))
VERTEX_AI_REGION: str = os.getenv("VERTEX_AI_REGION", "us-central1")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
