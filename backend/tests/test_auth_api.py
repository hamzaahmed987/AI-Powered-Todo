"""
Integration tests for authentication endpoints.

Tests user registration, login, and authentication flow.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db
from app.models import User


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
        db.query(User).delete()
        db.commit()
        db.close()


class TestUserRegistration:
    """Test cases for user registration endpoint."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePassword123",
                "full_name": "Test User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert "id" in data
        assert "password_hash" not in data

    def test_register_missing_email(self, client):
        """Test registration fails without email."""
        response = client.post(
            "/api/auth/register",
            json={
                "password": "SecurePassword123",
                "full_name": "Test User",
            },
        )

        assert response.status_code == 422

    def test_register_missing_password(self, client):
        """Test registration fails without password."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User",
            },
        )

        assert response.status_code == 422

    def test_register_password_too_short(self, client):
        """Test registration fails with password < 12 chars."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",
                "full_name": "Test User",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "at least 12 characters" in data["detail"]

    def test_register_duplicate_email(self, client, db_session):
        """Test registration fails with duplicate email."""
        # Register first user
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePassword123",
                "full_name": "Test User",
            },
        )

        # Try to register with same email
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePassword456",
                "full_name": "Another User",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"]

    def test_register_invalid_email(self, client):
        """Test registration fails with invalid email format."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "SecurePassword123",
                "full_name": "Test User",
            },
        )

        assert response.status_code == 422


class TestUserLogin:
    """Test cases for user login endpoint."""

    @pytest.fixture
    def registered_user(self, client):
        """Register a user for login tests."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePassword123",
                "full_name": "Test User",
            },
        )
        assert response.status_code == 201
        return response.json()

    def test_login_success(self, client, registered_user):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "SecurePassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_email(self, client):
        """Test login with non-existent email."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Password123",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid email or password" in data["detail"]

    def test_login_invalid_password(self, client, registered_user):
        """Test login with incorrect password."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword123",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid email or password" in data["detail"]

    def test_login_missing_email(self, client):
        """Test login fails without email."""
        response = client.post(
            "/api/auth/login",
            json={"password": "Password123"},
        )

        assert response.status_code == 422

    def test_login_missing_password(self, client):
        """Test login fails without password."""
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com"},
        )

        assert response.status_code == 422


class TestAuthenticatedEndpoints:
    """Test cases for endpoints requiring authentication."""

    @pytest.fixture
    def auth_token(self, client):
        """Get an authentication token."""
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

    def test_get_current_user_success(self, client, auth_token):
        """Test getting current user with valid token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert "password_hash" not in data

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/api/auth/me")

        assert response.status_code == 403

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        assert response.status_code == 403

    def test_logout_endpoint_exists(self, client, auth_token):
        """Test logout endpoint returns 200."""
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
