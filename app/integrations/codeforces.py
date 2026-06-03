"""
Codeforces REST API integration.
No authentication required — uses public API endpoints.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

CF_BASE = "https://codeforces.com/api"


async def fetch_codeforces_stats(handle: str) -> Optional[dict]:
    """
    Fetch Codeforces statistics for a given handle.

    Makes three API calls:
      1. user.info   — rating, maxRating, rank, maxRank
      2. user.rating — contest history (length = contests_attended)
      3. user.status — submissions for problems_solved & submissions_last_30_days

    Returns a dict on success, None on any error.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # ── Call 1: user info ─────────────────────────────────────────────
            r1 = await client.get(
                f"{CF_BASE}/user.info", params={"handles": handle}
            )
            r1.raise_for_status()
            d1 = r1.json()

            if d1.get("status") != "OK" or not d1.get("result"):
                logger.warning("Codeforces user.info failed for %s: %s", handle, d1)
                return None

            info = d1["result"][0]
            rating: int = info.get("rating", 0) or 0
            max_rating: int = info.get("maxRating", 0) or 0
            rank: str = info.get("rank", "unrated") or "unrated"
            max_rank: str = info.get("maxRank", "unrated") or "unrated"

            # ── Call 2: contest history ───────────────────────────────────────
            r2 = await client.get(
                f"{CF_BASE}/user.rating", params={"handle": handle}
            )
            r2.raise_for_status()
            d2 = r2.json()

            contests_attended: int = 0
            if d2.get("status") == "OK":
                contests_attended = len(d2.get("result", []))
            else:
                logger.warning(
                    "Codeforces user.rating failed for %s: %s", handle, d2
                )

            # ── Call 3: user submissions ──────────────────────────────────────
            r3 = await client.get(
                f"{CF_BASE}/user.status",
                params={"handle": handle, "from": 1, "count": 200},
            )
            r3.raise_for_status()
            d3 = r3.json()

            problems_solved: int = 0
            submissions_last_30_days: int = 0
            thirty_days_ago: int = int(time.time()) - 30 * 24 * 3600

            if d3.get("status") == "OK":
                submissions: list[dict] = d3.get("result", [])
                solved_problems: set[str] = set()

                for sub in submissions:
                    # Count unique accepted problems
                    if sub.get("verdict") == "OK":
                        problem = sub.get("problem", {})
                        problem_id = f"{sub.get('contestId', '')}{problem.get('index', '')}"
                        solved_problems.add(problem_id)

                    # Submissions in last 30 days (any verdict)
                    if sub.get("creationTimeSeconds", 0) > thirty_days_ago:
                        submissions_last_30_days += 1

                problems_solved = len(solved_problems)
            else:
                logger.warning(
                    "Codeforces user.status failed for %s: %s", handle, d3
                )

        return {
            "rating": rating,
            "max_rating": max_rating,
            "rank": rank,
            "max_rank": max_rank,
            "problems_solved": problems_solved,
            "contests_attended": contests_attended,
            "submissions_last_30_days": submissions_last_30_days,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    except httpx.HTTPStatusError as exc:
        logger.error(
            "Codeforces HTTP error for %s: %s %s",
            handle,
            exc.response.status_code,
            exc.response.text,
        )
        return None
    except httpx.RequestError as exc:
        logger.error("Codeforces request error for %s: %s", handle, exc)
        return None
    except Exception as exc:
        logger.error(
            "Unexpected error fetching Codeforces stats for %s: %s",
            handle,
            exc,
            exc_info=True,
        )
        return None


import requests as _requests


def get_user_stats(username: str) -> Optional[dict]:
    """Synchronous Codeforces stats fetch using requests."""
    try:
        user_res = _requests.get(f"{CF_BASE}/user.info?handles={username}", timeout=10)
        if user_res.status_code != 200:
            return None
        user_data = user_res.json()
        if user_data.get("status") != "OK":
            return None
        user = user_data["result"][0]

        sub_res = _requests.get(f"{CF_BASE}/user.status?handle={username}&count=2000", timeout=10)
        solved = set()
        if sub_res.status_code == 200 and sub_res.json().get("status") == "OK":
            for sub in sub_res.json()["result"]:
                if sub.get("verdict") == "OK":
                    p = sub.get("problem", {})
                    solved.add(f"{p.get('contestId')}-{p.get('index')}")

        return {
            "username": username,
            "rating": user.get("rating", 0),
            "max_rating": user.get("maxRating", 0),
            "rank": user.get("rank", "unrated"),
            "max_rank": user.get("maxRank", "unrated"),
            "problems_solved": len(solved),
            "contribution": user.get("contribution", 0),
            "profile_url": f"https://codeforces.com/profile/{username}",
            "avatar_url": user.get("titlePhoto", ""),
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as exc:
        logger.error("Sync Codeforces fetch failed for %s: %s", username, exc)
        return None


# ── legacy class shim ─────────────────────────────────────────────────────────

class CodeforcesClient:
    """Legacy shim — prefer the module-level fetch_codeforces_stats() function."""

    async def get_user_info(self, handle: str) -> Optional[dict]:
        return await fetch_codeforces_stats(handle)

    async def get_user_submissions(self, handle: str, count: int = 100) -> Optional[list]:
        return None  # Covered inside fetch_codeforces_stats


codeforces_client = CodeforcesClient()
