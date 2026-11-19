#!/usr/bin/env bash
# Generate the build context inputs from a local sglang clone that holds both commits.
# Usage: make-manifest.sh <sglang-repo> [context-dir]
set -euo pipefail

REPO=$1
CTX=$(realpath "${2:-$(dirname "$0")}")
BASE_SGLANG_COMMIT=7b5fb39bb952da5f6da3bb7fe73c671cf449b6fa
CUTOFF_COMMIT=a22079906bf873d1c888b9a0c4b7fdc70a4432f2

mkdir -p "$CTX/manifest"
git -C "$REPO" archive --format=tar.gz -o "$CTX/sglang-src.tar.gz" "$CUTOFF_COMMIT"

TREE=$(mktemp -d)
trap 'rm -rf "$TREE"' EXIT
tar -xzf "$CTX/sglang-src.tar.gz" -C "$TREE"

( cd "$TREE" && find . -type f -printf '%P\0' | LC_ALL=C sort -z | xargs -0 sha256sum ) \
    > "$CTX/manifest/cutoff-files.sha256"
( cd "$TREE" && find . -type l -printf '%P\t%l\n' | LC_ALL=C sort ) \
    > "$CTX/manifest/cutoff-symlinks.tsv"

git -C "$REPO" diff --name-status --no-renames "$BASE_SGLANG_COMMIT" "$CUTOFF_COMMIT" \
    | awk -F'\t' '$1 == "D" {print $2}' > "$CTX/manifest/base-only-files.txt"
git -C "$REPO" diff --name-status --no-renames "$BASE_SGLANG_COMMIT" "$CUTOFF_COMMIT" \
    | awk -F'\t' '$1 != "D" {print $2}' > "$CTX/manifest/changed-files.txt"

wc -l "$CTX"/manifest/*
