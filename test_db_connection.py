#!/usr/bin/env python
"""Test database connection."""
import sys
print("Testing database connection...")
sys.stdout.flush()

try:
    from app.core.config import settings
    print(f"✓ Config loaded")
    print(f"  DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    sys.stdout.flush()
    
    from sqlalchemy import create_engine, text
    print(f"✓ SQLAlchemy imported")
    sys.stdout.flush()
    
    print("Creating engine...")
    sys.stdout.flush()
    engine = create_engine(str(settings.DATABASE_URL), pool_pre_ping=True, connect_args={"connect_timeout": 5})
    print("✓ Engine created")
    sys.stdout.flush()
    
    print("Testing connection...")
    sys.stdout.flush()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        print(f"✓ Connection successful! Result: {result}")
        sys.exit(0)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
