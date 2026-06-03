import os
import uuid
import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# We'll use the environment variable directly
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("No DATABASE_URL found in .env")
    exit(1)

# Correct potential issue with postgres:// vs postgresql://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

try:
    engine = create_engine(db_url)

    print("Listing all assessments and their creators:")
    with engine.connect() as conn:
        res = conn.execute(text("""
            SELECT a.id, a.title, a.created_by, 
                   COALESCE(u.raw_user_meta_data->>'full_name', u.raw_user_meta_data->>'name', 'Unknown') as full_name,
                   a.status, a.is_published
            FROM assessments a
            LEFT JOIN auth.users u ON a.created_by = u.id
        """))
        rows = res.all()
        for row in rows:
             print(f"ID: {row[0]} | Title: {row[1]} | Creator ID: {row[2]} | Creator Name: {row[3]} | Status: {row[4]} | Published: {row[5]}")

except Exception as e:
    print(f"Error: {e}")
