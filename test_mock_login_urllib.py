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
        return {"error": str(e)}

def decode_token(token):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return "Invalid token format"
        payload_b64 = parts[1]
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_json = base64.b64decode(payload_b64).decode("utf-8")
        return json.loads(payload_json)
    except Exception as e:
        return f"Decode error: {e}"

if __name__ == "__main__":
    print("\n--- STUDENT MOCK LOGIN ---")
    student_resp = mock_login("student")
    print(json.dumps(student_resp, indent=2))
    if "access_token" in student_resp:
        print("\nDecoded Student Payload:")
        print(json.dumps(decode_token(student_resp["access_token"]), indent=2))

    print("\n--- FACULTY MOCK LOGIN ---")
    faculty_resp = mock_login("faculty")
    print(json.dumps(faculty_resp, indent=2))
    if "access_token" in faculty_resp:
        print("\nDecoded Faculty Payload:")
        print(json.dumps(decode_token(faculty_resp["access_token"]), indent=2))
