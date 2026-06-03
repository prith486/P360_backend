"""
APScheduler-based background task scheduler.
Runs a daily refresh of all students' external platform stats at midnight.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.database import SessionLocal
from app.models.student import Student
from app.api.v1.students import fetch_and_save_platform_stats

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def refresh_all_students_stats():
    """Daily job: refresh stats for all students with linked platforms."""
    logger.info("=== [Scheduler] Starting daily platform refresh ===")
    db = SessionLocal()
    try:
        students = db.query(Student).all()
        for student in students:
            platforms = ["leetcode", "codeforces", "codechef", "hackerrank", "github"]
            for p in platforms:
                username = getattr(student, f"{p}_username", None)
                if username:
                    # Execute synchronous fetch for each platform
                    fetch_and_save_platform_stats(p, username, student.id)
    except Exception as exc:
        logger.error(f"[Scheduler] Error during daily refresh: {exc}")
    finally:
        db.close()
    logger.info("=== [Scheduler] Daily platform refresh complete ===")

def recalculate_scores_job():
    from app.core.database import SessionLocal
    from app.services.analytics_service import recalculate_all_students
    db = SessionLocal()
    try:
        results = recalculate_all_students(db)
        print(f"Score recalc: {results['updated']} updated, {results['errors']} errors")
    finally:
        db.close()

def start_scheduler():
    """Start the background scheduler."""
    if not scheduler.running:
        scheduler.add_job(
            refresh_all_students_stats,
            CronTrigger(hour=0, minute=0), # Daily at midnight
            id="refresh_stats_daily",
            replace_existing=True
        )
        scheduler.add_job(
            recalculate_scores_job,
            CronTrigger(hour=1, minute=0),   # 1 AM daily — after platform refresh at midnight
            id="daily_score_recalc",
            replace_existing=True
        )
        scheduler.start()
        logger.info("APScheduler started (BackgroundScheduler) - daily at midnight")

def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped")
