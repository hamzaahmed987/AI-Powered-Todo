"""Diagnose all issues in one script."""
from dotenv import load_dotenv
load_dotenv()

print("=" * 50)
print("DIAGNOSING YOUR TODO APP")
print("=" * 50)

# Step 1: Test database connection
print("\n[1] Testing database connection...")
try:
    from app.database.session import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("    OK - Database connection works")
except Exception as e:
    print(f"    FAILED - Database connection: {e}")
    exit(1)

# Step 2: Check if tables exist
print("\n[2] Checking if tables exist...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result]
        print(f"    Found tables: {tables}")

        if 'users' not in tables:
            print("    MISSING - 'users' table")
            print("\n    >>> RUN: python recreate_tables.py <<<")
            exit(1)
        else:
            print("    OK - 'users' table exists")

        if 'tasks' not in tables:
            print("    MISSING - 'tasks' table")
            print("\n    >>> RUN: python recreate_tables.py <<<")
            exit(1)
        else:
            print("    OK - 'tasks' table exists")
except Exception as e:
    print(f"    FAILED: {e}")
    exit(1)

# Step 3: Check users table columns
print("\n[3] Checking 'users' table columns...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'users'
        """))
        columns = [row[0] for row in result]
        print(f"    Columns: {columns}")

        required = ['id', 'email', 'password_hash', 'full_name']
        missing = [c for c in required if c not in columns]
        if missing:
            print(f"    MISSING columns: {missing}")
            print("\n    >>> RUN: python recreate_tables.py <<<")
            exit(1)
        print("    OK - All required columns exist")
except Exception as e:
    print(f"    FAILED: {e}")
    exit(1)

# Step 4: Check tasks table columns
print("\n[4] Checking 'tasks' table columns...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'tasks'
        """))
        columns = [row[0] for row in result]
        print(f"    Columns: {columns}")

        required = ['id', 'owner_id', 'title', 'status', 'priority']
        missing = [c for c in required if c not in columns]
        if missing:
            print(f"    MISSING columns: {missing}")
            print("\n    >>> RUN: python recreate_tables.py <<<")
            exit(1)
        print("    OK - All required columns exist")
except Exception as e:
    print(f"    FAILED: {e}")
    exit(1)

# Step 5: Try to create a test user
print("\n[5] Testing user creation...")
try:
    from app.database.session import SessionLocal
    from app.models.user import User
    from app.services.auth_service import hash_password
    from uuid import uuid4

    db = SessionLocal()
    test_email = f"test_{uuid4().hex[:8]}@test.com"

    user = User(
        email=test_email,
        password_hash=hash_password("Test123!"),
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"    OK - User created: {user.id}")

    # Step 6: Try to create a test task
    print("\n[6] Testing task creation...")
    from app.models.task import Task, TaskStatus, TaskPriority

    task = Task(
        owner_id=user.id,
        title="Test Task",
        description="Test description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    print(f"    OK - Task created: {task.id}")

    # Cleanup
    db.delete(task)
    db.delete(user)
    db.commit()
    print("    OK - Cleanup done")

    db.close()
except Exception as e:
    print(f"    FAILED: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 50)
print("ALL TESTS PASSED!")
print("=" * 50)
