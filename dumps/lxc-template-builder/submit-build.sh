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
: "${PACKAGES:?PACKAGES must be set in $ENV_FILE}"

# BASE_IMAGE (Arch) and DEBIAN_RELEASE (Debian) are pipeline-specific -
# only pass along whichever one is actually set in the env file, and let
# the yaml's own default apply for the other.
SUBSTITUTIONS="_PACKAGES=${PACKAGES},_BUCKET=${BUCKET}"
[[ -n "${BASE_IMAGE:-}" ]] && SUBSTITUTIONS+=",_BASE_IMAGE=${BASE_IMAGE}"
[[ -n "${DEBIAN_RELEASE:-}" ]] && SUBSTITUTIONS+=",_DEBIAN_RELEASE=${DEBIAN_RELEASE}"

gcloud builds submit \
  --region="asia-south2" \
  --project="$PROJECT_ID" \
  --config="$CONFIG_FILE" \
  --no-source \
  --substitutions="$SUBSTITUTIONS"
