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

**Prerequisites:** `gcloud` CLI installed and authenticated, APIs enabled for Cloud Run, Artifact Registry, Cloud Build, and Cloud Scheduler.

**1. Build and push the image:**

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT/summarizer-repo/summarizer
```

**2. Create the Cloud Run Job:**

```bash
gcloud run jobs create summarizer \
  --image=us-central1-docker.pkg.dev/YOUR_PROJECT/summarizer-repo/summarizer \
  --region=us-central1 \
  --task-timeout=600 \
  --service-account=YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com \
  --set-env-vars="GCP_PROJECT_ID=YOUR_PROJECT,BIGQUERY_DATASET=YOUR_DATASET,BIGQUERY_TABLE=YOUR_TABLE"
```

The job uses the attached service account for authentication — no credentials file needed on Cloud Run.

**3. Schedule it:**

```bash
gcloud scheduler jobs create http summarizer-schedule \
  --schedule="0 8 * * *" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/YOUR_PROJECT/jobs/summarizer:run" \
  --message-body="{}" \
  --oauth-service-account-email=YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com \
  --location=us-central1
```

**Run manually:**

```bash
gcloud run jobs execute summarizer --region=us-central1
```

## Development

```bash
# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .
```
