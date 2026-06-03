
import requests
import time
import json

BASE = "http://localhost:8000/api/v1"

try:
    # Try login
    login_res = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"}, timeout=5)
    if login_res.status_code == 200:
        st = login_res.json()["access_token"]
        sh = {"Authorization": f"Bearer {st}"}

        # Test GitHub
        print("Linking GitHub (torvalds)...")
        r = requests.post(f"{BASE}/students/me/external-platform", headers=sh, json={"platform": "github", "username": "torvalds"}, timeout=5)
        print(f"Link GitHub: {r.status_code}")
        
        print("Waiting 10s for GitHub fetch (GitHub API is slower)...")
        time.sleep(10)
        
        me = requests.get(f"{BASE}/students/me", headers=sh, timeout=5).json()
        gh = me.get("github_stats") or (me.get("data") or {}).get("github_stats")
        
        # If still null, try platform_stats
        if not gh:
            gh = me.get("platform_stats", {}).get("github")

        print(f"GitHub stats present: {gh is not None and bool(gh)}")
        if gh:
            print(f"  contributions: {gh.get('total_contributions_6m') or gh.get('total_contributions')}")
            print(f"  heatmap days: {len(gh.get('contribution_heatmap') or gh.get('heatmap') or [])}")
            print(f"  languages count: {len(gh.get('languages') or gh.get('top_languages') or [])}")
        else:
            print(f"  Full Reponse: {json.dumps(me, indent=2)}")
    else:
        print(f"Login failed: {login_res.status_code}")
except Exception as e:
    print(f"Error: {e}")
