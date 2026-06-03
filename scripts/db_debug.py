
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import User, Student
from sqlalchemy import inspect
from app.core.database import engine

print("Imported models")

try:
    mapper = inspect(User)
    print(f"User mapper: {mapper}")
    # accessing relationships triggers configuration
    print(f"User relationships: {mapper.relationships.keys()}")
    
    student_mapper = inspect(Student)
    print(f"Student mapper: {student_mapper}")
    print(f"Student columns: {student_mapper.columns.keys()}")
    
except Exception as e:
    print(f"Error inspecting mapper: {e}")
    import traceback
    traceback.print_exc()
