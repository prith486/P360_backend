import requests, json

BASE = "http://localhost:8000/api/v1"

def test_student_results():
    print("\n--- TEST 1: STUDENT RESULTS ---")
    st = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"}).json()["access_token"]
    sh = {"Authorization": f"Bearer {st}"}
    
    r = requests.get(f"{BASE}/students/me/results", headers=sh)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json().get("data", {})
        summary = data.get("summary", {})
        print(f"Summary Cards:")
        print(f"  Total Attempts: {summary.get('total_attempts')}")
        print(f"  Avg Score: {summary.get('average_percentage')}%")
        print(f"  Passed: {summary.get('passed')}")
        print(f"  Pass Rate: {summary.get('pass_rate')}%")
        
        results = data.get("results", [])
        print(f"\nRecent Results (First 3):")
        for res in results[:3]:
            print(f"  - {res['assessment_title']}: {res['percentage']}% ({'Pass' if res['is_passed'] else 'Fail'})")
            if res.get('tab_switch_count', 0) > 0:
                print(f"    [!] WARNING: {res['tab_switch_count']} tab switches detected")
    else:
        print(r.text)

def test_faculty_dashboard():
    print("\n--- TEST 2: FACULTY DASHBOARD ---")
    ft = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"}).json()["access_token"]
    fh = {"Authorization": f"Bearer {ft}"}
    
    r = requests.get(f"{BASE}/faculty/dashboard", headers=fh)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json().get("data", {})
        
        # 1. Stat cards
        stats = data.get("stats", {})
        print(f"Stat Cards:")
        print(f"  Dashboard Stats: {stats}")
        
        ra = data.get("readiness_analytics", {})
        print(f"Readiness Analytics Stats:")
        print(f"  Avg Readiness Score: {ra.get('average_score')}")
        print(f"  Placement Ready: {ra.get('placement_ready_count')}")
        
        # 2. Score distribution
        distribution = ra.get("segmentation", {}).get("distribution", [])
        print(f"\nScore Distribution Chart Data:")
        for d in distribution:
            print(f"  {d['label']}: {d['count']}")
            
        # 3. Student Segmentation
        segments = ra.get("segmentation", {}).get("segments", [])
        print(f"\nStudent Segmentation Pie Data:")
        for s in segments:
            print(f"  {s['id']}: {s['value']} ({s['label']})")
            
        # 4. At-Risk section
        at_risk = data.get("at_risk_students", [])
        print(f"\nAt-Risk Section (First 3):")
        for s in at_risk:
            print(f"  - {s['name']} (Score: {s['readiness_score']})")
            
        # 5. Top Performers
        top = data.get("top_performers", [])
        print(f"\nTop Performers (First 5):")
        for s in top:
            print(f"  - {s['name']} (Score: {s['readiness_score']})")

if __name__ == "__main__":
    try:
        test_student_results()
        test_faculty_dashboard()
    except Exception as e:
        print(f"Connection Error: {e}")
