#!/bin/bash
set -euo pipefail

# --- config ---
IMAGE_NAME="library-summarizer"
ARTIFACT_REPO="summarizer-repo"
JOB_NAME="library-summarizer"
REGION="us-central1"

# --- load .env ---
if [ ! -f .env ]; then
  echo "ERROR: .env file not found" >&2
  exit 1
fi

# Read .env, skip comments and blank lines, exclude local-only vars
ENV_VARS=$(grep -v '^#' .env | grep -v '^$' | grep -v '^GOOGLE_APPLICATION_CREDENTIALS' | sed 's/^/--update-env-vars /' | tr '\n' ' ')

# --- derive values from .env ---
GCP_PROJECT_ID=$(grep '^GCP_PROJECT_ID=' .env | cut -d= -f2)
if [ -z "$GCP_PROJECT_ID" ]; then
  echo "ERROR: GCP_PROJECT_ID not set in .env" >&2
  exit 1
fi

IMAGE="$REGION-docker.pkg.dev/$GCP_PROJECT_ID/$ARTIFACT_REPO/$IMAGE_NAME:latest"

# --- build & push via Cloud Build ---
echo "Building and pushing image via Cloud Build..."
gcloud builds submit \
  --tag "$IMAGE" \
  --project "$GCP_PROJECT_ID"

# --- create or update job ---
if gcloud run jobs describe "$JOB_NAME" --region "$REGION" --project "$GCP_PROJECT_ID" &>/dev/null; then
  echo "Updating Cloud Run job..."
  gcloud run jobs update "$JOB_NAME" \
    --image "$IMAGE" \
    --region "$REGION" \
    --project "$GCP_PROJECT_ID" \
    --max-retries 1 \
    $(echo "$ENV_VARS")
else
  echo "Creating Cloud Run job..."
  gcloud run jobs create "$JOB_NAME" \
    --image "$IMAGE" \
    --region "$REGION" \
    --project "$GCP_PROJECT_ID" \
    --max-retries 1 \
    $(echo "$ENV_VARS")
fi

echo "Done. Run with:"
echo "  gcloud run jobs execute $JOB_NAME --region $REGION --project $GCP_PROJECT_ID"
