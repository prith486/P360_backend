from app.core.database import get_session_local
from app.models.assessment import Assessment
from app.models.question import Question
from app.models.enums import DifficultyLevel, QuestionType
from app.models.assessment_question import AssessmentQuestion
import uuid

def publish_all():
    db = get_session_local()()
    try:
        # Get a sample question if it exists, or create one
        q = db.query(Question).first()
        if not q:
            q = Question(
                title='Sample DSA Problem',
                slug='sample-dsa-' + str(uuid.uuid4())[:4],
                difficulty=DifficultyLevel.MEDIUM,
                question_type=QuestionType.CODING,
                description='Solve this problem.',
                created_by=uuid.UUID('00000000-0000-0000-0000-000000000002'),
                is_public=True,
                is_active=True
            )
            db.add(q)
            db.commit()
            db.refresh(q)

        asss = db.query(Assessment).all()
        for a in asss:
            a.is_published = True
            a.status = 'scheduled'
            a.is_active = True
            
            # Ensure it has at least one question
            count = db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == a.id).count()
            if count == 0:
                aq = AssessmentQuestion(
                    assessment_id=a.id,
                    question_id=q.id,
                    marks=10,
                    question_order=1
                )
                db.add(aq)
                a.total_questions = 1
                a.total_marks = 10
            
        db.commit()
        print(f"Updated {len(asss)} assessments to Scheduled status and ensured they have questions.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    publish_all()
