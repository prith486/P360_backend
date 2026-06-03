"""
Faculty API endpoints.
"""
from typing import List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.cache import get_cached, set_cached
from app.api.deps import get_db, get_current_faculty, get_current_admin, get_current_user_id
from app.crud.faculty import faculty as crud_faculty
from app.schemas.faculty import FacultyCreate, FacultyRead, FacultyUpdate, FacultyDetailed
from app.models.faculty import Faculty

router = APIRouter()


@router.post("", response_model=FacultyRead, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=FacultyRead, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_faculty(
    faculty_in: FacultyCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Create new faculty profile.
    Can be called by the user themselves after signup.
    """
    # Verify user is creating their own profile
    if faculty_in.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create profile for another user"
        )
    
    # Check if profile already exists
    existing = crud_faculty.get_by_user_id(db, user_id=current_user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faculty profile already exists"
        )
    
    # Check if employee_id is already taken
    if crud_faculty.get_by_employee_id(db, employee_id=faculty_in.employee_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already exists"
        )
    
    return crud_faculty.create(db, obj_in=faculty_in)


@router.get("/me")
@router.get("/me/", include_in_schema=False)
async def get_my_profile(
    current_faculty: Faculty = Depends(get_current_faculty),
):
    """Get current authenticated faculty's profile."""
    from app.schemas.user import UserRead
    from app.schemas.faculty import FacultyRead
    
    # Manually build the response to avoid Pydantic ORM auto-serialization issues
    faculty_data = FacultyRead.model_validate(current_faculty, from_attributes=True).model_dump()
    
    # Build user data manually from AuthUser
    auth_user = current_faculty.user
    if auth_user:
        faculty_data["user"] = {
            "id": str(auth_user.id),
            "email": auth_user.email or "",
            "full_name": auth_user.full_name or "",
            "role": auth_user.computed_role if hasattr(auth_user, 'computed_role') else "authenticated",
            "is_active": auth_user.is_active if hasattr(auth_user, 'is_active') else True,
            "created_at": auth_user.created_at.isoformat() if auth_user.created_at else None,
            "updated_at": auth_user.updated_at.isoformat() if auth_user.updated_at else None,
            "email_confirmed_at": auth_user.email_confirmed_at.isoformat() if auth_user.email_confirmed_at else None,
        }
    else:
        faculty_data["user"] = None
    
    return faculty_data


@router.get("", response_model=List[FacultyRead])
@router.get("/", response_model=List[FacultyRead], include_in_schema=False)
async def list_faculty(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Faculty = Depends(get_current_admin)  # Admin only
):
    """List all faculty (admin only)."""
    return crud_faculty.get_multi(db, skip=skip, limit=limit)


@router.get("/dashboard", response_model=dict)
@router.get("/dashboard/", response_model=dict, include_in_schema=False)
async def get_faculty_dashboard(
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    """
    Get complete faculty dashboard data.
    Includes: profile, stats, assessments, student performance
    """
    cache_key = f"faculty_dashboard:{current_faculty.id}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    from app.models.student import Student
    from app.models.assessment import Assessment
    from app.models.assessment_attempt import AssessmentAttempt
    from app.models.question import Question
    from sqlalchemy import func, or_
    from datetime import datetime, timezone
    
    # 1. Profile data
    user_meta = current_faculty.user.raw_user_meta_data if current_faculty.user and hasattr(current_faculty.user, 'raw_user_meta_data') and current_faculty.user.raw_user_meta_data else {}
    full_name = user_meta.get("full_name", "")
    if not full_name and current_faculty.user and current_faculty.user.full_name:
        full_name = current_faculty.user.full_name
    name_parts = full_name.rsplit(" ", 1) if full_name else []
    
    first_name = name_parts[0] if len(name_parts) > 0 else ""
    last_name = name_parts[1] if len(name_parts) > 1 else ""
    
    profile = {
        "id": str(current_faculty.id),
        "firstName": first_name,
        "lastName": last_name,
        "email": current_faculty.user.email if current_faculty.user else "",
        "department": current_faculty.department,
        "designation": current_faculty.designation,
        "avatarUrl": None
    }
    
    # 2. Optimized Stats calculation (Combined into one single round-trip)
    from sqlalchemy import select
    from datetime import datetime as dt
    now_naive = dt.utcnow()

    # We use a single query with subqueries to get all counts at once
    # This reduces network round-trip latency significantly
    stats_query = db.execute(select(
        # total_students
        select(func.count(Student.id)).scalar_subquery(),
        # active_assessments
        select(func.count(Assessment.id)).filter(
            Assessment.created_by == current_faculty.user_id,
            Assessment.is_published == True,
            or_(Assessment.start_time == None, Assessment.start_time <= now_naive),
            or_(Assessment.end_time == None, Assessment.end_time >= now_naive)
        ).scalar_subquery(),
        # total_questions
        select(func.count(Question.id)).filter(
            Question.created_by == current_faculty.user_id
        ).scalar_subquery(),
        # pending_evaluations
        select(func.count(AssessmentAttempt.id)).join(Assessment).filter(
            Assessment.created_by == current_faculty.user_id,
            AssessmentAttempt.is_submitted == True,
            AssessmentAttempt.total_score == None
        ).scalar_subquery()
    )).first()

    stats = {
        "totalStudents": stats_query[0] or 0,
        "activeAssessments": stats_query[1] or 0,
        "totalQuestions": stats_query[2] or 0,
        "pendingEvaluations": stats_query[3] or 0
    }
    
    # 2.5 Fetch upcoming assessments
    upcoming_assessments_query = db.query(Assessment).filter(
        Assessment.created_by == current_faculty.user_id,
        Assessment.start_time > now_naive
    ).order_by(Assessment.start_time.asc()).limit(5).all()
    
    upcoming_assessments = []
    from app.api.v1.assessments import format_assessment_dict
    for a in upcoming_assessments_query:
        item = format_assessment_dict(a)
        item["submissionsCount"] = 0
        item["averageScore"] = 0.0
        item["totalStudents"] = stats["totalStudents"]
        upcoming_assessments.append(item)
    
    # 3. Recent assessments
    recent_assessments_query = db.query(Assessment).filter(
        Assessment.created_by == current_faculty.user_id
    ).order_by(Assessment.created_at.desc()).limit(5).all()
    
    assessment_ids = [a.id for a in recent_assessments_query]
    stats_map = {}
    if assessment_ids:
        assessment_stats = db.query(
            AssessmentAttempt.assessment_id,
            func.count(AssessmentAttempt.id).label('attempt_count'),
            func.avg(AssessmentAttempt.total_score).label('avg_score')
        ).filter(
            AssessmentAttempt.assessment_id.in_(assessment_ids),
            AssessmentAttempt.is_submitted == True
        ).group_by(AssessmentAttempt.assessment_id).all()
        
        stats_map = {
            str(s.assessment_id): {
                'count': s.attempt_count,
                'avg': float(s.avg_score or 0)
            }
            for s in assessment_stats
        }

    from app.api.v1.assessments import format_assessment_dict
    recent_assessments = []
    for assessment in recent_assessments_query:
        # Use centralized formatter for all fields
        item = format_assessment_dict(assessment)
        
        # Add dashboard-specific stats
        a_stats = stats_map.get(str(assessment.id), {'count': 0, 'avg': 0.0})
        item["submissionsCount"] = a_stats['count']
        item["averageScore"] = a_stats['avg']
        item["totalStudents"] = stats["totalStudents"]
        
        # Ensure camelCase for dashboard-specific additions if needed
        # (format_assessment_dict already handles the basics like startTime)
        recent_assessments.append(item)
    
    # 4. Student performance
    # Top performers (top 5 by problems solved)
    top_performers_query = db.query(Student).options(joinedload(Student.user)).order_by(
        Student.total_problems_solved.desc()
    ).limit(5).all()
    
    top_performers = []
    for student in top_performers_query:
        top_performers.append({
            "studentId": str(student.id),
            "name": student.user.full_name or student.user.email if student.user else "Unknown",
            "rollNumber": student.roll_number,
            "score": student.total_problems_solved,
            "avatarUrl": None
        })
    
    # Students needing attention (low readiness score)
    needs_attention_query = db.query(Student).options(joinedload(Student.user)).filter(
        Student.readiness_score < 50
    ).order_by(Student.readiness_score).limit(5).all()
    
    needs_attention = []
    for student in needs_attention_query:
        needs_attention.append({
            "studentId": str(student.id),
            "name": student.user.full_name or student.user.email if student.user else "Unknown",
            "rollNumber": student.roll_number,
            "score": float(student.readiness_score),
            "avatarUrl": None
        })
    
    # Average score across all students
    avg_student_score = db.query(func.avg(Student.readiness_score)).scalar() or 0
    
    student_performance = {
        "averageScore": float(avg_student_score),
        "topPerformers": top_performers,
        "needsAttention": needs_attention
    }
    
    # 5. Recent activity
    recent_activity = []
    # TODO: Implement activity tracking
    
    from app.services.analytics_service import get_batch_analytics
    
    # Batch readiness analytics
    batch_analytics = get_batch_analytics(db)
    
    # At-risk students list (readiness_score < 40)
    from app.models.student import Student
    at_risk_students = (
        db.query(Student)
        .filter(Student.readiness_score < 40)
        .order_by(Student.readiness_score.asc())
        .limit(10)
        .all()
    )
    
    at_risk_list = [
        {
            "id": str(s.id),
            "name": s.user.full_name or s.roll_number if s.user else s.roll_number,
            "roll_number": s.roll_number,
            "branch": s.branch,
            "readiness_score": float(s.readiness_score or 0),
            "cgpa": float(s.cgpa) if s.cgpa else None,
            "total_problems_solved": s.total_problems_solved or 0,
            "profile_completion": float(s.profile_completion_percent or 0),
        }
        for s in at_risk_students
    ]
    
    # Top performers list (readiness_score >= 55, sorted desc)
    top_students = (
        db.query(Student)
        .filter(Student.readiness_score >= 55)
        .order_by(Student.readiness_score.desc())
        .limit(5)
        .all()
    )
    
    top_performers_list = [
        {
            "id": str(s.id),
            "name": s.user.full_name or s.roll_number if s.user else s.roll_number,
            "roll_number": s.roll_number,
            "branch": s.branch,
            "readiness_score": float(s.readiness_score or 0),
            "cgpa": float(s.cgpa) if s.cgpa else None,
        }
        for s in top_students
    ]
    
    # Score distribution for chart (bucket counts)
    all_students = db.query(Student).all()
    score_distribution = [
        {"range": "0-40",   "count": sum(1 for s in all_students if float(s.readiness_score or 0) < 40),    "label": "At Risk"},
        {"range": "40-55",  "count": sum(1 for s in all_students if 40 <= float(s.readiness_score or 0) < 55), "label": "Need Attention"},
        {"range": "55-75",  "count": sum(1 for s in all_students if 55 <= float(s.readiness_score or 0) < 75), "label": "Steady"},
        {"range": "75-100", "count": sum(1 for s in all_students if float(s.readiness_score or 0) >= 75),   "label": "Ready"},
    ]
    
    # Branch performance for chart
    branch_performance = [
        {"branch": str(b).replace("_", " ").title(), "avg_score": avg, "raw_branch": b}
        for b, avg in batch_analytics.get("branch_averages", {}).items()
    ]
    
    result = {
        "success": True,
        "data": {
            "profile": profile,
            "stats": stats,
            "recentAssessments": recent_assessments,
            "upcomingAssessments": upcoming_assessments,
            "studentPerformance": student_performance,
            "performanceTrend": [
                {"month": "Jan", "averageScore": 65, "completionRate": 70},
                {"month": "Feb", "averageScore": 68, "completionRate": 72},
                {"month": "Mar", "averageScore": 75, "completionRate": 75}
            ],
            "skillDistribution": [
                {"name": "Data Structures", "value": 120},
                {"name": "Algorithms", "value": 98},
                {"name": "DBMS", "value": 86}
            ],
            "placementStats": [
                {"company": "Google", "applied": 120, "selected": 5},
                {"company": "Amazon", "applied": 150, "selected": 8},
                {"company": "Microsoft", "applied": 100, "selected": 4},
                {"company": "Meta", "applied": 80, "selected": 3},
            ],
            "atRiskStudents": [],
            "recentActivity": recent_activity,
            "readiness_analytics": {
                "average_score": batch_analytics.get("average_score", 0),
                "total_students": batch_analytics.get("total_students", 0),
                "placement_ready_count": batch_analytics.get("placement_ready_count", 0),
                "at_risk_count": batch_analytics.get("at_risk_count", 0),
                "segmentation": batch_analytics.get("segmentation", {}),
                "branch_averages": batch_analytics.get("branch_averages", {}),
                "score_distribution": score_distribution,
                "branch_performance": branch_performance,
            },
            "at_risk_students": at_risk_list,
            "top_performers": top_performers_list,
        }
    }
    set_cached(cache_key, result, ttl_seconds=300)
    return result


@router.get("/questions")
@router.get("/questions/", include_in_schema=False)
def get_faculty_questions(
    difficulty: Optional[str] = None,
    type: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    """
    Returns questions for the faculty question bank.
    Specifically added to match frontend's expected endpoint /api/v1/faculty/questions.
    """
    from app.api.v1.questions import get_questions
    return get_questions(difficulty, type, tag, db, current_faculty)


@router.post("/questions", response_model=dict)
@router.post("/questions/", response_model=dict, include_in_schema=False)
def create_faculty_question(
    data: Any, # Use Any to avoid circular schema imports or complicated validation here
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    from app.api.v1.questions import create_question
    from app.schemas.question import QuestionCreate
    # Re-validate here if needed, or trust the proxy
    return create_question(QuestionCreate.model_validate(data), db, current_faculty)


@router.put("/questions/{question_id}", response_model=dict)
@router.put("/questions/{question_id}/", response_model=dict, include_in_schema=False)
def update_faculty_question(
    question_id: UUID,
    data: Any,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    from app.api.v1.questions import update_question
    from app.schemas.question import QuestionUpdate
    return update_question(question_id, QuestionUpdate.model_validate(data), db, current_faculty)


@router.delete("/questions/{question_id}", response_model=dict)
@router.delete("/questions/{question_id}/", response_model=dict, include_in_schema=False)
def delete_faculty_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    from app.api.v1.questions import delete_question
    return delete_question(question_id, db, current_faculty)


@router.get("/{faculty_id}", response_model=FacultyDetailed)
async def get_faculty(
    faculty_id: UUID,
    db: Session = Depends(get_db),
    current_user: Faculty = Depends(get_current_faculty)
):
    """Get faculty by ID (faculty and admin only)."""
    faculty = crud_faculty.get_with_user(db, faculty_id=faculty_id)
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty not found"
        )
    return faculty


@router.put("/{faculty_id}", response_model=FacultyRead)
async def update_faculty(
    faculty_id: UUID,
    faculty_in: FacultyUpdate,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    """Update faculty profile."""
    faculty = crud_faculty.get(db, id=faculty_id)
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty not found"
        )
    
    # Only allow updating own profile
    if faculty.id != current_faculty.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update another faculty's profile"
        )
    
    return crud_faculty.update(db, db_obj=faculty, obj_in=faculty_in)
