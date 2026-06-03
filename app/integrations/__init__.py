from app.integrations.leetcode import leetcode_client
from app.integrations.codeforces import codeforces_client
from app.integrations.hackerrank import hackerrank_client
from app.integrations.codechef import codechef_client
from app.integrations.judge0 import judge0_client

# New module-level fetch functions (preferred over legacy clients)
from app.integrations.github import fetch_github_stats
from app.integrations.leetcode import fetch_leetcode_stats
from app.integrations.codeforces import fetch_codeforces_stats
from app.integrations.codechef import fetch_codechef_stats
from app.integrations.hackerrank import fetch_hackerrank_stats
from app.integrations.platform_fetcher import fetch_single_platform, fetch_all_platforms

__all__ = [
    # Legacy client instances
    "leetcode_client",
    "codeforces_client",
    "hackerrank_client",
    "codechef_client",
    "judge0_client",
    # Module-level fetch functions
    "fetch_github_stats",
    "fetch_leetcode_stats",
    "fetch_codeforces_stats",
    "fetch_codechef_stats",
    "fetch_hackerrank_stats",
    "fetch_single_platform",
    "fetch_all_platforms",
]
