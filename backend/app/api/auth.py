"""Authentication API endpoints.

Handles user registration, login, and token refresh.
"""

from fastapi import APIRouter, Depends, status, Query, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserResponse, UserLogin
from app.schemas.shared import AuthToken
from app.services.user_service import create_user, get_user_by_email
from app.services.auth_service import verify_password, create_tokens
from app.dependencies import get_current_user
from app.utils.exceptions import InvalidCredentialsError, ValidationError
from app.utils.response import create_success_response
from app.utils.logger import logger

router = APIRouter()


class RegisterResponse(BaseModel):
    """Registration response with both user and token for auto-login."""
    user: UserResponse
    access_token: str
    token_type: str
    expires_in: int


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    tags=["Authentication"],
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    """Register a new user account and return authentication token.

    **Request Body**:
    - `email`: User email address (must be unique)
    - `password`: Password (minimum 12 characters)
    - `full_name`: User's display name (optional)

    **Response**: User object + authentication token (201 Created)

    **Errors**:
    - 400: Invalid email or weak password
    - 409: Email already exists
    """
    logger.info(f"User registration attempt for email: {user_data.email}")

    # Validate password strength
    if len(user_data.password) < 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 12 characters long"
        )

    if not any(c.isupper() for c in user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one uppercase letter"
        )

    if not any(c.islower() for c in user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one lowercase letter"
        )

    if not any(c.isdigit() for c in user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one number"
        )

    # Check if email already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        logger.warning(f"Registration failed: email already exists {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered. Please login instead."
        )

    try:
        # Create user
        user = create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
        )
        logger.info(f"User registered successfully: {user.email}")

        # Auto-generate token for immediate login (better UX)
        token_data = create_tokens(str(user.id))
        logger.info(f"Auto-login token created for: {user.email}, user_id={user.id}, user_id_type={type(user.id)}")

        return RegisterResponse(
            user=UserResponse.model_validate(user),
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data.get("expires_in", 86400),
        )

    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise


@router.post(
    "/login",
    response_model=AuthToken,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    tags=["Authentication"],
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """Login with email and password.

    **Request Body**:
    - `email`: User email
    - `password`: User password

    **Response**: Authentication tokens (200 OK)

    **Errors**:
    - 401: Invalid credentials (email not found or wrong password)
    - 403: Account is inactive
    """
    logger.info(f"Login attempt for email: {credentials.email}")

    # Find user by email
    user = get_user_by_email(db, credentials.email)

    if not user:
        logger.warning(f"Login failed: user not found for email {credentials.email}")
        # Return specific error for email not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found. Please check your email or sign up."
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        logger.warning(f"Login failed: invalid password for user {credentials.email}")
        # Return specific error for incorrect password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please try again."
        )

    if not user.is_active:
        logger.warning(f"Login failed: user account inactive {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled. Please contact support."
        )

    # Create tokens
    token_data = create_tokens(str(user.id))
    logger.info(f"User logged in successfully: {user.email}")

    return AuthToken(**token_data)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    tags=["Authentication"],
)
def get_current_user_info(
    user: User = Depends(get_current_user),
):
    """Get information about the currently authenticated user.

    **Response**: Current user object (200 OK)

    **Errors**:
    - 401: Unauthorized (missing or invalid token)
    """
    return UserResponse.model_validate(user)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    tags=["Authentication"],
)
def logout(
    user: User = Depends(get_current_user),
):
    """Logout the current user.

    Note: Logout is handled on the frontend by removing tokens.
    This endpoint is provided for completeness and future extensions.

    **Response**: Success message (200 OK)

    **Errors**:
    - 401: Unauthorized
    """
    logger.info(f"User logged out: {user.email}")
    return {"status": "success", "message": "Logged out successfully"}


class EmailCheckResponse(BaseModel):
    """Email check response."""
    exists: bool
    message: str


@router.get(
    "/check-email",
    response_model=EmailCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Check if email is registered",
    tags=["Authentication"],
)
def check_email(
    email: str = Query(..., description="Email address to check"),
    db: Session = Depends(get_db),
):
    """Check if an email address is already registered.

    This endpoint is used for:
    - Login screen: Warn user if email is not registered
    - Register screen: Warn user if email is already taken

    **Query Parameters**:
    - `email`: Email address to check

    **Response**: Object with exists (boolean) and message (200 OK)

    **Errors**:
    - 400: Invalid email format
    """
    # Validate email format
    if not email or '@' not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Normalize email to lowercase for case-insensitive comparison
    email_lower = email.lower().strip()

    logger.info(f"Email check request for: {email_lower}")

    # Check if user exists in database
    user = get_user_by_email(db, email_lower)

    if user:
        logger.info(f"Email check: {email_lower} is registered")
        return EmailCheckResponse(
            exists=True,
            message="Email is already registered"
        )
    else:
        logger.info(f"Email check: {email_lower} is available")
        return EmailCheckResponse(
            exists=False,
            message="Email is available"
        )
