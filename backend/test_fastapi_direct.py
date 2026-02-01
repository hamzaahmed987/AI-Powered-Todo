"""Test FastAPI endpoints directly without uvicorn."""
from dotenv import load_dotenv
load_dotenv()

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("Testing with FastAPI TestClient...")

# Register
print("\n[1] Register...")
resp = client.post("/api/v1/auth/register", json={
    "email": "directtest@test.com",
    "password": "TestPassword123!",
    "full_name": "Direct Test"
})
print(f"Status: {resp.status_code}")
if resp.status_code == 409:
    print("User exists, continuing...")
elif resp.status_code != 201:
    print(f"Error: {resp.text}")

# Login
print("\n[2] Login...")
resp = client.post("/api/v1/auth/login", json={
    "email": "directtest@test.com",
    "password": "TestPassword123!"
})
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Error: {resp.text}")
    exit(1)

token = resp.json()["access_token"]
print(f"Token: {token[:30]}...")

# Create task
print("\n[3] Create task...")
resp = client.post("/api/v1/tasks",
    json={"title": "Test from TestClient"},
    headers={"Authorization": f"Bearer {token}"}
)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
