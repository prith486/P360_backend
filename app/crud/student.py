"""
CRUD operations for Student model.
"""

import uuid
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.models.student import Student
from app.models.auth_user import AuthUser
from app.schemas.student import StudentCreate, StudentUpdate
from app.models.enums import BranchType, AcademicYear


def get_student(db: Session, student_id: uuid.UUID) -> Optional[Student]:
    """Get student by ID with user relationship."""
    stmt = select(Student).where(Student.id == student_id).options(
        joinedload(Student.user)
    )
    result = db.execute(stmt).scalar_one_or_none()
    return result


def get_student_by_roll_number(db: Session, roll_number: str) -> Optional[Student]:
    """Get student by roll number."""
    stmt = select(Student).where(Student.roll_number == roll_number)
    return db.execute(stmt).scalar_one_or_none()


def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    branch: Optional[BranchType] = None,
    current_year: Optional[AcademicYear] = None,
) -> List[Student]:
    """Get list of students with optional filters."""
    stmt = select(Student)
    
    if branch:
        stmt = stmt.where(Student.branch == branch)
    if current_year:
        stmt = stmt.where(Student.current_year == current_year)
    
    stmt = stmt.offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def create_student(db: Session, student: StudentCreate) -> Student:
    """Create new student profile."""
    # Convert Pydantic model to dict, but verify user_id exists?
    # Usually created via API which passes user_id separately?
    # Or passed in `student` schema as `user_id`?
    # Our schema `StudentCreate` has `user_id`.
    
    db_student = Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(
    db: Session, student_id: uuid.UUID, student_update: StudentUpdate
) -> Optional[Student]:
    """Update student profile."""
    db_student = get_student(db, student_id)
    if not db_student:
        return None
    
    update_data = student_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student


def get_leaderboard(
    db: Session,
    branch: Optional[BranchType] = None,
    limit: int = 50
) -> List[Student]:
    """Get top students by problems solved."""
    stmt = select(Student).options(
        joinedload(Student.user)
    ).order_by(
        Student.total_problems_solved.desc(),
        Student.hard_solved.desc(),
        Student.medium_solved.desc()
    )
    
    if branch:
        stmt = stmt.where(Student.branch == branch)
    
    stmt = stmt.limit(limit)
    return list(db.execute(stmt).scalars().all())
