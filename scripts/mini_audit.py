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
        print("FACULTY:")
        res_f = conn.execute(text("SELECT u.id, u.email FROM auth.users u JOIN faculty f ON u.id = f.user_id")).all()
        for f in res_f:
            print(f"UID: {f[0]} | EMAIL: {f[1]}")
            
        print("\nASSESSMENTS:")
        res_a = conn.execute(text("SELECT id, title, created_by, status, is_published FROM assessments")).all()
        for a in res_a:
            print(f"AID: {a[0]} | TITLE: {a[1]} | CREATOR: {a[2]} | STATUS: {a[3]} | PUB: {a[4]}")
except Exception as e:
    print(f"Error: {e}")
