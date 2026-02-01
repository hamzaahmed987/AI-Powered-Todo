import requests

# Test the backend health endpoint
try:
    response = requests.get("http://localhost:8000/health")
    print("Backend health check:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test the root endpoint
    response = requests.get("http://localhost:8000/")
    print("Backend root endpoint:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test API docs endpoint
    response = requests.get("http://localhost:8000/docs")
    print("Backend docs endpoint:")
    print(f"Status Code: {response.status_code}")
    print(f"Response length: {len(response.text)} characters")
    
except requests.exceptions.ConnectionError:
    print("Could not connect to backend server")
except Exception as e:
    print(f"Error testing backend: {e}")