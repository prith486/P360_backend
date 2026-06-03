"""
LeetCode GraphQL API integration.
No authentication required for public profile data.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

_QUERY = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    submitStats {
      acSubmissionNum {
        difficulty
        count
      }
    }
    profile {
      ranking
      contributionPoints
      reputation
    }
    submissionCalendar
  }
  userContestRanking(username: $username) {
    rating
    attendedContestsCount
  }
}
"""


async def fetch_leetcode_stats(username: str) -> Optional[dict]:
    """
    Fetch LeetCode statistics for a given username.

    Returns a dict on success, None on any error.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                LEETCODE_GRAPHQL_URL,
                json={"query": _QUERY, "variables": {"username": username}},
                headers={
                    "Content-Type": "application/json",
                    "Referer": "https://leetcode.com",
                },
            )
            resp.raise_for_status()
            payload = resp.json()

        if "errors" in payload:
            logger.error(
                "LeetCode GraphQL errors for %s: %s", username, payload["errors"]
            )
            return None

        data = payload.get("data", {})
        matched_user = data.get("matchedUser")
        if not matched_user:
            logger.warning("LeetCode user not found: %s", username)
            return None

        # ── submission stats ──────────────────────────────────────────────────
        ac_stats: list[dict] = matched_user.get("submitStats", {}).get(
            "acSubmissionNum", []
        )
        solved_map: dict[str, int] = {
            entry["difficulty"]: entry["count"] for entry in ac_stats
        }
        total_solved: int = solved_map.get("All", 0)
        easy_solved: int = solved_map.get("Easy", 0)
        medium_solved: int = solved_map.get("Medium", 0)
        hard_solved: int = solved_map.get("Hard", 0)

        # ── profile ───────────────────────────────────────────────────────────
        profile: dict = matched_user.get("profile", {})
        ranking: int = profile.get("ranking", 0) or 0
        contribution_points: int = profile.get("contributionPoints", 0) or 0

        # ── submission calendar ───────────────────────────────────────────────
        raw_calendar: str | None = matched_user.get("submissionCalendar")
        submission_calendar: dict = {}
        if raw_calendar:
            try:
                submission_calendar = json.loads(raw_calendar)
            except (json.JSONDecodeError, TypeError):
                logger.warning(
                    "Could not parse submissionCalendar for %s", username
                )

        # ── contest ranking ───────────────────────────────────────────────────
        contest_ranking = data.get("userContestRanking")
        contest_rating: float | None = None
        contests_attended: int | None = None
        if contest_ranking:
            r = contest_ranking.get("rating")
            contest_rating = float(r) if r is not None else None
            contests_attended = contest_ranking.get("attendedContestsCount")

        return {
            "total_solved": total_solved,
            "easy_solved": easy_solved,
            "medium_solved": medium_solved,
            "hard_solved": hard_solved,
            "ranking": ranking,
            "contribution_points": contribution_points,
            "submission_calendar": submission_calendar,
            "contest_rating": contest_rating,
            "contests_attended": contests_attended,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    except httpx.HTTPStatusError as exc:
        logger.error(
            "LeetCode HTTP error for %s: %s %s",
            username,
            exc.response.status_code,
            exc.response.text,
        )
        return None
    except httpx.RequestError as exc:
        logger.error("LeetCode request error for %s: %s", username, exc)
        return None
    except Exception as exc:
        logger.error(
            "Unexpected error fetching LeetCode stats for %s: %s",
            username,
            exc,
            exc_info=True,
        )
        return None


import requests as _requests


def get_user_stats(username: str) -> Optional[dict]:
    """Synchronous LeetCode stats fetch using requests."""
    query = """
    query($username: String!) {
      allQuestionsCount {
        difficulty
        count
      }
      matchedUser(username: $username) {
        username
        profile { ranking reputation }
        submitStats {
          acSubmissionNum {
            difficulty
            count
          }
        }
        badges { id displayName }
      }
      userContestRanking(username: $username) {
        attendedContestsCount
        rating
        globalRanking
        topPercentage
      }
      userContestRankingHistory(username: $username) {
        attended
        rating
        contest {
          title
          startTime
        }
      }
    }
    """
    try:
        res = _requests.post(
            LEETCODE_GRAPHQL_URL,
            json={"query": query, "variables": {"username": username}},
            headers={
                "Content-Type": "application/json",
                "Referer": "https://leetcode.com",
                "User-Agent": "Mozilla/5.0"
            },
            timeout=15
        )
        if res.status_code != 200:
            return None

        payload = res.json()
        data = payload.get("data", {})
        user = data.get("matchedUser")
        if not user:
            return None

        # Map solved stats
        stats_map = {s["difficulty"]: s["count"] for s in user.get("submitStats", {}).get("acSubmissionNum", [])}
        
        contest = data.get("userContestRanking") or {}
        history = [h for h in data.get("userContestRankingHistory", []) if h.get("attended")]

        # Map total questions
        all_q_count = data.get("allQuestionsCount", [])
        total_map = {q["difficulty"]: q["count"] for q in all_q_count}

        return {
            "username": username,
            "total_solved": stats_map.get("All", 0),
            "total_questions": total_map.get("All", 0),
            "easy_solved": stats_map.get("Easy", 0),
            "easy_total": total_map.get("Easy", 0),
            "medium_solved": stats_map.get("Medium", 0),
            "medium_total": total_map.get("Medium", 0),
            "hard_solved": stats_map.get("Hard", 0),
            "hard_total": total_map.get("Hard", 0),
            "ranking": user.get("profile", {}).get("ranking", 0),
            "contest_rating": round(contest.get("rating") or 0),
            "contests_attended": contest.get("attendedContestsCount", 0),
            "global_ranking": contest.get("globalRanking", 0),
            "top_percentage": round(contest.get("topPercentage") or 0, 2),
            "badges_count": len(user.get("badges", [])),
            "rating_history": history[-20:] if history else [], # Last 20 attended contests
            "profile_url": f"https://leetcode.com/{username}",
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as exc:
        logger.error("Sync LeetCode fetch failed for %s: %s", username, exc)
        return None


# ── legacy class shim (keeps __init__.py import working) ─────────────────────

class LeetCodeClient:
    """Legacy shim — prefer the module-level fetch_leetcode_stats() function."""

    async def get_user_stats(self, username: str) -> Optional[dict]:
        return await fetch_leetcode_stats(username)


leetcode_client = LeetCodeClient()
