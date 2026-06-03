from app.core.database import get_session_local
from app.models.faculty import Faculty
from app.models.auth_user import AuthUser

def check_faculty():
    db = get_session_local()()
    try:
        fs = db.query(Faculty).all()
        print(f"Total faculty records: {len(fs)}")
        for f in fs:
            u = db.query(AuthUser).filter(AuthUser.id == f.user_id).first()
            if u:
                print(f"User ID: {f.user_id}, Name: {u.full_name}, Email: {u.email}")
            else:
                print(f"User ID: {f.user_id}, Profile exists but AuthUser missing!")
    finally:
        db.close()

if __name__ == "__main__":
    check_faculty()
