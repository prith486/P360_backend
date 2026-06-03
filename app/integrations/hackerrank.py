"""
HackerRank REST API integration.
Uses HackerRank's undocumented-but-stable REST endpoints for profile and badges.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

HR_PROFILE_URL = "https://www.hackerrank.com/rest/contests/master/hackers/{username}/profile"
HR_BADGES_URL = "https://www.hackerrank.com/rest/hackers/{username}/badges"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


async def fetch_hackerrank_stats(username: str) -> Optional[dict]:
    """
    Fetch HackerRank statistics for a given username.

    Makes two requests:
      1. Profile endpoint — level, points, rank, country_rank
      2. Badges endpoint  — list of badges with name and stars

    Returns a dict on success, None on any error.
    """
    try:
        async with httpx.AsyncClient(
            timeout=15.0, follow_redirects=True
        ) as client:
            # ── Request 1: profile ────────────────────────────────────────────
            profile_url = HR_PROFILE_URL.format(username=username)
            r1 = await client.get(profile_url, headers=_HEADERS)
            r1.raise_for_status()
            profile_payload = r1.json()

            profile_data: dict = profile_payload.get("model", {})
            if not profile_data:
                profile_data = profile_payload.get("data", {})

            level: str | None = profile_data.get("level") or None
            points: float | None = None
            raw_points = profile_data.get("current_points") or profile_data.get("score")
            if raw_points is not None:
                try:
                    points = float(raw_points)
                except (ValueError, TypeError):
                    points = None

            rank: int | None = None
            raw_rank = profile_data.get("rank")
            if raw_rank is not None:
                try:
                    rank = int(raw_rank)
                except (ValueError, TypeError):
                    rank = None

            country_rank: int | None = None
            raw_cr = profile_data.get("country_rank")
            if raw_cr is not None:
                try:
                    country_rank = int(raw_cr)
                except (ValueError, TypeError):
                    country_rank = None

            # ── Request 2: badges ──────────────────────────────────────────────
            badges_url = HR_BADGES_URL.format(username=username)
            r2 = await client.get(badges_url, headers=_HEADERS)
            r2.raise_for_status()
            badges_payload = r2.json()

            raw_badges: list = (
                badges_payload.get("models")
                or badges_payload.get("data")
                or []
            )
            badges: list[dict] = []
            for badge in raw_badges:
                name = badge.get("name") or badge.get("badge_name", "")
                stars_raw = badge.get("stars") or badge.get("star_count", 0)
                try:
                    stars = int(stars_raw)
                except (ValueError, TypeError):
                    stars = 0
                if name:
                    badges.append({"name": name, "stars": stars})

        return {
            "level": level,
            "points": points,
            "rank": rank,
            "country_rank": country_rank,
            "badges": badges,
            "badge_count": len(badges),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    except httpx.HTTPStatusError as exc:
        logger.error(
            "HackerRank HTTP error for %s: %s %s",
            username,
            exc.response.status_code,
            exc.response.text[:200],
        )
        return None
    except httpx.RequestError as exc:
        logger.error("HackerRank request error for %s: %s", username, exc)
        return None
    except Exception as exc:
        logger.error(
            "Unexpected error fetching HackerRank stats for %s: %s",
            username,
            exc,
            exc_info=True,
        )
        return None


import requests as _requests


def get_user_stats(username: str) -> Optional[dict]:
    """Synchronous HackerRank stats fetch using requests."""
    try:
        profile_res = _requests.get(
            f"https://www.hackerrank.com/rest/hackers/{username}/profile",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        if profile_res.status_code != 200:
            return None

        profile = profile_res.json().get("model", {})

        badges_res = _requests.get(
            f"https://www.hackerrank.com/rest/hackers/{username}/badges",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        badges = []
        if badges_res.status_code == 200:
            badges = badges_res.json().get("models", [])

        return {
            "username": username,
            "name": profile.get("name", username),
            "level": profile.get("level", 0),
            "points": profile.get("points", 0),
            "rank": profile.get("rank", 0),
            "badges_count": len(badges),
            "badges": [{"name": b.get("badge_name"), "stars": b.get("stars", 0)} for b in badges[:5]],
            "solved_problems": profile.get("solved_problems", 0),
            "profile_url": f"https://www.hackerrank.com/{username}",
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as exc:
        logger.error("Sync HackerRank fetch failed for %s: %s", username, exc)
        return None


# ── legacy class shim ─────────────────────────────────────────────────────────

class HackerRankClient:
    """Legacy shim — prefer fetch_hackerrank_stats()."""

    async def get_user_stats(self, username: str) -> Optional[dict]:
        return await fetch_hackerrank_stats(username)


hackerrank_client = HackerRankClient()
