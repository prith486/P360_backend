from app.core.database import get_db
from app.models.assessment import Assessment
from app.models.assessment_attempt import AssessmentAttempt
from app.models.student import Student
from app.models.assessment_question import AssessmentQuestion
from decimal import Decimal
import uuid
from datetime import datetime
import traceback

db = next(get_db())

a = db.query(Assessment).filter(Assessment.id == uuid.UUID('420d9cf7-2a51-40b1-b15e-277e62c35551')).first()
s = db.query(Student).filter(Student.user_id == uuid.UUID('00000000-0000-0000-0000-000000000001')).first()

print('Assessment:', a.title if a else 'NOT FOUND')
print('Student:', s.roll_number if s else 'NOT FOUND')

if not a or not s:
    exit(1)

cnt = db.query(AssessmentAttempt).filter(
    AssessmentAttempt.assessment_id == a.id,
    AssessmentAttempt.student_id == s.user_id
).count()
print('Previous attempts:', cnt)

try:
    attempt = AssessmentAttempt(
        assessment_id=a.id,
        student_id=s.user_id,
        attempt_number=cnt + 1,
        started_at=datetime.utcnow(),
        is_submitted=False,
        is_graded=False,
        total_score=Decimal("0.0"),
        max_score=a.total_marks,
        tab_switch_count=0,
        questions_attempted=0,
        questions_correct=0
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    print('SUCCESS: Attempt created:', attempt.id)
except Exception as e:
    db.rollback()
    traceback.print_exc()
    print('ERROR:', str(e))
