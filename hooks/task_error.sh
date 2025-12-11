#!/bin/bash
# Claude Code Hook: Task Error
# Send notification when a task fails

TASK_NAME="${1:-Unknown Task}"
ERROR_MSG="${2:-Unknown Error}"

# Get the project directory (parent of hooks directory)
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

python3 "$PROJECT_DIR/notify.py" \
  "Task Error" \
  "${TASK_NAME}: ${ERROR_MSG}" \
  "error"
