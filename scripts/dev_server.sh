#!/bin/bash
# Development server startup script for Placement360 backend

if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

echo "Starting Placement360 Backend (Development Mode)..."

uvicorn app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level debug \
    --reload-dir app \
    --reload-delay 0.5
