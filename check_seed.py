import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)

with engine.connect() as conn:
    tables = conn.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'")).fetchall()
    print("TABLES AND DATA:")
    for t in tables:
        table_name = t[0]
        try:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            if count > 0:
                print(f"- {table_name}: {count} rows")
            else:
                print(f"- {table_name}: empty")
        except Exception as e:
            pass
