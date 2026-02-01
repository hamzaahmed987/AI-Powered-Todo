"""Shared Pydantic schemas used across API.

Common response types, error handling, and pagination.
"""

from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Error detail information.

    Attributes:
        code: Machine-readable error code
        message: Human-readable error message
        details: Optional additional error details
    """
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response format.

    Attributes:
        status: Always "error"
        error: ErrorDetail object with error information
    """
    status: str = "error"
    error: ErrorDetail


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response format.

    Attributes:
        status: Always "success"
        data: Response payload (generic type)
    """
    status: str = "success"
    data: T


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints.

    Attributes:
        skip: Number of items to skip (default: 0)
        limit: Number of items to return (default: 20, max: 100)
    """
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response with metadata.

    Attributes:
        status: Always "success"
        items: List of items
        total: Total count of items (without pagination)
        skip: Number of items skipped
        limit: Number of items per page
    """
    status: str = "success"
    items: list[T]
    total: int
    skip: int
    limit: int


class AuthToken(BaseModel):
    """Authentication token response.

    Attributes:
        access_token: JWT access token
        refresh_token: JWT refresh token (for token renewal)
        token_type: Token type (always "bearer")
        expires_in: Token expiration time in seconds
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    """Simple message response.

    Attributes:
        status: Response status
        message: Message text
    """
    status: str
    message: str
