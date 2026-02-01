"""Authentication service for user registration and login.

Provides password hashing, verification, and JWT token generation.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Password hashing context - use pbkdf2_sha256 as primary with bcrypt fallback
# pbkdf2_sha256: Industry-standard, no external dependencies, configurable rounds
# bcrypt: Added for backwards compatibility and additional security
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
    pbkdf2_sha256__rounds=29000,  # OWASP recommended rounds
)

# JWT configuration from environment
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))
REFRESH_TOKEN_EXPIRATION_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRATION_DAYS", 7))


def hash_password(password: str) -> str:
    """Hash a plain text password using PBKDF2-SHA256.

    Args:
        password: Plain text password

    Returns:
        str: PBKDF2-SHA256 hashed password

    Example:
        >>> hashed = hash_password("my_secure_password")
        >>> verify_password("my_secure_password", hashed)
        True
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: PBKDF2-SHA256 or bcrypt hash to check against

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> Tuple[str, datetime]:
    """Create a JWT access token.

    Args:
        subject: Subject to encode (usually user ID)
        expires_delta: Custom expiration delta (default: 24 hours)

    Returns:
        Tuple[str, datetime]: (token, expiration_datetime)
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)

    to_encode = {"sub": str(subject), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return encoded_jwt, expire


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> Tuple[str, datetime]:
    """Create a JWT refresh token.

    Args:
        subject: Subject to encode (usually user ID)
        expires_delta: Custom expiration delta (default: 7 days)

    Returns:
        Tuple[str, datetime]: (token, expiration_datetime)
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return encoded_jwt, expire


def verify_token(token: str) -> Optional[str]:
    """Verify and decode a JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Optional[str]: Subject (user ID) if valid, None if invalid

    Example:
        >>> user_id = verify_token(access_token)
        >>> if user_id:
        ...     print(f"Token is valid for user {user_id}")
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        subject: str = payload.get("sub")
        if subject is None:
            return None
        return subject
    except JWTError:
        return None


def create_tokens(subject: str) -> dict:
    """Create both access and refresh tokens.

    Args:
        subject: Subject to encode (usually user ID)

    Returns:
        dict: Dictionary with access_token, refresh_token, token_type, expires_in
    """
    access_token, access_expire = create_access_token(subject)
    refresh_token, refresh_expire = create_refresh_token(subject)

    # Calculate seconds until expiration
    now = datetime.now(timezone.utc)
    expires_in = int((access_expire - now).total_seconds())

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }
