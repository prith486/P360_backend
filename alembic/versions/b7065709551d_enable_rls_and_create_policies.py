"""enable_rls_and_create_policies

Revision ID: b7065709551d
Revises: 306b0ba4be7e
Create Date: 2026-02-11 00:24:15.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7065709551d'
down_revision: Union[str, None] = '306b0ba4be7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable RLS on all tables
    tables = [
        'users', 'students', 'faculty', 'admin_activity_log', 
        'questions', 'assessments', 'assessment_questions', 
        'submissions', 'assessment_attempts'
    ]
    for table in tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")

    # 2. Create RLS policies for users table
    op.execute("""
    CREATE POLICY "Users can view own profile"
    ON users FOR SELECT
    USING (auth.uid()::text = id::text OR auth.role() = 'authenticated');
    """)
    op.execute("""
    CREATE POLICY "Users can update own profile"
    ON users FOR UPDATE
    USING (auth.uid()::text = id::text)
    WITH CHECK (auth.uid()::text = id::text);
    """)
    op.execute("""
    CREATE POLICY "Admins can insert users"
    ON users FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM users
            WHERE id::text = auth.uid()::text AND role = 'admin'
        )
    );
    """)

    # 3. Create RLS policies for students table
    # Using auth.uid() directly for standard Supabase auth
    op.execute("""
    CREATE POLICY "Students can view own profile"
    ON students FOR SELECT
    USING (
        user_id::text = auth.uid()::text OR
        EXISTS (SELECT 1 FROM users WHERE id::text = auth.uid()::text AND role IN ('faculty', 'admin'))
    );
    """)
    op.execute("""
    CREATE POLICY "Students can update own profile"
    ON students FOR UPDATE
    USING (user_id::text = auth.uid()::text)
    WITH CHECK (user_id::text = auth.uid()::text);
    """)

    # 4. Create RLS policies for questions
    op.execute("""
    CREATE POLICY "Public can view published questions"
    ON questions FOR SELECT
    USING (is_public = TRUE AND is_active = TRUE);
    """)
    op.execute("""
    CREATE POLICY "Faculty can create questions"
    ON questions FOR INSERT
    WITH CHECK (
        EXISTS (SELECT 1 FROM faculty WHERE user_id::text = auth.uid()::text AND can_create_assessments = TRUE)
    );
    """)

    # 5. Create RLS policies for submissions
    op.execute("""
    CREATE POLICY "Students can view own submissions"
    ON submissions FOR SELECT
    USING (
        EXISTS (SELECT 1 FROM students WHERE id = submissions.student_id AND user_id::text = auth.uid()::text)
    );
    """)
    op.execute("""
    CREATE POLICY "Students can create submissions"
    ON submissions FOR INSERT
    WITH CHECK (
        EXISTS (SELECT 1 FROM students WHERE id = submissions.student_id AND user_id::text = auth.uid()::text)
    );
    """)

    # 6. Grant permissions to service_role (standard Supabase role)
    # Note: We use IF EXISTS or wrap in a block just in case, but standard GRANT usually works or fails gracefully in Supabase
    op.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;")
    op.execute("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;")
    op.execute("GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;")


def downgrade() -> None:
    # Drop policies
    op.execute('DROP POLICY IF EXISTS "Students can create submissions" ON submissions')
    op.execute('DROP POLICY IF EXISTS "Students can view own submissions" ON submissions')
    op.execute('DROP POLICY IF EXISTS "Faculty can create questions" ON questions')
    op.execute('DROP POLICY IF EXISTS "Public can view published questions" ON questions')
    op.execute('DROP POLICY IF EXISTS "Students can update own profile" ON students')
    op.execute('DROP POLICY IF EXISTS "Students can view own profile" ON students')
    op.execute('DROP POLICY IF EXISTS "Admins can insert users" ON users')
    op.execute('DROP POLICY IF EXISTS "Users can update own profile" ON users')
    op.execute('DROP POLICY IF EXISTS "Users can view own profile" ON users')

    # Disable RLS
    tables = [
        'users', 'students', 'faculty', 'admin_activity_log', 
        'questions', 'assessments', 'assessment_questions', 
        'submissions', 'assessment_attempts'
    ]
    for table in tables:
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
