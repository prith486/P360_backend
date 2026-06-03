import os, requests, sys
from dotenv import load_dotenv
from sqlalchemy.orm import Session
sys.path.append(os.getcwd()) # For imports

from app.core.database import get_session_local
from app.models.faculty import Faculty
from app.models.auth_user import AuthUser
from app.models.assessment import Assessment

load_dotenv()

def reassign_assessments():
    SessionLocal = get_session_local()
    db = SessionLocal()
    
    # 1. Get Dr. Priya's REAL UUID
    real_drpriya = db.query(AuthUser).filter(AuthUser.email == "drpriya@placement360.dev").first()
    if not real_drpriya:
        print("Real Dr. Priya user not found in DB.")
        db.close()
        return
        
    real_uid = real_drpriya.id
    print(f"Real Dr. Priya UUID: {real_uid}")
    
    # 2. Get old mock faculty ID
    old_uid = "00000000-0000-0000-0000-000000000002"
    
    # 3. Update assessments
    updated = db.query(Assessment).filter(Assessment.created_by == old_uid).update({"created_by": real_uid})
    db.commit()
    print(f"Updated {updated} assessments and assigned to Dr. Priya.")
    
    # Ensure they are published so they show up for everyone
    # Actually, keep them as is, but now they are "Mine" for Dr. Priya.
    
    db.close()

if __name__ == "__main__":
    reassign_assessments()
