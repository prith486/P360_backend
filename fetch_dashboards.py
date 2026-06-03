import json
import urllib.request
import base64

BASE_URL = "http://localhost:8000/api/v1"

def mock_login(role):
    url = f"{BASE_URL}/auth/mock-login"
    data = json.dumps({"role": role}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"error": f"Login error: {str(e)}"}

def get_dashboard(path, token):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode('utf-8')}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("--- FETCHING TOKENS ---")
    student_auth = mock_login("student")
    faculty_auth = mock_login("faculty")
    
    if "access_token" in student_auth:
        print("\n--- STUDENT DASHBOARD ---")
        student_dash = get_dashboard("/students/dashboard", student_auth["access_token"])
        print(json.dumps(student_dash, indent=2))
    else:
        print(f"Student Auth Failed: {student_auth}")

    if "access_token" in faculty_auth:
        print("\n--- FACULTY DASHBOARD ---")
        faculty_dash = get_dashboard("/faculty/dashboard", faculty_auth["access_token"])
        print(json.dumps(faculty_dash, indent=2))
    else:
        print(f"Faculty Auth Failed: {faculty_auth}")
