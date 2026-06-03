import sys, os
sys.path.insert(0, os.getcwd())
from dotenv import load_dotenv
load_dotenv(".env")
from sqlalchemy import text
from app.core.database import engine

with engine.connect() as conn:
    print("Checking auth.users structure...")
    res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema = 'auth' AND table_name = 'users';"))
    cols = [row[0] for row in res]
    print(f"Columns: {cols}")
    if "full_name" in cols:
        print("✓ full_name exists")
    else:
        print("✗ full_name MISSING")
