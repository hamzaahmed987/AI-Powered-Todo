"""Start server with full debug output."""
import sys
import os

# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# Load env
from dotenv import load_dotenv
load_dotenv()

print("Starting server with debug...")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')[:50]}...")

import uvicorn
uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="debug")
