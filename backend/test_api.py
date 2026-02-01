"""Test the actual API endpoints."""
from dotenv import load_dotenv
load_dotenv()

import requests

BASE_URL = "http://localhost:8000/api/v1"

print("Testing API...")

# Login
resp = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "apitest@test.com",
    "password": "TestPassword123!"
}, timeout=30)

if resp.status_code != 200:
    print(f"Login failed: {resp.status_code} - {resp.text}")
    exit(1)

token = resp.json().get("access_token")
print(f"Login OK, token: {token[:30]}...")

# Create task
headers = {"Authorization": f"Bearer {token}"}
resp = requests.post(f"{BASE_URL}/tasks", json={
    "title": "Test Task"
}, headers=headers, timeout=30)

print(f"\nTask creation: {resp.status_code}")
print(f"Response: {resp.text}")
