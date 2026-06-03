"""
Final system verification for the Placement360 Database Schema.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def run_final_verification():
    print("=" * 80)
    print("PLACEMENT360 DATABASE FINAL SYSTEM VERIFICATION")
    print("=" * 80)
    
    with engine.connect() as conn:
        # 1. Tables check
        print("\n1. TABLES IN PUBLIC SCHEMA:")
        tables = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")).fetchall()
        for t in tables:
            print(f"  [TABLE] {t[0]}")

        # 2. Indexes count
        print("\n2. TOTAL INDEXES:")
        index_count = conn.execute(text("SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public'")).scalar()
        print(f"  [COUNT] {index_count} indexes (Expected 50+)")

        # 3. ENUMs check
        print("\n3. ENUM TYPES:")
        enums = conn.execute(text("SELECT DISTINCT enumtypid::regtype FROM pg_enum")).fetchall()
        print(f"  [COUNT] {len(enums)} Enums")
        for e in enums:
            print(f"  [ENUM] {e[0]}")

        # 4. RLS status
        print("\n4. ROW LEVEL SECURITY (RLS) STATUS:")
        rls = conn.execute(text("SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public'")).fetchall()
        for r in rls:
            status = "ENABLED" if r[1] else "DISABLED"
            print(f"  [RLS] {r[0]}: {status}")

        # 5. Materialized View check
        print("\n5. MATERIALIZED VIEW CHECK:")
        try:
            mv_count = conn.execute(text("SELECT COUNT(*) FROM student_leaderboard")).scalar()
            print(f"  [VIEW] student_leaderboard exists. Current row count: {mv_count}")
        except Exception as e:
            print(f"  [ERROR] student_leaderboard check failed: {e}")

        # 6. Triggers check
        print("\n6. CUSTOM TRIGGERS:")
        triggers = conn.execute(text("SELECT tgname, tgrelid::regclass FROM pg_trigger WHERE tgisinternal = FALSE")).fetchall()
        for tr in triggers:
            # Filtering out storage/realtime triggers if they show up in public check or regclass
            print(f"  [TRIGGER] {tr[0]} on {tr[1]}")

        # 7. Functions check
        print("\n7. CUSTOM FUNCTIONS (PUBLIC):")
        funcs = conn.execute(text("SELECT proname FROM pg_proc WHERE pronamespace = 'public'::regnamespace")).fetchall()
        for f in funcs:
            print(f"  [FUNCTION] {f[0]}")

    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    run_final_verification()
