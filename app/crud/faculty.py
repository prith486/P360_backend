"""
CRUD operations for Faculty model.
"""
import uuid
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from app.crud.base import CRUDBase
from app.models.faculty import Faculty
from app.schemas.faculty import FacultyCreate, FacultyUpdate


class CRUDFaculty(CRUDBase[Faculty, FacultyCreate, FacultyUpdate]):
    """CRUD operations for Faculty."""
    
    def get_by_user_id(self, db: Session, *, user_id: uuid.UUID) -> Optional[Faculty]:
        """Get faculty by user_id."""
        return db.query(Faculty).filter(Faculty.user_id == user_id).first()
    
    def get_by_employee_id(self, db: Session, *, employee_id: str) -> Optional[Faculty]:
        """Get faculty by employee_id."""
        return db.query(Faculty).filter(Faculty.employee_id == employee_id).first()
    
    def get_with_user(self, db: Session, *, faculty_id: uuid.UUID) -> Optional[Faculty]:
        """Get faculty with user relationship loaded."""
        return (
            db.query(Faculty)
            .options(joinedload(Faculty.user))
            .filter(Faculty.id == faculty_id)
            .first()
        )


faculty = CRUDFaculty(Faculty)
