"""User-related Pydantic schemas.

Schemas for user registration, login, and responses.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserRegister(BaseModel):
    """User registration request schema.

    Attributes:
        email: User email address
        password: User password (min 12 characters)
        full_name: User's display name (optional)
    """
    email: EmailStr
    password: str = Field(..., min_length=12, description="Minimum 12 characters")
    full_name: Optional[str] = Field(None, max_length=255)


class UserLogin(BaseModel):
    """User login request schema.

    Attributes:
        email: User email address
        password: User password
    """
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema (public data).

    Attributes:
        id: User UUID
        email: User email
        full_name: User's display name
        is_active: Whether account is active
        created_at: Account creation timestamp
    """
    id: UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    """User database schema (internal use).

    Includes password hash for internal authentication operations.

    Attributes:
        password_hash: Bcrypt hashed password
    """
    password_hash: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update request schema.

    All fields are optional for partial updates.

    Attributes:
        full_name: Updated display name
        email: Updated email (unique)
    """
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None

    class Config:
        from_attributes = True
