from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.student import Student
from app.models.assessment_attempt import AssessmentAttempt
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
        if b is not None and hasattr(b, "value"):
            b = b.value
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
    }
