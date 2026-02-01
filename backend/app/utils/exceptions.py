"""Custom exception classes for the application.

Provides standardized exceptions with HTTP status codes and error messages.
"""

from typing import Any, Optional


class AppException(Exception):
    """Base application exception.

    All custom exceptions inherit from this class.
    """

    def __init__(self, code: str, message: str, status_code: int = 500, details: Optional[Any] = None):
        """Initialize exception.

        Args:
            code: Machine-readable error code
            message: Human-readable error message
            status_code: HTTP status code (default: 500)
            details: Optional additional error details
        """
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class InvalidCredentialsError(AppException):
    """Raised when authentication credentials are invalid.

    HTTP Status: 401 Unauthorized
    """

    def __init__(self, message: str = "Invalid credentials", details: Optional[Any] = None):
        super().__init__(
            code="INVALID_CREDENTIALS",
            message=message,
            status_code=401,
            details=details,
        )


class ForbiddenError(AppException):
    """Raised when user lacks required permissions.

    HTTP Status: 403 Forbidden
    """

    def __init__(self, message: str = "Access forbidden", details: Optional[Any] = None):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=403,
            details=details,
        )


class NotFoundError(AppException):
    """Raised when requested resource does not exist.

    HTTP Status: 404 Not Found
    """

    def __init__(self, resource: str = "Resource", details: Optional[Any] = None):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} not found",
            status_code=404,
            details=details,
        )


class ValidationError(AppException):
    """Raised when request validation fails.

    HTTP Status: 400 Bad Request
    """

    def __init__(self, message: str = "Validation failed", details: Optional[Any] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=400,
            details=details,
        )


class ConflictError(AppException):
    """Raised when request conflicts with existing resource.

    HTTP Status: 409 Conflict
    """

    def __init__(self, message: str = "Resource conflict", details: Optional[Any] = None):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409,
            details=details,
        )


class AIUnavailableError(AppException):
    """Raised when AI service is temporarily unavailable.

    HTTP Status: 503 Service Unavailable
    Indicates graceful degradation - operation can continue without AI features.
    """

    def __init__(self, message: str = "AI service temporarily unavailable", details: Optional[Any] = None):
        super().__init__(
            code="AI_UNAVAILABLE",
            message=message,
            status_code=503,
            details=details,
        )


class DatabaseError(AppException):
    """Raised when database operation fails.

    HTTP Status: 500 Internal Server Error
    """

    def __init__(self, message: str = "Database error", details: Optional[Any] = None):
        super().__init__(
            code="DATABASE_ERROR",
            message=message,
            status_code=500,
            details=details,
        )


class UnauthorizedError(AppException):
    """Raised when request lacks authentication.

    HTTP Status: 401 Unauthorized
    """

    def __init__(self, message: str = "Authentication required", details: Optional[Any] = None):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=401,
            details=details,
        )
