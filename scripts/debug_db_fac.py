import os, sys
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_session_local
from app.models.faculty import Faculty

# Use absolute path to .env
env_path = r"c:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend\.env"
load_dotenv(dotenv_path=env_path)

def check():
    SessionLocal = get_session_local()
    db = SessionLocal()
    
    facs = db.query(Faculty).all()
    print(f"Total faculty in DB: {len(facs)}")
    for f in facs:
        print(f"  - ID: {f.id} | UserID: {f.user_id} | EmpID: {f.employee_id} | Dept: {f.department}")
    
    db.close()

if __name__ == "__main__":
    check()
