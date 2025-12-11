#!/bin/bash
# Claude Code Hook: File Changed
# Send notification when a file is modified

FILE_PATH="${1:-Unknown File}"
ACTION="${2:-modified}"

# Get the project directory (parent of hooks directory)
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

python3 "$PROJECT_DIR/notify.py" \
  "File ${ACTION^}" \
  "$(basename ${FILE_PATH})" \
  "info"
