"""
Production uvicorn configuration for Placement360 backend.
Optimized for 4-5K concurrent students with high availability.
"""
import multiprocessing
import os

# Server binding
bind = "0.0.0.0:8000"
host = "0.0.0.0"
port = int(os.getenv("PORT", "8000"))

# Worker configuration - Formula: (2 x CPU cores) + 1, capped at 8
workers = min(multiprocessing.cpu_count() * 2 + 1, 8)

# Worker class
worker_class = "uvicorn.workers.UvicornWorker"

# Timeouts
timeout = 120  # Worker timeout (2 minutes for AI operations)
keepalive = 5  # Keep-alive timeout
graceful_timeout = 30  # Graceful shutdown timeout

# Limits
worker_connections = 1000  # Max clients per worker
max_requests = 10000  # Restart worker after N requests
max_requests_jitter = 1000  # Randomize restart

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log errors to stdout
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "placement360-backend"

# Server mechanics
preload_app = True  # Load application before forking workers
daemon = False      # Run in foreground

# Development vs Production
reload = os.getenv("ENVIRONMENT", "production") == "development"
