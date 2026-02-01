#!/usr/bin/env python3
"""
Simple server startup script that handles database connection issues.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Override database URL to use SQLite for development
os.environ.setdefault('DATABASE_URL', 'sqlite:///./todo_app_dev.db')

# Set environment to development to handle database issues gracefully
os.environ.setdefault('ENVIRONMENT', 'development')
os.environ.setdefault('DEBUG', 'true')

def main():
    try:
        # Import after setting environment variables
        from app.main import app
        import uvicorn
        
        print("Starting server on http://127.0.0.1:8000")
        print(f"Using database: {os.getenv('DATABASE_URL')}")
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=False,  # Disable reload for cleaner output
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()