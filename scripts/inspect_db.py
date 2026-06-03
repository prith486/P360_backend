import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'")).fetchall()
    print("Columns in 'users' table:")
    for row in result:
        print(f"  - {row[0]}")
    
    result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'students'")).fetchall()
    print("\nColumns in 'students' table:")
    for row in result:
        print(f"  - {row[0]}")
finally:
    db.close()
