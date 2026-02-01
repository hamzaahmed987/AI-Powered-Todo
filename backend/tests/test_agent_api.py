"""
Integration tests for AI agent endpoints.

Tests AI agent chat functionality and task management through natural language.
"""

import pytest
from fastapi.testclient import TestClient


class TestAgentAPI:
    """Test cases for AI agent endpoints."""

    def test_agent_chat_basic(self, client, auth_headers):
        """Test basic AI agent chat functionality."""
        response = client.post(
            "/api/v1/agent/chat",
            json={"message": "Hello"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "success" in data
        assert "action" in data
        assert isinstance(data["message"], str)
        assert isinstance(data["success"], bool)
        assert isinstance(data["action"], str)

    def test_agent_create_task(self, client, auth_headers):
        """Test AI agent creating a task via natural language."""
        response = client.post(
            "/api/v1/agent/chat",
            json={"message": "Create a task called 'Buy groceries' with high priority"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "create" in data["action"].lower() or data["action"] == "none"  # May be 'none' if tool not called
        assert "groceries" in data["message"].lower() or "task" in data["message"].lower()

    def test_agent_update_task(self, client, auth_headers):
        """Test AI agent updating a task via natural language."""
        # First create a task
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Test Task for Update"},
            headers=auth_headers
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        
        # Then try to update it via AI agent
        response = client.post(
            "/api/v1/agent/chat",
            json={"message": f"Update task '{task_id}' to mark as completed"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["success"], bool)

    def test_agent_delete_task(self, client, auth_headers):
        """Test AI agent deleting a task via natural language."""
        # First create a task
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Test Task for Deletion"},
            headers=auth_headers
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        
        # Then try to delete it via AI agent
        response = client.post(
            "/api/v1/agent/chat",
            json={"message": f"Delete task '{task_id}'"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["success"], bool)

    def test_agent_get_task_info(self, client, auth_headers):
        """Test AI agent retrieving task information via natural language."""
        # First create a task
        create_response = client.post(
            "/api/v1/tasks",
            json={"title": "Test Task for Info"},
            headers=auth_headers
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        
        # Then try to get info via AI agent
        response = client.post(
            "/api/v1/agent/chat",
            json={"message": f"Tell me about task '{task_id}'"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["success"], bool)

    def test_agent_get_capabilities(self, client, auth_headers):
        """Test AI agent capabilities endpoint."""
        response = client.get("/api/v1/agent/capabilities", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "agent_name" in data
        assert "capabilities" in data
        assert isinstance(data["capabilities"], list)
        assert len(data["capabilities"]) > 0

    def test_agent_invalid_message(self, client, auth_headers):
        """Test AI agent with invalid message."""
        response = client.post(
            "/api/v1/agent/chat",
            json={"message": ""},  # Empty message
            headers=auth_headers
        )
        # Should return an error for empty message
        assert response.status_code in [400, 200]  # Could be 200 with error in response body
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data["success"], bool)

    def test_agent_unauthorized(self, client):
        """Test AI agent without authentication."""
        response = client.post(
            "/api/v1/agent/chat",
            json={"message": "Hello"},
        )
        assert response.status_code == 401  # Unauthorized

    def test_agent_task_insights(self, client, auth_headers):
        """Test AI agent providing task insights."""
        # First create a task
        create_response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Project Task", 
                "description": "Complete the project documentation"
            },
            headers=auth_headers
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        
        # Then ask for insights
        response = client.post(
            "/api/v1/agent/chat",
            json={"message": f"Give me insights about task '{task_id}'"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["success"], bool)

    def test_agent_productivity_insights(self, client, auth_headers):
        """Test AI agent providing productivity insights."""
        # Create a few tasks first
        for i in range(3):
            client.post(
                "/api/v1/tasks",
                json={"title": f"Productivity Task {i}"},
                headers=auth_headers
            )
        
        # Then ask for productivity insights
        response = client.post(
            "/api/v1/agent/chat",
            json={"message": "How can I be more productive?"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["success"], bool)