#!/usr/bin/env bash
# Custom build-time script for the Debian template.
#
# Runs INSIDE the build container, after packages (base + PACKAGES) are
# installed and BEFORE final cleanup. Anything this script creates - files,
# configs, users, etc. - becomes a permanent part of the baked template
# image. This is NOT a container startup script and does not run again on
# every clone/boot - it only ever runs once, at image build time.
#
# The build fails if this script exits non-zero (set -e below), so a no-op
# script (the default) is always safe to leave in place.

set -euo pipefail

# Example (uncomment to use):
# mkdir -p /etc/myapp
# echo "hello from build time" > /etc/myapp/config.txt
echo "built on $(date)" > /etc/build-info
