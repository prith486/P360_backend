#!/usr/bin/env python3
"""
Initialize database schema for Placement360.
Creates all tables defined in SQLAlchemy models.
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database schema."""
    logger.info("Initializing database schema...")
    
    try:
        # Import all models to register them with Base
        from app.models.base import BaseModel
        from app.models.test import TestItem
        # Add more model imports as you create them
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✓ Database schema initialized successfully")
        
        # Test the connection
        from app.core.database import test_connection
        test_connection()
        
        logger.info("✓ Database verification completed")
        
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("Initializing Placement360 Database...")
    init_database()
    print("Database initialization complete!")
