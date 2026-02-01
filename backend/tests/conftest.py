"""Pytest configuration and shared fixtures.

Provides test database session, API client, and test data fixtures.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.database.session import Base
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.services.auth_service import hash_password

# Test database URL - use SQLite in-memory for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test.

    Creates fresh tables before each test and drops them after.

    Yields:
        Session: SQLAlchemy session for test database
    """
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = TestingSessionLocal()

    yield db

    # Cleanup
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """FastAPI test client with test database dependency override.

    Yields:
        TestClient: FastAPI test client
    """
    from app.dependencies import get_db

    def override_get_db():
        return test_db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(test_db):
    """Create a test user in the test database.

    Returns:
        User: Test user object with known credentials
            - email: test@example.com
            - password: test_password_123
    """
    user = User(
        id=uuid4(),
        email="test@example.com",
        password_hash=hash_password("test_password_123"),
        full_name="Test User",
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    return user


@pytest.fixture(scope="function")
def test_task(test_db, test_user):
    """Create a test task for the test user.

    Args:
        test_db: Test database session
        test_user: Test user fixture

    Returns:
        Task: Test task object owned by test_user
            - title: "Test Task"
            - status: pending
            - owner_id: test_user.id
    """
    task = Task(
        id=uuid4(),
        owner_id=test_user.id,
        title="Test Task",
        description="This is a test task",
        status=TaskStatus.PENDING,
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)

    return task


@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Generate authentication headers with valid JWT token for test_user.

    Args:
        test_user: Test user fixture

    Returns:
        dict: Headers dict with Authorization bearer token
            Example: {"Authorization": "Bearer eyJhbGc..."}
    """
    from app.services.auth_service import create_access_token

    token, _ = create_access_token(str(test_user.id))

    return {"Authorization": f"Bearer {token}"}
