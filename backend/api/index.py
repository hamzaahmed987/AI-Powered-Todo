"""
Vercel serverless function entry point for FastAPI application.

This module imports the FastAPI app from app.main and exports it
for Vercel's serverless environment.
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and export the FastAPI app
from app.main import app

# Export the app for Vercel
__all__ = ["app"]
