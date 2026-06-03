Context: Placement360 FastAPI backend. app/services/analytics_service.py has an empty calculate_readiness_score placeholder. The students table has all signal columns. Build the full readiness score engine, wire it to auto-update on relevant events, seed test CGPA data, and expose the score breakdown via API.Task 1 — Seed realistic test dataMost students have cgpa=NULL and total_problems_solved=0. Fix this so the score engine has real data to compute from. Run this SQL directly via SQLAlchemy in a one-time seed script seed_readiness_data.py:pythonfrom app.core.database import SessionLocal
from app.models.student import Student
import random

db = SessionLocal()

seed_data = [
    # (roll_number, cgpa, easy, medium, hard, profile_completion)
    ("CS21B001", 9.6,  80,  90,  30, 85),
    ("CS21B002", 7.8,  60,  45,  10, 60),
    ("CS21B003", 8.2,  40,  30,   5, 55),
    ("IT21B001", 6.9,  20,  10,   0, 40),
    ("CS22B001", 8.9, 200, 180,  60, 75),
    ("TEST4211", 8.5,  30,  20,   2, 45),
]

for roll, cgpa, easy, med, hard, completion in seed_data:
    s = db.query(Student).filter(Student.roll_number == roll).first()
    if s:
        s.cgpa = cgpa
        s.easy_solved = easy
        s.medium_solved = med
        s.hard_solved = hard
        s.total_problems_solved = easy + med + hard
        s.profile_completion_percent = completion

db.commit()
db.close()
print("Seeded.")Run it: venv\Scripts\python seed_readiness_data.pyTask 2 — Implement app/services/analytics_service.pyReplace the entire file with this implementation:pythonfrom typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.student import Student
from app.models.assessment import AssessmentAttempt
import math


# ── Weight constants (must sum to 100) ──────────────────────────────────────
W_CODING    = 35   # External platform coding activity
W_ACADEMIC  = 25   # CGPA
W_ASSESSMENT = 30  # Internal assessment performance
W_PROFILE   = 10   # Profile completeness


def _coding_score(student: Student) -> float:
    """
    Score 0–100 based on problems solved across platforms.
    Weights: Hard=3pts, Medium=2pts, Easy=1pt — capped at a realistic ceiling.
    Also adds bonuses for contest ratings.
    """
    easy   = student.easy_solved   or 0
    medium = student.medium_solved or 0
    hard   = student.hard_solved   or 0

    # Weighted problem score — ceiling = 500 weighted points → maps to 70/100
    weighted = (easy * 1) + (medium * 2) + (hard * 3)
    problem_score = min(weighted / 500 * 70, 70)

    # Contest rating bonuses (up to 30 extra points)
    bonus = 0.0
    lc = student.leetcode_stats or {}
    cf = student.codeforces_stats or {}
    cc = student.codechef_stats or {}

    lc_rating = lc.get("contest_rating", 0) or 0
    cf_rating  = cf.get("rating", 0) or 0
    cc_rating  = cc.get("rating", 0) or 0

    # LeetCode contest: 1500 → 10pts, 2000 → 20pts
    if lc_rating >= 2000:
        bonus += 20
    elif lc_rating >= 1500:
        bonus += 10
    elif lc_rating >= 1200:
        bonus += 5

    # Codeforces: 1200(Pupil)=5, 1600(Specialist)=12, 1900(Expert)=20
    if cf_rating >= 1900:
        bonus += 20
    elif cf_rating >= 1600:
        bonus += 12
    elif cf_rating >= 1200:
        bonus += 5

    # CodeChef stars
    stars = cc.get("stars", 0) or 0
    bonus += min(stars * 2, 10)

    return min(problem_score + bonus, 100)


def _academic_score(student: Student) -> float:
    """
    Score 0–100 based on CGPA on a 10-point scale.
    Below 5.0 → 0. 10.0 → 100.
    Uses a slight curve to reward higher GPAs more.
    """
    cgpa = student.cgpa
    if not cgpa or cgpa < 5.0:
        return 0.0
    # Linear from 5→0 to 10→100
    raw = (float(cgpa) - 5.0) / 5.0 * 100
    return min(max(raw, 0), 100)


def _assessment_score(student: Student, db: Session) -> float:
    """
    Score 0–100 based on average percentage across all submitted attempts.
    Weights recent attempts more heavily (last 5 attempts = 60%, rest = 40%).
    Returns 50 (neutral) if no attempts exist.
    """
    attempts = (
        db.query(AssessmentAttempt)
        .filter(
            AssessmentAttempt.student_id == student.id,
            AssessmentAttempt.is_submitted == True,
            AssessmentAttempt.percentage != None,
        )
        .order_by(AssessmentAttempt.submitted_at.desc())
        .all()
    )

    if not attempts:
        return 50.0  # neutral — no data

    percentages = [float(a.percentage) for a in attempts if a.percentage is not None]
    if not percentages:
        return 50.0

    if len(percentages) <= 5:
        return sum(percentages) / len(percentages)

    # Recent 5 weighted at 60%, rest at 40%
    recent = percentages[:5]
    older  = percentages[5:]
    recent_avg = sum(recent) / len(recent)
    older_avg  = sum(older)  / len(older)
    return recent_avg * 0.6 + older_avg * 0.4


def _profile_score(student: Student) -> float:
    """Score 0–100 directly from profile_completion_percent."""
    return float(student.profile_completion_percent or 0)


def calculate_readiness_score(
    student: Student,
    db: Session,
    save: bool = True
) -> Dict[str, Any]:
    """
    Compute full placement readiness score for a student.
    Returns breakdown dict and optionally saves to DB.
    """
    coding_raw     = _coding_score(student)
    academic_raw   = _academic_score(student)
    assessment_raw = _assessment_score(student, db)
    profile_raw    = _profile_score(student)

    # Weighted total
    total = (
        coding_raw     * (W_CODING    / 100) +
        academic_raw   * (W_ACADEMIC  / 100) +
        assessment_raw * (W_ASSESSMENT / 100) +
        profile_raw    * (W_PROFILE   / 100)
    )
    total = round(min(max(total, 0), 100), 2)

    breakdown = {
        "total": total,
        "components": {
            "coding": {
                "score": round(coding_raw, 2),
                "weight": W_CODING,
                "weighted": round(coding_raw * W_CODING / 100, 2),
            },
            "academic": {
                "score": round(academic_raw, 2),
                "weight": W_ACADEMIC,
                "weighted": round(academic_raw * W_ACADEMIC / 100, 2),
            },
            "assessment": {
                "score": round(assessment_raw, 2),
                "weight": W_ASSESSMENT,
                "weighted": round(assessment_raw * W_ASSESSMENT / 100, 2),
            },
            "profile": {
                "score": round(profile_raw, 2),
                "weight": W_PROFILE,
                "weighted": round(profile_raw * W_PROFILE / 100, 2),
            },
        },
        "signals": {
            "problems_solved": (student.easy_solved or 0) + (student.medium_solved or 0) + (student.hard_solved or 0),
            "easy": student.easy_solved or 0,
            "medium": student.medium_solved or 0,
            "hard": student.hard_solved or 0,
            "cgpa": float(student.cgpa) if student.cgpa else None,
            "profile_completion": float(student.profile_completion_percent or 0),
        }
    }

    # Determine placement status
    if total >= 75:
        status = "placed"
        is_ready = True
    elif total < 40:
        status = "at_risk"
        is_ready = False
    else:
        status = "active"
        is_ready = False

    breakdown["status"] = status

    if save:
        student.readiness_score = total
        student.is_placement_ready = is_ready
        from datetime import datetime, timezone
        student.last_score_update = datetime.now(timezone.utc)
        db.commit()

    return breakdown


def recalculate_all_students(db: Session) -> Dict[str, Any]:
    """Bulk recalculate scores for all students. Used by scheduler and admin."""
    students = db.query(Student).all()
    results = {"updated": 0, "errors": 0, "scores": []}

    for student in students:
        try:
            breakdown = calculate_readiness_score(student, db, save=True)
            results["updated"] += 1
            results["scores"].append({
                "roll_number": student.roll_number,
                "score": breakdown["total"],
                "status": breakdown["status"],
            })
        except Exception as e:
            results["errors"] += 1

    return results


def get_score_breakdown(student_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """Get score breakdown for a student without recalculating."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return None
    return calculate_readiness_score(student, db, save=False)


def get_batch_analytics(db: Session) -> Dict[str, Any]:
    """
    Aggregate analytics for faculty dashboard:
    - Score distribution buckets
    - Branch-wise averages
    - Student segmentation tiers
    - At-risk count
    """
    students = db.query(Student).all()
    if not students:
        return {}

    scores = [float(s.readiness_score or 0) for s in students]

    # Segmentation tiers
    high_performers   = [s for s in students if float(s.readiness_score or 0) >= 75]
    steady_improvers  = [s for s in students if 55 <= float(s.readiness_score or 0) < 75]
    need_attention    = [s for s in students if 40 <= float(s.readiness_score or 0) < 55]
    critical          = [s for s in students if float(s.readiness_score or 0) < 40]

    # Branch breakdown
    branch_map: Dict[str, list] = {}
    for s in students:
        b = s.branch or "unknown"
        branch_map.setdefault(b, []).append(float(s.readiness_score or 0))
    branch_averages = {
        b: round(sum(v) / len(v), 2)
        for b, v in branch_map.items()
    }

    return {
        "total_students": len(students),
        "average_score": round(sum(scores) / len(scores), 2),
        "max_score": round(max(scores), 2),
        "min_score": round(min(scores), 2),
        "placement_ready_count": sum(1 for s in students if s.is_placement_ready),
        "at_risk_count": len(critical),
        "segmentation": {
            "high_performers":  len(high_performers),
            "steady_improvers": len(steady_improvers),
            "need_attention":   len(need_attention),
            "critical":         len(critical),
        },
        "branch_averages": branch_averages,
        "score_distribution": {
            "0_40":   sum(1 for s in scores if s < 40),
            "40_55":  sum(1 for s in scores if 40 <= s < 55),
            "55_75":  sum(1 for s in scores if 55 <= s < 75),
            "75_100": sum(1 for s in scores if s >= 75),
        },
    }Task 3 — Wire score recalculation to eventsIn app/api/v1/students.py, find these 3 endpoints and add score recalculation after the relevant DB commit:After platform stats are saved (in fetch_and_save_platform_stats):
python# Add at the end of the try block, after db.commit():
from app.services.analytics_service import calculate_readiness_score
calculate_readiness_score(student, db, save=True)After PATCH /students/me (profile update):
python# After the existing commit, add:
from app.services.analytics_service import calculate_readiness_score
calculate_readiness_score(current_student, db, save=True)After assessment attempt is submitted — find the submit endpoint in app/api/v1/assessments.py. After is_submitted = True and db.commit(), add:
pythonfrom app.services.analytics_service import calculate_readiness_score
from app.models.student import Student
student = db.query(Student).filter(Student.id == attempt.student_id).first()
if student:
    calculate_readiness_score(student, db, save=True)Task 4 — Add score recalculation to APSchedulerIn app/tasks/scheduler.py, add a second daily job that recalculates all scores after platform stats are refreshed:pythonfrom app.services.analytics_service import recalculate_all_students

def recalculate_scores_job():
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        results = recalculate_all_students(db)
        print(f"Score recalc: {results['updated']} updated, {results['errors']} errors")
    finally:
        db.close()

# Add this job in start_scheduler():
scheduler.add_job(
    recalculate_scores_job,
    CronTrigger(hour=1, minute=0),   # 1 AM daily — after platform refresh at midnight
    id="daily_score_recalc",
    replace_existing=True
)Task 5 — New API endpointsAdd these to app/api/v1/students.py:pythonfrom app.services.analytics_service import (
    calculate_readiness_score,
    get_score_breakdown,
    get_batch_analytics,
    recalculate_all_students,
)

# Student: GET their own score breakdown
@router.get("/me/score-breakdown")
async def get_my_score_breakdown(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    breakdown = get_score_breakdown(str(current_student.id), db)
    return {"success": True, "data": breakdown}

# Student: POST to force recalculate their own score
@router.post("/me/recalculate-score")
async def recalculate_my_score(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    breakdown = calculate_readiness_score(current_student, db, save=True)
    return {"success": True, "data": breakdown}

# Faculty: GET batch analytics
@router.get("/analytics/batch")
async def get_batch_analytics_endpoint(
    current_faculty=Depends(get_current_faculty),
    db: Session = Depends(get_db)
):
    data = get_batch_analytics(db)
    return {"success": True, "data": data}

# Faculty: POST to recalculate scores for all students
@router.post("/analytics/recalculate-all")
async def recalculate_all_scores(
    current_faculty=Depends(get_current_faculty),
    db: Session = Depends(get_db)
):
    results = recalculate_all_students(db)
    return {"success": True, "data": results}Task 6 — Make sure GET /students/me returns updated scoreConfirm readiness_score and is_placement_ready are in the response of GET /students/me. They should already be there — just verify they reflect the new computed value after Task 3 wiring.VerificationRun this after all tasks and paste complete output:pythonimport requests, time

BASE = "http://localhost:8000/api/v1"

# Seed data first
import subprocess
subprocess.run(["venv\\Scripts\\python", "seed_readiness_data.py"])
time.sleep(1)

ft = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"}).json()["access_token"]
st = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"}).json()["access_token"]
fh = {"Authorization": f"Bearer {ft}"}
sh = {"Authorization": f"Bearer {st}"}

# Recalculate all
r1 = requests.post(f"{BASE}/students/analytics/recalculate-all", headers=fh)
print(f"Recalculate all: {r1.status_code}")
data = r1.json().get("data", {})
print(f"  Updated: {data.get('updated')}, Errors: {data.get('errors')}")
for s in data.get("scores", []):
    print(f"  {s['roll_number']}: {s['score']} ({s['status']})")

# Student score breakdown
r2 = requests.get(f"{BASE}/students/me/score-breakdown", headers=sh)
print(f"\nScore breakdown: {r2.status_code}")
bd = r2.json().get("data", {})
print(f"  Total: {bd.get('total')}")
print(f"  Status: {bd.get('status')}")
comps = bd.get("components", {})
for name, c in comps.items():
    print(f"  {name}: {c.get('score')} (weighted: {c.get('weighted')})")

# Batch analytics
r3 = requests.get(f"{BASE}/students/analytics/batch", headers=fh)
print(f"\nBatch analytics: {r3.status_code}")
ba = r3.json().get("data", {})
print(f"  Total students: {ba.get('total_students')}")
print(f"  Average score: {ba.get('average_score')}")
print(f"  Segmentation: {ba.get('segmentation')}")
print(f"  Branch averages: {ba.get('branch_averages')}")
print(f"  At-risk count: {ba.get('at_risk_count')}")Paste complete output.