#!/usr/bin/env bash
# Submits an LXC template build to Google Cloud Build.
#
# Usage:
#   DISTRO=arch   ./submit-build.sh
#   DISTRO=debian ./submit-build.sh
#
# DISTRO selects which files this script uses:
#   - <DISTRO>.env          distro-specific settings (packages, base image, ...)
#   - cloudbuild-<DISTRO>.yaml   the Cloud Build pipeline itself
#
# Settings shared across every distro (GCP project, region, upload bucket)
# always come from build.env.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

: "${DISTRO:?Set DISTRO to select a pipeline, e.g. DISTRO=arch ./submit-build.sh}"

BUILD_ENV_FILE="$SCRIPT_DIR/build.env"
DISTRO_ENV_FILE="$SCRIPT_DIR/${DISTRO}.env"
CONFIG_FILE="$SCRIPT_DIR/cloudbuild-${DISTRO}.yaml"

for f in "$BUILD_ENV_FILE" "$DISTRO_ENV_FILE" "$CONFIG_FILE"; do
  if [[ ! -f "$f" ]]; then
    echo "Required file not found: $f" >&2
    exit 1
  fi
done

set -a
# shellcheck disable=SC1090
source "$BUILD_ENV_FILE"
# shellcheck disable=SC1090
source "$DISTRO_ENV_FILE"
set +a

: "${PROJECT_ID:?PROJECT_ID must be set in build.env}"
: "${REGION:?REGION must be set in build.env}"
: "${BUCKET:?BUCKET must be set in build.env}"
: "${PACKAGES:?PACKAGES must be set in ${DISTRO}.env}"

# Distro-specific substitutions vary per pipeline (BASE_IMAGE for arch,
# DEBIAN_RELEASE for debian, ...) - only pass along what's actually set in
# the sourced env file, and let that pipeline's own yaml default apply for
# anything not overridden.
SUBSTITUTIONS="_PACKAGES=${PACKAGES},_BUCKET=${BUCKET}"
[[ -n "${BASE_IMAGE:-}" ]] && SUBSTITUTIONS+=",_BASE_IMAGE=${BASE_IMAGE}"
[[ -n "${MIRROR:-}" ]] && SUBSTITUTIONS+=",_MIRROR=${MIRROR}"
[[ -n "${DEBIAN_RELEASE:-}" ]] && SUBSTITUTIONS+=",_DEBIAN_RELEASE=${DEBIAN_RELEASE}"

echo "==> DISTRO=${DISTRO}  project=${PROJECT_ID}  region=${REGION}  config=$(basename "$CONFIG_FILE")"

gcloud builds submit \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --config="$CONFIG_FILE" \
  --no-source \
  --substitutions="$SUBSTITUTIONS"
