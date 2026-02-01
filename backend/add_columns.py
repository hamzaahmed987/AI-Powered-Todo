"""Quick script to add new columns to the tasks table."""
import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not set!")
    exit(1)

engine = create_engine(DATABASE_URL)

# SQL to add new columns (IF NOT EXISTS for safety)
statements = [
    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS tags TEXT DEFAULT ''",
    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS category VARCHAR(100)",
    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE",
    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(20) DEFAULT 'none'",
    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_end_date TIMESTAMP WITH TIME ZONE",
    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL",
    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_enabled BOOLEAN DEFAULT FALSE",
    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_time TIMESTAMP WITH TIME ZONE",
    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE",
]

print("Adding new columns to tasks table...")
with engine.connect() as conn:
    for sql in statements:
        try:
            conn.execute(text(sql))
            print(f"✓ {sql[:50]}...")
        except Exception as e:
            print(f"✗ {sql[:50]}... - {e}")
    conn.commit()

print("\nDone! Restart your backend.")
