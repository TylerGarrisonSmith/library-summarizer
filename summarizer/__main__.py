import json
from datetime import datetime, timezone

from google.cloud import bigquery

from . import config
from .ai import init_model, summarize
from .bq import ensure_table, get_existing_ids, write_rows
from .feed import fetch_feed
from .scraper import fetch_article_text


def main() -> None:
    bq_client = bigquery.Client(project=config.GCP_PROJECT_ID)
    ensure_table(bq_client, config.BIGQUERY_DATASET, config.BIGQUERY_TABLE)

    ai_client = init_model(config.GCP_PROJECT_ID, config.VERTEX_AI_REGION, config.GEMINI_MODEL)

    items = fetch_feed(config.FEED_URL, config.LOOKBACK_DAYS)
    print(f"Fetched {len(items)} item(s) within {config.LOOKBACK_DAYS}-day lookback window")

    existing_ids = get_existing_ids(bq_client, config.BIGQUERY_DATASET, config.BIGQUERY_TABLE)
    items = [i for i in items if i["content_id"] not in existing_ids]
    items = items[: config.MAX_ARTICLES_PER_RUN]
    print(f"{len(items)} new item(s) to process after dedup and cap")

    fetched_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for item in items:
        print(f"  Scraping:    {item['title']}")
        text = fetch_article_text(item["source_url"], config.MAX_TEXT_CHARS)

        print(f"  Summarizing: {item['title']}")
        summary = summarize(ai_client, config.GEMINI_MODEL, text, item["title"])

        rows.append({
            "content_id": item["content_id"],
            "source_type": item["source_type"],
            "source_url": item["source_url"],
            "title": item["title"],
            "published_at": item["published_at"].isoformat(),
            "categories": item["categories"],
            "summary": summary,
            "metadata": json.dumps(item["metadata"]),
            "fetched_at": fetched_at,
        })

    write_rows(bq_client, config.BIGQUERY_DATASET, config.BIGQUERY_TABLE, rows)
    print(f"Done. Wrote {len(rows)} row(s) to BigQuery.")


if __name__ == "__main__":
    main()
