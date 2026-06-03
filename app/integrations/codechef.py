"""
CodeChef profile scraper.
Scrapes https://www.codechef.com/users/{username} via BeautifulSoup.

Each field extraction is wrapped independently so a single parsing failure
does not kill the whole response — partial data is returned if available.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

CODECHEF_PROFILE_URL = "https://www.codechef.com/users/{username}"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _safe_int(value: str | None) -> int | None:
    """Parse an integer from a string, returning None on failure."""
    if value is None:
        return None
    try:
        cleaned = re.sub(r"[^\d]", "", value)
        return int(cleaned) if cleaned else None
    except (ValueError, TypeError):
        return None


async def fetch_codechef_stats(username: str) -> Optional[dict]:
    """
    Scrape CodeChef profile for rating, stars, ranks, and problem stats.

    Returns a partial dict if at least one field is parseable, or None on
    network / HTTP failures.
    """
    url = CODECHEF_PROFILE_URL.format(username=username)

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=_HEADERS)
            resp.raise_for_status()
            html = resp.text

    except httpx.HTTPStatusError as exc:
        logger.error(
            "CodeChef HTTP error for %s: %s %s",
            username,
            exc.response.status_code,
            exc.response.text[:200],
        )
        return None
    except httpx.RequestError as exc:
        logger.error("CodeChef request error for %s: %s", username, exc)
        return None
    except Exception as exc:
        logger.error(
            "Unexpected error fetching CodeChef page for %s: %s",
            username,
            exc,
            exc_info=True,
        )
        return None

    soup = BeautifulSoup(html, "html.parser")
    result: dict = {
        "rating": None,
        "stars": None,
        "global_rank": None,
        "country_rank": None,
        "problems_solved": None,
        "contests_attended": None,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    # ── Rating ────────────────────────────────────────────────────────────────
    try:
        rating_el = soup.find("div", class_="rating-number")
        if not rating_el:
            # Fallback: look for the rating heading section
            rating_el = soup.find("div", class_="rating-header")
        if rating_el:
            result["rating"] = _safe_int(rating_el.get_text(strip=True))
    except Exception as exc:
        logger.debug("CodeChef rating parse error for %s: %s", username, exc)

    # ── Stars ─────────────────────────────────────────────────────────────────
    try:
        star_text = ""
        # Look for star span inside rating header
        star_span = soup.find("span", class_="rating")
        if star_span:
            star_text = star_span.get_text(strip=True)
        else:
            header = soup.find("div", class_="rating-header")
            if header:
                star_text = header.get_text()
        result["stars"] = star_text.count("★")
    except Exception as exc:
        logger.debug("CodeChef stars parse error for %s: %s", username, exc)

    # ── Global rank and Country rank ──────────────────────────────────────────
    try:
        # Typically inside a <div class="rating-ranks"> with two <li> elements
        rank_section = soup.find("div", class_="rating-ranks")
        if rank_section:
            rank_links = rank_section.find_all("a")
            if len(rank_links) >= 1:
                result["global_rank"] = _safe_int(rank_links[0].get_text(strip=True))
            if len(rank_links) >= 2:
                result["country_rank"] = _safe_int(rank_links[1].get_text(strip=True))
        else:
            # Fallback: search for rank data anywhere
            ranks = soup.find_all("a", href=re.compile(r"/ratings/"))
            for a in ranks:
                text = a.get_text(strip=True)
                val = _safe_int(text)
                if val and result["global_rank"] is None:
                    result["global_rank"] = val
    except Exception as exc:
        logger.debug("CodeChef rank parse error for %s: %s", username, exc)

    # ── Problems solved ───────────────────────────────────────────────────────
    try:
        # "Fully Solved" section
        solved_header = soup.find(
            lambda tag: tag.name in ("h3", "h5", "p", "span")
            and "fully solved" in (tag.get_text(strip=True) or "").lower()
        )
        if solved_header:
            # The count is usually the next sibling or in the parent
            parent = solved_header.find_parent()
            if parent:
                text_val = re.search(r"\d+", parent.get_text())
                if text_val:
                    result["problems_solved"] = int(text_val.group())
    except Exception as exc:
        logger.debug("CodeChef problems_solved parse error for %s: %s", username, exc)

    # ── Contests attended ─────────────────────────────────────────────────────
    try:
        # Look for a section mentioning "contest" count
        contest_section = soup.find(
            lambda tag: tag.name in ("section", "div", "article")
            and "contest" in (tag.get("class") or [""])[0].lower()
            if tag.get("class") else False
        )
        if contest_section:
            rows = contest_section.find_all("tr")
            result["contests_attended"] = max(0, len(rows) - 1)  # minus header
    except Exception as exc:
        logger.debug("CodeChef contests_attended parse error for %s: %s", username, exc)

    # Return None only if every field is still None (complete failure)
    non_null = sum(
        1
        for k, v in result.items()
        if k != "fetched_at" and v is not None
    )
    if non_null == 0:
        logger.warning(
            "CodeChef scrape returned no data for %s — page structure may have changed",
            username,
        )
        return None

    return result


import requests as _requests


def get_user_stats(username: str) -> Optional[dict]:
    """Synchronous CodeChef stats fetch using scraping."""
    try:
        url = f"https://www.codechef.com/users/{username}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = _requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        rating = 0
        rating_div = soup.find("div", class_="rating-number")
        if rating_div:
            try:
                rating = int(rating_div.text.strip())
            except Exception:
                pass

        stars = 0
        stars_span = soup.find("span", class_="rating")
        if stars_span:
            stars = stars_span.text.count("★")

        problems_solved = 0
        for section in soup.find_all("section"):
            h3 = section.find("h3")
            if h3 and "Fully Solved" in h3.text:
                problems_container = section.find("div", class_="problems-solved")
                if problems_container:
                    all_links = problems_container.find_all("a")
                    problems_solved = len(all_links)
                break

        return {
            "username": username,
            "rating": rating,
            "stars": stars,
            "problems_solved": problems_solved,
            "profile_url": f"https://www.codechef.com/users/{username}",
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as exc:
        logger.error("Sync CodeChef fetch failed for %s: %s", username, exc)
        return None


# ── legacy class shim ─────────────────────────────────────────────────────────

class CodeChefClient:
    """Legacy shim — prefer fetch_codechef_stats()."""

    async def get_user_stats(self, username: str) -> Optional[dict]:
        return await fetch_codechef_stats(username)


codechef_client = CodeChefClient()
