#!/bin/bash
set -e

echo "[STARTUP] Initializing virtual X11 framebuffer (Xvfb :99)..."
Xvfb :99 -screen 0 1920x1080x24 -ac -nolisten tcp &
XVFB_PID=$!
sleep 1

export DISPLAY=:99
export PYTHONUNBUFFERED=1

echo "[STARTUP] Virtual display ready. Launching Python Actor..."
python3 -u -m src.main
EXIT_CODE=$?

kill $XVFB_PID 2>/dev/null || true
exit $EXIT_CODE
