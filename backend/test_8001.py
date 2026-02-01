"""Test on port 8001."""
import requests

BASE = "http://localhost:8001/api/v1"

# Login
r = requests.post(f"{BASE}/auth/login", json={
    "email": "apitest@test.com",
    "password": "TestPassword123!"
})
print(f"Login: {r.status_code}")
if r.status_code != 200:
    print(f"Login error: {r.text}")
    exit(1)

token = r.json()["access_token"]
print(f"Token: {token[:40]}...")

# Create task
headers = {"Authorization": f"Bearer {token}"}
r = requests.post(f"{BASE}/tasks", json={"title": "Test on 8001"}, headers=headers)
print(f"\nCreate task: {r.status_code}")
print(f"Response: {r.text}")
