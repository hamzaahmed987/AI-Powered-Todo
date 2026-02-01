"""
Integration tests for task endpoints.

Tests task creation, retrieval, update, deletion, and access control.
"""

import pytest
from fastapi.testclient import TestClient
from uuid import UUID
from datetime import datetime

from app.models.task import TaskStatus, TaskPriority


class TestTaskAPI:
    """Test cases for task endpoints."""

    def test_task_lifecycle(self, client, auth_headers, test_user):
        """Test complete task lifecycle: create, read, update, delete."""
        # Create a task
        create_response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description",
                "estimated_duration": 60
            },
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        created_task = create_response.json()["data"]
        assert created_task["title"] == "Test Task"
        assert created_task["description"] == "Test Description"
        assert created_task["status"] == "pending"
        assert created_task["priority"] == "medium"
        assert created_task["estimated_duration"] == 60
        
        task_id = created_task["id"]
        
        # Retrieve the task
        get_response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        assert get_response.status_code == 200
        retrieved_task = get_response.json()["data"]
        assert retrieved_task["id"] == task_id
        assert retrieved_task["title"] == "Test Task"
        
        # Update the task
        update_response = client.put(
            f"/api/v1/tasks/{task_id}",
            json={
                "title": "Updated Task",
                "status": "in_progress",
                "priority": "high"
            },
            headers=auth_headers
        )
        assert update_response.status_code == 200
        updated_task = update_response.json()["data"]
        assert updated_task["title"] == "Updated Task"
        assert updated_task["status"] == "in_progress"
        assert updated_task["priority"] == "high"
        
        # List tasks
        list_response = client.get("/api/v1/tasks", headers=auth_headers)
        assert list_response.status_code == 200
        tasks_list = list_response.json()["data"]
        assert tasks_list["items"]
        assert any(task["id"] == task_id for task in tasks_list["items"])
        
        # Delete the task
        delete_response = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        assert delete_response.status_code == 204
        
        # Verify task is deleted
        get_deleted_response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        assert get_deleted_response.status_code == 404

    def test_task_validation_errors(self, client, auth_headers):
        """Test task validation errors."""
        # Try to create task without title
        response = client.post(
            "/api/v1/tasks",
            json={"description": "Task without title"},
            headers=auth_headers
        )
        assert response.status_code == 400  # Validation error
        
        # Try to create task with invalid priority
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "priority": "invalid_priority"
            },
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error from Pydantic
        
        # Try to create task with too long title
        long_title = "x" * 501
        response = client.post(
            "/api/v1/tasks",
            json={"title": long_title},
            headers=auth_headers
        )
        assert response.status_code == 400  # Validation error

    def test_task_filters(self, client, auth_headers, test_user):
        """Test task filtering by status and priority."""
        # Create tasks with different statuses and priorities
        client.post(
            "/api/v1/tasks",
            json={"title": "Pending Low Task", "status": "pending", "priority": "low"},
            headers=auth_headers
        )
        client.post(
            "/api/v1/tasks",
            json={"title": "Pending High Task", "status": "pending", "priority": "high"},
            headers=auth_headers
        )
        client.post(
            "/api/v1/tasks",
            json={"title": "In Progress Task", "status": "in_progress", "priority": "medium"},
            headers=auth_headers
        )
        
        # Filter by status
        response = client.get("/api/v1/tasks?status=pending", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()["data"]
        pending_tasks = [task for task in data["items"] if task["status"] == "pending"]
        assert len(pending_tasks) == 2
        
        # Filter by priority
        response = client.get("/api/v1/tasks?priority=high", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()["data"]
        high_priority_tasks = [task for task in data["items"] if task["priority"] == "high"]
        assert len(high_priority_tasks) == 1

    def test_task_pagination(self, client, auth_headers):
        """Test task pagination."""
        # Create multiple tasks
        for i in range(5):
            client.post(
                "/api/v1/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers
            )
        
        # Test pagination
        response = client.get("/api/v1/tasks?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["items"]) == 2
        assert data["total"] >= 5

    def test_unauthorized_access(self, client, test_task):
        """Test that unauthorized users cannot access tasks."""
        # Try to access without auth headers
        response = client.get(f"/api/v1/tasks/{test_task.id}")
        assert response.status_code == 401  # Unauthorized
        
        # Try to create without auth headers
        response = client.post("/api/v1/tasks", json={"title": "Unauthorized task"})
        assert response.status_code == 401  # Unauthorized

    def test_task_not_found(self, client, auth_headers):
        """Test accessing non-existent task."""
        fake_uuid = "12345678-1234-5678-9012-123456789012"
        response = client.get(f"/api/v1/tasks/{fake_uuid}", headers=auth_headers)
        assert response.status_code == 404

    def test_task_update_validation(self, client, auth_headers):
        """Test validation during task updates."""
        # Create a task first
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Update Test Task"},
            headers=auth_headers
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        
        # Try to update with invalid status
        response = client.put(
            f"/api/v1/tasks/{task_id}",
            json={"status": "invalid_status"},
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error from Pydantic
        
        # Try to update with empty title
        response = client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": ""},
            headers=auth_headers
        )
        assert response.status_code == 400  # Validation error from business logic

    def test_task_estimated_duration(self, client, auth_headers):
        """Test task estimated duration functionality."""
        # Create task with estimated duration
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Task with Duration",
                "estimated_duration": 120  # 2 hours
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        task = response.json()["data"]
        assert task["estimated_duration"] == 120
        
        # Update estimated duration
        task_id = task["id"]
        response = client.put(
            f"/api/v1/tasks/{task_id}",
            json={"estimated_duration": 180},  # 3 hours
            headers=auth_headers
        )
        assert response.status_code == 200
        updated_task = response.json()["data"]
        assert updated_task["estimated_duration"] == 180
        
        # Test invalid estimated duration
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Task with Invalid Duration",
                "estimated_duration": 0  # Should be invalid
            },
            headers=auth_headers
        )
        assert response.status_code == 400  # Validation error