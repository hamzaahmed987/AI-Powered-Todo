import requests

# Test the backend with the correct port (8000)
try:
    print("Testing backend on port 8000...")
    
    # Test the health endpoint
    response = requests.get("http://localhost:8000/health")
    print("Backend health check:")
    print(f"Status Code: {response.status_code}")
    if response.headers.get('content-type', '').startswith('application/json'):
        print(f"Response: {response.json()}")
    else:
        print(f"Response: {response.text[:200]}...")
    print()
    
    # Test the root endpoint
    response = requests.get("http://localhost:8000/")
    print("Backend root endpoint:")
    print(f"Status Code: {response.status_code}")
    if response.headers.get('content-type', '').startswith('application/json'):
        print(f"Response: {response.json()}")
    else:
        print(f"Response: {response.text[:200]}...")
    print()
    
    # Test the docs endpoint
    response = requests.get("http://localhost:8000/docs")
    print("Backend docs endpoint:")
    print(f"Status Code: {response.status_code}")
    print(f"Response length: {len(response.text)} characters")
    print()
    
    # Test the API tasks endpoint
    response = requests.get("http://localhost:8000/api/tasks")
    print("Backend API tasks endpoint:")
    print(f"Status Code: {response.status_code}")
    if response.headers.get('content-type', '').startswith('application/json'):
        print(f"Response: {response.json()}")
    else:
        print(f"Response: {response.text[:200]}...")
        
except requests.exceptions.ConnectionError:
    print("Could not connect to backend server on port 8000")
except Exception as e:
    print(f"Error testing backend: {e}")