#!/bin/bash
# Claude Code Hook: Task Complete
# Send notification when a task completes

TASK_NAME="${1:-Unknown Task}"
DURATION="${2:-0}"

# Get the project directory (parent of hooks directory)
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

python3 "$PROJECT_DIR/notify.py" \
  "Task Completed" \
  "${TASK_NAME} finished in ${DURATION}s" \
  "success"
