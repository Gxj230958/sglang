#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${REPO_DIR:-$(git rev-parse --show-toplevel)}"
UPSTREAM_URL="${UPSTREAM_URL:-https://github.com/sgl-project/sglang.git}"
UPSTREAM_BRANCH="${UPSTREAM_BRANCH:-main}"
TARGET_REMOTE="${TARGET_REMOTE:-origin}"
TARGET_BRANCH="${TARGET_BRANCH:-sglang-main}"
UPSTREAM_REF="refs/remotes/sglang-upstream/${UPSTREAM_BRANCH}"
TARGET_REF="refs/remotes/${TARGET_REMOTE}/${TARGET_BRANCH}"

export GIT_TERMINAL_PROMPT=0

echo "===== $(date -u +'%Y-%m-%dT%H:%M:%SZ') sync start ====="
git -C "${REPO_DIR}" fetch --no-tags "${TARGET_REMOTE}" \
  "+refs/heads/${TARGET_BRANCH}:${TARGET_REF}"
git -C "${REPO_DIR}" fetch --no-tags "${UPSTREAM_URL}" \
  "+refs/heads/${UPSTREAM_BRANCH}:${UPSTREAM_REF}"

UPSTREAM_SHA="$(git -C "${REPO_DIR}" rev-parse "${UPSTREAM_REF}")"
TARGET_SHA="$(git -C "${REPO_DIR}" rev-parse "${TARGET_REF}")"

if [[ "${TARGET_SHA}" == "${UPSTREAM_SHA}" ]]; then
  echo "----- target ${TARGET_BRANCH} already matches upstream ${UPSTREAM_BRANCH} at ${UPSTREAM_SHA:0:12}"
  echo "===== $(date -u +'%Y-%m-%dT%H:%M:%SZ') sync done ====="
  exit 0
fi

if ! git -C "${REPO_DIR}" merge-base --is-ancestor "${TARGET_REF}" "${UPSTREAM_REF}"; then
  echo "ERROR: target ${TARGET_BRANCH} has diverged from upstream ${UPSTREAM_BRANCH}; refusing a non-fast-forward update." >&2
  echo "----- upstream/${UPSTREAM_BRANCH} $(git -C "${REPO_DIR}" rev-parse "${UPSTREAM_REF}")" >&2
  echo "----- ${TARGET_REMOTE}/${TARGET_BRANCH} $(git -C "${REPO_DIR}" rev-parse "${TARGET_REF}")" >&2
  exit 1
fi

git -C "${REPO_DIR}" push "${TARGET_REMOTE}" \
  "${UPSTREAM_REF}:refs/heads/${TARGET_BRANCH}"
echo "----- upstream/${UPSTREAM_BRANCH} $(git -C "${REPO_DIR}" rev-parse --short "${UPSTREAM_REF}")"
echo "----- ${TARGET_REMOTE}/${TARGET_BRANCH} $(git -C "${REPO_DIR}" rev-parse --short "${UPSTREAM_REF}")"
echo "===== $(date -u +'%Y-%m-%dT%H:%M:%SZ') sync done ====="
