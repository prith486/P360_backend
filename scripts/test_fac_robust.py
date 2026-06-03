import requests, time

BASE = "http://localhost:8003/api/v1"

def test():
    print("Trying login for Dr. Priya...")
    try:
        r1 = requests.post(f"{BASE}/auth/login", json={"email": "drpriya@placement360.dev", "password": "Faculty@123"}, timeout=30)
        if r1.status_code != 200:
            print(f"Login failed: {r1.status_code} - {r1.text}")
            return
        token = r1.json()["access_token"]
        uid = r1.json()["user_id"]
        print(f"Logged in, UID: {uid}")
        
        print("Fetching assessments...")
        res = requests.get(f"{BASE}/assessments/", headers={"Authorization": f"Bearer {token}"}, timeout=30)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()["data"]
            print(f"Total: {len(data)}")
            if data:
                print(f"Sample is_mine: {data[0].get('is_mine')}")
                print(f"Sample created_by: {data[0].get('created_by')}")
                print(f"Sample created_by_name: {data[0].get('created_by_name')}")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test()
