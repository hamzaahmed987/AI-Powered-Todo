"""Add recurring tasks and notifications fields.

Migration: 002_add_recurring_and_notifications
Date: 2024-01-26
Description: Adds support for recurring tasks, tags, categories, and notifications.
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine


def upgrade(engine: Engine) -> None:
    """Apply migration - add new columns to tasks table."""
    with engine.connect() as conn:
        # Add tags column (PostgreSQL array)
        conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS tags VARCHAR(50)[] DEFAULT '{}' NOT NULL
        """))

        # Add category column
        conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS category VARCHAR(100)
        """))

        # Add recurring task columns
        conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE NOT NULL
        """))

        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recurrencepattern') THEN
                    CREATE TYPE recurrencepattern AS ENUM (
                        'none', 'daily', 'weekly', 'biweekly', 'monthly', 'yearly'
                    );
                END IF;
            END
            $$;
        """))

        conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS recurrence_pattern recurrencepattern DEFAULT 'none' NOT NULL
        """))

        conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS recurrence_end_date TIMESTAMP WITH TIME ZONE
        """))

        conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL
        """))

        # Add notification columns
        conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS reminder_enabled BOOLEAN DEFAULT FALSE NOT NULL
        """))

        conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS reminder_time TIMESTAMP WITH TIME ZONE
        """))

        conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE NOT NULL
        """))

        # Add indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_task_category ON tasks(category)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_task_is_recurring ON tasks(is_recurring)
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_task_reminder ON tasks(reminder_enabled, reminder_time)
        """))

        conn.commit()
        print("Migration 002: Added recurring tasks and notifications fields")


def downgrade(engine: Engine) -> None:
    """Revert migration - remove added columns."""
    with engine.connect() as conn:
        # Remove indexes
        conn.execute(text("DROP INDEX IF EXISTS idx_task_category"))
        conn.execute(text("DROP INDEX IF EXISTS idx_task_is_recurring"))
        conn.execute(text("DROP INDEX IF EXISTS idx_task_reminder"))

        # Remove columns
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS tags"))
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS category"))
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS is_recurring"))
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS recurrence_pattern"))
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS recurrence_end_date"))
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS parent_task_id"))
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS reminder_enabled"))
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS reminder_time"))
        conn.execute(text("ALTER TABLE tasks DROP COLUMN IF EXISTS reminder_sent"))

        # Drop enum type
        conn.execute(text("DROP TYPE IF EXISTS recurrencepattern"))

        conn.commit()
        print("Migration 002: Reverted recurring tasks and notifications fields")


if __name__ == "__main__":
    import os
    from sqlalchemy import create_engine

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        engine = create_engine(database_url)
        upgrade(engine)
    else:
        print("DATABASE_URL not set")
