import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine  # type: ignore
from sqlalchemy import text  # type: ignore

with engine.connect() as conn:
    res = conn.execute(text("SELECT enum_range(NULL::branch_type)"))
    print('branch_type:', res.fetchone()[0])
    
    res = conn.execute(text("SELECT enum_range(NULL::academic_year)"))
    print('academic_year:', res.fetchone()[0])
    
    res = conn.execute(text("SELECT enum_range(NULL::user_role)"))
    print('user_role:', res.fetchone()[0])

    res = conn.execute(text("SELECT COUNT(*) FROM public.students"))
    print('students count:', res.fetchone()[0])
    
    res = conn.execute(text("SELECT COUNT(*) FROM public.faculty"))
    print('faculty count:', res.fetchone()[0])
    
    # Sample a student row to see actual stored values
    res = conn.execute(text("SELECT branch, current_year FROM public.students LIMIT 3"))
    rows = res.fetchall()
    print('sample student rows:', rows)
