from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import psutil
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check - lightweight, called frequently."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": int(time.time())
    }

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check - verifies dependencies are operational."""
    try:
        # Use execute() on the session and fetch result
        result = db.execute(text("SELECT 1")).scalar()
        if result != 1:
            raise HTTPException(status_code=503, detail="Database check failed")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")
    
    return {
        "status": "ready",
        "database": "connected",
        "timestamp": int(time.time())
    }

@router.get("/live")
async def liveness_check():
    """Liveness check - verifies process is alive."""
    return {
        "status": "alive",
        "timestamp": int(time.time())
    }

@router.get("/metrics")
async def metrics_endpoint():
    """Performance metrics for monitoring."""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    return {
        "timestamp": int(time.time()),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_gb": round(memory.used / (1024 ** 3), 2),
        },
        "process": {
            "memory_mb": round(psutil.Process().memory_info().rss / 1024 / 1024, 2),
            "cpu_percent": psutil.Process().cpu_percent(interval=0.1),
            "threads": psutil.Process().num_threads()
        }
    }
