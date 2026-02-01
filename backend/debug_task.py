"""Debug task creation API."""
from dotenv import load_dotenv
load_dotenv()

import requests

BASE_URL = "http://localhost:8000/api/v1"

print("=== Debug Task API ===\n")

# First, register/login
print("[1] Login...")
resp = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "apitest@test.com",
    "password": "TestPassword123!"
}, timeout=30)

if resp.status_code != 200:
    print(f"Login failed: {resp.status_code}")
    print(f"Response: {resp.text}")
    # Try to register first
    print("\n[1b] Register first...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "apitest@test.com",
        "password": "TestPassword123!",
        "full_name": "API Test"
    }, timeout=30)
    print(f"Register: {resp.status_code} - {resp.text}")

    # Now login again
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "apitest@test.com",
        "password": "TestPassword123!"
    }, timeout=30)

if resp.status_code != 200:
    print(f"Final login failed: {resp.status_code} - {resp.text}")
    exit(1)

token = resp.json().get("access_token")
print(f"Token OK: {token[:30]}...")

# Create task with full details
print("\n[2] Creating task...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
payload = {"title": "Debug Test Task"}
print(f"URL: {BASE_URL}/tasks")
print(f"Headers: {headers}")
print(f"Payload: {payload}")

resp = requests.post(f"{BASE_URL}/tasks", json=payload, headers=headers, timeout=60)

print(f"\n=== RESPONSE ===")
print(f"Status: {resp.status_code}")
print(f"Headers: {dict(resp.headers)}")
print(f"Body: {resp.text}")

# Also try to list tasks
print("\n[3] List tasks...")
resp = requests.get(f"{BASE_URL}/tasks", headers=headers, timeout=30)
print(f"Status: {resp.status_code}")
print(f"Body: {resp.text[:500] if len(resp.text) > 500 else resp.text}")
