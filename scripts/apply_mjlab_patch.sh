#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MJLAB_DIR="${1:-$ROOT_DIR/research/mjlab}"
PATCH_FILE="$ROOT_DIR/patches/mjlab-body29-local-flow.patch"

if [[ ! -d "$MJLAB_DIR/.git" ]]; then
  echo "Expected a git repo at: $MJLAB_DIR" >&2
  exit 1
fi

if [[ ! -f "$PATCH_FILE" ]]; then
  echo "Patch file not found: $PATCH_FILE" >&2
  exit 1
fi

if git -C "$MJLAB_DIR" apply --check "$PATCH_FILE" >/dev/null 2>&1; then
  git -C "$MJLAB_DIR" apply "$PATCH_FILE"
  echo "Applied patch to $MJLAB_DIR"
  exit 0
fi

if git -C "$MJLAB_DIR" apply --reverse --check "$PATCH_FILE" >/dev/null 2>&1; then
  echo "Patch already applied in $MJLAB_DIR"
  exit 0
fi

echo "Patch could not be applied cleanly to $MJLAB_DIR" >&2
exit 1

