"""
Database health check and diagnostic endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import time

from app.core.config import settings
from app.core.database import get_db, engine
from app.utils.db_monitor import get_pool_stats, check_pool_health

router = APIRouter()

@router.get("/db-health")
async def database_health_check(db: Session = Depends(get_db)):
    """
    Quick database health check.
    Tests if database is reachable and responsive.
    """
    try:
        start_time = time.time()
        # Using Session to execute simple query
        result = db.execute(text("SELECT 1")).scalar()
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        if result == 1:
            return {
                "status": "healthy",
                "database": "connected",
                "latency_ms": latency_ms,
                "environment": settings.ENVIRONMENT,
                "message": "Database connection successful"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database query returned unexpected result"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

@router.get("/db-info")
async def database_info():
    """
    Detailed database information and connection pool stats.
    Only available in development or non-production environments for security.
    """
    if settings.is_production:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Database info not available in production"
        )

    try:
        with engine.connect() as connection:
            # Get PostgreSQL version
            version = connection.execute(text("SELECT version()")).scalar()
            database = connection.execute(text("SELECT current_database()")).scalar()
            
            # Get pool statistics
            pool = engine.pool
            pool_stats = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "max_overflow": settings.DB_MAX_OVERFLOW, # Using settings for max overflow
                # pool.overflow() + pool.size() gives current total connections roughly
            }
            
            return {
                "status": "connected",
                "version": version,
                "database": database,
                "pool_stats": pool_stats
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to get database info: {str(e)}"
        )

@router.get("/db-pool-stats")
async def database_pool_stats():
    """
    Get current connection pool statistics and health check.
    Useful for monitoring dashboards or alerts.
    """
    # Only expose detailed stats to authorized users or in non-production if strict security is needed
    # For now, we allow it but you might want to wrap this in a dependency later.
    
    try:
        stats = get_pool_stats()
        is_healthy, message = check_pool_health()
        
        return {
            "timestamp": time.time(),
            "pool_stats": stats,
            "health": {
                "is_healthy": is_healthy,
                "message": message,
                "utilization_level": "CRITICAL" if stats['utilization_percent'] > 90 else "HIGH" if stats['utilization_percent'] > 70 else "NORMAL"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pool stats: {str(e)}"
        )

@router.get("/db-test-query")
async def test_database_query(db: Session = Depends(get_db)):
    """Test database query execution."""
    try:
        start_time = time.time()
        
        results = {}
        results["select_1"] = db.execute(text("SELECT 1 as num")).scalar()
        results["current_timestamp"] = str(db.execute(text("SELECT NOW()")).scalar()) # Convert to string for JSON serialization
        results["current_database"] = db.execute(text("SELECT current_database()")).scalar()
        
        execution_time_ms = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "success",
            "results": results,
            "execution_time_ms": execution_time_ms
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )
