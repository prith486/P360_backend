from typing import Generator, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

def create_database_engine():
    from sqlalchemy import create_engine
    from sqlalchemy.pool import QueuePool
    """
    Create SQLAlchemy engine with optimized connection pooling.
    """
    
    connect_args = {
        "connect_timeout": 10,
        "options": "-c timezone=utc",
        "application_name": "placement360"
    }
    
    engine = create_engine(
        str(settings.DATABASE_URL),
        poolclass=QueuePool,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=True,
        echo=settings.DB_ECHO,
        connect_args=connect_args,
        future=True
    )
    
    logger.info(f"Database engine created")
    return engine

engine = None

def get_engine():
    """Lazy-load database engine."""
    global engine
    if engine is None:
        engine = create_database_engine()
    return engine

# SessionLocal factory will be initialized lazily
_SessionLocal = None

def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        from sqlalchemy.orm import sessionmaker
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            bind=get_engine()
        )
    return _SessionLocal

def get_db() -> Generator:
    """FastAPI dependency for database sessions."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        # Only log actual database errors, not FastAPI HTTPExceptions 
        # (which can propagate through dependencies)
        if not hasattr(e, "status_code"):
            logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()

def test_connection() -> bool:
    """Test database connectivity."""
    from sqlalchemy import text
    try:
        with get_engine().connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            return result == 1
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def dispose_engine() -> None:
    """Dispose database engine."""
    global engine
    if engine is not None:
        engine.dispose()

def init_db():
    """Create all tables."""
    from app.models.base import Base
    Base.metadata.create_all(bind=get_engine())

def drop_db():
    """Drop all tables."""
    from app.models.base import Base
    Base.metadata.drop_all(bind=get_engine())

# Export a default SessionLocal factory for convenience
SessionLocal = get_session_local()
