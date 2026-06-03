import requests

SUPABASE_URL = "https://imjmjqboggaoyjdktnau.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imltam1qcWJvZ2dhb3lqZGt0bmF1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3MDgwNDcsImV4cCI6MjA4NjI4NDA0N30.fXOio3VuTtj4WsptTcWCy1dfaVV0-P5xqRy3tFkpJC4"

headers = {
    "apikey": ANON_KEY
}

try:
    res = requests.get(f"{SUPABASE_URL}/auth/v1/settings", headers=headers)
    print(f"Auth Settings Status: {res.status_code}")
    if res.status_code == 200:
        import json
        settings = res.json()
        print(json.dumps(settings, indent=2))
    else:
        print(f"Error getting settings: {res.status_code} - {res.text}")
except Exception as e:
    print(f"Request failed: {str(e)}")
