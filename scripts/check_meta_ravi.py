import os
import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT email, raw_user_meta_data FROM auth.users WHERE email IN ('ravi@placement360.dev', 'drpriya@placement360.dev')")).all()
        for row in res:
            print(f"EMAIL: {row[0]} | METADATA: {row[1]}")
except Exception as e:
    print(f"Error: {e}")
