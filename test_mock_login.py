import os
import requests
import base64
import json

BASE_URL = "http://localhost:8000/api/v1"

def mock_login(role):
    url = f"{BASE_URL}/auth/mock-login"
    try:
        resp = requests.post(url, json={"role": role})
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def decode_token(token):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return "Invalid token format"
        
        payload_b64 = parts[1]
        # Padding
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_json = base64.b64decode(payload_b64).decode("utf-8")
        return json.loads(payload_json)
    except Exception as e:
        return f"Decode error: {e}"

if __name__ == "__main__":
    print("--- STUDENT MOCK LOGIN ---")
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
