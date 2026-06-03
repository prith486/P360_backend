"""
Verify RLS and security policies.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def verify_security():
    print("=" * 60)
    print("VERIFYING ROW LEVEL SECURITY (RLS)")
    print("=" * 60)
    
    with engine.connect() as conn:
        # 1. Check if RLS is enabled on tables
        print("\nChecking RLS status on tables:")
        query = text("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
              AND tablename IN (
                'users', 'students', 'faculty', 'admin_activity_log', 
                'questions', 'assessments', 'assessment_questions', 
                'submissions', 'assessment_attempts'
              )
            ORDER BY tablename;
        """)
        result = conn.execute(query).fetchall()
        for row in result:
            status = "ENABLED" if row[1] else "DISABLED"
            print(f" - {row[0]}: {status}")

        # 2. Check policies
        print("\nChecking RLS policies:")
        policy_query = text("""
            SELECT tablename, policyname, cmd 
            FROM pg_policies 
            WHERE schemaname = 'public'
            ORDER BY tablename, cmd;
        """)
        policies = conn.execute(policy_query).fetchall()
        if not policies:
            print(" No policies found.")
        for row in policies:
            print(f" - [{row[0]}] {row[1]} ({row[2]})")

        # 3. Check service_role permissions (simplified check)
        print("\nChecking service_role grants (existence check):")
        try:
             # Just checking if we can query as something that might check roles, 
             # but we'll just check if the role exists in pg_roles
             role_check = conn.execute(text("SELECT 1 FROM pg_roles WHERE rolname = 'service_role'")).scalar()
             if role_check:
                 print(" - role 'service_role' exists in the database.")
             else:
                 print(" - role 'service_role' does not exist (may be managed externally or by Supabase).")
        except Exception as e:
            print(f" Could not check roles: {e}")

if __name__ == "__main__":
    verify_security()
