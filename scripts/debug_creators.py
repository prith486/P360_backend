import sys, os
sys.path.append(r"c:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend\.env")

from app.core.database import get_session_local
from app.models.assessment import Assessment
from app.models.faculty import Faculty
from app.models.auth_user import AuthUser

SessionLocal = get_session_local()
db = SessionLocal()

# Which user IDs created assessments?
results = db.query(Assessment.created_by).distinct().all()
print(f"Distinct created_by values in assessments table:")
for (uid,) in results:
    print(f"  {uid}")
    # Check if faculty record exists with this user_id
    fac = db.query(Faculty).filter(Faculty.user_id == uid).first()
    if fac:
        auth = db.query(AuthUser).filter(AuthUser.id == uid).first()
        name = auth.full_name if auth else "No AuthUser"
        print(f"    -> Faculty: {fac.employee_id} | Name: {name}")
    else:
        print(f"    -> No Faculty record found for this user_id")

db.close()
