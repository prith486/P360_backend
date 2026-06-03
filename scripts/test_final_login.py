import requests
url = "http://localhost:8000/api/v1/auth/login"
data = {"email": "ravi@placement360.dev", "password": "Faculty@123"}
res = requests.post(url, json=data)
print(f"Status: {res.status_code}")
print(f"Body: {res.text}")
