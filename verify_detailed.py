import requests, json

BASE = "http://localhost:8000/api/v1"

def test_student_results():
    print("\n--- TEST 1: STUDENT RESULTS ---")
    st_res = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"}).json()
    st = st_res["access_token"]
    sh = {"Authorization": f"Bearer {st}"}
    
    print(f"Logged in as student: {st_res['user']['email']}")
    
    r = requests.get(f"{BASE}/students/me/results", headers=sh)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

def test_faculty_dashboard():
    print("\n--- TEST 2: FACULTY DASHBOARD ---")
    ft_res = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"}).json()
    ft = ft_res["access_token"]
    fh = {"Authorization": f"Bearer {ft}"}
    
    print(f"Logged in as faculty: {ft_res['user']['email']}")
    
    r = requests.get(f"{BASE}/faculty/dashboard", headers=fh)
    print(f"Status: {r.status_code}")

if __name__ == "__main__":
    try:
        test_student_results()
        test_faculty_dashboard()
    except Exception as e:
        print(f"Connection Error: {e}")
