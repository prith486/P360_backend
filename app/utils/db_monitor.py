"""
Database connection pool monitoring utilities.
Implementation for monitoring SQLAlchemy connection pool health and statistics.
"""
from app.core.database import engine
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_pool_stats() -> dict:
    """Get current connection pool statistics."""
    # SQLAlchemy QueuePool exposes these methods
    pool = engine.pool
    
    # Calculate potential total connections (pool_size + max_overflow)
    # Note: pool.size() returns the configured pool_size
    # pool.overflow() returns currently created connections above pool_size
    # max_overflow is stored in _max_overflow usually
    
    max_overflow = getattr(pool, '_max_overflow', settings.DB_MAX_OVERFLOW)
    current_total_capacity = pool.size() + max_overflow
    
    # Checked out connections are those currently in use
    checked_out = pool.checkedout()
    
    # Utilization based on total possible capacity
    # If using NullPool (no pooling), these might be 0/different, but we use QueuePool
    if current_total_capacity > 0:
        utilization = (checked_out / current_total_capacity) * 100
    else:
        utilization = 0
        
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": checked_out,
        "overflow": pool.overflow(),
        "max_overflow": max_overflow,
        "current_total_connections": pool.checkedin() + checked_out + pool.overflow(), # connections actually open in DB
        "utilization_percent": round(utilization, 2)
    }

def check_pool_health() -> tuple[bool, str]:
    """
    Check if connection pool is healthy.
    Returns (is_healthy, message)
    """
    stats = get_pool_stats()
    
    # Critical: Very high utilization (> 90%)
    if stats['utilization_percent'] > 90:
        return False, f"CRITICAL: Pool utilization at {stats['utilization_percent']}%"
        
    # Warning: High utilization (> 70%)
    if stats['utilization_percent'] > 70:
        return True, f"WARNING: High pool utilization: {stats['utilization_percent']}%"
    
    # Info: Using overflow connections
    if stats['overflow'] > 0:
        return True, f"Pool healthy (using {stats['overflow']} overflow connections)"
    
    # Healthy
    return True, "Pool healthy"

def log_pool_stats():
    """Log current pool statistics to application logger."""
    stats = get_pool_stats()
    logger.info(
        f"DB Pool Stats: "
        f"InUse={stats['checked_out']} "
        f"Available={stats['checked_in']} "
        f"Overflow={stats['overflow']}/{stats['max_overflow']} "
        f"Util={stats['utilization_percent']}%"
    )
