import requests
url = "http://127.0.0.1:8003/api/v1/auth/login"
data = {"email": "ravi@placement360.dev", "password": "Faculty@123"}
try:
    res = requests.post(url, json=data)
    print(f"Status: {res.status_code}")
    print(f"Body: {res.text}")
except Exception as e:
    print(f"FAILED: {str(e)}")
