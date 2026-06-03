from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from typing import Type

from app.core.config import settings
from app.core.validation import config_validator
from app.core.logging_config import setup_logging, get_logger
from app.api.v1.router import api_router
from app.core.database import test_connection, dispose_engine
from app.tasks.scheduler import start_scheduler, stop_scheduler
from app.core.exceptions import (
    placement360_exception_handler,
    database_exception_handler,
    validation_exception_handler,
    Placement360Exception
)

# Setup logging before app creation
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 70)
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    
    # Validate configuration
    # Validate configuration
    config_validator.validate_or_exit()
    
    # Test database connection
    try:
        if test_connection():
            logger.info("✓ Database connection established")
        else:
            logger.error("✗ Database connection check returned False")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")

    logger.info("Application startup complete")
    logger.info("=" * 70)
    
    # Start background scheduler
    try:
        start_scheduler()
    except Exception as e:
        logger.warning(f"Scheduler startup failed (non-fatal): {e}")

    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    stop_scheduler()
    dispose_engine()
    logger.info("✓ Database connections closed")

# Update FastAPI app initialization to include lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for campus placement preparation",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS — Must be added BEFORE routers so every response (including preflight
# OPTIONS requests) gets the Access-Control-Allow-* headers.
# Reads from ALLOWED_ORIGINS env var — add your Vercel URL there.
# ─────────────────────────────────────────────────────────────────────────────
_origins = settings.allowed_origins_list
# Always allow local dev regardless of env var
_local_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
for _o in _local_origins:
    if _o not in _origins:
        _origins.append(_o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Register custom exception handlers
app.add_exception_handler(Placement360Exception, placement360_exception_handler)

# Special handler for IntegrityError to avoid import at top level
def register_db_exceptions(app: FastAPI):
    try:
        from sqlalchemy.exc import IntegrityError
        app.add_exception_handler(IntegrityError, database_exception_handler)
    except ImportError:
        logger.warning("SQLAlchemy not available, skipping IntegrityError handler")

register_db_exceptions(app)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Placement360 Backend API",
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else None,
        "health": f"{settings.API_V1_STR}/health"
    }
