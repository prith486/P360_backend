import os, requests

# Fallback keys from app/core/config.py
SUPABASE_URL = "https://imjmjqboggaoyjdktnau.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imltam1qcWJvZ2dhb3lqZGt0bmF1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDcwODA0NywiZXhwIjoyMDg2Mjg0MDQ3fQ.4xBMTmFDCK3jCLGw2vHCD5sHWuv1HA2VAtHC5g_Mwvw"

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json"
}

# Try to list existing auth users
try:
    res = requests.get(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        headers=headers,
        timeout=10
    )
    print(f"List users status: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        users = data.get('users', [])
        print(f"Total auth users: {len(users)}")
        for u in users[:3]:
            # Use data.get to safely access fields
            print(f"  - {u.get('email')} | role: {u.get('app_metadata', {}).get('role')}")
    else:
        print(f"Error listing users: {res.status_code} - {res.text[:200]}")

    # Check seeded users
    print("\nChecking seeded users...")
    res2 = requests.get(
        f"{SUPABASE_URL}/auth/v1/admin/users/00000000-0000-0000-0000-000000000001",
        headers=headers,
        timeout=10
    )
    print(f"Seeded student (0...01) in auth: {res2.status_code}")

    res3 = requests.get(
        f"{SUPABASE_URL}/auth/v1/admin/users/00000000-0000-0000-0000-000000000002", 
        headers=headers,
        timeout=10
    )
    print(f"Seeded faculty (0...02) in auth: {res3.status_code}")
except Exception as e:
    print(f"Failed to connect: {str(e)}")
