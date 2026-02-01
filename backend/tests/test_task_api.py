"""
Integration tests for task endpoints.

Tests task creation, retrieval, update, deletion, and access control.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db
from app.models import User, Task


@pytest.fixture
def client(db_session):
    """Provide a test client with dependency injection."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def db_session():
    """Provide a test database session."""
    from app.database import SessionLocal, Base, engine

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.query(Task).delete()
        db.query(User).delete()
        db.commit()
        db.close()


@pytest.fixture
def auth_token(client):
    """Get an authentication token for a test user."""
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123",
            "full_name": "Test User",
        },
    )
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123",
        },
    )
    return response.json()["access_token"]


@pytest.fixture
def another_auth_token(client):
    """Get an authentication token for a second test user."""
    client.post(
        "/api/auth/register",
        json={
            "email": "another@example.com",
            "password": "SecurePassword456",
            "full_name": "Another User",
        },
    )
    response = client.post(
        "/api/auth/login",
        json={
            "email": "another@example.com",
            "password": "SecurePassword456",
        },
    )
    return response.json()["access_token"]


class TestTaskCreation:
    """Test cases for task creation endpoint."""

    def test_create_task_success(self, client, auth_token):
        """Test successful task creation."""
        response = client.post(
            "/api/tasks/",
            json={
                "title": "Complete project",
                "description": "Finish the project implementation",
                "priority": "high",
                "deadline": "2024-12-31T23:59:59Z",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Complete project"
        assert data["description"] == "Finish the project implementation"
        assert data["priority"] == "high"
        assert data["status"] == "pending"
        assert "id" in data

    def test_create_task_minimal(self, client, auth_token):
        """Test task creation with only required field."""
        response = client.post(
            "/api/tasks/",
            json={"title": "Simple task"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Simple task"
        assert data["status"] == "pending"
        assert data["priority"] == "medium"

    def test_create_task_no_title(self, client, auth_token):
        """Test task creation fails without title."""
        response = client.post(
            "/api/tasks/",
            json={"description": "Missing title"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 422

    def test_create_task_no_auth(self, client):
        """Test task creation fails without authentication."""
        response = client.post(
            "/api/tasks/",
            json={"title": "Unauthorized task"},
        )

        assert response.status_code == 403


class TestTaskRetrieval:
    """Test cases for task retrieval endpoints."""

    @pytest.fixture
    def sample_task(self, client, auth_token):
        """Create a sample task for retrieval tests."""
        response = client.post(
            "/api/tasks/",
            json={
                "title": "Sample task",
                "description": "For testing retrieval",
                "priority": "medium",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        return response.json()

    def test_list_tasks_success(self, client, auth_token, sample_task):
        """Test successful task list retrieval."""
        response = client.get(
            "/api/tasks/",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == "Sample task"

    def test_list_tasks_no_auth(self, client):
        """Test task list fails without authentication."""
        response = client.get("/api/tasks/")

        assert response.status_code == 403

    def test_get_task_success(self, client, auth_token, sample_task):
        """Test successful single task retrieval."""
        response = client.get(
            f"/api/tasks/{sample_task['id']}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_task["id"]
        assert data["title"] == "Sample task"

    def test_get_task_not_found(self, client, auth_token):
        """Test getting non-existent task."""
        response = client.get(
            "/api/tasks/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 404

    def test_list_tasks_filter_by_status(self, client, auth_token, sample_task):
        """Test filtering tasks by status."""
        # Create another task with different status
        client.post(
            "/api/tasks/",
            json={
                "title": "In progress task",
                "status": "in_progress",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Filter by pending status
        response = client.get(
            "/api/tasks/?status=pending",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"

    def test_list_tasks_filter_by_priority(self, client, auth_token):
        """Test filtering tasks by priority."""
        client.post(
            "/api/tasks/",
            json={
                "title": "High priority",
                "priority": "high",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        client.post(
            "/api/tasks/",
            json={
                "title": "Low priority",
                "priority": "low",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Filter by high priority
        response = client.get(
            "/api/tasks/?priority=high",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == "high"

    def test_list_tasks_pagination(self, client, auth_token):
        """Test task list pagination."""
        # Create multiple tasks
        for i in range(5):
            client.post(
                "/api/tasks/",
                json={"title": f"Task {i}"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )

        # Get first page (limit=2)
        response = client.get(
            "/api/tasks/?skip=0&limit=2",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestTaskUpdate:
    """Test cases for task update endpoint."""

    @pytest.fixture
    def sample_task(self, client, auth_token):
        """Create a sample task for update tests."""
        response = client.post(
            "/api/tasks/",
            json={
                "title": "Original title",
                "description": "Original description",
                "priority": "low",
                "status": "pending",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        return response.json()

    def test_update_task_success(self, client, auth_token, sample_task):
        """Test successful task update."""
        response = client.put(
            f"/api/tasks/{sample_task['id']}",
            json={
                "title": "Updated title",
                "priority": "high",
                "status": "in_progress",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["priority"] == "high"
        assert data["status"] == "in_progress"
        assert data["description"] == "Original description"  # Unchanged

    def test_update_task_partial(self, client, auth_token, sample_task):
        """Test partial task update."""
        response = client.put(
            f"/api/tasks/{sample_task['id']}",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["title"] == "Original title"  # Unchanged

    def test_update_task_no_auth(self, client, sample_task):
        """Test task update fails without authentication."""
        response = client.put(
            f"/api/tasks/{sample_task['id']}",
            json={"title": "New title"},
        )

        assert response.status_code == 403

    def test_update_task_not_found(self, client, auth_token):
        """Test updating non-existent task."""
        response = client.put(
            "/api/tasks/00000000-0000-0000-0000-000000000000",
            json={"title": "Updated"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 404


class TestTaskDeletion:
    """Test cases for task deletion endpoint."""

    @pytest.fixture
    def sample_task(self, client, auth_token):
        """Create a sample task for deletion tests."""
        response = client.post(
            "/api/tasks/",
            json={"title": "Task to delete"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        return response.json()

    def test_delete_task_success(self, client, auth_token, sample_task):
        """Test successful task deletion."""
        response = client.delete(
            f"/api/tasks/{sample_task['id']}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 204

        # Verify task is deleted
        get_response = client.get(
            f"/api/tasks/{sample_task['id']}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert get_response.status_code == 404

    def test_delete_task_no_auth(self, client, sample_task):
        """Test task deletion fails without authentication."""
        response = client.delete(f"/api/tasks/{sample_task['id']}")

        assert response.status_code == 403

    def test_delete_task_not_found(self, client, auth_token):
        """Test deleting non-existent task."""
        response = client.delete(
            "/api/tasks/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 404


class TestTaskAccessControl:
    """Test cases for task access control."""

    @pytest.fixture
    def user1_task(self, client, auth_token):
        """Create a task for user 1."""
        response = client.post(
            "/api/tasks/",
            json={"title": "User 1 task"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        return response.json()

    def test_user_cannot_access_other_user_task(
        self, client, auth_token, another_auth_token, user1_task
    ):
        """Test user cannot access another user's task."""
        response = client.get(
            f"/api/tasks/{user1_task['id']}",
            headers={"Authorization": f"Bearer {another_auth_token}"},
        )

        assert response.status_code == 403

    def test_user_cannot_update_other_user_task(
        self, client, auth_token, another_auth_token, user1_task
    ):
        """Test user cannot update another user's task."""
        response = client.put(
            f"/api/tasks/{user1_task['id']}",
            json={"title": "Hacked!"},
            headers={"Authorization": f"Bearer {another_auth_token}"},
        )

        assert response.status_code == 403

    def test_user_cannot_delete_other_user_task(
        self, client, auth_token, another_auth_token, user1_task
    ):
        """Test user cannot delete another user's task."""
        response = client.delete(
            f"/api/tasks/{user1_task['id']}",
            headers={"Authorization": f"Bearer {another_auth_token}"},
        )

        assert response.status_code == 403
