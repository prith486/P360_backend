import requests, time, os
from dotenv import load_dotenv

# Path to .env from this script's location
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)

BASE = "http://localhost:8000/api/v1"

def test_platform(headers, platform, username):
    print(f"\n--- Testing {platform.upper()} (username: {username}) ---")
    link = requests.post(f"{BASE}/students/me/external-platform", headers=headers, json={
        "platform": platform,
        "username": username
    })
    if link.status_code != 200:
        print(f"FAILED to link {platform}: {link.status_code}")
        return False
    
    print(f"✓ Linked {platform}. Waiting for background fetch...")
    time.sleep(12) # Wait for scraping/API calls

    me = requests.get(f"{BASE}/students/me", headers=headers).json()
    stats = me.get(f"{platform}_stats")
    
    if stats and len(stats) > 0:
        print(f"✓ {platform.upper()} stats fetched successfully!")
        # Print a few key fields
        if platform == "github":
            print(f"  Contributions: {stats.get('total_contributions')}")
        elif platform == "leetcode":
            print(f"  Solved: {stats.get('total_solved')} (E: {stats.get('easy_solved')}, M: {stats.get('medium_solved')}, H: {stats.get('hard_solved')})")
        elif platform == "codeforces":
            print(f"  Rating: {stats.get('rating')}, Rank: {stats.get('rank')}")
        elif platform == "codechef":
            print(f"  Stars: {stats.get('stars')}, Global Rank: {stats.get('global_rank')}")
        elif platform == "hackerrank":
            print(f"  Level: {stats.get('level')}, Followers: {stats.get('followers_count')}")
        return True
    else:
        print(f"✗ Failed to fetch {platform} stats (empty or None)")
        return False

def run_full_verification():
    print(f"--- Starting Full Platform Verification ---")
    try:
        login_res = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"})
        if login_res.status_code != 200:
            print("FAILED: Mock login failed")
            return
        
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✓ Mock login successful.\n")

        platforms_to_test = [
            ("github", "torvalds"),
            ("leetcode", "neal_wu"),
            ("codeforces", "tourist"),
            ("codechef", "gennady.korotkevich"),
            ("hackerrank", "tourist")
        ]

        results = {}
        for platform, username in platforms_to_test:
            results[platform] = test_platform(headers, platform, username)

        print("\n" + "="*40)
        print("FINAL VERIFICATION SUMMARY")
        print("="*40)
        for platform, success in results.items():
            status = "PASS" if success else "FAIL"
            print(f"{platform:<15}: {status}")
        print("="*40)

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")

if __name__ == "__main__":
    run_full_verification()
