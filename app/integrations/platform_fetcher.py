"""
Platform fetcher — routes to the correct integration by platform name
and orchestrates concurrent fetching for all platforms linked to a student.

IMPORTANT: Background tasks must create their own DB session.
Never pass a request-scoped session into a background task.
"""

import asyncio
import logging
from typing import Optional

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


# ── Single-platform router ────────────────────────────────────────────────────

async def fetch_single_platform(platform: str, username: str) -> Optional[dict]:
    """
    Route to the correct integration module by platform name and return stats.

    platform values: "github", "leetcode", "codeforces", "codechef", "hackerrank"
    Returns a stats dict on success, or None on failure.
    """
    platform = platform.lower().strip()

    if platform == "github":
        from app.integrations.github import fetch_github_stats
        return await fetch_github_stats(username)

    elif platform == "leetcode":
        from app.integrations.leetcode import fetch_leetcode_stats
        return await fetch_leetcode_stats(username)

    elif platform == "codeforces":
        from app.integrations.codeforces import fetch_codeforces_stats
        return await fetch_codeforces_stats(username)

    elif platform == "codechef":
        from app.integrations.codechef import fetch_codechef_stats
        return await fetch_codechef_stats(username)

    elif platform == "hackerrank":
        from app.integrations.hackerrank import fetch_hackerrank_stats
        return await fetch_hackerrank_stats(username)

    else:
        logger.warning("fetch_single_platform: unknown platform '%s'", platform)
        return None


# ── All-platforms concurrent fetcher ─────────────────────────────────────────

async def fetch_all_platforms(student_id: str, db: Session) -> dict:
    """
    Fetch all linked external platforms concurrently for a student.

    - Uses asyncio.gather to run fetches in parallel.
    - Only fetches platforms where the username field is not None/empty.
    - Updates the corresponding *_stats JSONB columns on the Student row.
    - The caller is responsible for providing a session that it owns
      (typically a freshly created SessionLocal() for background tasks).

    Returns a dict {platform: stats_or_None} for every platform that was fetched.
    """
    from app.models.student import Student

    try:
        from uuid import UUID
        student = db.query(Student).filter(
            Student.id == UUID(str(student_id))
        ).first()
    except Exception as exc:
        logger.error("fetch_all_platforms: could not load student %s: %s", student_id, exc)
        return {}

    if not student:
        logger.warning("fetch_all_platforms: student %s not found", student_id)
        return {}

    # Map platform names → (username, stats_column)
    platform_map = {
        "github": (student.github_username, "github_stats"),
        "leetcode": (student.leetcode_username, "leetcode_stats"),
        "codeforces": (student.codeforces_username, "codeforces_stats"),
        "codechef": (student.codechef_username, "codechef_stats"),
        "hackerrank": (student.hackerrank_username, "hackerrank_stats"),
    }

    # Only fetch linked platforms
    platforms_to_fetch = {
        platform: username
        for platform, (username, _) in platform_map.items()
        if username
    }

    if not platforms_to_fetch:
        logger.info("fetch_all_platforms: student %s has no linked platforms", student_id)
        return {}

    logger.info(
        "fetch_all_platforms: fetching %d platform(s) for student %s: %s",
        len(platforms_to_fetch),
        student_id,
        list(platforms_to_fetch.keys()),
    )

    # Run all fetches concurrently
    results_list = await asyncio.gather(
        *[
            fetch_single_platform(platform, username)
            for platform, username in platforms_to_fetch.items()
        ],
        return_exceptions=True,
    )

    results: dict = {}
    for platform, result in zip(platforms_to_fetch.keys(), results_list):
        if isinstance(result, Exception):
            logger.error(
                "fetch_all_platforms: exception for %s/%s: %s",
                platform,
                student_id,
                result,
            )
            results[platform] = None
        else:
            results[platform] = result

    # ── Persist to DB ─────────────────────────────────────────────────────────
    try:
        for platform, stats in results.items():
            if stats is not None:
                _, column_name = platform_map[platform]
                if hasattr(student, column_name):
                    setattr(student, column_name, stats)

        db.commit()
        db.refresh(student)
        logger.info(
            "fetch_all_platforms: successfully updated stats for student %s", student_id
        )
    except Exception as exc:
        db.rollback()
        logger.error(
            "fetch_all_platforms: DB commit failed for student %s: %s",
            student_id,
            exc,
            exc_info=True,
        )

    return results
