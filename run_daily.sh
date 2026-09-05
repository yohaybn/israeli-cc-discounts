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
  "$REPO_DIR/.venv/bin/python" "$REPO_DIR/scripts/join_businesses.py" >> "$LOG_FILE" 2>&1
  EXIT_CODE=$?
fi

if [ $EXIT_CODE -ne 0 ]; then
    echo "[CRON ERROR] main.py exited with code $EXIT_CODE" >> "$LOG_FILE"
fi

# Commit and push only if data files changed
git add data/*.json data/**/*.json docs/data/*.json docs/data/businesses/*.json
if git diff --cached --quiet; then
    echo "[CRON] No data changes to commit." >> "$LOG_FILE"
else
    git -c user.name="discount-bot" -c user.email="discount-bot@$(hostname)" \
        commit -m "Auto update discount data $(date +%Y-%m-%d) [skip ci]" >> "$LOG_FILE" 2>&1
    if git push origin "$BRANCH" >> "$LOG_FILE" 2>&1; then
        echo "[CRON] Pushed updated data to origin/$BRANCH." >> "$LOG_FILE"
    else
        echo "[CRON ERROR] git push failed. Will retry next run." >> "$LOG_FILE"
        # Reset the local commit so it doesn't pile up? Keep it; next push may succeed after pull.
        git pull --rebase origin "$BRANCH" >> "$LOG_FILE" 2>&1 || true
    fi
fi

echo "===== Run finished: $(date -Is) =====" >> "$LOG_FILE"

# Keep log file from growing indefinitely (keep last ~2000 lines)
tail -n 2000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
