"""Response helper utilities.

Provides helper functions for creating standardized success and error responses.
"""

from typing import Any, Optional
from fastapi.responses import JSONResponse
from app.schemas.shared import SuccessResponse, ErrorResponse, ErrorDetail, PaginatedResponse


def create_success_response(
    data: Any,
    status_code: int = 200,
) -> JSONResponse:
    """Create a standardized success response.

    Args:
        data: Response payload
        status_code: HTTP status code (default: 200)

    Returns:
        JSONResponse: Formatted success response
    """
    response = SuccessResponse(data=data)
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


def create_error_response(
    code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Any] = None,
) -> JSONResponse:
    """Create a standardized error response.

    Args:
        code: Machine-readable error code
        message: Human-readable error message
        status_code: HTTP status code (default: 400)
        details: Optional additional error details

    Returns:
        JSONResponse: Formatted error response
    """
    error_detail = ErrorDetail(code=code, message=message, details=details)
    response = ErrorResponse(error=error_detail)
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


def create_paginated_response(
    items: list[Any],
    total: int,
    skip: int,
    limit: int,
    status_code: int = 200,
) -> JSONResponse:
    """Create a standardized paginated response.

    Args:
        items: List of items
        total: Total count (without pagination)
        skip: Number of items skipped
        limit: Number of items per page
        status_code: HTTP status code (default: 200)

    Returns:
        JSONResponse: Formatted paginated response
    """
    response = PaginatedResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )
