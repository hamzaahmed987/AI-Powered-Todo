#!/usr/bin/env python3
"""
Simple test script to start the backend server with minimal configuration.
"""

import os
import sys

# Set environment variables to use SQLite and disable problematic features
os.environ['DATABASE_URL'] = 'sqlite:///./todo_app_test.db'
os.environ['DEBUG'] = 'true'
os.environ['ENVIRONMENT'] = 'development'

# Temporarily remove the problematic import issue by mocking the function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    try:
        # Import the app after setting environment
        from backend.app.simple_main import app
        import uvicorn
        
        print("Starting server on http://127.0.0.1:8000 with SQLite database...")
        print(f"Database URL: {os.environ.get('DATABASE_URL')}")
        
        # Start the server
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()