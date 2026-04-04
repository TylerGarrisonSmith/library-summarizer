from google.cloud import bigquery
from google.cloud.exceptions import NotFound


def get_existing_ids(client: bigquery.Client, dataset: str, table: str) -> set[str]:
    """Return the set of content_ids already in the table (empty set if table doesn't exist)."""
    table_ref = f"{client.project}.{dataset}.{table}"
    try:
        result = client.query(f"SELECT content_id FROM `{table_ref}`").result()
        return {row.content_id for row in result}
    except NotFound:
        return set()


def ensure_table(client: bigquery.Client, dataset: str, table: str) -> None:
    """Create the table if it doesn't exist."""
    table_ref = f"{client.project}.{dataset}.{table}"
    schema = [
        bigquery.SchemaField("content_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_url", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("title", "STRING"),
        bigquery.SchemaField("published_at", "TIMESTAMP"),
        bigquery.SchemaField("categories", "STRING"),
        bigquery.SchemaField("summary", "STRING"),
        bigquery.SchemaField("metadata", "JSON"),
        bigquery.SchemaField("fetched_at", "TIMESTAMP", mode="REQUIRED"),
    ]
    bq_table = bigquery.Table(table_ref, schema=schema)
    client.create_table(bq_table, exists_ok=True)


def write_rows(client: bigquery.Client, dataset: str, table: str, rows: list[dict]) -> None:
    """Insert rows into BigQuery. Raises on any insert errors."""
    if not rows:
        return
    table_ref = f"{client.project}.{dataset}.{table}"
    errors = client.insert_rows_json(table_ref, rows)
    if errors:
        raise RuntimeError(f"BigQuery insert errors: {errors}")
