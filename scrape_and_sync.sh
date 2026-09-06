#!/bin/bash
# Daily discount scraper: run main.py, commit & push data changes to GitHub.
# Designed to be invoked by cron.

set -u

REPO_DIR="/home/ubuntu/discount-finder"
DATA_DIR="$REPO_DIR/data"
LOG_FILE="$DATA_DIR/scraper_cron.log"
BRANCH="main"

mkdir -p "$DATA_DIR"
cd "$REPO_DIR" || exit 1
shopt -s globstar nullglob

echo "===== Run started: $(date -Is) =====" >> "$LOG_FILE"

# Run the scraper and refresh the physical-store discount list for the static HTML.
"$REPO_DIR/.venv/bin/python" "$REPO_DIR/main.py" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
  "$REPO_DIR/.venv/bin/python" "$REPO_DIR/fetch_osm_data.py" >> "$LOG_FILE" 2>&1
  EXIT_CODE=$?
fi
if [ $EXIT_CODE -eq 0 ]; then
  "$REPO_DIR/.venv/bin/python" "$REPO_DIR/scripts/join_businesses.py" >> "$LOG_FILE" 2>&1
  EXIT_CODE=$?
fi

if [ $EXIT_CODE -ne 0 ]; then
    echo "[CRON ERROR] main.py exited with code $EXIT_CODE" >> "$LOG_FILE"
fi



echo "===== Run finished: $(date -Is) =====" >> "$LOG_FILE"

# Keep log file from growing indefinitely (keep last ~2000 lines)
tail -n 2000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
