#!/bin/bash
# Start the Discount Finder REST API
# Usage: ./run_api.sh [port]
cd "$(dirname "$0")"
PORT="${1:-9203}"
exec .venv/bin/uvicorn api_server:app --host 0.0.0.0 --port "$PORT"
