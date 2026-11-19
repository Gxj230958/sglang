#!/usr/bin/env bash
# Build the image for the native architecture of this machine.
set -euo pipefail
cd "$(dirname "$0")"

REPO=xinyuantongradixark/sglang-private
TAG=dev-glm-loop-1118
case "$(uname -m)" in
    x86_64)  ARCH=amd64; BASE_PLATFORM_DIGEST=sha256:b2eb906e383d53e918ac761ea15db31f04afc0c4ec3859ca16774fc28e4b23a8 ;;
    aarch64) ARCH=arm64; BASE_PLATFORM_DIGEST=sha256:d42a31385980dd921667d4986909468ae2bd7bec7f98881fa2114308c3891e2c ;;
    *) echo "unsupported architecture: $(uname -m)" >&2; exit 1 ;;
esac

# One plain image manifest per architecture, so the two can be joined into a manifest list.
docker build --progress=plain --provenance=false --sbom=false \
    --build-arg BASE_PLATFORM_DIGEST="$BASE_PLATFORM_DIGEST" \
    --build-arg IMAGE_TAG="$REPO:$TAG" \
    -t "$REPO:$TAG-$ARCH" .
