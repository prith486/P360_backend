import requests
BASE = "http://localhost:8000/api/v1"

def test_assessments():
    # 1. Login
    res = requests.post(f"{BASE}/auth/login", json={
        "email": "priya.p@placement360.dev",
        "password": "Student@123"
    })
    
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
        
    token = res.json()["access_token"]
    
    # 2. Get assessments
    res2 = requests.get(f"{BASE}/assessments/my", headers={
        "Authorization": f"Bearer {token}"
    })
    
    print(f"Assessments status: {res2.status_code}")
    if res2.status_code == 200:
        print(f"Found {len(res2.json()['data'])} assessments")
    else:
        print(res2.text[:500])

if __name__ == "__main__":
    test_assessments()
