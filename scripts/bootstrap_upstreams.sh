#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESEARCH_DIR="$ROOT_DIR/research"
LOCK_FILE="$ROOT_DIR/upstreams/lock.json"

mkdir -p "$RESEARCH_DIR"

clone_and_pin() {
  local url="$1"
  local dir="$2"
  local commit="$3"

  if [[ ! -d "$dir/.git" ]]; then
    git clone "$url" "$dir"
  fi

  git -C "$dir" fetch --all --tags
  git -C "$dir" checkout "$commit"
}

MJLAB_URL="https://github.com/mujocolab/mjlab"
MJLAB_COMMIT="6abd0eb"
TWIST2_URL="https://github.com/amazon-far/TWIST2"
TWIST2_COMMIT="d5c7108e9ef82d1b8770e5b692f27a1294f3aa8a"
UNITREE_MUJOCO_URL="https://github.com/unitreerobotics/unitree_mujoco"
UNITREE_MUJOCO_COMMIT="1a37b05"
UNITREE_SDK2_PY_URL="https://github.com/unitreerobotics/unitree_sdk2_python"
UNITREE_SDK2_PY_COMMIT="ab0d8ae"

clone_and_pin "$MJLAB_URL" "$RESEARCH_DIR/mjlab" "$MJLAB_COMMIT"
clone_and_pin "$TWIST2_URL" "$RESEARCH_DIR/TWIST2" "$TWIST2_COMMIT"
clone_and_pin "$UNITREE_MUJOCO_URL" "$RESEARCH_DIR/unitree_mujoco" "$UNITREE_MUJOCO_COMMIT"
clone_and_pin "$UNITREE_SDK2_PY_URL" "$RESEARCH_DIR/unitree_sdk2_python" "$UNITREE_SDK2_PY_COMMIT"

bash "$ROOT_DIR/scripts/apply_mjlab_patch.sh" "$RESEARCH_DIR/mjlab"

echo
echo "Bootstrap complete."
echo "Pinned upstreams are documented in: $LOCK_FILE"
echo "Next:"
echo "  cd \"$RESEARCH_DIR/mjlab\""
echo "  uv sync"
