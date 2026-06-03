
import sys
import os
from uuid import UUID

# Add the project root to sys.path
sys.path.append(os.getcwd())

try:
    from sqlalchemy import inspect
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID
    from app.models.user import User
    from app.models.student import Student
    from app.models.faculty import Faculty
    from app.models.question import Question
    from app.models.assessment import Assessment
    from app.models.assessment_question import AssessmentQuestion
    from app.models.submission import Submission
    from app.models.assessment_attempt import AssessmentAttempt
    from app.models.admin_activity import AdminActivityLog
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def verify_model(model_class):
    print(f"\n--- Verifying Model: {model_class.__name__} ---")
    mapper = inspect(model_class)
    
    # Check Primary Key
    pk_column = mapper.primary_key[0]
    pk_type = pk_column.type
    print(f"Primary Key: {pk_column.name} ({pk_type})")
    
    if not isinstance(pk_type, PG_UUID):
        print(f"  x ERROR: Primary Key {pk_column.name} is NOT a UUID!")
    else:
        print(f"  w SUCCESS: Primary Key is UUID")

    # Check Columns
    for column in mapper.columns:
        col_type = column.type
        
        # If it's a foreign key
        if column.foreign_keys:
            for fk in column.foreign_keys:
                print(f"Foreign Key: {column.name} -> {fk.target_fullname} ({col_type})")
                if not isinstance(col_type, PG_UUID):
                    print(f"  x ERROR: Foreign Key {column.name} is NOT a UUID type!")
                else:
                    print(f"  w SUCCESS: Foreign Key {column.name} is UUID")
        
        # Optional: Check if other ID-like fields are UUIDs (e.g. user_id in logs)
        elif column.name.endswith('_id') or column.name == 'id':
             if not isinstance(col_type, PG_UUID):
                  print(f"Column: {column.name} ({col_type}) - Check if this should be UUID")

models_to_test = [
    User, Student, Faculty, Question, Assessment, 
    AssessmentQuestion, Submission, AssessmentAttempt, AdminActivityLog
]

for model in models_to_test:
    try:
        verify_model(model)
    except Exception as e:
        print(f"Error inspecting {model.__name__}: {e}")

print("\nVerification Complete.")
