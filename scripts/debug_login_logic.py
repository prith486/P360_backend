import os, sys, requests
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import get_session_local
from app.models.student import Student
from app.models.faculty import Faculty

def debug_login():
    email = "ravi@placement360.dev"
    password = "Faculty@123"
    
    SessionLocal = get_session_local()
    db = SessionLocal()
    
    try:
        # Step 1
        res = requests.post(
            f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": settings.SUPABASE_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password}
        )
        print(f"Supabase status: {res.status_code}")
        if res.status_code != 200:
            print(f"Auth failed: {res.text}")
            return
            
        data = res.json()
        user_id = data["user"]["id"]
        role = data["user"].get("user_metadata", {}).get("role") or data["user"].get("app_metadata", {}).get("role")
        print(f"Role: {role}, ID: {user_id}")
        
        # Step 3
        if role == "faculty":
            profile = db.query(Faculty).filter(Faculty.user_id == user_id).first()
            if not profile:
                print("Faculty profile NOT FOUND")
            else:
                print(f"Profile found: {profile.id}")
                
        # Step 4
        payload = {
            "sub": str(user_id),
            "role": role,
            "email": email,
            "name": data["user"].get("user_metadata", {}).get("full_name", email)
        }
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload.update({"iat": datetime.utcnow(), "exp": expire, "type": "access"})
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        print("JWT created successfully")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_login()
