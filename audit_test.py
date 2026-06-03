
import requests
import json

BASE = "http://localhost:8000/api/v1"

try:
    login_res = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"})
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.status_code} {login_res.text}")
        exit(1)
    
    ft = login_res.json()["access_token"]
    fh = {"Authorization": f"Bearer {ft}"}

    endpoints = [
        ("GET /students/", f"{BASE}/students/"),
        ("GET /students/me", f"{BASE}/students/me"),  # will 403 with faculty token - expected
    ]

    print("=== LIVE ENDPOINT AUDIT ===")
    for name, url in endpoints:
        r = requests.get(url, headers=fh)
        print(f"{name}: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                print(f"  count: {len(data)}")
                if data: print(f"  first item fields: {list(data[0].keys())[:15]}")
            elif isinstance(data, dict):
                # Try common wrappers
                items = data.get("data", data.get("students", []))
                if isinstance(items, list):
                    print(f"  count: {len(items)}")
                    if items: print(f"  first item fields: {list(items[0].keys())[:15]}")
                else:
                    print(f"  keys: {list(data.keys())}")
        else:
            print(f"  error: {r.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
