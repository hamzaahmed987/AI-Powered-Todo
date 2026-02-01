import subprocess
import os
import time

# Start the frontend server programmatically
os.chdir("frontend")

# Set environment variable for the backend API
env = os.environ.copy()
env["NEXT_PUBLIC_API_URL"] = "http://localhost:8000/api/v1"

# Start the Next.js development server
process = subprocess.Popen(
    ["npx", "next", "dev", "-p", "3000"],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait a bit for the server to start
time.sleep(5)

# Check if the process is still running
if process.poll() is None:
    print("Frontend server started successfully on port 3000")
    print("You can access the application at http://localhost:3000")
else:
    print("Failed to start frontend server")
    stdout, stderr = process.communicate()
    print(f"STDOUT: {stdout}")
    print(f"STDERR: {stderr}")