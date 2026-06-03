"""
GitHub GraphQL API v4 integration.
Fetches contribution stats, language breakdown, and repo metrics
for a given GitHub username using a server-side personal access token.
"""

import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

# ── helpers ──────────────────────────────────────────────────────────────────

def _compute_streaks(daily_data: list[dict]) -> tuple[int, int]:
    """Return (max_streak, current_streak) from a list of {date, count} dicts."""
    max_streak = 0
    current_streak = 0
    temp_streak = 0

    # Sort ascending by date
    sorted_days = sorted(daily_data, key=lambda d: d["date"])

    for day in sorted_days:
        if day["count"] > 0:
            temp_streak += 1
            max_streak = max(max_streak, temp_streak)
        else:
            temp_streak = 0

    # current_streak: count backwards from today
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for day in reversed(sorted_days):
        if day["date"] > today_str:
            continue
        if day["count"] > 0:
            current_streak += 1
        else:
            break

    return max_streak, current_streak


# ── main fetch function ───────────────────────────────────────────────────────

async def fetch_github_stats(github_username: str) -> Optional[dict]:
    """
    Fetch GitHub statistics for a given username via the GraphQL API v4.

    Returns a dict on success, None on any error.
    """
    token = settings.GITHUB_ACCESS_TOKEN
    if not token:
        logger.error("GITHUB_ACCESS_TOKEN is not set — cannot fetch GitHub stats")
        return None

    now = datetime.now(timezone.utc)
    six_months_ago = now - timedelta(days=183)
    from_iso = six_months_ago.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # ── Query 1: Contributions ────────────────────────────────────────────────
    contributions_query = """
    query ContributionStats($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          totalPullRequestContributions
          totalIssueContributions
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    # ── Query 2: Repos + Languages ────────────────────────────────────────────
    repos_query = """
    query RepoStats($login: String!) {
      user(login: $login) {
        repositories(
          first: 10,
          orderBy: { field: STARGAZERS, direction: DESC },
          ownerAffiliations: OWNER,
          privacy: PUBLIC
        ) {
          nodes {
            stargazerCount
            languages(first: 5, orderBy: { field: SIZE, direction: DESC }) {
              edges {
                size
                node { name }
              }
            }
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # ── Execute Query 1 ───────────────────────────────────────────────
            resp1 = await client.post(
                GITHUB_GRAPHQL_URL,
                headers=headers,
                json={
                    "query": contributions_query,
                    "variables": {
                        "login": github_username,
                        "from": from_iso,
                        "to": to_iso,
                    },
                },
            )
            resp1.raise_for_status()
            data1 = resp1.json()

            if "errors" in data1:
                logger.error(
                    "GitHub GraphQL errors (contributions) for %s: %s",
                    github_username,
                    data1["errors"],
                )
                return None

            user_data1 = data1.get("data", {}).get("user")
            if not user_data1:
                logger.warning("GitHub user not found: %s", github_username)
                return None

            collection = user_data1["contributionsCollection"]
            calendar = collection["contributionCalendar"]

            # Flatten daily contribution days
            daily_data: list[dict] = []
            for week in calendar["weeks"]:
                for day in week["contributionDays"]:
                    daily_data.append(
                        {
                            "date": day["date"],
                            "count": day["contributionCount"],
                        }
                    )

            total_contributions_6m: int = calendar["totalContributions"]
            active_days_6m: int = sum(1 for d in daily_data if d["count"] > 0)
            max_streak, current_streak = _compute_streaks(daily_data)

            total_commits: int = collection["totalCommitContributions"]
            total_prs: int = collection["totalPullRequestContributions"]
            total_issues: int = collection["totalIssueContributions"]

            # ── Execute Query 2 ───────────────────────────────────────────────
            resp2 = await client.post(
                GITHUB_GRAPHQL_URL,
                headers=headers,
                json={
                    "query": repos_query,
                    "variables": {"login": github_username},
                },
            )
            resp2.raise_for_status()
            data2 = resp2.json()

            if "errors" in data2:
                logger.error(
                    "GitHub GraphQL errors (repos) for %s: %s",
                    github_username,
                    data2["errors"],
                )
                return None

            repos = (
                data2.get("data", {})
                .get("user", {})
                .get("repositories", {})
                .get("nodes", [])
            )

            # Aggregate stars and languages
            total_stars: int = 0
            lang_bytes: dict[str, int] = {}
            for repo in repos:
                total_stars += repo.get("stargazerCount", 0)
                for edge in repo.get("languages", {}).get("edges", []):
                    name = edge["node"]["name"]
                    size = edge.get("size", 0)
                    lang_bytes[name] = lang_bytes.get(name, 0) + size

            total_lang_bytes = sum(lang_bytes.values())
            languages: list[dict] = []
            if total_lang_bytes > 0:
                sorted_langs = sorted(
                    lang_bytes.items(), key=lambda x: x[1], reverse=True
                )[:5]
                for lang_name, lang_size in sorted_langs:
                    percentage = round((lang_size / total_lang_bytes) * 100, 2)
                    languages.append({"name": lang_name, "percentage": percentage})

        return {
            "total_contributions_6m": total_contributions_6m,
            "active_days_6m": active_days_6m,
            "max_streak": max_streak,
            "current_streak": current_streak,
            "contribution_heatmap": daily_data,
            "languages": languages,
            "stars": total_stars,
            "commits": total_commits,
            "pull_requests": total_prs,
            "issues": total_issues,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    except httpx.HTTPStatusError as exc:
        logger.error(
            "GitHub API HTTP error for %s: %s %s",
            github_username,
            exc.response.status_code,
            exc.response.text,
        )
        return None
    except httpx.RequestError as exc:
        logger.error("GitHub API request error for %s: %s", github_username, exc)
        return None
    except Exception as exc:
        logger.error(
            "Unexpected error fetching GitHub stats for %s: %s",
            github_username,
            exc,
            exc_info=True,
        )
        return None


# ── Sync version for background tasks (no event loop needed) ─────────────────

def get_user_stats(username: str) -> Optional[dict]:
    """
    Synchronous GitHub stats fetch using the requests library.
    Used by fetch_and_save_platform_stats (BackgroundTasks / APScheduler).
    """
    import requests as _requests
    from datetime import datetime, timedelta, timezone as _tz

    token = settings.GITHUB_ACCESS_TOKEN
    if not token:
        logger.error("GITHUB_ACCESS_TOKEN not set")
        return None

    now = datetime.now(_tz.utc)
    six_months_ago = now - timedelta(days=182)

    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        name bio avatarUrl
        followers { totalCount }
        following { totalCount }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes { stargazerCount primaryLanguage { name } }
        }
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          totalPullRequestContributions
          totalIssueContributions
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount } }
          }
        }
      }
    }
    """

    try:
        res = _requests.post(
            GITHUB_GRAPHQL_URL,
            json={
                "query": query,
                "variables": {
                    "username": username,
                    "from": six_months_ago.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "to": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        if res.status_code != 200:
            return None
        data = res.json()
        if "errors" in data:
            return None
        user = data.get("data", {}).get("user")
        if not user:
            return None

        repos = user["repositories"]["nodes"]
        total_stars = sum(r["stargazerCount"] for r in repos)

        languages: dict = {}
        for repo in repos:
            lang = repo.get("primaryLanguage")
            if lang and lang.get("name"):
                languages[lang["name"]] = languages.get(lang["name"], 0) + 1
        total_lang_count = sum(languages.values()) or 1
        top_languages = {
            k: round((v / total_lang_count) * 100, 1)
            for k, v in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
        }

        contrib = user["contributionsCollection"]
        calendar = contrib["contributionCalendar"]

        heatmap = []
        active_days = 0
        for week in calendar["weeks"]:
            for day in week["contributionDays"]:
                count = day["contributionCount"]
                heatmap.append({"date": day["date"], "count": count})
                if count > 0:
                    active_days += 1

        current_streak, max_streak, temp_streak = 0, 0, 0
        for day in reversed(heatmap):
            if day["count"] > 0:
                temp_streak += 1
                if current_streak == 0:
                    current_streak = temp_streak
                max_streak = max(max_streak, temp_streak)
            else:
                if current_streak == 0:
                    temp_streak = 0
                else:
                    break

        return {
            "username": username,
            "name": user.get("name", username),
            "bio": user.get("bio", ""),
            "avatar_url": user.get("avatarUrl", ""),
            "public_repos": user["repositories"]["totalCount"],
            "followers": user["followers"]["totalCount"],
            "following": user["following"]["totalCount"],
            "total_stars": total_stars,
            "total_contributions": calendar["totalContributions"],
            "total_commits": contrib["totalCommitContributions"],
            "total_prs": contrib["totalPullRequestContributions"],
            "total_issues": contrib["totalIssueContributions"],
            "active_days": active_days,
            "current_streak": current_streak,
            "max_streak": max_streak,
            "top_languages": top_languages,
            "heatmap": heatmap,
            "profile_url": f"https://github.com/{username}",
            "fetched_at": now.isoformat(),
        }
    except Exception as exc:
        logger.error("Sync GitHub fetch failed for %s: %s", username, exc)
        return None
