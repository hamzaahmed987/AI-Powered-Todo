"""Application configuration.

Reads from environment variables and provides centralized configuration access.
"""

from dataclasses import dataclass, field
from typing import Optional
import os


@dataclass
class Settings:
    """Application settings loaded from environment variables.

    All configuration should be read from environment variables to support
    different deployment environments (development, staging, production).
    """

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/todo_app",
    )

    # Gemini & AI Services
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")

    # JWT Authentication
    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY",
        "your-secret-key-change-in-production",
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", 24))
    refresh_token_expiration_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRATION_DAYS", 7))

    # Server Configuration
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))

    # CORS & Security
    # For mobile apps, we need to allow all origins since mobile apps don't send Origin headers
    # React Native and other mobile apps require ALLOWED_ORIGINS="*" to work properly
    allowed_origins: list[str] = field(default_factory=lambda: [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "*"  # Default: Allow all origins for mobile app support (React Native, Flutter, etc.)
        ).split(",")
    ])

    # Allow credentials - MUST be False when allowed_origins includes "*" (CORS spec requirement)
    # For mobile apps using JWT tokens in Authorization header, credentials=False is fine
    @property
    def allow_credentials(self) -> bool:
        """Determine if credentials should be allowed based on origins.

        CORS specification requires allow_credentials=False when allow_origins=["*"].
        This is fine for mobile apps since they use Authorization header for JWT tokens,
        not cookies (which require credentials=True).
        """
        return "*" not in self.allowed_origins

    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # AI Feature Configuration
    ai_timeout_seconds: int = int(os.getenv("AI_TIMEOUT_SECONDS", 3))
    ai_rate_limit_calls: int = int(os.getenv("AI_RATE_LIMIT_CALLS", 10))
    ai_rate_limit_window: int = int(os.getenv("AI_RATE_LIMIT_WINDOW", 60))

    # Application Metadata
    app_name: str = "Todo App API"
    app_version: str = "0.1.0"
    app_description: str = "AI-Powered Todo Application with task management and AI suggestions"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def __post_init__(self):
        """Validate settings after initialization."""
        if self.is_production and self.jwt_secret_key == "your-secret-key-change-in-production":
            raise ValueError("JWT_SECRET_KEY must be set in production environment")

        if not self.gemini_api_key and not self.is_development:
            raise ValueError("GEMINI_API_KEY must be set for non-development environments")


# Global settings instance
settings = Settings()
