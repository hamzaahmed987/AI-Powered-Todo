"""Test task creation directly without HTTP."""
from dotenv import load_dotenv
load_dotenv()

print("Testing task creation directly...")

try:
    from app.database.session import SessionLocal
    from app.models.user import User
    from app.models.task import Task, TaskStatus, TaskPriority
    from app.schemas.task import TaskCreate, TaskResponse
    from app.services.task_service import create_task as create_task_service

    db = SessionLocal()

    # Get or create test user
    from app.services.auth_service import hash_password
    user = db.query(User).filter(User.email == "apitest@test.com").first()
    if not user:
        print("Creating test user...")
        user = User(
            email="apitest@test.com",
            password_hash=hash_password("TestPassword123!"),
            full_name="API Test"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    print(f"User: {user.id}")

    # Create task data (simulating what frontend sends)
    task_data = TaskCreate(
        title="Test Task Direct",
        description="Testing direct creation"
    )
    print(f"TaskCreate: {task_data}")

    # Call the service
    print("\nCalling create_task_service...")
    task = create_task_service(
        db=db,
        user_id=user.id,
        title=task_data.title,
        description=task_data.description,
        deadline=task_data.deadline,
        estimated_duration=task_data.estimated_duration,
        priority=task_data.priority,
    )
    print(f"Task created: {task}")
    print(f"Task ID: {task.id}")

    # Try to convert to response (this is where it might fail)
    print("\nConverting to TaskResponse...")
    response = TaskResponse.model_validate(task)
    print(f"TaskResponse: {response}")

    # Cleanup
    db.delete(task)
    db.commit()
    db.close()

    print("\nSUCCESS!")

except Exception as e:
    import traceback
    print(f"\nFAILED: {e}")
    traceback.print_exc()
