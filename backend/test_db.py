"""Quick database connection test."""
import os
import sys
from dotenv import load_dotenv
load_dotenv()

print("Testing database connection...")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')[:50]}...")

try:
    from sqlalchemy import create_engine, text

    url = os.getenv("DATABASE_URL")
    if not url:
        print("ERROR: DATABASE_URL not set!")
        sys.exit(1)

    print("Creating engine...")
    engine = create_engine(
        url,
        connect_args={"connect_timeout": 5},
        pool_pre_ping=True,
    )

    print("Connecting...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"SUCCESS! Database connected: {result.fetchone()}")

except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
    sys.exit(1)
