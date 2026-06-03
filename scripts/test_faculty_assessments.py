import requests

BASE = "http://localhost:8003/api/v1"

def test():
    # Login as Dr. Priya (faculty 1)
    r1 = requests.post(f"{BASE}/auth/login", json={"email": "drpriya@placement360.dev", "password": "Faculty@123"})
    if r1.status_code != 200:
        print(f"Login failed for drpriya: {r1.text[:200]}")
        return
    token1 = r1.json()["access_token"]
    print(f"Logged in as: {r1.json()['name']}")

    # Login as Ravi (faculty 2)
    r2 = requests.post(f"{BASE}/auth/login", json={"email": "ravi@placement360.dev", "password": "Faculty@123"})
    if r2.status_code != 200:
        print(f"Login failed for ravi: {r2.text[:200]}")
        return
    token2 = r2.json()["access_token"]
    print(f"Logged in as: {r2.json()['name']}")

    # Fetch assessments for Dr. Priya
    res1 = requests.get(f"{BASE}/assessments/", headers={"Authorization": f"Bearer {token1}"})
    print(f"\nDrPriya - GET /assessments/: {res1.status_code}")
    if res1.status_code == 200:
        data1 = res1.json()["data"]
        print(f"  Total assessments visible: {len(data1)}")
        mine = [a for a in data1 if a.get("is_mine")]
        others = [a for a in data1 if not a.get("is_mine")]
        print(f"  Mine (is_mine=True): {len(mine)}")
        print(f"  Others (is_mine=False): {len(others)}")
        if others:
            sample = others[0]
            print(f"  Sample other assessment:")
            print(f"    title: {sample['title']}")
            print(f"    created_by_name: {sample.get('created_by_name')}")
            print(f"    created_by_employee_id: {sample.get('created_by_employee_id')}")
            print(f"    created_by_department: {sample.get('created_by_department')}")
    else:
        print(f"  Error: {res1.text[:200]}")

    # Fetch assessments for Ravi
    res2 = requests.get(f"{BASE}/assessments/", headers={"Authorization": f"Bearer {token2}"})
    print(f"\nRavi - GET /assessments/: {res2.status_code}")
    if res2.status_code == 200:
        data2 = res2.json()["data"]
        print(f"  Total assessments visible: {len(data2)}")
        mine2 = [a for a in data2 if a.get("is_mine")]
        others2 = [a for a in data2 if not a.get("is_mine")]
        print(f"  Mine (is_mine=True): {len(mine2)}")
        print(f"  Others (is_mine=False): {len(others2)}")
    else:
        print(f"  Error: {res2.text[:200]}")

    # Test mine_only filter
    res3 = requests.get(f"{BASE}/assessments/?mine_only=true", headers={"Authorization": f"Bearer {token1}"})
    print(f"\nDrPriya - mine_only=true: {res3.status_code}")
    if res3.status_code == 200:
        print(f"  Count: {len(res3.json()['data'])}")

if __name__ == "__main__":
    test()
