#!/bin/bash
# Production server startup script for Placement360 backend
set -e

# Environment validation
if [ "$ENVIRONMENT" != "production" ] && [ "$ENVIRONMENT" != "staging" ]; then
    echo "WARNING: ENVIRONMENT is not set to 'production' or 'staging'"
fi

echo "Starting Placement360 Backend in PRODUCTION mode..."
echo "Workers: $(python -c 'import multiprocessing; print(min(multiprocessing.cpu_count() * 2 + 1, 8))')"
echo "Environment: ${ENVIRONMENT:-production}"

# Start server with Gunicorn + Uvicorn workers
gunicorn app.main:app \
    --config uvicorn_config.py \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --max-requests 10000 \
    --max-requests-jitter 1000 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload
