#!/usr/bin/env bash
# Push this machine's architecture tag. Run `docker login` first.
set -euo pipefail

REPO=xinyuantongradixark/sglang-private
TAG=dev-glm-loop-1118
case "$(uname -m)" in
    x86_64)  ARCH=amd64 ;;
    aarch64) ARCH=arm64 ;;
    *) echo "unsupported architecture: $(uname -m)" >&2; exit 1 ;;
esac

docker push "$REPO:$TAG-$ARCH"
docker buildx imagetools inspect "$REPO:$TAG-$ARCH"
