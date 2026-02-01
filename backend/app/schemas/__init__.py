"""Schemas package.

Exports all Pydantic schemas for convenient importing.
"""

from .shared import (
    ErrorDetail,
    ErrorResponse,
    SuccessResponse,
    PaginationParams,
    PaginatedResponse,
    AuthToken,
    MessageResponse,
)
from .user import UserRegister, UserLogin, UserResponse, UserInDB, UserUpdate
from .task import TaskCreate, TaskUpdate, TaskResponse, TaskInDB, TaskListParams

__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "SuccessResponse",
    "PaginationParams",
    "PaginatedResponse",
    "AuthToken",
    "MessageResponse",
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "UserInDB",
    "UserUpdate",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskInDB",
    "TaskListParams",
]
