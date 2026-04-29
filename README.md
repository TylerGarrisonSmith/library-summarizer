# library-summarizer

Fetches articles from RSS feeds and web listing pages, summarizes them using Gemini (Vertex AI), and writes the results to BigQuery. Runs on a schedule via Cloud Run Jobs.

## How it works

1. Fetches articles from configured RSS feeds and listing URLs within a lookback window
2. Deduplicates against articles already in BigQuery
3. Scrapes full article text for each new item
4. Summarizes each article using Gemini via Vertex AI
5. Writes results to BigQuery

## Local setup

**Requirements:** Python 3.12+, [uv](https://docs.astral.sh/uv/), a GCP service account JSON with BigQuery and Vertex AI access.

```bash
# Install dependencies
uv sync

# Copy and fill in environment variables
cp .env.example .env
```

**.env variables:**

| Variable | Description |
|---|---|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to your GCP service account JSON |
| `GCP_PROJECT_ID` | GCP project ID |
| `BIGQUERY_DATASET` | Target BigQuery dataset |
| `BIGQUERY_TABLE` | Target BigQuery table |

Optional variables (have defaults):

| Variable | Default |
|---|---|
| `FEED_URL` | Microsoft Fabric blog RSS feed |
| `LISTING_URLS` | _(empty)_ |
| `VERTEX_AI_REGION` | `us-central1` |
| `GEMINI_MODEL` | `gemini-2.5-flash` |

**Run locally:**

```bash
uv run python -m summarizer
```

## Deployment (Cloud Run)

**Prerequisites:** `gcloud` CLI installed and authenticated, Docker running, APIs enabled for Cloud Run, Artifact Registry, and Cloud Scheduler.

**1. Deploy:**

```bash
bash deploy.sh
```

`deploy.sh` reads your `.env`, builds and pushes the Docker image to Artifact Registry, and creates or updates the Cloud Run job with the correct environment variables. `GOOGLE_APPLICATION_CREDENTIALS` is excluded — on Cloud Run, auth is handled by the job's service account.

**2. Schedule it:**

```bash
gcloud scheduler jobs create http summarizer-schedule \
  --schedule="0 8 * * *" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/resource-summarizer/jobs/library-summarizer:run" \
  --message-body="{}" \
  --oauth-service-account-email=YOUR_SERVICE_ACCOUNT@resource-summarizer.iam.gserviceaccount.com \
  --location=us-central1
```

**Run manually:**

```bash
gcloud run jobs execute library-summarizer --region=us-central1 --project=resource-summarizer
```

## Development

```bash
# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .
```
