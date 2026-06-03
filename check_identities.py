from app.core.database import get_session_local
from app.models.auth_user import AuthUser
from app.models.student import Student
from app.models.faculty import Faculty
import uuid

def check_all():
    db = get_session_local()()
    try:
        s_id = uuid.UUID('00000000-0000-0000-0000-000000000001')
        f_id = uuid.UUID('00000000-0000-0000-0000-000000000002')
        
        s_u = db.query(AuthUser).get(s_id)
        f_u = db.query(AuthUser).get(f_id)
        s_p = db.query(Student).filter(Student.user_id == s_id).first()
        f_p = db.query(Faculty).filter(Faculty.user_id == f_id).first()
        
        print(f"--- Student (000...0001) ---")
        if s_u:
            print(f"AuthUser Name: {s_u.full_name}, Email: {s_u.email}")
        else:
            print("AuthUser: MISSING")
        print(f"Student Profile: {'Exists' if s_p else 'MISSING'}")
        
        print(f"\n--- Faculty (000...0002) ---")
        if f_u:
            print(f"AuthUser Name: {f_u.full_name}, Email: {f_u.email}")
        else:
            print("AuthUser: MISSING")
        print(f"Faculty Profile: {'Exists' if f_p else 'MISSING'}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_all()
