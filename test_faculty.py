import sys
import traceback
from app.core.database import SessionLocal
from app.models.faculty import Faculty
from app.api.v1.faculty import get_faculty_dashboard

db = SessionLocal()
current_faculty = db.query(Faculty).first()
if not current_faculty:
    print("No faculty found.")
    sys.exit(0)

print(f"Testing with faculty: {current_faculty.id}")
try:
    import asyncio
    res = asyncio.run(get_faculty_dashboard(db=db, current_faculty=current_faculty))
    print("Success")
except Exception as e:
    traceback.print_exc()
