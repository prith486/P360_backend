from app.core.database import get_session_local
from app.models.assessment import Assessment

def fix_system_design():
    db = get_session_local()()
    try:
        a = db.query(Assessment).filter(Assessment.title.like('system design%')).first()
        if a:
            print(f"Found: '{a.title}' with status {a.status}")
            a.title = a.title.strip()
            a.status = 'scheduled'
            a.is_published = True
            db.commit()
            print("Successfully updated system design assessment")
        else:
            print("Assessment not found")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_system_design()
