#!/usr/bin/env bash
# dev.sh — rebuild the site and serve it locally.
#
# Usage:
#   ./dev.sh          # serve on port 8000
#   ./dev.sh 8080     # serve on a custom port

set -e

ROOT="$(dirname "$(readlink -f "$0")")"
PORT="${1:-3000}"

cd "$ROOT"

# 1. Kill any existing server on this port
PID=$(lsof -ti tcp:"$PORT" 2>/dev/null || true)
if [ -n "$PID" ]; then
  echo "Stopping existing server on port $PORT (pid $PID)..."
  kill "$PID"
  sleep 0.5
fi

# 2. Build
echo "Building..."
uv run build/build.py

# 3. Serve
echo "Serving dist/ at http://localhost:$PORT"
cd dist
python3 -m http.server "$PORT"
