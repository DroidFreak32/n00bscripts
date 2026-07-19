#!/usr/bin/env bash
# Submits the LXC template build to Google Cloud Build, pulling variables
# from an env file (default: build.env) instead of hardcoding them in yaml.
#
# Usage:
#   ./submit-build.sh                                    # build.env + cloudbuild.yaml
#   ./submit-build.sh other.env                          # other.env + cloudbuild.yaml
#   ./submit-build.sh build-debian.env cloudbuild-debian.yaml

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${1:-$SCRIPT_DIR/build.env}"
CONFIG_FILE="${2:-$SCRIPT_DIR/cloudbuild.yaml}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Env file not found: $ENV_FILE" >&2
  exit 1
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Config file not found: $CONFIG_FILE" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${PROJECT_ID:?PROJECT_ID must be set in $ENV_FILE}"
: "${BUCKET:?BUCKET must be set in $ENV_FILE}"
: "${SRC_TEMPLATE:?SRC_TEMPLATE must be set in $ENV_FILE}"
: "${PACKAGES:?PACKAGES must be set in $ENV_FILE}"

gcloud builds submit \
  --region="asia-south2" \
  --project="$PROJECT_ID" \
  --config="$CONFIG_FILE" \
  --no-source \
  --substitutions="_PACKAGES=${PACKAGES},_BUCKET=${BUCKET},_SRC_TEMPLATE=${SRC_TEMPLATE}"
