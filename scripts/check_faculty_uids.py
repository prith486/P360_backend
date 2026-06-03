import os
import uuid
import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("No DATABASE_URL found in .env")
    exit(1)

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

try:
    engine = create_engine(db_url)

    print("Listing all faculty and their UIDs:")
    with engine.connect() as conn:
        res = conn.execute(text("""
            SELECT u.id, u.email, u.raw_user_meta_data->>'full_name' as name, f.employee_id, f.department
            FROM auth.users u
            JOIN faculty f ON u.id = f.user_id
        """))
        for row in res:
             print(f"ID: {row[0]} | Email: {row[1]} | Name: {row[2]}")

except Exception as e:
    print(f"Error: {e}")
