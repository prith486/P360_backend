import requests
url = "http://127.0.0.1:8003/api/v1/auth/login"
data = {"email": "priya.p@placement360.dev", "password": "Student@123"}
res = requests.post(url, json=data)
print(f"Status: {res.status_code}")
print(f"Body: {res.text}")
