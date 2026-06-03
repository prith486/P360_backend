"""
Student profile API endpoints.
"""

import logging
from typing import Optional, List, Any
import uuid
from decimal import Decimal
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.database import get_db, SessionLocal
from app.core.config import settings
import requests
from sqlalchemy import or_, func, desc as sa_desc
from app.core.cache import get_cached, set_cached
from app.api.deps import (
    get_current_active_user,
    get_current_student,
    get_current_faculty,
    get_current_admin
)
from app.models.student import Student
from app.models.auth_user import AuthUser
from app.models.faculty import Faculty
from app.models.assessment_attempt import AssessmentAttempt
from app.models.assessment import Assessment
from app.models.enums import BranchType, AcademicYear
from app.schemas.student import (
    StudentRead,
    StudentDetailedRead,
    StudentUpdate,
    ExternalPlatformConnect,
    ExternalPlatformDisconnect,
    StudentCreate,
    StudentLeaderboard,
    StudentFacultyUpdate,
    StudentCreateByFaculty
)
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    DatabaseException
)
from app.core.error_codes import ErrorCode
from app.crud import student as crud_student

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# NEW PROFILE ENDPOINTS
# ============================================================================

def calculate_profile_completion(student: Student) -> float:
    """
    Calculate profile completion percentage based on weighted criteria.
    """
    total_points = 100
    earned_points = 0
    
    # Basic information (20 points)
    if student.cgpa is not None and student.cgpa > 0:
        earned_points += 10
    if student.current_year:
        earned_points += 10
    
    # External platforms (30 points - max 6 platforms at 5 points each)
    platforms_connected = 0
    if student.leetcode_username:
        platforms_connected += 1
    if student.codeforces_username:
        platforms_connected += 1
    if student.codechef_username:
        platforms_connected += 1
    if student.geeksforgeeks_username:
        platforms_connected += 1
    if student.hackerrank_username:
        platforms_connected += 1
    if student.github_username:
        platforms_connected += 1
    
    earned_points += min(platforms_connected * 5, 30)
    
    # Skills (20 points - max 5 skills at 4 points each)
    if student.skills:
        skills_count = len(student.skills)
        earned_points += min(skills_count * 4, 20)
    
    # Resume (15 points)
    if student.resume_url:
        earned_points += 15
    
    # Portfolio and LinkedIn (15 points total)
    if student.portfolio_url:
        earned_points += 7
    if student.linkedin_url:
        earned_points += 8
    
    # Calculate percentage
    completion_percent = (earned_points / total_points) * 100
    
    return round(completion_percent, 2)


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

def fetch_and_save_platform_stats(platform: str, username: str, student_id: uuid.UUID):
    """
    Background Task: Fetch stats from platform and save to DB.
    Always creates its own SessionLocal to avoid thread safety issues.
    """
    from app.core.database import SessionLocal
    from app.models.student import Student
    from app.integrations import leetcode, codeforces, codechef, github, hackerrank

    db = SessionLocal()
    try:
        stats = None
        if platform == "leetcode":
            stats = leetcode.get_user_stats(username)
        elif platform == "codeforces":
            stats = codeforces.get_user_stats(username)
        elif platform == "codechef":
            stats = codechef.get_user_stats(username)
        elif platform == "github":
            stats = github.get_user_stats(username)
        elif platform == "hackerrank":
            stats = hackerrank.get_user_stats(username)

        if stats:
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                # Update the specific JSONB column
                setattr(student, f"{platform}_stats", stats)
                
                # SPECIAL SYNC: Update top-level solved columns if LeetCode
                if platform == "leetcode":
                    student.total_problems_solved = stats.get("total_solved", 0)
                    student.easy_solved = stats.get("easy_solved", 0)
                    student.medium_solved = stats.get("medium_solved", 0)
                    student.hard_solved = stats.get("hard_solved", 0)
                
                student.profile_completion_percent = calculate_profile_completion(student)
                db.commit()
                from app.services.analytics_service import calculate_readiness_score
                calculate_readiness_score(student, db, save=True)
                logger.info(f"Background: Successfully updated {platform} stats for student {student_id}")

    except Exception as exc:
        db.rollback()
        logger.error(f"Background: Failed to fetch {platform} stats for {student_id}: {exc}")
    finally:
        db.close()


# ============================================================================
# PROFILE ENDPOINTS
# ============================================================================


def validate_platform_username(platform: str, username: str) -> bool:
    """Validate username format for specific platforms."""
    import re
    
    validation_rules = {
        "leetcode": {
            "pattern": r"^[a-zA-Z0-9_-]{3,30}$",
            "message": "LeetCode username must be 3-30 characters (alphanumeric, underscore, hyphen)"
        },
        "codeforces": {
            "pattern": r"^[a-zA-Z0-9_]{3,24}$",
            "message": "Codeforces username must be 3-24 characters (alphanumeric, underscore)"
        },
        "github": {
            "pattern": r"^[a-zA-Z0-9]([a-zA-Z0-9-]){0,38}$",
            "message": "GitHub username must be 1-39 characters (alphanumeric, hyphen)"
        },
        "codechef": {
            "pattern": r"^[a-zA-Z][a-zA-Z0-9_]{4,14}$",
            "message": "CodeChef username must be 5-15 characters starting with a letter"
        }
    }
    
    if platform in validation_rules:
        rule = validation_rules[platform]
        if not re.match(rule["pattern"], username):
            raise ValidationException(
                message=f"Invalid {platform} username format",
                status_code=400 # ErrorCode.INVALID_FORMAT passed in exception if updated
            )
            
    return True


@router.get(
    "/me",
    response_model=StudentRead,
    summary="Get current student profile"
)
@router.get("/me/", response_model=StudentRead, include_in_schema=False)
def get_my_profile(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get current authenticated student's profile.
    Enriches DB fields with user identity from auth.users.
    """
    if not current_student:
        raise NotFoundException(message="Student Profile not found")

    user = current_student.user

    # Split full_name into first / last
    name_parts = (user.full_name or "").split() if user else []
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[-1] if len(name_parts) > 1 else ""

    # Pull role from Supabase app_metadata (set at registration)
    role = "student"
    if user and getattr(user, "raw_app_meta_data", None):
        role = user.raw_app_meta_data.get("role", "student")

    # Build enriched response dict — SQLAlchemy model fields + injected user fields
    response_data = {
        # --- identity from auth.users ---
        "first_name": first_name,
        "last_name": last_name,
        "email": user.email if user else None,
        "role": role,
        "phone_number": getattr(user, "phone", None),
        "avatar_url": None,
        "year": current_student.current_year.value if hasattr(current_student.current_year, "value") else str(current_student.current_year),
        # --- all student table fields ---
        "id": current_student.id,
        "user_id": current_student.user_id,
        "roll_number": current_student.roll_number,
        "branch": current_student.branch,
        "batch_year": current_student.batch_year,
        "current_year": current_student.current_year,
        "cgpa": current_student.cgpa,
        "readiness_score": current_student.readiness_score,
        "last_assessment_date": current_student.last_assessment_date,
        "leetcode_username": current_student.leetcode_username,
        "codeforces_username": current_student.codeforces_username,
        "codechef_username": current_student.codechef_username,
        "geeksforgeeks_username": current_student.geeksforgeeks_username,
        "hackerrank_username": current_student.hackerrank_username,
        "github_username": current_student.github_username,
        "leetcode_stats": current_student.leetcode_stats or {},
        "codeforces_stats": current_student.codeforces_stats or {},
        "codechef_stats": current_student.codechef_stats or {},
        "geeksforgeeks_stats": current_student.geeksforgeeks_stats or {},
        "hackerrank_stats": current_student.hackerrank_stats or {},
        "github_stats": current_student.github_stats or {},
        # Aggregated platform_stats view (convenience field for frontend)
        "platform_stats": {
            "github": current_student.github_stats or {},
            "leetcode": current_student.leetcode_stats or {},
            "codeforces": current_student.codeforces_stats or {},
            "codechef": current_student.codechef_stats or {},
            "hackerrank": current_student.hackerrank_stats or {},
        },
        "resume_url": current_student.resume_url,
        "portfolio_url": current_student.portfolio_url,
        "linkedin_url": current_student.linkedin_url,
        "skills": current_student.skills or [],
        "preferred_roles": current_student.preferred_roles or [],
        "languages_known": current_student.languages_known or [],
        "section": current_student.section,
        "expected_ctc_min": current_student.expected_ctc_min,
        "expected_ctc_max": current_student.expected_ctc_max,
        "total_problems_solved": current_student.total_problems_solved or 0,
        "easy_solved": current_student.easy_solved or 0,
        "medium_solved": current_student.medium_solved or 0,
        "hard_solved": current_student.hard_solved or 0,
        "profile_completion_percent": current_student.profile_completion_percent,
        "created_at": current_student.created_at,
        "updated_at": current_student.updated_at,
    }

    return response_data


@router.get(
    "/me/detailed",
    response_model=StudentDetailedRead,
    summary="Get detailed student profile"
)
def get_my_detailed_profile(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get detailed profile including user info.
    """
    # Assuming current_student.user is loaded or lazy loaded
    user = current_student.user
    
    # Construct response
    profile_data = {
        **current_student.__dict__,
        "email": user.email if user else None,
        "full_name": user.full_name if user else None,
        "phone": user.phone_number if hasattr(user, 'phone_number') else None, # Check attribute
        "email_verified": True, # Supabase handles this, maybe check user.email_confirmed_at
        "account_status": "active" # Placeholder
    }
    return profile_data


@router.patch(
    "/me",
    response_model=StudentRead,
    summary="Update current student profile"
)
def update_my_profile(
    profile_update: StudentUpdate,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
) -> Any:
    """Update current student's profile."""
    
    update_data = profile_update.model_dump(exclude_unset=True)
    
    # Validation logic
    if "expected_ctc_min" in update_data and "expected_ctc_max" in update_data:
        if update_data["expected_ctc_min"] > update_data["expected_ctc_max"]:
            raise ValidationException(message="Minimum CTC cannot exceed maximum CTC")
            
    # Apply updates
    updated_fields = []
    try:
        for field, value in update_data.items():
            if hasattr(current_student, field):
                old_value = getattr(current_student, field)
                setattr(current_student, field, value)
                if old_value != value:
                    updated_fields.append(field)
        
        # Recalculate completion
        current_student.profile_completion_percent = calculate_profile_completion(current_student)
        
        db.commit()
        from app.services.analytics_service import calculate_readiness_score
        calculate_readiness_score(current_student, db, save=True)
        db.refresh(current_student)
        
    except IntegrityError:
        db.rollback()
        raise DatabaseException(message="Database constraint violation")
    except Exception as e:
        db.rollback()
        logger.error(f"Update failed: {e}")
        raise HTTPException(status_code=500, detail="Update failed")
        
    return current_student


@router.post(
    "/me/external-platform",
    summary="Connect external platform"
)
def connect_external_platform(
    platform_data: ExternalPlatformConnect,
    background_tasks: BackgroundTasks,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
) -> Any:
    """Connect external platform username and trigger fetch."""
    platform = platform_data.platform.lower().strip()
    username = platform_data.username.strip()
    
    # Update username on student row
    field_name = f"{platform}_username"
    if hasattr(current_student, field_name):
        setattr(current_student, field_name, username)
        db.commit()
    else:
        raise ValidationException(message=f"Platform {platform} is not supported")

    # Trigger background fetch & save
    background_tasks.add_task(fetch_and_save_platform_stats, platform, username, current_student.id)

    return {
        "success": True,
        "message": f"Successfully connected {platform}. Statistics will be updated in the background.",
        "username": username
    }


@router.delete(
    "/me/external-platform",
    response_model=StudentRead,
    summary="Disconnect external platform"
)
def disconnect_external_platform(
    platform_data: ExternalPlatformDisconnect,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
) -> Any:
    """Disconnect external platform."""
    field_name = f"{platform_data.platform}_username"
    stats_field = f"{platform_data.platform}_stats"
    
    if hasattr(current_student, field_name):
        setattr(current_student, field_name, None)
        if hasattr(current_student, stats_field):
            setattr(current_student, stats_field, {})
            
        current_student.profile_completion_percent = calculate_profile_completion(current_student)
        db.commit()
        db.refresh(current_student)
    
    return current_student


@router.get(
    "/me/completion",
    summary="Get profile completion breakdown"
)
def get_profile_completion_breakdown(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
) -> dict:
    """Get detailed profile completion breakdown."""
    student = current_student
    
    # Calculate breakdown
    breakdown = {
        "overall_completion": float(student.profile_completion_percent),
        "categories": {
            "basic_info": {"score": 0, "max_score": 20, "completed": [], "missing": []},
            "external_platforms": {"score": 0, "max_score": 30, "completed": [], "missing": []},
            "skills": {"score": 0, "max_score": 20, "completed": [], "missing": []},
            "resume": {"score": 0, "max_score": 15, "completed": [], "missing": []},
            "professional_links": {"score": 0, "max_score": 15, "completed": [], "missing": []}
        },
        "recommendations": []
    }
    
    # Basic info
    if student.cgpa and student.cgpa > 0:
        breakdown["categories"]["basic_info"]["score"] += 10
        breakdown["categories"]["basic_info"]["completed"].append("CGPA")
    else:
        breakdown["categories"]["basic_info"]["missing"].append("CGPA")
        breakdown["recommendations"].append("Add CGPA")
        
    if student.current_year:
        breakdown["categories"]["basic_info"]["score"] += 10
        breakdown["categories"]["basic_info"]["completed"].append("Current Year")
        
    # Platforms
    platforms = ["leetcode", "codeforces", "codechef", "geeksforgeeks", "hackerrank", "github"]
    connected = 0
    for p in platforms:
        if getattr(student, f"{p}_username", None):
            connected += 1
            breakdown["categories"]["external_platforms"]["completed"].append(p)
        else:
            breakdown["categories"]["external_platforms"]["missing"].append(p)
    
    breakdown["categories"]["external_platforms"]["score"] = min(connected * 5, 30)
    if connected < 2:
        breakdown["recommendations"].append("Connect at least 2 platforms")
        
    # Skills
    skills_count = len(student.skills) if student.skills else 0
    breakdown["categories"]["skills"]["score"] = min(skills_count * 4, 20)
    if skills_count < 5:
        breakdown["recommendations"].append("Add more skills")
        
    # Resume
    if student.resume_url:
        breakdown["categories"]["resume"]["score"] = 15
        breakdown["categories"]["resume"]["completed"].append("Resume")
    else:
        breakdown["recommendations"].append("Upload resume")
        
    # Links
    if student.portfolio_url:
        breakdown["categories"]["professional_links"]["score"] += 7
        breakdown["categories"]["professional_links"]["completed"].append("Portfolio")
    if student.linkedin_url:
        breakdown["categories"]["professional_links"]["score"] += 8
        breakdown["categories"]["professional_links"]["completed"].append("LinkedIn")
        
    return breakdown


# ============================================================================
# PLATFORM STATS REFRESH ENDPOINT
# ============================================================================

@router.post(
    "/me/refresh-stats",
    summary="Trigger a manual refresh of external platform stats"
)
def refresh_my_stats(
    background_tasks: BackgroundTasks,
    current_student: Student = Depends(get_current_student),
) -> dict:
    """
    Triggers background refreshes for all linked platforms for the current student.
    """
    platforms = ["leetcode", "codeforces", "codechef", "hackerrank", "github"]
    triggered = []

    for platform in platforms:
        username = getattr(current_student, f"{platform}_username", None)
        if username:
            background_tasks.add_task(fetch_and_save_platform_stats, platform, username, current_student.id)
            triggered.append(platform)

    return {
        "success": True,
        "message": f"Triggered refresh for: {', '.join(triggered)}" if triggered else "No platforms linked.",
        "triggered": triggered
    }


# ============================================================================
# LEGACY / ADMIN ENDPOINTS (Preserved)
# ============================================================================

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_student_by_faculty(
    student_in: StudentCreateByFaculty,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    """
    Create a new student profile (Faculty).
    Registers user in Supabase Auth first, then creates DB record.
    """
    # 1. Check if roll number already exists
    existing = crud_student.get_student_by_roll_number(db, student_in.roll_number)
    if existing:
        raise HTTPException(status_code=400, detail="Student with this roll number already exists")

    # 2. Create Supabase Auth User via Admin API
    SERVICE_KEY = settings.SUPABASE_SERVICE_ROLE_KEY
    SUPABASE_URL = settings.SUPABASE_URL
    TEMP_PASSWORD = "TempPass@123"

    res = requests.post(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "email": student_in.email,
            "password": TEMP_PASSWORD,
            "email_confirm": True,
            "user_metadata": {
                "full_name": student_in.full_name,
                "role": "student"
            }
        }
    )

    if res.status_code == 422:
        raise HTTPException(status_code=409, detail="Email already registered in system")
    if res.status_code not in [200, 201]:
        logger.error(f"Auth creation failed: {res.text}")
        raise HTTPException(status_code=500, detail="Failed to create auth user for student")

    auth_user_data = res.json()
    new_user_id = auth_user_data["id"]

    # 3. Create student profile in DB
    try:
        new_student = Student(
            user_id=new_user_id,
            roll_number=student_in.roll_number,
            branch=student_in.branch,
            batch_year=student_in.batch_year,
            current_year=student_in.current_year,
            cgpa=student_in.cgpa,
            section=student_in.section,
            readiness_score=Decimal("0.0"),
            profile_completion_percent=Decimal("15.00")
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        
        # Enrich for response
        response_data = {
            "id": str(new_student.id),
            "roll_number": new_student.roll_number,
            "email": student_in.email,
            "full_name": student_in.full_name,
            "branch": new_student.branch
        }

        return {
            "success": True,
            "data": response_data,
            "message": f"Student created. Temporary password: {TEMP_PASSWORD}"
        }

    except Exception as e:
        db.rollback()
        # Cleanup: delete the auth user if DB insert fails
        requests.delete(
            f"{SUPABASE_URL}/auth/v1/admin/users/{new_user_id}",
            headers={"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}"}
        )
        logger.error(f"Student creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database error while creating profile: {str(e)}")

@router.get("/dashboard", response_model=dict)
@router.get("/dashboard/", response_model=dict, include_in_schema=False)
async def get_student_dashboard(
    submissionsPage: int = 1,
    submissionsLimit: int = 5,
    assessmentsPage: int = 1,
    assessmentsLimit: int = 5,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    """Get complete student dashboard data."""
    cache_key = f"student_dashboard:{current_student.id}:{submissionsPage}:{submissionsLimit}:{assessmentsPage}:{assessmentsLimit}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        from app.models.question import Question
        from app.models.submission import Submission
        from app.models.assessment import Assessment
        
        # 1. Profile Info
        user = current_student.user
        user_meta = user.raw_user_meta_data if user and hasattr(user, 'raw_user_meta_data') and user.raw_user_meta_data else {}
        full_name = user_meta.get("full_name", "")
        if not full_name and user and user.full_name:
            full_name = user.full_name
        name_parts = full_name.rsplit(" ", 1) if full_name else []
        profile = {
            "id": str(current_student.id),
            "firstName": name_parts[0] if name_parts else "",
            "lastName": name_parts[1] if len(name_parts) > 1 else "",
            "email": user.email if user else "",
            "rollNumber": current_student.roll_number,
            "branch": current_student.branch.value if hasattr(current_student.branch, 'value') else str(current_student.branch),
            "year": current_student.current_year.value if hasattr(current_student.current_year, 'value') else str(current_student.current_year),
            "readinessScore": float(current_student.readiness_score or 0),
            "avatarUrl": None,
            "github_username": current_student.github_username,
            "leetcode_username": current_student.leetcode_username,
            "codeforces_username": current_student.codeforces_username,
            "codechef_username": current_student.codechef_username,
            "hackerrank_username": current_student.hackerrank_username,
            "github_stats": current_student.github_stats or {},
            "leetcode_stats": current_student.leetcode_stats or {},
            "codeforces_stats": current_student.codeforces_stats or {},
            "codechef_stats": current_student.codechef_stats or {},
            "hackerrank_stats": current_student.hackerrank_stats or {},
            "profileCompletion": current_student.profile_completion_percent or 0
        }
        
        # 2. Stats
        total_problems = db.query(Question).count()
        stats = {
            "problemsSolved": current_student.total_problems_solved or 0,
            "totalProblems": total_problems,
            "totalScore": int(current_student.readiness_score or 0),
            "currentStreak": 0,   # TODO: implement streak tracking
            "longestStreak": 0,   # TODO: implement streak tracking
            "rank": 0,            # TODO: calculate from leaderboard
            "branchRank": 0       # TODO: calculate from branch leaderboard
        }
        
        # 3. Recent Submissions with Question details
        subs_query = db.query(Submission, Question).join(Question, Submission.question_id == Question.id)\
            .filter(Submission.student_id == current_student.id)\
            .order_by(Submission.created_at.desc())
        
        # Apply pagination
        total_subs = subs_query.count()
        subs_result = subs_query.offset((submissionsPage - 1) * submissionsLimit).limit(submissionsLimit).all()
        
        recent_submissions = []
        for sub, quest in subs_result:
            recent_submissions.append({
                "id": str(sub.id),
                "description": quest.title,
                "problemTitle": quest.title,  # Keep for compatibility
                "difficulty": quest.difficulty.value if hasattr(quest.difficulty, 'value') else str(quest.difficulty),
                "status": sub.status.value if hasattr(sub.status, 'value') else str(sub.status),
                "language": sub.language,
                "score": sub.score,
                "xp": 10 if sub.score > 0 else 0, # Placeholder XP
                "time": sub.created_at.strftime("%b %d, %H:%M") if sub.created_at else "Now",
                "submittedAt": sub.created_at.isoformat() if sub.created_at else None
            })
        
        # 4. Upcoming Assessments
        # Fetch active assessments
        now = datetime.now(timezone.utc)
        up_assessments = db.query(Assessment)\
            .filter(Assessment.end_time > now)\
            .order_by(Assessment.start_time.asc())\
            .limit(assessmentsLimit)\
            .all()
        
        # Refined Creator Resolution
        creator_uids = [exam.created_by for exam in up_assessments]
        creator_names = {}
        if creator_uids:
            creators = db.query(AuthUser).filter(AuthUser.id.in_(creator_uids)).all()
            creator_names = {str(c.id): c.full_name for c in creators}

        upcoming_assessments = []
        for exam in up_assessments:
            upcoming_assessments.append({
                "id": str(exam.id),
                "title": exam.title,
                "startTime": exam.start_time.isoformat() if exam.start_time else None,
                "endTime": exam.end_time.isoformat() if exam.end_time else None,
                "duration": exam.duration_minutes,
                "totalQuestions": exam.total_questions,
                "type": exam.assessment_type.value if hasattr(exam.assessment_type, 'value') else str(exam.assessment_type),
                "created_by_name": creator_names.get(str(exam.created_by), "Faculty")
            })
            
        result = {
            "success": True,
            "data": {
                "profile": profile,
                "stats": stats,
                "recentSubmissions": recent_submissions,
                "upcomingAssessments": upcoming_assessments,
                "performanceTrend": [
                    {"month": "Mon", "score": 45}, {"month": "Tue", "score": 52},
                    {"month": "Wed", "score": 48}, {"month": "Thu", "score": 61},
                    {"month": "Fri", "score": 55}, {"month": "Sat", "score": 67},
                    {"month": "Sun", "score": 72}
                ],
                "skillProgress": {
                    "Data Structures": 85, "Algorithms": 72, "Database": 90,
                    "Operating Systems": 65, "Computer Networks": 40
                },
                "submissionsPagination": {
                    "total": total_subs, "page": submissionsPage, "limit": submissionsLimit
                }
            }
        }
        set_cached(cache_key, result, ttl_seconds=300)
        return result
    except Exception as e:
        logger.error(f"Error in student dashboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{student_id}", response_model=StudentDetailedRead)
def get_student_profile_faculty(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    """
    Get detailed student profile (Faculty).
    Includes assessment history and aggregated performance stats.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    user = student.user
    
    # 1. Fetch Assessment Attempts
    attempts_query = db.query(AssessmentAttempt, Assessment.title.label("assessment_title"))\
        .join(Assessment, AssessmentAttempt.assessment_id == Assessment.id)\
        .filter(AssessmentAttempt.student_id == student_id, AssessmentAttempt.is_submitted == True)\
        .order_by(AssessmentAttempt.submitted_at.desc())
    
    # Logic for summary stats
    total_submitted = attempts_query.count()
    avg_score = db.query(func.avg(AssessmentAttempt.percentage))\
        .filter(AssessmentAttempt.student_id == student_id, AssessmentAttempt.is_submitted == True)\
        .scalar() or 0.0

    recent_attempts = attempts_query.limit(5).all()
    
    attempts_data = []
    for att, title in recent_attempts:
        attempts_data.append({
            "assessment_title": title,
            "total_score": float(att.total_score),
            "max_score": att.max_score,
            "percentage": float(att.percentage) if att.percentage else 0.0,
            "is_passed": att.is_passed,
            "submitted_at": att.submitted_at
        })

    # 2. Build Enriched Response
    completion = calculate_profile_completion(student)
    
    # Compute status
    computed_status = "active"
    if student.is_placement_ready:
        computed_status = "placed"
    elif student.readiness_score < 40:
        computed_status = "at_risk"

    name_parts = (user.full_name or "").split()
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[-1] if len(name_parts) > 1 else ""

    response_data = {
        # Identity
        "id": student.id,
        "user_id": student.user_id,
        "roll_number": student.roll_number,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": user.full_name,
        "email": user.email,
        "phone_number": getattr(user, "phone", None),
        "branch": student.branch,
        "current_year": student.current_year,
        "batch_year": student.batch_year,
        "section": student.section,
        "cgpa": student.cgpa,
        "readiness_score": student.readiness_score,
        "is_placement_ready": student.is_placement_ready,
        "profile_completion_percent": completion,
        "total_problems_solved": student.total_problems_solved,
        "easy_solved": student.easy_solved,
        "medium_solved": student.medium_solved,
        "hard_solved": student.hard_solved,
        "skills": student.skills or [],
        "preferred_roles": student.preferred_roles or [],
        "languages_known": student.languages_known or [],
        "linkedin_url": student.linkedin_url,
        "github_url": student.github_url,
        "portfolio_url": student.portfolio_url,
        # Platforms
        "leetcode_username": student.leetcode_username,
        "leetcode_stats": student.leetcode_stats or {},
        "github_username": student.github_username,
        "github_stats": student.github_stats or {},
        "codeforces_username": student.codeforces_username,
        "codeforces_stats": student.codeforces_stats or {},
        "codechef_username": student.codechef_username,
        "codechef_stats": student.codechef_stats or {},
        "hackerrank_username": student.hackerrank_username,
        "hackerrank_stats": student.hackerrank_stats or {},
        "status": computed_status,
        # Assessment Performance
        "assessment_attempts": attempts_data,
        "assessment_count": total_submitted,
        "average_score": round(float(avg_score), 2)
    }

    return response_data

# Endpoints re-ordered to avoid path shadowing
@router.get("/me/results")
async def get_my_results(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    # Simplified imports - relying on top-level imports in this module

    attempts = (
        db.query(AssessmentAttempt)
        .filter(AssessmentAttempt.student_id == current_student.id, AssessmentAttempt.is_submitted == True)
        .order_by(AssessmentAttempt.submitted_at.desc())
        .all()
    )

    results = []
    for attempt in attempts:
        assessment = db.query(Assessment).filter(Assessment.id == attempt.assessment_id).first()
        if not assessment: continue

        results.append({
            "attempt_id": str(attempt.id),
            "assessment_title": assessment.title,
            "assessment_type": assessment.assessment_type,
            "total_score": float(attempt.total_score or 0),
            "max_score": float(attempt.max_score or assessment.total_marks or 100),
            "percentage": float(attempt.percentage or 0),
            "is_passed": bool(attempt.is_passed),
            "time_taken_minutes": attempt.time_taken_minutes,
            "tab_switch_count": attempt.tab_switch_count or 0,
            "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
            "attempt_number": attempt.attempt_number or 1,
        })

    summary = {
        "total_attempts": len(results),
        "passed": len([r for r in results if r["is_passed"]]),
        "failed": len([r for r in results if not r["is_passed"]]),
        "average_percentage": round(sum(r["percentage"] for r in results)/len(results), 2) if results else 0,
        "pass_rate": round(len([r for r in results if r["is_passed"]])/len(results)*100, 2) if results else 0,
    }

    return {"success": True, "data": {"results": results, "summary": summary}}

@router.get("/{student_id}/results")
async def get_student_results_by_faculty(
    student_id: str,
    current_faculty=Depends(get_current_faculty),
    db: Session = Depends(get_db)
):
    # Simplified imports
    from uuid import UUID

    attempts = (
        db.query(AssessmentAttempt)
        .filter(
            AssessmentAttempt.student_id == student_id,
            AssessmentAttempt.is_submitted == True,
        )
        .order_by(AssessmentAttempt.submitted_at.desc())
        .all()
    )

    results = []
    for attempt in attempts:
        assessment = db.query(Assessment).filter(
            Assessment.id == attempt.assessment_id
        ).first()
        if not assessment:
            continue

        results.append({
            "attempt_id": str(attempt.id),
            "assessment_id": str(attempt.assessment_id),
            "assessment_title": assessment.title,
            "assessment_type": assessment.assessment_type,
            "total_score": float(attempt.total_score or 0),
            "max_score": float(attempt.max_score or assessment.total_marks or 100),
            "percentage": float(attempt.percentage or 0),
            "is_passed": bool(attempt.is_passed),
            "time_taken_minutes": attempt.time_taken_minutes,
            "tab_switch_count": attempt.tab_switch_count or 0,
            "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
            "attempt_number": attempt.attempt_number or 1,
        })

    return {
        "success": True,
        "data": {"results": results, "total": len(results)}
    }

@router.put("/{student_id}")
async def update_student_by_faculty(
    student_id: uuid.UUID,
    update_data: StudentFacultyUpdate,
    current_faculty: Faculty = Depends(get_current_faculty),
    db: Session = Depends(get_db)
):
    """
    Update student profile (Faculty).
    Only allows updating non-essential fields (cgpa, status, skills, etc.).
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    data = update_data.model_dump(exclude_unset=True)
    
    try:
        for field, value in data.items():
            if hasattr(student, field):
                setattr(student, field, value)
        
        # Recalculate completion
        student.profile_completion_percent = calculate_profile_completion(student)
        
        db.commit()
        db.refresh(student)
        
        return {
            "success": True,
            "data": student,
            "message": "Student profile updated successfully"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Faculty update failed for {student_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.get("", response_model=dict)
@router.get("/", response_model=dict, include_in_schema=False)
def list_students_enhanced(
    skip: int = 0,
    limit: Optional[int] = None,
    page: Optional[int] = None,
    branch: Optional[BranchType] = None,
    year: Optional[AcademicYear] = None,
    batch_year: Optional[int] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "roll_number",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    """List students with enhanced filtering."""
    query = db.query(Student).join(Student.user)
    
    if branch:
        query = query.filter(Student.branch == branch)
    if year:
        query = query.filter(Student.current_year == year)
    if batch_year:
        query = query.filter(Student.batch_year == batch_year)
        
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Student.roll_number.ilike(search_term),
                AuthUser.email.ilike(search_term),
                AuthUser.raw_user_meta_data['full_name'].astext.ilike(search_term)
            )
        )
        
    sort_attr = getattr(Student, sort_by, None)
    if sort_attr is None:
        sort_attr = Student.roll_number
        
    if sort_order.lower() == "desc":
        query = query.order_by(sa_desc(sort_attr))
    else:
        query = query.order_by(sort_attr.asc())
        
    if page is not None:
        pagination_limit = limit or 20
        pagination_skip = (page - 1) * pagination_limit
        total_count = query.count()
        students = query.offset(pagination_skip).limit(pagination_limit).all()
    else:
        students = query.offset(skip).limit(limit or 1000).all()
        total_count = query.count()

    results = []
    for s in students:
        user = s.user
        computed_status = "active"
        if s.is_placement_ready:
            computed_status = "placed"
        elif s.readiness_score < 40:
            computed_status = "at_risk"
            
        if status and computed_status != status:
            continue
            
        name_parts = (user.full_name or "").split()
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[-1] if len(name_parts) > 1 else ""

        results.append({
            "id": s.id,
            "user_id": s.user_id,
            "roll_number": s.roll_number,
            "first_name": first_name,
            "last_name": last_name,
            "email": user.email,
            "branch": s.branch,
            "current_year": s.current_year,
            "batch_year": s.batch_year,
            "cgpa": s.cgpa,
            "readiness_score": s.readiness_score,
            "is_placement_ready": s.is_placement_ready,
            "profile_completion_percent": s.profile_completion_percent,
            "total_problems_solved": s.total_problems_solved or 0,
            "skills": s.skills or [],
            "preferred_roles": s.preferred_roles or [],
            "status": computed_status
        })

    return {
        "success": True,
        "count": len(results),
        "total": total_count,
        "data": results
    }

@router.get("/leaderboard/", response_model=List[StudentLeaderboard])
def get_leaderboard(
    branch: Optional[BranchType] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """Get leaderboard."""
    students = crud_student.get_leaderboard(db, branch, limit)
    result = []
    for idx, s in enumerate(students, start=1):
        name = s.user.full_name if s.user else "Unknown"
        result.append(StudentLeaderboard(
            id=s.id,
            roll_number=s.roll_number,
            full_name=name,
            branch=s.branch,
            total_problems_solved=s.total_problems_solved,
            easy_solved=s.easy_solved,
            medium_solved=s.medium_solved,
            hard_solved=s.hard_solved,
            readiness_score=s.readiness_score,
            rank=idx
        ))
    return result

from app.services.analytics_service import (
    calculate_readiness_score,
    get_score_breakdown,
    get_batch_analytics,
    recalculate_all_students,
)

@router.get("/me/score-breakdown")
async def get_my_score_breakdown(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    breakdown = get_score_breakdown(str(current_student.id), db)
    return {"success": True, "data": breakdown}


@router.post("/me/recalculate-score")
async def recalculate_my_score(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    breakdown = calculate_readiness_score(current_student, db, save=True)
    return {"success": True, "data": breakdown}

@router.get("/analytics/batch")
async def get_batch_analytics_endpoint(
    current_faculty=Depends(get_current_faculty),
    db: Session = Depends(get_db)
):
    data = get_batch_analytics(db)
    return {"success": True, "data": data}

@router.post("/analytics/recalculate-all")
async def recalculate_all_scores(
    current_faculty=Depends(get_current_faculty),
    db: Session = Depends(get_db)
):
    results = recalculate_all_students(db)
    return {"success": True, "data": results}
