# library-summarizer

RSS feed summarizer that fetches articles, summarizes them with Gemini (Vertex AI), and writes results to BigQuery. Runs on a schedule via Cloud Run.

## Stack

| Layer | Choice |
|---|---|
| Language | Python 3.12+ |
| Package manager | uv |
| AI | Gemini via Vertex AI SDK (`google-cloud-aiplatform`) |
| Output | Google BigQuery (`google-cloud-bigquery`) |
| Auth | GCP service account JSON (`resource-summarizer-8b243a5a648a.json`, gitignored) |
| Scheduler | Cloud Run Jobs / Cloud Scheduler |
| Tests | pytest |

## Common Commands

```bash
# Install deps
uv sync

# Add a dependency
uv add <package>

# Run the summarizer
uv run python -m summarizer

# Run tests
uv run pytest

# Run a single test file
uv run pytest tests/test_foo.py -v
```

## Environment Variables

Stored in `.env` (gitignored). Copy from `.env.example`.

| Variable | Purpose |
|---|---|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to the service account JSON |
| `GCP_PROJECT_ID` | GCP project (`resource-summarizer`) |
| `BIGQUERY_DATASET` | Target BigQuery dataset |
| `BIGQUERY_TABLE` | Target BigQuery table |

## GCP / Auth

- Auth uses the service account at `resource-summarizer-8b243a5a648a.json` (gitignored, never commit).
- Set `GOOGLE_APPLICATION_CREDENTIALS` to its path when running locally.
- On Cloud Run, use Workload Identity or mount the secret via Secret Manager.
- Vertex AI region: default to `us-central1` unless specified.

## BigQuery Conventions

- Write rows via the BigQuery client library (not streaming insert unless latency matters).
- Include a `fetched_at` TIMESTAMP column on every table for auditability.
- Schema changes go through migration scripts in `migrations/`.

## Code Style

- Follow PEP 8; use `ruff` for linting and formatting.
- Keep functions small and focused. No classes unless state is genuinely needed.
- Do not commit secrets, credentials, or `.env` files.
- All GCP clients should be initialized once and passed as arguments (not globals).
